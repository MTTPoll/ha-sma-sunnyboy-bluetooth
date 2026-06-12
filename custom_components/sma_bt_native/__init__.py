from __future__ import annotations

from datetime import datetime, timedelta
import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_AC_INTERVAL,
    CONF_BT_ADDRESS,
    CONF_ENERGY_TODAY_INTERVAL,
    CONF_ENERGY_TOTAL_INTERVAL,
    CONF_PASSWORD,
    CONF_TEMPERATURE_INTERVAL,
    DEFAULT_AC_INTERVAL,
    DEFAULT_ENERGY_TODAY_INTERVAL,
    DEFAULT_ENERGY_TOTAL_INTERVAL,
    DEFAULT_TEMPERATURE_INTERVAL,
    DOMAIN,
    BINARY_SENSOR_CONNECTED,
    SENSOR_AC_POWER,
    SENSOR_ENERGY_TODAY,
    SENSOR_ENERGY_TOTAL,
    SENSOR_OPERATION_TIME,
    SENSOR_FEED_IN_TIME,
    SENSOR_TEMPERATURE,
)
from .protocol import SMABluetoothClient
from .bluetooth import extract_serial_from_name, read_device_name
from .device import DEVICE_INFO_KEY

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the SMA Sunny Boy Bluetooth Home Assistant Integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


_READ_INTERVAL_KEYS = {
    SENSOR_AC_POWER: CONF_AC_INTERVAL,
    SENSOR_ENERGY_TODAY: CONF_ENERGY_TODAY_INTERVAL,
    SENSOR_ENERGY_TOTAL: CONF_ENERGY_TOTAL_INTERVAL,
    SENSOR_OPERATION_TIME: CONF_ENERGY_TOTAL_INTERVAL,
    SENSOR_FEED_IN_TIME: CONF_ENERGY_TOTAL_INTERVAL,
    SENSOR_TEMPERATURE: CONF_TEMPERATURE_INTERVAL,
}
_DEFAULT_INTERVALS = {
    CONF_AC_INTERVAL: DEFAULT_AC_INTERVAL,
    CONF_ENERGY_TODAY_INTERVAL: DEFAULT_ENERGY_TODAY_INTERVAL,
    CONF_ENERGY_TOTAL_INTERVAL: DEFAULT_ENERGY_TOTAL_INTERVAL,
    CONF_TEMPERATURE_INTERVAL: DEFAULT_TEMPERATURE_INTERVAL,
}


def _interval(entry: ConfigEntry, key: str) -> int:
    return int(entry.options.get(key, entry.data.get(key, _DEFAULT_INTERVALS[key])))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    cache: dict[str, Any] = {
        SENSOR_AC_POWER: None,
        SENSOR_ENERGY_TODAY: None,
        SENSOR_ENERGY_TOTAL: None,
        SENSOR_OPERATION_TIME: None,
        SENSOR_FEED_IN_TIME: None,
        SENSOR_TEMPERATURE: None,
        BINARY_SENSOR_CONNECTED: False,
        DEVICE_INFO_KEY: {},
    }
    last_update: dict[str, datetime | None] = {
        SENSOR_AC_POWER: None,
        SENSOR_ENERGY_TODAY: None,
        SENSOR_ENERGY_TOTAL: None,
        SENSOR_OPERATION_TIME: None,
        SENSOR_FEED_IN_TIME: None,
        SENSOR_TEMPERATURE: None,
    }
    last_success: datetime | None = None
    sleep_retry_after: datetime | None = None
    connected_grace = timedelta(minutes=5)
    sleeping_backoff = timedelta(minutes=5)
    startup_backoff = timedelta(seconds=30)
    client = SMABluetoothClient(
        entry.data[CONF_BT_ADDRESS],
        entry.data[CONF_PASSWORD],
        timeout=8,
    )
    device_info_loaded = False
    last_device_info_attempt: datetime | None = None
    device_info_retry = timedelta(minutes=30)

    async def _update_ha_device_registry(info: dict[str, Any]) -> None:
        """Push dynamic device metadata into Home Assistant's device registry."""
        try:
            registry = dr.async_get(hass)
            device = registry.async_get_device(identifiers={(DOMAIN, entry.data[CONF_BT_ADDRESS])})
            if not device:
                return
            # Keep this deliberately conservative. Some HA versions do not
            # accept name/default_name here; one unsupported keyword would make
            # the whole device-registry update fail. Entity device_info provides
            # the display name, while the registry update only patches metadata.
            kwargs: dict[str, Any] = {"manufacturer": "SMA"}
            if info.get("model"):
                kwargs["model"] = info["model"]
            if info.get("serial_number"):
                kwargs["serial_number"] = info["serial_number"]
            if info.get("sw_version"):
                kwargs["sw_version"] = info["sw_version"]
            registry.async_update_device(device.id, **kwargs)
        except Exception as err:
            _LOGGER.debug("Could not update SMA device registry metadata: %s", err)

    async def _read_and_cache_device_info() -> None:
        nonlocal device_info_loaded
        if device_info_loaded:
            return

        bt_address = entry.data[CONF_BT_ADDRESS]
        try:
            bt_name = await hass.async_add_executor_job(read_device_name, bt_address)
        except Exception:
            bt_name = None
        serial = extract_serial_from_name(bt_name)

        try:
            proto_info = await hass.async_add_executor_job(client.read_device_info)
        except Exception as err:
            _LOGGER.debug("SMA protocol device info read failed: %s", err)
            proto_info = None

        info: dict[str, Any] = {}
        if proto_info and proto_info.model:
            info["model"] = proto_info.model
        if proto_info and proto_info.sw_version:
            info["sw_version"] = proto_info.sw_version
        if serial:
            info["serial_number"] = serial
        if info.get("model"):
            info["name"] = f"SMA {info['model']}"
        elif bt_name:
            info["name"] = bt_name

        if info:
            cache[DEVICE_INFO_KEY] = {**cache.get(DEVICE_INFO_KEY, {}), **info}
            await _update_ha_device_registry(cache[DEVICE_INFO_KEY])
            # Serial from BlueZ can be available before the SMA TypeLabel query.
            # Keep retrying until we also have the inverter model from the SMA
            # protocol, but do not spam every 30 s once at least serial is known.
            device_info_loaded = bool(cache[DEVICE_INFO_KEY].get("model"))
            _LOGGER.info("SMA device info: %s", cache[DEVICE_INFO_KEY])

    async def async_update_data():
        nonlocal last_success, sleep_retry_after, last_device_info_attempt
        now = datetime.utcnow()

        # If the inverter is probably asleep, do not hammer Bluetooth every 30 seconds.
        # Keep returning cached data and try again after the backoff window.
        if sleep_retry_after is not None and now < sleep_retry_after:
            cache[BINARY_SENSOR_CONNECTED] = bool(
                last_success and (now - last_success) < connected_grace
            )
            return cache

        wanted = [
            sensor
            for sensor, interval_key in _READ_INTERVAL_KEYS.items()
            if last_update[sensor] is None
            or (now - last_update[sensor]).total_seconds() >= _interval(entry, interval_key)
        ]
        if not wanted:
            return cache

        try:
            def _read_sma():
                return client.read_values(wanted)

            # Important: production values are the primary job of the integration.
            # Device-info protocol reads are optional and must never block or break
            # normal sensor updates. Therefore values are read first.
            values = await hass.async_add_executor_job(_read_sma)
            for key, value in values.items():
                cache[key] = value
                last_update[key] = now
            last_success = now
            sleep_retry_after = None
            cache[BINARY_SENSOR_CONNECTED] = True

            # Opportunistic device-info update. Serial from BlueZ is cheap; the
            # SMA TypeLabel/Firmware protocol query is retried slowly until it
            # succeeds, but failures are ignored so sensor values keep working.
            should_try_device_info = (
                not device_info_loaded
                and (last_device_info_attempt is None or now - last_device_info_attempt >= device_info_retry)
            )
            if should_try_device_info:
                last_device_info_attempt = now
                try:
                    await _read_and_cache_device_info()
                except Exception as info_err:
                    _LOGGER.debug("SMA optional device-info update failed: %s", info_err)

            return cache
        except Exception as err:
            # A sleeping inverter at night looks like connection/login/request timeouts.
            # This is expected for SMA Bluetooth devices, so do not raise UpdateFailed
            # and do not force Home Assistant into a permanent reconnect loop.
            # Before the first successful read, HA may simply be faster than the
            # Bluetooth stack during startup. Retry quickly until we have read
            # the inverter once. After that, use the longer night/sleep backoff.
            sleep_retry_after = now + (startup_backoff if last_success is None else sleeping_backoff)
            cache[BINARY_SENSOR_CONNECTED] = bool(
                last_success and (now - last_success) < connected_grace
            )
            _LOGGER.info(
                "SMA Bluetooth update failed; inverter may be sleeping. "
                "Next retry after %s: %s",
                sleep_retry_after.isoformat(timespec="seconds"),
                err,
            )
            return cache

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="SMA Sunny Boy Bluetooth",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )
    coordinator.sma_client = client

    # Do NOT connect to the inverter during Home Assistant startup.
    # Bluetooth/RFCOMM can block or fail while HAOS is still bringing up other
    # integrations. We publish initial unavailable values, finish setup quickly,
    # and start the first real read only after HA has fully started.
    coordinator.async_set_updated_data(cache)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _refresh_after_ha_started() -> None:
        if entry.entry_id not in hass.data.get(DOMAIN, {}):
            return
        # Give HAOS/Bluetooth a small extra grace period after the started event.
        await asyncio.sleep(30)
        if entry.entry_id not in hass.data.get(DOMAIN, {}):
            return
        await coordinator.async_request_refresh()

    if hass.state == CoreState.running:
        hass.async_create_task(_refresh_after_ha_started())
    else:
        async def _on_ha_started(event) -> None:
            hass.async_create_task(_refresh_after_ha_started())
        # Do not register the one-time listener's remove callback with
        # entry.async_on_unload(). Home Assistant removes listen_once listeners
        # automatically when the event fires; calling the remove callback later
        # can produce "Unable to remove unknown job listener" in the log.
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_ha_started)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        if coordinator and hasattr(coordinator, "sma_client"):
            await hass.async_add_executor_job(coordinator.sma_client.close)
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

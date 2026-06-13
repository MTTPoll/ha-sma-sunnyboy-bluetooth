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
    CONF_BLUETOOTH_SIGNAL_INTERVAL,
    CONF_MPPT_INTERVAL,
    DEFAULT_AC_INTERVAL,
    DEFAULT_ENERGY_TODAY_INTERVAL,
    DEFAULT_ENERGY_TOTAL_INTERVAL,
    DEFAULT_TEMPERATURE_INTERVAL,
    DEFAULT_BLUETOOTH_SIGNAL_INTERVAL,
    DEFAULT_MPPT_INTERVAL,
    DOMAIN,
    BINARY_SENSOR_CONNECTED,
    SENSOR_AC_POWER,
    SENSOR_ENERGY_TODAY,
    SENSOR_ENERGY_TOTAL,
    SENSOR_OPERATION_TIME,
    SENSOR_FEED_IN_TIME,
    SENSOR_BLUETOOTH_SIGNAL,
    SENSOR_MPPT1_POWER,
    SENSOR_MPPT2_POWER,
    SENSOR_DC_TOTAL_POWER,
    SENSOR_EFFICIENCY,
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
    SENSOR_BLUETOOTH_SIGNAL: CONF_BLUETOOTH_SIGNAL_INTERVAL,
    SENSOR_TEMPERATURE: CONF_TEMPERATURE_INTERVAL,
    SENSOR_MPPT1_POWER: CONF_MPPT_INTERVAL,
    SENSOR_MPPT2_POWER: CONF_MPPT_INTERVAL,
    SENSOR_DC_TOTAL_POWER: CONF_MPPT_INTERVAL,
}

_DEFAULT_INTERVALS = {
    CONF_AC_INTERVAL: DEFAULT_AC_INTERVAL,
    CONF_ENERGY_TODAY_INTERVAL: DEFAULT_ENERGY_TODAY_INTERVAL,
    CONF_ENERGY_TOTAL_INTERVAL: DEFAULT_ENERGY_TOTAL_INTERVAL,
    CONF_TEMPERATURE_INTERVAL: DEFAULT_TEMPERATURE_INTERVAL,
    CONF_BLUETOOTH_SIGNAL_INTERVAL: DEFAULT_BLUETOOTH_SIGNAL_INTERVAL,
    CONF_MPPT_INTERVAL: DEFAULT_MPPT_INTERVAL,
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
        SENSOR_BLUETOOTH_SIGNAL: None,
        SENSOR_TEMPERATURE: None,
        SENSOR_MPPT1_POWER: None,
        SENSOR_MPPT2_POWER: None,
        SENSOR_DC_TOTAL_POWER: None,
        SENSOR_EFFICIENCY: None,
        BINARY_SENSOR_CONNECTED: False,
        DEVICE_INFO_KEY: {},
    }

    last_update: dict[str, datetime | None] = {
        SENSOR_AC_POWER: None,
        SENSOR_ENERGY_TODAY: None,
        SENSOR_ENERGY_TOTAL: None,
        SENSOR_OPERATION_TIME: None,
        SENSOR_FEED_IN_TIME: None,
        SENSOR_BLUETOOTH_SIGNAL: None,
        SENSOR_TEMPERATURE: None,
        SENSOR_MPPT1_POWER: None,
        SENSOR_MPPT2_POWER: None,
        SENSOR_DC_TOTAL_POWER: None,
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
            device = registry.async_get_device(
                identifiers={(DOMAIN, entry.data[CONF_BT_ADDRESS])}
            )
            if not device:
                return

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
            device_client = SMABluetoothClient(
                entry.data[CONF_BT_ADDRESS],
                entry.data[CONF_PASSWORD],
                timeout=8,
            )

            proto_info = await hass.async_add_executor_job(
                device_client.read_device_info
            )

            await hass.async_add_executor_job(
                device_client.close
            )

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

            device_info_loaded = bool(cache[DEVICE_INFO_KEY].get("model"))
            _LOGGER.info("SMA device info: %s", cache[DEVICE_INFO_KEY])

    async def async_update_data():
        nonlocal last_success, sleep_retry_after, last_device_info_attempt

        now = datetime.utcnow()

        if sleep_retry_after is not None and now < sleep_retry_after:
            cache[BINARY_SENSOR_CONNECTED] = bool(
                last_success and (now - last_success) < connected_grace
            )
            return cache

        wanted = [
            sensor
            for sensor, interval_key in _READ_INTERVAL_KEYS.items()
            if last_update[sensor] is None
            or (now - last_update[sensor]).total_seconds()
            >= _interval(entry, interval_key)
        ]

        if not wanted:
            return cache

        try:
            def _read_sma():
                return client.read_values(wanted)

            values = await hass.async_add_executor_job(_read_sma)

            for key, value in values.items():
                cache[key] = value
                last_update[key] = now

            # Calculate efficiency from existing AC/DC power values
            ac_power = cache.get(SENSOR_AC_POWER)
            dc_total_power = cache.get(SENSOR_DC_TOTAL_POWER)

            if (
                ac_power is not None
                and dc_total_power is not None
                and dc_total_power > 0
            ):
                efficiency = round((ac_power / dc_total_power) * 100, 2)
                cache[SENSOR_EFFICIENCY] = min(efficiency, 100.0)
            else:
                cache[SENSOR_EFFICIENCY] = None

            last_success = now
            sleep_retry_after = None
            cache[BINARY_SENSOR_CONNECTED] = True

            should_try_device_info = (
                not device_info_loaded
                and (
                    last_device_info_attempt is None
                    or now - last_device_info_attempt >= device_info_retry
                )
            )

            if should_try_device_info:
                last_device_info_attempt = now
                try:
                    await asyncio.sleep(10)
                    await _read_and_cache_device_info()
                except Exception as info_err:
                    _LOGGER.debug(
                        "SMA optional device-info update failed: %s",
                        info_err,
                    )

            return cache

        except Exception as err:
            error_text = str(err).lower()

            sleeping_error = any(
                text in error_text
                for text in (
                    "sleep",
                    "night",
                    "timeout",
                )
            )

            if sleeping_error:
                sleep_retry_after = now + (
                    startup_backoff if last_success is None else sleeping_backoff
                )

                _LOGGER.info(
                    "SMA inverter appears to be sleeping. "
                    "Next retry after %s: %s",
                    sleep_retry_after.isoformat(timespec="seconds"),
                    err,
                )
            else:
                sleep_retry_after = None

                _LOGGER.warning(
                    "SMA Bluetooth communication error: %s",
                    err,
                )

            cache[BINARY_SENSOR_CONNECTED] = bool(
                last_success and (now - last_success) < connected_grace
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

    coordinator.async_set_updated_data(cache)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _refresh_after_ha_started() -> None:
        if entry.entry_id not in hass.data.get(DOMAIN, {}):
            return

        await asyncio.sleep(30)

        if entry.entry_id not in hass.data.get(DOMAIN, {}):
            return

        await coordinator.async_request_refresh()

    if hass.state == CoreState.running:
        hass.async_create_task(_refresh_after_ha_started())
    else:
        async def _on_ha_started(event) -> None:
            hass.async_create_task(_refresh_after_ha_started())

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

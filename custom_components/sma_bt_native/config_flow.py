from __future__ import annotations

import re
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .bluetooth import normalize_mac
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
)

MAC_RE = re.compile(r"^[0-9A-F]{2}(:[0-9A-F]{2}){5}$")


def _valid_mac(address: str) -> bool:
    return bool(MAC_RE.match(normalize_mac(address)))


INTERVAL_KEYS = (
    CONF_AC_INTERVAL,
    CONF_ENERGY_TODAY_INTERVAL,
    CONF_ENERGY_TOTAL_INTERVAL,
    CONF_TEMPERATURE_INTERVAL,
)


def _interval_schema(defaults: dict | None = None) -> dict:
    defaults = defaults or {}
    return {
        vol.Optional(CONF_AC_INTERVAL, default=defaults.get(CONF_AC_INTERVAL, DEFAULT_AC_INTERVAL)): int,
        vol.Optional(CONF_ENERGY_TODAY_INTERVAL, default=defaults.get(CONF_ENERGY_TODAY_INTERVAL, DEFAULT_ENERGY_TODAY_INTERVAL)): int,
        vol.Optional(CONF_ENERGY_TOTAL_INTERVAL, default=defaults.get(CONF_ENERGY_TOTAL_INTERVAL, DEFAULT_ENERGY_TOTAL_INTERVAL)): int,
        vol.Optional(CONF_TEMPERATURE_INTERVAL, default=defaults.get(CONF_TEMPERATURE_INTERVAL, DEFAULT_TEMPERATURE_INTERVAL)): int,
    }


def _interval_data(user_input: dict) -> dict:
    return {key: int(user_input[key]) for key in INTERVAL_KEYS if key in user_input}


class SMABluetoothNativeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            address = normalize_mac(user_input[CONF_BT_ADDRESS])
            if not _valid_mac(address):
                errors[CONF_BT_ADDRESS] = "invalid_bt_address"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()
                data = {
                    CONF_BT_ADDRESS: address,
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    **_interval_data(user_input),
                }
                return self.async_create_entry(title=f"SMA {address}", data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_BT_ADDRESS): str,
                vol.Required(CONF_PASSWORD): str,
                **_interval_schema(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SMABluetoothNativeOptionsFlow(config_entry)


class SMABluetoothNativeOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        super().__init__()

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        defaults = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(_interval_schema(defaults)),
        )

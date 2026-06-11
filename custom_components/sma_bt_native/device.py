from __future__ import annotations

from .const import CONF_BT_ADDRESS, DOMAIN

DEVICE_INFO_KEY = "_device_info"


def get_device_info(entry, coordinator=None):
    """Return shared Home Assistant device information."""
    bt_address = entry.data[CONF_BT_ADDRESS]
    runtime = {}
    if coordinator is not None and coordinator.data:
        runtime = coordinator.data.get(DEVICE_INFO_KEY, {}) or {}

    model = runtime.get("model") or "Sunny Boy Bluetooth Inverter"
    serial = runtime.get("serial_number")
    sw_version = runtime.get("sw_version")
    name = runtime.get("name") or (f"SMA {model}" if model else "SMA Sunny Boy Bluetooth")

    info = {
        "identifiers": {(DOMAIN, bt_address)},
        "connections": {("bluetooth", bt_address)},
        "name": name,
        "manufacturer": "SMA",
        "model": model,
    }
    if serial:
        info["serial_number"] = serial
    if sw_version:
        info["sw_version"] = sw_version
    return info

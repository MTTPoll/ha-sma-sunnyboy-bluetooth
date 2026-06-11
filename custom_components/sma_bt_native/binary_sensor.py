from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BINARY_SENSOR_CONNECTED, DOMAIN
from .device import get_device_info


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SMABluetoothConnectedBinarySensor(coordinator, entry)])


class SMABluetoothConnectedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "SMA Bluetooth Connected"
        self._attr_unique_id = f"{entry.entry_id}_{BINARY_SENSOR_CONNECTED}"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self):
        if not self.coordinator.data:
            return False
        return bool(self.coordinator.data.get(BINARY_SENSOR_CONNECTED))

    @property
    def device_info(self):
        return get_device_info(self._entry, self.coordinator)

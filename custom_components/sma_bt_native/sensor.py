from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_AC_POWER,
    SENSOR_ENERGY_TODAY,
    SENSOR_ENERGY_TOTAL,
    SENSOR_TEMPERATURE,
)
from .device import get_device_info

SENSORS = {
    SENSOR_AC_POWER: {
        "name": "SMA AC Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": None,
    },
    SENSOR_ENERGY_TODAY: {
        "name": "SMA Energy Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": None,
    },
    SENSOR_ENERGY_TOTAL: {
        "name": "SMA Energy Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": None,
    },
    SENSOR_TEMPERATURE: {
        "name": "SMA Inverter Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": None,
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SMABluetoothSensor(coordinator, entry, key, desc) for key, desc in SENSORS.items()])


class SMABluetoothSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, desc):
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_name = desc["name"]
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = desc["unit"]
        self._attr_device_class = desc["device_class"]
        self._attr_state_class = desc["state_class"]
        self._attr_icon = desc["icon"]

    @property
    def native_value(self):
        return None if not self.coordinator.data else self.coordinator.data.get(self._key)

    @property
    def device_info(self):
        return get_device_info(self._entry, self.coordinator)

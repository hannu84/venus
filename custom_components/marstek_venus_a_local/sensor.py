"""Sensor platform for Marstek Venus A Local."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTemperature, SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import MarstekVenusALocalCoordinator


@dataclass(frozen=True, kw_only=True)
class MarstekSensorDescription(SensorEntityDescription):
    """Marstek sensor description."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[MarstekSensorDescription, ...] = (
    MarstekSensorDescription(key="battery_soc", translation_key="battery_soc", native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("battery_soc")),
    MarstekSensorDescription(key="battery_temperature", translation_key="battery_temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("battery_temperature")),
    MarstekSensorDescription(key="pv1_power", translation_key="pv1_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("pv1_power")),
    MarstekSensorDescription(key="pv2_power", translation_key="pv2_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("pv2_power")),
    MarstekSensorDescription(key="pv3_power", translation_key="pv3_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("pv3_power")),
    MarstekSensorDescription(key="pv4_power", translation_key="pv4_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("pv4_power")),
    MarstekSensorDescription(key="pv_power_total", translation_key="pv_power_total", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("pv_power_total")),
    MarstekSensorDescription(key="grid_power", translation_key="grid_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("grid_power")),
    MarstekSensorDescription(key="offgrid_power", translation_key="offgrid_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("offgrid_power")),
    MarstekSensorDescription(key="meter_total_power", translation_key="meter_total_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("meter_total_power")),
    MarstekSensorDescription(key="total_grid_output_energy_wh", translation_key="total_grid_output_energy_wh", native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda data: data.get("total_grid_output_energy_wh")),
    MarstekSensorDescription(key="total_grid_input_energy_wh", translation_key="total_grid_input_energy_wh", native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, value_fn=lambda data: data.get("total_grid_input_energy_wh")),
    MarstekSensorDescription(key="wifi_rssi", translation_key="wifi_rssi", native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda data: data.get("wifi_rssi")),
    MarstekSensorDescription(key="operating_mode", translation_key="operating_mode", value_fn=lambda data: data.get("operating_mode")),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Marstek sensors from a config entry."""
    coordinator: MarstekVenusALocalCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MarstekSensor(coordinator, entry, description) for description in SENSORS)


class MarstekSensor(CoordinatorEntity[MarstekVenusALocalCoordinator]):
    """Representation of a Marstek sensor."""

    entity_description: MarstekSensorDescription

    def __init__(self, coordinator: MarstekVenusALocalCoordinator, entry: ConfigEntry, description: MarstekSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=entry.title,
        )

    @property
    def native_value(self) -> Any:
        """Return the native value."""
        return self.entity_description.value_fn(self.coordinator.data)

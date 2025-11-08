"""Hatch Rest config flow."""

import dataclasses
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_ADDRESS, CONF_SENSOR_TYPE

from .api import PyHatchBabyRestAsync
from .const import DOMAIN, MANUFACTURER_ID

_LOGGER = logging.getLogger(__name__)


# Much of this is sourced from the Switchbot official component
def format_unique_id(address: str) -> str:
    """Format the unique ID for a Hatch Rest."""
    return address.replace(":", "").lower()


def short_address(address: str) -> str:
    """Convert a Bluetooth address to a short address."""
    results = address.replace("-", ":").split(":")
    return f"{results[-2].upper()}{results[-1].upper()}"[-4:]


@dataclasses.dataclass
class DiscoveredDevice:
    """Discovered device information."""

    name: str
    discovery_info: BluetoothServiceInfoBleak
    hatch_rest_device: PyHatchBabyRestAsync


class HatchBabyRestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hatch Rest config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_device: DiscoveredDevice | None = None
        self._discovered_devices: dict[str, DiscoveredDevice] = {}
        self._device_name: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the Bluetooth discovery step."""
        _LOGGER.debug("Discovered Hatch Rest %s", discovery_info.as_dict())
        await self.async_set_unique_id(format_unique_id(discovery_info.address))
        self._abort_if_unique_id_configured()

        try:
            ble_device = async_ble_device_from_address(
                self.hass, discovery_info.address, connectable=True
            )
            if not ble_device:
                raise ValueError("BLEDevice does not exist")  # noqa: TRY301
            hatch_rest_device = PyHatchBabyRestAsync(ble_device)
            await hatch_rest_device.refresh_data()
        except Exception as e:  # noqa: BLE001
            _LOGGER.debug("Unexpected error during async_step_bluetooth: %r", e)
            return self.async_abort(reason="unknown")

        self._device_name = hatch_rest_device.name
        self._discovered_device = DiscoveredDevice(
            name=hatch_rest_device.name or "",
            discovery_info=discovery_info,
            hatch_rest_device=hatch_rest_device,
        )

        self.context["title_placeholders"] = {
            "name": self._device_name or "",
            "address": short_address(discovery_info.address),
        }

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Blueooth confirmation step."""
        if user_input is not None:
            return await self._async_create_entry_from_discovery(user_input)

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": self.context["title_placeholders"]["name"]
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """User input step."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(
                short_address(address), raise_on_progress=False
            )
            self._abort_if_unique_id_configured()
            discovery = self._discovered_devices[address]

            self.context["title_placeholders"] = {"name": discovery.name}

            self._discovered_device = discovery

            return await self._async_create_entry_from_discovery(user_input)

        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue

            if MANUFACTURER_ID not in discovery_info.manufacturer_data:
                continue

            try:
                ble_device = async_ble_device_from_address(
                    self.hass, discovery_info.address
                )
                if not ble_device:
                    raise ValueError("BLEDevice does not exist")  # noqa: TRY301
                hatch_rest_device = PyHatchBabyRestAsync(ble_device)
                await hatch_rest_device.refresh_data()
            except Exception as e:  # noqa: BLE001
                _LOGGER.debug("Unexpected error during async_step_user: %r", e)
                return self.async_abort(reason="unknown")
            name = hatch_rest_device.name
            self._discovered_devices[address] = DiscoveredDevice(
                name or "", discovery_info, hatch_rest_device
            )

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        titles = {
            address: name for (address, discovery) in self._discovered_devices.items()
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(titles)}),
        )

    async def _async_create_entry_from_discovery(
        self, user_input: dict[str, Any]
    ) -> ConfigFlowResult:
        if self._discovered_device:
            address = self._discovered_device.discovery_info.address
        return self.async_create_entry(
            title=self._device_name or "",
            data={
                **user_input,
                CONF_ADDRESS: address,
                CONF_SENSOR_TYPE: "switch",  # is this even required? I have other platforms supported
            },
        )

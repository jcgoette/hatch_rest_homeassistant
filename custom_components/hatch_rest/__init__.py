"""Hatch Rest integration."""

from homeassistant import config_entries, core
from homeassistant.components import bluetooth
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.exceptions import ConfigEntryNotReady

from .api import PyHatchBabyRestAsync
from .coordinator import HatchBabyRestUpdateCoordinator

PLATFORMS = [Platform.LIGHT, Platform.MEDIA_PLAYER, Platform.SWITCH]


# async_setup_entry handles the setup of individual configuration
# entries created by users via the UI (i.e., Config Entry)
async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up the Hatch Rest component."""

    address = entry.data[CONF_ADDRESS]
    ble_device = bluetooth.async_ble_device_from_address(hass, address.upper())
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Hatch Rest device with address {address}"
        )
    hatch_rest_device = PyHatchBabyRestAsync(ble_device)
    coordinator = HatchBabyRestUpdateCoordinator(
        hass,
        entry.unique_id,
        hatch_rest_device,
    )
    entry.runtime_data = coordinator

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload Hatch Rest config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)

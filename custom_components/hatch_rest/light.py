"""Hatch Rest light."""

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    LightEntity,
)
from homeassistant.components.light.const import ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import HatchBabyRestEntity, HatchBabyRestUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hatch Rest light."""
    coordinator = config_entry.runtime_data
    # only need to update_before_add on one entity -- switch is "master" entity
    async_add_entities([HatchBabyRestLight(coordinator)], update_before_add=False)


class HatchBabyRestLight(HatchBabyRestEntity, LightEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Hatch Rest light entity."""

    def __init__(self, coordinator: HatchBabyRestUpdateCoordinator) -> None:
        """Initialize the light entity."""
        super().__init__(coordinator)
        # Remembered brightness so a bare toggle-off/on restores the prior level.
        # The device has no separate lamp power, so "off" is brightness 0.
        self._last_brightness: int = 255

    @property
    def brightness(self) -> int | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return the brightness of the light."""
        _LOGGER.debug("light brightness = %s", self.coordinator.data.get("brightness"))
        return self.coordinator.data.get("brightness")

    @property
    def color_mode(self) -> ColorMode:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return color mode."""
        return ColorMode.RGB

    @property
    def is_on(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return if the light is on."""
        # if power is off, then it's off
        if self.coordinator.data.get("power") is False:
            return False
        brightness = self.coordinator.data.get("brightness")
        if brightness:
            _LOGGER.debug("light is_on = %s", brightness > 0)
            # if brightness is greater than 0, then it's on
            return brightness > 0
        return False

    @property
    def name(self) -> str | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return the name of the entity."""
        if self._hatch_rest_device.name:
            return f"{self._hatch_rest_device.name.title()} Light"
        return None

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return the RGB color of the light."""
        _LOGGER.debug("light rgb_color = %s", self.coordinator.data.get("color"))
        return self.coordinator.data.get("color")

    @property
    def supported_color_modes(self) -> set[ColorMode]:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return supported color modes."""
        return {ColorMode.RGB}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb = kwargs.get(ATTR_RGB_COLOR)

        if not self._hatch_rest_device.power:
            _LOGGER.debug("light _hatch_rest_device power not on -- turning on")
            await self._hatch_rest_device.turn_power_on()

        # A bare toggle-on (no brightness or color) would otherwise leave
        # brightness at 0 -- which reads as "off" -- so the light could never be
        # switched back on from the UI. Restore the last-known brightness stored
        # by async_turn_off (falling back to full brightness).
        if brightness is None and not (self.coordinator.data.get("brightness") or 0):
            brightness = self._last_brightness or 255

        if brightness:
            self._last_brightness = brightness
            _LOGGER.debug("light setting brightness = %s", brightness)
            await self._hatch_rest_device.set_brightness(brightness)
        if rgb:
            _LOGGER.debug("light setting RBG = (%s[0], %s[1], %s[2])", *rgb)
            await self._hatch_rest_device.set_color(*rgb)

        # https://developers.home-assistant.io/docs/integration_fetching_data/
        # If this method is used on a coordinator that polls, it will reset the time until the next time it will poll for data.
        # each _send_command calls _refresh_data and updates API data states, so use that
        self.coordinator.async_set_updated_data(self.coordinator.get_current_data())

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Set the light off."""
        # Stash the current brightness before zeroing so async_turn_on can
        # restore it (the device has no separate lamp power; off == brightness 0).
        if current := (self.coordinator.data.get("brightness") or 0):
            self._last_brightness = current
        await self._hatch_rest_device.set_brightness(0)

        # https://developers.home-assistant.io/docs/integration_fetching_data/
        # If this method is used on a coordinator that polls, it will reset the time until the next time it will poll for data.
        # each _send_command calls _refresh_data and updates API data states, so use that
        self.coordinator.async_set_updated_data(self.coordinator.get_current_data())

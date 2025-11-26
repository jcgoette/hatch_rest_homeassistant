"""Tests for Hatch Rest light entity."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_RGB_COLOR
from homeassistant.components.light.const import ColorMode

from custom_components.hatch_rest.coordinator import HatchBabyRestUpdateCoordinator
from custom_components.hatch_rest.light import HatchBabyRestLight


class TestHatchBabyRestLight:
    """Tests for HatchBabyRestLight."""

    @pytest.fixture
    def light_entity(
        self, mock_coordinator: HatchBabyRestUpdateCoordinator
    ) -> HatchBabyRestLight:
        """Create light entity."""
        return HatchBabyRestLight(mock_coordinator)

    def test_brightness(self, light_entity: HatchBabyRestLight):
        """Test brightness property."""
        assert light_entity.brightness == 128

    def test_brightness_none(self, light_entity: HatchBabyRestLight):
        """Test brightness when not set."""
        light_entity.coordinator.data["brightness"] = None
        assert light_entity.brightness is None

    def test_color_mode(self, light_entity: HatchBabyRestLight):
        """Test color mode is RGB."""
        assert light_entity.color_mode == ColorMode.RGB

    def test_supported_color_modes(self, light_entity: HatchBabyRestLight):
        """Test supported color modes."""
        assert light_entity.supported_color_modes == {ColorMode.RGB}

    def test_rgb_color(self, light_entity: HatchBabyRestLight):
        """Test RGB color property."""
        assert light_entity.rgb_color == (255, 128, 64)

    def test_is_on_when_power_and_brightness(self, light_entity: HatchBabyRestLight):
        """Test is_on when power is on and brightness > 0."""
        light_entity.coordinator.data["power"] = True
        light_entity.coordinator.data["brightness"] = 100
        assert light_entity.is_on is True

    def test_is_off_when_power_off(self, light_entity: HatchBabyRestLight):
        """Test is_on when power is off."""
        light_entity.coordinator.data["power"] = False
        light_entity.coordinator.data["brightness"] = 100
        assert light_entity.is_on is False

    def test_is_off_when_brightness_zero(self, light_entity: HatchBabyRestLight):
        """Test is_on when brightness is 0."""
        light_entity.coordinator.data["power"] = True
        light_entity.coordinator.data["brightness"] = 0
        assert light_entity.is_on is False

    def test_is_off_when_brightness_none(self, light_entity: HatchBabyRestLight):
        """Test is_on when brightness is None."""
        light_entity.coordinator.data["power"] = True
        light_entity.coordinator.data["brightness"] = None
        assert light_entity.is_on is False

    def test_name(self, light_entity: HatchBabyRestLight):
        """Test name property."""
        assert light_entity.name == "Hatch Rest Light"

    def test_name_when_device_name_none(self, light_entity: HatchBabyRestLight):
        """Test name when device name is None."""
        light_entity._hatch_rest_device.name = None
        assert light_entity.name is None

    @pytest.mark.asyncio
    async def test_async_turn_on_basic(self, light_entity: HatchBabyRestLight):
        """Test turning on the light."""
        light_entity._hatch_rest_device.power = False
        light_entity._hatch_rest_device.turn_power_on = AsyncMock()

        await light_entity.async_turn_on()

        light_entity._hatch_rest_device.turn_power_on.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_turn_on_with_brightness(
        self, light_entity: HatchBabyRestLight
    ):
        """Test turning on with brightness."""
        light_entity._hatch_rest_device.power = True
        light_entity._hatch_rest_device.set_brightness = AsyncMock()

        await light_entity.async_turn_on(**{ATTR_BRIGHTNESS: 200})

        light_entity._hatch_rest_device.set_brightness.assert_called_once_with(200)

    @pytest.mark.asyncio
    async def test_async_turn_on_with_rgb(self, light_entity: HatchBabyRestLight):
        """Test turning on with RGB color."""
        light_entity._hatch_rest_device.power = True
        light_entity._hatch_rest_device.set_color = AsyncMock()

        await light_entity.async_turn_on(**{ATTR_RGB_COLOR: (255, 0, 128)})

        light_entity._hatch_rest_device.set_color.assert_called_once_with(255, 0, 128)

    @pytest.mark.asyncio
    async def test_async_turn_on_powers_on_if_needed(
        self, light_entity: HatchBabyRestLight
    ):
        """Test turn_on powers device on if off."""
        light_entity._hatch_rest_device.power = False
        light_entity._hatch_rest_device.turn_power_on = AsyncMock()
        light_entity._hatch_rest_device.set_brightness = AsyncMock()

        await light_entity.async_turn_on(**{ATTR_BRIGHTNESS: 100})

        light_entity._hatch_rest_device.turn_power_on.assert_called_once()
        light_entity._hatch_rest_device.set_brightness.assert_called_once_with(100)

    @pytest.mark.asyncio
    async def test_async_turn_off(self, light_entity: HatchBabyRestLight):
        """Test turning off the light."""
        light_entity._hatch_rest_device.set_brightness = AsyncMock()

        await light_entity.async_turn_off()

        light_entity._hatch_rest_device.set_brightness.assert_called_once_with(0)

    @pytest.mark.asyncio
    async def test_turn_on_updates_coordinator(self, light_entity: HatchBabyRestLight):
        """Test turn_on updates coordinator data."""
        light_entity._hatch_rest_device.power = True
        light_entity.coordinator.async_set_updated_data = AsyncMock()
        light_entity.coordinator.get_current_data = lambda: {"brightness": 100}

        await light_entity.async_turn_on()

        light_entity.coordinator.async_set_updated_data.assert_called_once_with(
            {"brightness": 100}
        )

    @pytest.mark.asyncio
    async def test_turn_off_updates_coordinator(self, light_entity: HatchBabyRestLight):
        """Test turn_off updates coordinator data."""
        light_entity._hatch_rest_device.set_brightness = AsyncMock()
        light_entity.coordinator.async_set_updated_data = AsyncMock()
        light_entity.coordinator.get_current_data = lambda: {"brightness": 0}

        await light_entity.async_turn_off()

        light_entity.coordinator.async_set_updated_data.assert_called_once_with(
            {"brightness": 0}
        )

"""Tests for Hatch Rest switch entity."""

from unittest.mock import AsyncMock

import pytest

from custom_components.hatch_rest.coordinator import HatchBabyRestUpdateCoordinator
from custom_components.hatch_rest.switch import HatchBabyRestSwitch


class TestHatchBabyRestSwitch:
    """Tests for HatchBabyRestSwitch."""

    @pytest.fixture
    def switch_entity(
        self, mock_coordinator: HatchBabyRestUpdateCoordinator
    ) -> HatchBabyRestSwitch:
        """Create switch entity."""
        return HatchBabyRestSwitch(mock_coordinator)

    def test_is_on_true(self, switch_entity: HatchBabyRestSwitch):
        """Test is_on when power is True."""
        switch_entity.coordinator.data["power"] = True
        assert switch_entity.is_on is True

    def test_is_on_false(self, switch_entity: HatchBabyRestSwitch):
        """Test is_on when power is False."""
        switch_entity.coordinator.data["power"] = False
        assert switch_entity.is_on is False

    def test_is_on_none(self, switch_entity: HatchBabyRestSwitch):
        """Test is_on when power is None."""
        switch_entity.coordinator.data["power"] = None
        assert switch_entity.is_on is None

    def test_name(self, switch_entity: HatchBabyRestSwitch):
        """Test name property."""
        assert switch_entity.name == "Hatch Rest Switch"

    def test_name_when_device_name_none(self, switch_entity: HatchBabyRestSwitch):
        """Test name when device name is None."""
        switch_entity._hatch_rest_device.name = None
        assert switch_entity.name is None

    @pytest.mark.asyncio
    async def test_async_turn_on_when_off(self, switch_entity: HatchBabyRestSwitch):
        """Test turning on when switch is off."""
        switch_entity.coordinator.data["power"] = False
        switch_entity._hatch_rest_device.turn_power_on = AsyncMock()
        switch_entity.coordinator.async_set_updated_data = AsyncMock()
        switch_entity.coordinator.get_current_data = lambda: {"power": True}

        await switch_entity.async_turn_on()

        switch_entity._hatch_rest_device.turn_power_on.assert_called_once()
        switch_entity.coordinator.async_set_updated_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_turn_on_when_already_on(
        self, switch_entity: HatchBabyRestSwitch
    ):
        """Test turning on when switch is already on does nothing."""
        switch_entity.coordinator.data["power"] = True
        switch_entity._hatch_rest_device.turn_power_on = AsyncMock()

        await switch_entity.async_turn_on()

        switch_entity._hatch_rest_device.turn_power_on.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_turn_off_when_on(self, switch_entity: HatchBabyRestSwitch):
        """Test turning off when switch is on."""
        switch_entity.coordinator.data["power"] = True
        switch_entity._hatch_rest_device.turn_power_off = AsyncMock()
        switch_entity.coordinator.async_set_updated_data = AsyncMock()
        switch_entity.coordinator.get_current_data = lambda: {"power": False}

        await switch_entity.async_turn_off()

        switch_entity._hatch_rest_device.turn_power_off.assert_called_once()
        switch_entity.coordinator.async_set_updated_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_turn_off_when_already_off(
        self, switch_entity: HatchBabyRestSwitch
    ):
        """Test turning off when switch is already off does nothing."""
        switch_entity.coordinator.data["power"] = False
        switch_entity._hatch_rest_device.turn_power_off = AsyncMock()

        await switch_entity.async_turn_off()

        switch_entity._hatch_rest_device.turn_power_off.assert_not_called()

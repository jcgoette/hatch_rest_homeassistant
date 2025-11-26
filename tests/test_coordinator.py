"""Tests for Hatch Rest coordinator."""

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.hatch_rest.const import DOMAIN, PyHatchBabyRestSound
from custom_components.hatch_rest.coordinator import (
    HatchBabyRestEntity,
    HatchBabyRestUpdateCoordinator,
)


class TestHatchBabyRestUpdateCoordinator:
    """Tests for HatchBabyRestUpdateCoordinator."""

    def test_init(self, hass: HomeAssistant, mock_hatch_api: AsyncMock):
        """Test coordinator initialization."""
        coordinator = HatchBabyRestUpdateCoordinator(
            hass,
            unique_id="aabbccddeeff",
            hatch_rest_device=mock_hatch_api,
        )

        assert coordinator.unique_id == "aabbccddeeff"
        assert coordinator.hatch_rest_device == mock_hatch_api
        assert coordinator.name == DOMAIN
        assert coordinator.update_interval == timedelta(seconds=60)

    def test_get_current_data(self, mock_coordinator: HatchBabyRestUpdateCoordinator):
        """Test get_current_data returns device state."""
        data = mock_coordinator.get_current_data()

        assert data["brightness"] == 128
        assert data["color"] == (255, 128, 64)
        assert data["power"] is True
        assert data["sound"] == PyHatchBabyRestSound.ocean
        assert data["volume"] == 100

    @pytest.mark.asyncio
    async def test_async_update_data_success(
        self, hass: HomeAssistant, mock_hatch_api: AsyncMock
    ):
        """Test successful data update."""
        coordinator = HatchBabyRestUpdateCoordinator(
            hass,
            unique_id="aabbccddeeff",
            hatch_rest_device=mock_hatch_api,
        )

        data = await coordinator._async_update_data()

        mock_hatch_api.refresh_data.assert_called_once()
        assert data["brightness"] == 128
        assert data["color"] == (255, 128, 64)
        assert data["power"] is True

    @pytest.mark.asyncio
    async def test_async_update_data_failure_with_cache(
        self, hass: HomeAssistant, mock_hatch_api: AsyncMock
    ):
        """Test update failure returns cached data when available."""
        coordinator = HatchBabyRestUpdateCoordinator(
            hass,
            unique_id="aabbccddeeff",
            hatch_rest_device=mock_hatch_api,
        )

        # Set up cached data
        coordinator.data = {
            "brightness": 50,
            "color": (100, 100, 100),
            "power": False,
            "sound": PyHatchBabyRestSound.rain,
            "volume": 50,
        }

        mock_hatch_api.refresh_data.side_effect = Exception("Connection failed")

        data = await coordinator._async_update_data()

        # Should return cached data
        assert data["brightness"] == 50
        assert data["power"] is False

    @pytest.mark.asyncio
    async def test_async_update_data_failure_without_cache(
        self, hass: HomeAssistant, mock_hatch_api: AsyncMock
    ):
        """Test update failure raises when no cached data."""
        coordinator = HatchBabyRestUpdateCoordinator(
            hass,
            unique_id="aabbccddeeff",
            hatch_rest_device=mock_hatch_api,
        )
        coordinator.data = None

        mock_hatch_api.refresh_data.side_effect = Exception("Connection failed")

        with pytest.raises(UpdateFailed, match="Device update failed"):
            await coordinator._async_update_data()


class TestHatchBabyRestEntity:
    """Tests for HatchBabyRestEntity."""

    def test_init(self, mock_coordinator: HatchBabyRestUpdateCoordinator):
        """Test entity initialization."""
        entity = HatchBabyRestEntity(mock_coordinator)

        assert entity._hatch_rest_device == mock_coordinator.hatch_rest_device
        assert entity._attr_unique_id == "aabbccddeeff"

    def test_device_info(self, mock_coordinator: HatchBabyRestUpdateCoordinator):
        """Test device_info property."""
        entity = HatchBabyRestEntity(mock_coordinator)

        device_info = entity.device_info

        assert device_info["manufacturer"] == "Hatch"
        assert device_info["model"] == "Rest"
        assert device_info["name"] == "Hatch Rest"
        assert ("hatch_rest", "aabbccddeeff") in device_info["identifiers"]

    def test_device_info_missing_address_raises(
        self, mock_coordinator: HatchBabyRestUpdateCoordinator
    ):
        """Test device_info raises when address is missing."""
        mock_coordinator.hatch_rest_device.address = None
        entity = HatchBabyRestEntity(mock_coordinator)

        with pytest.raises(ValueError, match="Missing bluetooth address"):
            _ = entity.device_info

    def test_device_info_missing_unique_id_raises(
        self, mock_coordinator: HatchBabyRestUpdateCoordinator
    ):
        """Test device_info raises when unique_id is missing."""
        mock_coordinator.unique_id = None
        entity = HatchBabyRestEntity(mock_coordinator)

        with pytest.raises(ValueError, match="Missing bluetooth address"):
            _ = entity.device_info

    def test_device_name(self, mock_coordinator: HatchBabyRestUpdateCoordinator):
        """Test device_name property."""
        entity = HatchBabyRestEntity(mock_coordinator)

        assert entity.device_name == "Hatch Rest"

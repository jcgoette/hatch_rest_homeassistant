"""Tests for Hatch Rest config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hatch_rest.config_flow import (
    format_unique_id,
    short_address,
)
from custom_components.hatch_rest.const import DOMAIN


class TestHelperFunctions:
    """Tests for config flow helper functions."""

    def test_format_unique_id(self):
        """Test unique ID formatting."""
        assert format_unique_id("AA:BB:CC:DD:EE:FF") == "aabbccddeeff"
        assert format_unique_id("aa:bb:cc:dd:ee:ff") == "aabbccddeeff"

    def test_short_address(self):
        """Test short address formatting."""
        assert short_address("AA:BB:CC:DD:EE:FF") == "EEFF"
        assert short_address("AA-BB-CC-DD-EE-FF") == "EEFF"


class TestHatchBabyRestConfigFlow:
    """Tests for HatchBabyRestConfigFlow."""

    @pytest.fixture
    def mock_setup_entry(self) -> AsyncMock:
        """Mock async_setup_entry."""
        with patch(
            "custom_components.hatch_rest.async_setup_entry",
            return_value=True,
        ) as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_bluetooth_discovery_step(
        self, hass: HomeAssistant, mock_service_info, mock_setup_entry
    ):
        """Test Bluetooth discovery initiates config flow."""
        mock_api = MagicMock()
        mock_api.name = "Hatch Rest"
        mock_api.refresh_data = AsyncMock()

        with patch(
            "custom_components.hatch_rest.config_flow.async_ble_device_from_address",
            return_value=MagicMock(),
        ):
            with patch(
                "custom_components.hatch_rest.config_flow.PyHatchBabyRestAsync",
                return_value=mock_api,
            ):
                result = await hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": config_entries.SOURCE_BLUETOOTH},
                    data=mock_service_info,
                )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "bluetooth_confirm"

    @pytest.mark.asyncio
    async def test_bluetooth_confirm_creates_entry(
        self, hass: HomeAssistant, mock_service_info, mock_setup_entry
    ):
        """Test Bluetooth confirmation creates config entry."""
        mock_api = MagicMock()
        mock_api.name = "Hatch Rest"
        mock_api.refresh_data = AsyncMock()

        with patch(
            "custom_components.hatch_rest.config_flow.async_ble_device_from_address",
            return_value=MagicMock(),
        ):
            with patch(
                "custom_components.hatch_rest.config_flow.PyHatchBabyRestAsync",
                return_value=mock_api,
            ):
                result = await hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": config_entries.SOURCE_BLUETOOTH},
                    data=mock_service_info,
                )

                result = await hass.config_entries.flow.async_configure(
                    result["flow_id"],
                    user_input={},
                )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Hatch Rest"
        assert result["data"][CONF_ADDRESS] == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.asyncio
    async def test_bluetooth_discovery_no_ble_device(
        self, hass: HomeAssistant, mock_service_info
    ):
        """Test Bluetooth discovery aborts when BLE device not found."""
        with patch(
            "custom_components.hatch_rest.config_flow.async_ble_device_from_address",
            return_value=None,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_BLUETOOTH},
                data=mock_service_info,
            )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "unknown"

    @pytest.mark.asyncio
    async def test_bluetooth_discovery_connection_error(
        self, hass: HomeAssistant, mock_service_info
    ):
        """Test Bluetooth discovery aborts on connection error."""
        mock_api = MagicMock()
        mock_api.refresh_data = AsyncMock(side_effect=Exception("Connection failed"))

        with patch(
            "custom_components.hatch_rest.config_flow.async_ble_device_from_address",
            return_value=MagicMock(),
        ):
            with patch(
                "custom_components.hatch_rest.config_flow.PyHatchBabyRestAsync",
                return_value=mock_api,
            ):
                result = await hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": config_entries.SOURCE_BLUETOOTH},
                    data=mock_service_info,
                )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "unknown"

    @pytest.mark.asyncio
    async def test_user_step_no_devices(self, hass: HomeAssistant):
        """Test user step aborts when no devices found."""
        with patch(
            "custom_components.hatch_rest.config_flow.async_discovered_service_info",
            return_value=[],
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_USER},
            )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "no_devices_found"

    @pytest.mark.asyncio
    async def test_user_step_shows_discovered_devices(
        self, hass: HomeAssistant, mock_service_info
    ):
        """Test user step shows form with discovered devices."""
        mock_api = MagicMock()
        mock_api.name = "Hatch Rest"
        mock_api.refresh_data = AsyncMock()

        with patch(
            "custom_components.hatch_rest.config_flow.async_discovered_service_info",
            return_value=[mock_service_info],
        ):
            with patch(
                "custom_components.hatch_rest.config_flow.async_ble_device_from_address",
                return_value=MagicMock(),
            ):
                with patch(
                    "custom_components.hatch_rest.config_flow.PyHatchBabyRestAsync",
                    return_value=mock_api,
                ):
                    result = await hass.config_entries.flow.async_init(
                        DOMAIN,
                        context={"source": config_entries.SOURCE_USER},
                    )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_already_configured(self, hass: HomeAssistant, mock_service_info):
        """Test flow aborts if the device is already configured."""

        # Create a proper HA config entry
        existing_entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id=format_unique_id(mock_service_info.address),
            data={
                "address": "AA:BB:CC:DD:EE:FF",
                "sensor_type": "switch",
            },
        )
        existing_entry.add_to_hass(hass)

        # Mock API + BLE
        mock_api = MagicMock()
        mock_api.name = "Hatch Rest"
        mock_api.refresh_data = AsyncMock()

        with (
            patch(
                "custom_components.hatch_rest.config_flow.async_ble_device_from_address",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.hatch_rest.config_flow.PyHatchBabyRestAsync",
                return_value=mock_api,
            ),
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_BLUETOOTH},
                data=mock_service_info,
            )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"

    @pytest.mark.asyncio
    async def test_user_step_filters_non_hatch_devices(
        self, hass: HomeAssistant, mock_service_info
    ):
        """Test user step filters out non-Hatch devices."""
        # Create a non-Hatch device (different manufacturer ID)
        non_hatch_info = MagicMock()
        non_hatch_info.address = "11:22:33:44:55:66"
        non_hatch_info.manufacturer_data = {9999: b"\x00"}  # Not Hatch

        with patch(
            "custom_components.hatch_rest.config_flow.async_discovered_service_info",
            return_value=[non_hatch_info],
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_USER},
            )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "no_devices_found"

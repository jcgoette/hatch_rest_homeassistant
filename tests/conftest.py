"""Fixtures for Hatch Rest tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bleak.backends.device import BLEDevice
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

# from custom_components.hatch_rest.api import PyHatchBabyRestAsync
from custom_components.hatch_rest.const import (
    DOMAIN,
    MANUFACTURER_ID,
    PyHatchBabyRestSound,
)
from custom_components.hatch_rest.coordinator import HatchBabyRestUpdateCoordinator


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations."""
    return


@pytest.fixture
def mock_ble_device() -> BLEDevice:
    """Create a mock BLE device."""
    device = MagicMock(spec=BLEDevice)
    device.address = "AA:BB:CC:DD:EE:FF"
    device.name = "Hatch Rest"
    return device


@pytest.fixture
def mock_service_info() -> BluetoothServiceInfoBleak:
    """Create mock Bluetooth service info."""
    return BluetoothServiceInfoBleak(
        name="Hatch Rest",
        address="AA:BB:CC:DD:EE:FF",
        rssi=-60,
        manufacturer_data={MANUFACTURER_ID: b"\x00\x01\x02"},
        service_data={},
        service_uuids=[],
        source="local",
        device=MagicMock(spec=BLEDevice),
        advertisement=MagicMock(),
        connectable=True,
        time=0,
        tx_power=None,
    )


@pytest.fixture
def mock_hatch_api(mock_ble_device: BLEDevice) -> Generator[AsyncMock, None, None]:
    """Create a mock Hatch API."""
    with patch(
        "custom_components.hatch_rest.api.PyHatchBabyRestAsync", autospec=True
    ) as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.device = mock_ble_device
        mock_api.address = mock_ble_device.address
        mock_api.name = "Hatch Rest"

        # Default state
        mock_api.color = (255, 128, 64)
        mock_api.brightness = 128
        mock_api.sound = PyHatchBabyRestSound.ocean
        mock_api.volume = 100
        mock_api.power = True

        # Async methods
        mock_api.refresh_data = AsyncMock()
        mock_api.turn_power_on = AsyncMock()
        mock_api.turn_power_off = AsyncMock()
        mock_api.set_sound = AsyncMock()
        mock_api.set_volume = AsyncMock()
        mock_api.set_color = AsyncMock()
        mock_api.set_brightness = AsyncMock()

        yield mock_api


@pytest.fixture
def mock_coordinator(
    hass: HomeAssistant, mock_hatch_api: AsyncMock
) -> HatchBabyRestUpdateCoordinator:
    """Create a mock coordinator."""
    coordinator = HatchBabyRestUpdateCoordinator(
        hass,
        unique_id="aabbccddeeff",
        hatch_rest_device=mock_hatch_api,
    )
    coordinator.data = {
        "brightness": 128,
        "color": (255, 128, 64),
        "power": True,
        "sound": PyHatchBabyRestSound.ocean,
        "volume": 100,
    }
    return coordinator


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry_id",
        unique_id="aabbccddeeff",
        data={
            "address": "AA:BB:CC:DD:EE:FF",
            "sensor_type": "switch",
        },
        options={},
    )

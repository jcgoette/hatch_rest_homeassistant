"""Tests for Hatch Rest media player entity."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.components.media_player import MediaPlayerDeviceClass
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaPlayerState,
)

from custom_components.hatch_rest.const import PyHatchBabyRestSound
from custom_components.hatch_rest.coordinator import HatchBabyRestUpdateCoordinator
from custom_components.hatch_rest.media_player import HatchBabyRestMediaPlayer


class TestHatchBabyRestMediaPlayer:
    """Tests for HatchBabyRestMediaPlayer."""

    @pytest.fixture
    def media_player_entity(
        self, mock_coordinator: HatchBabyRestUpdateCoordinator
    ) -> HatchBabyRestMediaPlayer:
        """Create media player entity."""
        return HatchBabyRestMediaPlayer(mock_coordinator)

    def test_device_class(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test device class is speaker."""
        assert media_player_entity.device_class == MediaPlayerDeviceClass.SPEAKER

    def test_name(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test name property."""
        assert media_player_entity.name == "Hatch Rest Media Player"

    def test_name_when_device_name_none(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test name when device name is None."""
        media_player_entity._hatch_rest_device.name = None
        assert media_player_entity.name is None

    def test_source(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test source property returns capitalized sound name."""
        media_player_entity.coordinator.data["sound"] = PyHatchBabyRestSound.ocean
        assert media_player_entity.source == "Ocean"

    def test_source_none(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test source when sound is None."""
        media_player_entity.coordinator.data["sound"] = None
        assert media_player_entity.source is None

    def test_source_list(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test source_list contains all sounds."""
        sources = media_player_entity.source_list

        assert "None" in sources
        assert "Ocean" in sources
        assert "Rain" in sources
        assert "Stream" in sources
        assert "Bird" in sources
        assert len(sources) == len(PyHatchBabyRestSound)

    def test_state_off_when_power_off(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test state is OFF when power is off."""
        media_player_entity.coordinator.data["power"] = False
        assert media_player_entity.state == MediaPlayerState.OFF

    def test_state_paused_when_sound_none(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test state is PAUSED when sound is none."""
        media_player_entity.coordinator.data["power"] = True
        media_player_entity.coordinator.data["sound"] = PyHatchBabyRestSound.none
        assert media_player_entity.state == MediaPlayerState.PAUSED

    def test_state_playing_when_sound_active(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test state is PLAYING when sound is active."""
        media_player_entity.coordinator.data["power"] = True
        media_player_entity.coordinator.data["sound"] = PyHatchBabyRestSound.ocean
        assert media_player_entity.state == MediaPlayerState.PLAYING

    def test_supported_features(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test supported features."""
        features = media_player_entity.supported_features

        assert features & MediaPlayerEntityFeature.PLAY
        assert features & MediaPlayerEntityFeature.PAUSE
        assert features & MediaPlayerEntityFeature.VOLUME_SET
        assert features & MediaPlayerEntityFeature.SELECT_SOURCE

    def test_volume_level(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test volume_level property."""
        media_player_entity.coordinator.data["volume"] = 128
        # Volume is stored as 0-255, converted to 0-1 float
        assert media_player_entity.volume_level == pytest.approx(128 / 255)

    def test_volume_level_max(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test volume_level at max."""
        media_player_entity.coordinator.data["volume"] = 255
        assert media_player_entity.volume_level == pytest.approx(1.0)

    def test_volume_level_none(self, media_player_entity: HatchBabyRestMediaPlayer):
        """Test volume_level when volume is None."""
        media_player_entity.coordinator.data["volume"] = None
        assert media_player_entity.volume_level is None

    @pytest.mark.asyncio
    async def test_async_set_volume_level(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test setting volume level."""
        media_player_entity._hatch_rest_device.set_volume = AsyncMock()
        media_player_entity.coordinator.async_set_updated_data = AsyncMock()
        media_player_entity.coordinator.get_current_data = lambda: {"volume": 128}

        await media_player_entity.async_set_volume_level(0.5)

        media_player_entity._hatch_rest_device.set_volume.assert_called_once_with(127)

    @pytest.mark.asyncio
    async def test_async_set_volume_level_max(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test setting volume to max."""
        media_player_entity._hatch_rest_device.set_volume = AsyncMock()
        media_player_entity.coordinator.async_set_updated_data = AsyncMock()
        media_player_entity.coordinator.get_current_data = lambda: {"volume": 255}

        await media_player_entity.async_set_volume_level(1.0)

        media_player_entity._hatch_rest_device.set_volume.assert_called_once_with(255)

    @pytest.mark.asyncio
    async def test_async_select_source(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test selecting a source."""
        media_player_entity._hatch_rest_device.set_sound = AsyncMock()
        media_player_entity.coordinator.async_set_updated_data = AsyncMock()
        media_player_entity.coordinator.get_current_data = lambda: {
            "sound": PyHatchBabyRestSound.rain
        }

        await media_player_entity.async_select_source("Rain")

        media_player_entity._hatch_rest_device.set_sound.assert_called_once_with(
            PyHatchBabyRestSound.rain
        )
        assert media_player_entity._previous_sound == PyHatchBabyRestSound.rain

    @pytest.mark.asyncio
    async def test_async_media_pause(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test pausing media."""
        media_player_entity._hatch_rest_device.sound = PyHatchBabyRestSound.ocean
        media_player_entity._hatch_rest_device.set_sound = AsyncMock()
        media_player_entity.coordinator.async_set_updated_data = AsyncMock()
        media_player_entity.coordinator.get_current_data = lambda: {
            "sound": PyHatchBabyRestSound.none
        }

        await media_player_entity.async_media_pause()

        # Should save previous sound and set to none
        assert media_player_entity._previous_sound == PyHatchBabyRestSound.ocean
        media_player_entity._hatch_rest_device.set_sound.assert_called_once_with(
            PyHatchBabyRestSound.none
        )

    @pytest.mark.asyncio
    async def test_async_media_play_restores_sound(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test playing restores previous sound."""
        media_player_entity._previous_sound = PyHatchBabyRestSound.rain
        media_player_entity._hatch_rest_device.power = True
        media_player_entity._hatch_rest_device.set_sound = AsyncMock()
        media_player_entity.coordinator.async_set_updated_data = AsyncMock()
        media_player_entity.coordinator.get_current_data = lambda: {
            "sound": PyHatchBabyRestSound.rain
        }

        await media_player_entity.async_media_play()

        media_player_entity._hatch_rest_device.set_sound.assert_called_once_with(
            PyHatchBabyRestSound.rain
        )

    @pytest.mark.asyncio
    async def test_async_media_play_powers_on_if_needed(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test play powers on device if off."""
        media_player_entity._previous_sound = PyHatchBabyRestSound.ocean
        media_player_entity._hatch_rest_device.power = False
        media_player_entity._hatch_rest_device.turn_power_on = AsyncMock()
        media_player_entity._hatch_rest_device.set_sound = AsyncMock()
        media_player_entity.coordinator.async_set_updated_data = AsyncMock()
        media_player_entity.coordinator.get_current_data = lambda: {
            "sound": PyHatchBabyRestSound.ocean
        }

        await media_player_entity.async_media_play()

        media_player_entity._hatch_rest_device.turn_power_on.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_media_play_no_previous_sound(
        self, media_player_entity: HatchBabyRestMediaPlayer
    ):
        """Test play with no previous sound does not call set_sound."""
        media_player_entity._previous_sound = None
        media_player_entity._hatch_rest_device.power = True
        media_player_entity._hatch_rest_device.set_sound = AsyncMock()
        media_player_entity.coordinator.async_set_updated_data = AsyncMock()
        media_player_entity.coordinator.get_current_data = lambda: {"sound": None}

        await media_player_entity.async_media_play()

        media_player_entity._hatch_rest_device.set_sound.assert_not_called()

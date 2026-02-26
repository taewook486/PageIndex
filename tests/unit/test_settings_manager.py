"""
Unit tests for SettingsManager.

Tests M7: Settings Management Dialog functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pageindex.gui.managers.settings_manager import SettingsManager


@pytest.fixture
def temp_settings_file():
    """Create a temporary settings file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_key_file():
    """Create a temporary key file."""
    # Create a temporary file and write a dummy encryption key
    fd, path = tempfile.mkstemp(suffix='.key')
    temp_path = Path(path)
    # Write a dummy Fernet key (44 bytes base64)
    import base64
    key = base64.urlsafe_b64encode(b'0' * 32).decode()
    with open(temp_path, 'w') as f:
        f.write(key)

    yield temp_path

    # Cleanup
    try:
        temp_path.unlink()
    except:
        pass


@pytest.fixture
def settings_manager(temp_settings_file, temp_key_file):
    """Create a SettingsManager with temporary files."""
    with patch.object(SettingsManager, 'SETTINGS_FILE', temp_settings_file):
        with patch.object(SettingsManager, 'KEY_FILE', temp_key_file):
            manager = SettingsManager()
            yield manager


class TestSettingsManager:
    """Test SettingsManager class."""

    def test_init_creates_defaults(self, settings_manager):
        """Test that initialization creates default settings."""
        settings = settings_manager.get_settings()

        assert "api" in settings
        assert "appearance" in settings
        assert "pdf_options" in settings
        assert "output_options" in settings

    def test_default_api_settings(self, settings_manager):
        """Test default API settings."""
        api = settings_manager.get_setting("api", "base_url")
        model = settings_manager.get_setting("api", "model")

        assert api == "https://api.z.ai/api/coding/paas/v4"
        assert model == "glm-5"

    def test_default_appearance_settings(self, settings_manager):
        """Test default appearance settings."""
        theme = settings_manager.get_setting("appearance", "theme")
        font_size = settings_manager.get_setting("appearance", "font_size")

        assert theme == "dark"
        assert font_size == 12

    def test_api_key_encryption(self, settings_manager):
        """Test that API key is encrypted."""
        api_key = "test-api-key-12345"
        settings_manager.set_api_key(api_key)

        # Check that stored value is not plain text
        settings_raw = settings_manager._settings
        encrypted = settings_raw["api"]["api_key"]

        assert encrypted != api_key
        assert len(encrypted) > 0

        # Check that decryption works
        decrypted = settings_manager.get_api_key()
        assert decrypted == api_key

    def test_get_setting(self, settings_manager):
        """Test getting specific settings."""
        value = settings_manager.get_setting("appearance", "theme")
        assert value == "dark"

    def test_set_setting(self, settings_manager):
        """Test setting specific values."""
        settings_manager.set_setting("appearance", "theme", "light")

        value = settings_manager.get_setting("appearance", "theme")
        assert value == "light"

    def test_validate_settings_valid(self, settings_manager):
        """Test validation with valid settings."""
        settings_manager.set_api_key("test-api-key")

        errors = settings_manager.validate_settings()

        assert len(errors) == 0

    def test_validate_settings_no_api_key(self, settings_manager):
        """Test validation fails without API key."""
        settings_manager.set_api_key("")

        errors = settings_manager.validate_settings()

        assert len(errors) > 0
        assert any("API key" in e for e in errors)

    def test_validate_settings_invalid_url(self, settings_manager):
        """Test validation fails with invalid URL."""
        settings_manager.set_setting("api", "base_url", "not-a-url")
        settings_manager.set_api_key("test-key")

        errors = settings_manager.validate_settings()

        assert len(errors) > 0
        assert any("Base URL" in e for e in errors)

    def test_reset_to_defaults(self, settings_manager):
        """Test resetting to defaults."""
        # Set an API key first
        settings_manager.set_api_key("test-api-key")

        # Change some settings
        settings_manager.set_setting("appearance", "theme", "light")
        settings_manager.set_setting("pdf_options", "max_pages", 999)

        # Reset
        api_key = settings_manager.get_api_key()
        settings_manager.reset_to_defaults()

        # Check values are reset (except API key)
        # Note: We need to read directly from _settings since get_setting may have side effects
        assert settings_manager._settings.get("appearance", {}).get("theme") == "dark"
        assert settings_manager._settings.get("pdf_options", {}).get("max_pages") == 10
        assert settings_manager.get_api_key() == api_key  # Preserved

        # Verify API key was preserved
        assert api_key == "test-api-key"

    def test_persistence(self, settings_manager, temp_settings_file):
        """Test that settings persist across manager instances."""
        # Change setting
        settings_manager.set_setting("appearance", "theme", "light")

        # Create new manager instance
        with patch.object(SettingsManager, 'SETTINGS_FILE', temp_settings_file):
            with patch.object(SettingsManager, 'KEY_FILE', settings_manager.KEY_FILE):
                new_manager = SettingsManager()

        # Check setting persisted
        theme = new_manager.get_setting("appearance", "theme")
        assert theme == "light"

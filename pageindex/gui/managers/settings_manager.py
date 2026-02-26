"""
Settings Manager for PageIndex GUI.

This module provides functionality to manage application settings with secure
API key storage using Fernet encryption.
Implements M7 of SPEC-GUI-002.
"""

import copy
import json
import os
from base64 import urlsafe_b64encode
from pathlib import Path
from typing import Any, Optional

from cryptography.fernet import Fernet


def _get_default_settings() -> dict:
    """Get a fresh copy of default settings.

    Returns:
        Dictionary with default settings
    """
    return {
        "api": {
            "api_key": "",
            "base_url": "https://api.z.ai/api/coding/paas/v4",
            "model": "glm-5"
        },
        "appearance": {
            "theme": "dark",
            "font_size": 12
        },
        "pdf_options": {
            "toc_check_pages": 20,
            "max_pages": 10,
            "max_tokens": 20000
        },
        "output_options": {
            "add_node_id": True,
            "add_node_summary": True,
            "add_doc_description": False,
            "add_node_text": False
        }
    }


class SettingsManager:
    """Manages application settings with encrypted API key storage.

    Stores settings in ~/.pageIndex/settings.json
    API keys are encrypted using Fernet symmetric encryption.
    """

    SETTINGS_FILE = Path.home() / ".pageIndex" / "settings.json"
    KEY_FILE = Path.home() / ".pageIndex" / ".encryption_key"

    def __init__(self):
        """Initialize the settings manager and load settings."""
        self._cipher: Optional[Fernet] = None
        self._settings: dict[str, Any] = {}
        self._init_encryption()
        self._load_settings()

    def _init_encryption(self) -> None:
        """Initialize Fernet encryption cipher.

        Creates or loads encryption key from KEY_FILE.
        """
        key: Optional[bytes] = None

        # Try to load existing key
        if self.KEY_FILE.exists():
            try:
                with open(self.KEY_FILE, 'rb') as f:
                    key = f.read()
            except (IOError, OSError):
                pass

        # Generate new key if needed
        if key is None:
            key = Fernet.generate_key()
            self.KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.KEY_FILE, 'wb') as f:
                f.write(key)

        self._cipher = Fernet(key)

    def get_settings(self) -> dict[str, Any]:
        """Get current settings.

        Returns:
            Dictionary containing all settings
        """
        return self._settings.copy()

    def get_api_key(self) -> str:
        """Get decrypted API key.

        Returns:
            Decrypted API key string
        """
        encrypted_key = self._settings.get("api", {}).get("api_key", "")
        if not encrypted_key:
            return ""

        try:
            decrypted = self._cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception:
            # Decryption failed, return empty
            return ""

    def set_api_key(self, api_key: str) -> None:
        """Encrypt and store API key.

        Args:
            api_key: Plain text API key to encrypt and store
        """
        if not api_key:
            encrypted = ""
        else:
            encrypted = self._cipher.encrypt(api_key.encode()).decode()

        if "api" not in self._settings:
            self._settings["api"] = {}
        self._settings["api"]["api_key"] = encrypted
        self._save_settings()

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value.

        Args:
            section: Settings section (e.g., 'api', 'appearance')
            key: Setting key within section
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        return self._settings.get(section, {}).get(key, default)

    def set_setting(self, section: str, key: str, value: Any) -> None:
        """Set a specific setting value.

        Args:
            section: Settings section (e.g., 'api', 'appearance')
            key: Setting key within section
            value: Value to set
        """
        if section not in self._settings:
            self._settings[section] = {}
        self._settings[section][key] = value
        self._save_settings()

    def reset_to_defaults(self) -> None:
        """Reset all settings to default values.

        Note: This does NOT clear the API key.
        """
        # Preserve API key
        api_key = self._settings.get("api", {}).get("api_key", "")

        # Reset to defaults
        self._settings = _get_default_settings()

        # Restore API key
        if "api" not in self._settings:
            self._settings["api"] = {}
        self._settings["api"]["api_key"] = api_key

        self._save_settings()

    def validate_settings(self) -> list[str]:
        """Validate current settings.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate API settings
        api_key = self.get_api_key()
        if not api_key:
            errors.append("API key is required")

        base_url = self.get_setting("api", "base_url", "")
        if base_url and not (base_url.startswith("http://") or base_url.startswith("https://")):
            errors.append("Base URL must start with http:// or https://")

        # Validate PDF options
        toc_pages = self.get_setting("pdf_options", "toc_check_pages", 20)
        try:
            if int(toc_pages) < 1:
                errors.append("TOC Check Pages must be at least 1")
        except (ValueError, TypeError):
            errors.append("TOC Check Pages must be a valid number")

        max_pages = self.get_setting("pdf_options", "max_pages", 10)
        try:
            if int(max_pages) < 1:
                errors.append("Max Pages/Node must be at least 1")
        except (ValueError, TypeError):
            errors.append("Max Pages/Node must be a valid number")

        max_tokens = self.get_setting("pdf_options", "max_tokens", 20000)
        try:
            if int(max_tokens) < 100:
                errors.append("Max Tokens/Node must be at least 100")
        except (ValueError, TypeError):
            errors.append("Max Tokens/Node must be a valid number")

        return errors

    def _load_settings(self) -> None:
        """Load settings from disk."""
        if not self.SETTINGS_FILE.exists():
            # Use defaults
            self._settings = _get_default_settings()
            return

        try:
            with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            # Merge with defaults to handle missing keys
            self._settings = self._merge_with_defaults(loaded)

        except (json.JSONDecodeError, TypeError):
            # Corrupted file, use defaults
            self._settings = _get_default_settings()

    def _save_settings(self) -> None:
        """Save settings to disk."""
        # Ensure directory exists
        self.SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

    def _merge_with_defaults(self, loaded: dict[str, Any]) -> dict[str, Any]:
        """Merge loaded settings with defaults.

        Ensures all default keys exist even if not in loaded file.

        Args:
            loaded: Settings loaded from file

        Returns:
            Merged settings dictionary
        """
        import copy
        result = copy.deepcopy(_get_default_settings())

        for section, values in loaded.items():
            if section not in result:
                result[section] = copy.deepcopy(values)
            elif isinstance(values, dict):
                result[section].update(values)

        return result

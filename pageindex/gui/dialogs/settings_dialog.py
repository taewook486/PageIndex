"""
Settings Dialog for PageIndex GUI.

This module provides a comprehensive dialog for managing application settings.
Implements M7 of SPEC-GUI-002.
"""

from typing import Optional

import customtkinter as ctk
import tkinter.messagebox as messagebox

from ..managers.settings_manager import SettingsManager


class SettingsDialog(ctk.CTkToplevel):
    """Dialog for managing application settings."""

    def __init__(self, parent, settings_manager: SettingsManager):
        """Initialize the settings dialog.

        Args:
            parent: Parent window
            settings_manager: SettingsManager instance
        """
        super().__init__(parent)

        self.settings_manager = settings_manager

        # Configure window
        self.title("Settings")
        self.geometry("650x500")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Store original values for cancel
        self._original_settings = self.settings_manager.get_settings()

        # Build UI
        self._create_ui()

        # Load current settings
        self._load_settings()

        # Center on parent
        self._center_on_parent()

    def _create_ui(self):
        """Create the dialog UI."""
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # API Configuration Section
        self._create_api_section(main_frame)

        # Appearance Section
        self._create_appearance_section(main_frame)

        # PDF Options Section
        self._create_pdf_options_section(main_frame)

        # Output Options Section
        self._create_output_options_section(main_frame)

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)

        # Reset button
        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_to_defaults,
            fg_color="gray",
            hover_color="darkgray"
        )
        reset_btn.pack(side="left", padx=5)

        # Apply button
        apply_btn = ctk.CTkButton(
            button_frame,
            text="Apply",
            command=self._apply_settings
        )
        apply_btn.pack(side="right", padx=5)

        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_settings
        )
        save_btn.pack(side="right", padx=5)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            fg_color="darkred",
            hover_color="red"
        )
        cancel_btn.pack(side="right", padx=5)

    def _create_api_section(self, parent):
        """Create API configuration section.

        Args:
            parent: Parent widget
        """
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=5, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            section_frame,
            text="API Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 10), padx=10, anchor="w")

        # API Key
        key_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        key_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(key_frame, text="API Key:", width=100, anchor="w").pack(side="left")

        self.api_key_var = ctk.StringVar()
        self.api_key_entry = ctk.CTkEntry(
            key_frame,
            textvariable=self.api_key_var,
            show="•",
            width=400
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True)

        # Base URL
        url_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(url_frame, text="Base URL:", width=100, anchor="w").pack(side="left")

        self.base_url_var = ctk.StringVar()
        self.base_url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.base_url_var,
            width=400
        )
        self.base_url_entry.pack(side="left", fill="x", expand=True)

        # Model
        model_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(model_frame, text="Model:", width=100, anchor="w").pack(side="left")

        self.model_var = ctk.StringVar()
        self.model_entry = ctk.CTkEntry(
            model_frame,
            textvariable=self.model_var,
            width=400
        )
        self.model_entry.pack(side="left", fill="x", expand=True)

    def _create_appearance_section(self, parent):
        """Create appearance settings section.

        Args:
            parent: Parent widget
        """
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=5, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            section_frame,
            text="Appearance",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 10), padx=10, anchor="w")

        # Theme selection
        theme_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(theme_frame, text="Theme:", width=100, anchor="w").pack(side="left")

        self.theme_var = ctk.StringVar(value="dark")
        theme_options = ["dark", "light", "system"]

        for i, theme in enumerate(theme_options):
            radio = ctk.CTkRadioButton(
                theme_frame,
                text=theme.capitalize(),
                variable=self.theme_var,
                value=theme,
                command=self._on_theme_change
            )
            radio.pack(side="left", padx=10)

        # Font size
        font_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        font_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(font_frame, text="Font Size:", width=100, anchor="w").pack(side="left")

        self.font_size_var = ctk.StringVar()
        self.font_size_entry = ctk.CTkEntry(
            font_frame,
            textvariable=self.font_size_var,
            width=100
        )
        self.font_size_entry.pack(side="left")

    def _create_pdf_options_section(self, parent):
        """Create PDF options section.

        Args:
            parent: Parent widget
        """
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=5, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            section_frame,
            text="PDF Options (Defaults)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 10), padx=10, anchor="w")

        # Grid layout for options
        grid_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=(0, 10))

        # TOC Check Pages
        ctk.CTkLabel(grid_frame, text="TOC Check Pages:", width=150, anchor="w").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.toc_pages_var = ctk.StringVar()
        ctk.CTkEntry(grid_frame, textvariable=self.toc_pages_var, width=100).grid(
            row=0, column=1, sticky="w", pady=5
        )

        # Max Pages/Node
        ctk.CTkLabel(grid_frame, text="Max Pages/Node:", width=150, anchor="w").grid(
            row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.max_pages_var = ctk.StringVar()
        ctk.CTkEntry(grid_frame, textvariable=self.max_pages_var, width=100).grid(
            row=0, column=3, sticky="w", pady=5
        )

        # Max Tokens/Node
        ctk.CTkLabel(grid_frame, text="Max Tokens/Node:", width=150, anchor="w").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.max_tokens_var = ctk.StringVar()
        ctk.CTkEntry(grid_frame, textvariable=self.max_tokens_var, width=100).grid(
            row=1, column=1, sticky="w", pady=5
        )

    def _create_output_options_section(self, parent):
        """Create output options section.

        Args:
            parent: Parent widget
        """
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=5, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            section_frame,
            text="Output Options (Defaults)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 10), padx=10, anchor="w")

        # Checkboxes
        options_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.add_node_id_var = ctk.BooleanVar()
        self.add_summary_var = ctk.BooleanVar()
        self.add_doc_desc_var = ctk.BooleanVar()
        self.add_node_text_var = ctk.BooleanVar()

        ctk.CTkCheckBox(
            options_frame,
            text="Add Node ID",
            variable=self.add_node_id_var
        ).grid(row=0, column=0, sticky="w", pady=5, padx=5)

        ctk.CTkCheckBox(
            options_frame,
            text="Add Summary",
            variable=self.add_summary_var
        ).grid(row=0, column=1, sticky="w", pady=5, padx=5)

        ctk.CTkCheckBox(
            options_frame,
            text="Add Doc Description",
            variable=self.add_doc_desc_var
        ).grid(row=1, column=0, sticky="w", pady=5, padx=5)

        ctk.CTkCheckBox(
            options_frame,
            text="Add Node Text",
            variable=self.add_node_text_var
        ).grid(row=1, column=1, sticky="w", pady=5, padx=5)

    def _load_settings(self):
        """Load current settings into the dialog."""
        # API settings
        api_key = self.settings_manager.get_api_key()
        self.api_key_var.set(api_key)

        base_url = self.settings_manager.get_setting("api", "base_url", "")
        self.base_url_var.set(base_url)

        model = self.settings_manager.get_setting("api", "model", "")
        self.model_var.set(model)

        # Appearance
        theme = self.settings_manager.get_setting("appearance", "theme", "dark")
        self.theme_var.set(theme)

        font_size = self.settings_manager.get_setting("appearance", "font_size", 12)
        self.font_size_var.set(str(font_size))

        # PDF options
        toc_pages = self.settings_manager.get_setting("pdf_options", "toc_check_pages", 20)
        self.toc_pages_var.set(str(toc_pages))

        max_pages = self.settings_manager.get_setting("pdf_options", "max_pages", 10)
        self.max_pages_var.set(str(max_pages))

        max_tokens = self.settings_manager.get_setting("pdf_options", "max_tokens", 20000)
        self.max_tokens_var.set(str(max_tokens))

        # Output options
        self.add_node_id_var.set(
            self.settings_manager.get_setting("output_options", "add_node_id", True)
        )
        self.add_summary_var.set(
            self.settings_manager.get_setting("output_options", "add_node_summary", True)
        )
        self.add_doc_desc_var.set(
            self.settings_manager.get_setting("output_options", "add_doc_description", False)
        )
        self.add_node_text_var.set(
            self.settings_manager.get_setting("output_options", "add_node_text", False)
        )

    def _apply_settings(self):
        """Apply settings without closing dialog."""
        if not self._validate_and_save():
            return

        messagebox.showinfo("Settings", "Settings applied successfully!")

    def _save_settings(self):
        """Save settings and close dialog."""
        if self._validate_and_save():
            self.destroy()

    def _cancel(self):
        """Cancel and close dialog without saving."""
        # Restore original settings
        self.settings_manager._settings = self._original_settings
        self.settings_manager._save_settings()
        self.destroy()

    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        result = messagebox.askyesno(
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values? "
            "Your API key will be preserved."
        )

        if result:
            self.settings_manager.reset_to_defaults()
            self._load_settings()
            messagebox.showinfo("Settings", "Settings reset to defaults.")

    def _validate_and_save(self) -> bool:
        """Validate and save settings.

        Returns:
            True if settings are valid and saved, False otherwise
        """
        # Save to manager
        self.settings_manager.set_api_key(self.api_key_var.get().strip())
        self.settings_manager.set_setting("api", "base_url", self.base_url_var.get().strip())
        self.settings_manager.set_setting("api", "model", self.model_var.get().strip())

        self.settings_manager.set_setting("appearance", "theme", self.theme_var.get())
        try:
            self.settings_manager.set_setting(
                "appearance", "font_size", int(self.font_size_var.get())
            )
        except ValueError:
            messagebox.showerror("Invalid Value", "Font size must be a number.")
            return False

        try:
            self.settings_manager.set_setting(
                "pdf_options", "toc_check_pages", int(self.toc_pages_var.get())
            )
            self.settings_manager.set_setting(
                "pdf_options", "max_pages", int(self.max_pages_var.get())
            )
            self.settings_manager.set_setting(
                "pdf_options", "max_tokens", int(self.max_tokens_var.get())
            )
        except ValueError:
            messagebox.showerror("Invalid Value", "PDF options must be numbers.")
            return False

        self.settings_manager.set_setting("output_options", "add_node_id", self.add_node_id_var.get())
        self.settings_manager.set_setting(
            "output_options", "add_node_summary", self.add_summary_var.get()
        )
        self.settings_manager.set_setting(
            "output_options", "add_doc_description", self.add_doc_desc_var.get()
        )
        self.settings_manager.set_setting("output_options", "add_node_text", self.add_node_text_var.get())

        # Validate
        errors = self.settings_manager.validate_settings()
        if errors:
            messagebox.showerror("Invalid Settings", "\n".join(errors))
            return False

        return True

    def _on_theme_change(self):
        """Handle theme change (apply immediately)."""
        # For now, just show info message
        # Theme change would require application restart
        theme = self.theme_var.get()
        messagebox.showinfo(
            "Theme Change",
            f"Theme changed to {theme}. Please restart the application for full effect."
        )

    def _center_on_parent(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()

        parent = self.master
        if parent:
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()

            dialog_width = self.winfo_width()
            dialog_height = self.winfo_height()

            x = parent_x + (parent_width // 2) - (dialog_width // 2)
            y = parent_y + (parent_height // 2) - (dialog_height // 2)

            self.geometry(f'{dialog_width}x{dialog_height}+{x}+{y}')

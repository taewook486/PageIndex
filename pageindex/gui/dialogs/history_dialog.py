"""
History Dialog for PageIndex GUI.

This module provides a dialog for viewing and managing recent files.
Implements M6 of SPEC-GUI-002.
"""

from typing import Optional, Callable

import customtkinter as ctk

from ..managers.history_manager import HistoryManager, HistoryEntry


class HistoryDialog(ctk.CTkToplevel):
    """Dialog for viewing and managing recent files history."""

    def __init__(
        self,
        parent,
        history_manager: HistoryManager,
        on_file_selected: Optional[Callable[[str], None]] = None
    ):
        """Initialize the history dialog.

        Args:
            parent: Parent window
            history_manager: HistoryManager instance
            on_file_selected: Callback when a file is selected from history
        """
        super().__init__(parent)

        self.history_manager = history_manager
        self.on_file_selected = on_file_selected

        # Configure window
        self.title("Recent Files")
        self.geometry("600x400")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._create_ui()

        # Load history
        self._refresh_history()

        # Center on parent
        self._center_on_parent()

    def _create_ui(self):
        """Create the dialog UI."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Recently Processed Files",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # Scrollable frame for file list
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame, height=300)
        self.scroll_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        # Clear history button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear History",
            command=self._clear_history,
            fg_color="darkred",
            hover_color="red"
        )
        clear_btn.pack(side="right", padx=5)

        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy
        )
        close_btn.pack(side="right", padx=5)

    def _refresh_history(self):
        """Refresh the history display."""
        # Clear existing content
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Get recent files
        recent_files = self.history_manager.get_recent_files()

        if not recent_files:
            # No files message
            no_files_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No recent files found",
                font=ctk.CTkFont(size=14, slant="italic")
            )
            no_files_label.pack(pady=20)
            return

        # Display each file
        for entry in recent_files:
            self._create_file_entry(entry)

    def _create_file_entry(self, entry: HistoryEntry):
        """Create a widget for displaying a file entry.

        Args:
            entry: HistoryEntry to display
        """
        import os
        from datetime import datetime

        # Entry frame
        entry_frame = ctk.CTkFrame(self.scroll_frame)
        entry_frame.pack(fill="x", padx=5, pady=5)

        # File info
        info_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=10)

        # File name
        file_name = os.path.basename(entry.path)
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x")

        # File path
        path_label = ctk.CTkLabel(
            info_frame,
            text=entry.path,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        path_label.pack(fill="x")

        # Metadata frame
        meta_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        meta_frame.pack(fill="x", pady=(5, 0))

        # Status indicator
        status_color = "green" if entry.status == "success" else "red"
        status_text = "✓" if entry.status == "success" else "✗"
        status_label = ctk.CTkLabel(
            meta_frame,
            text=f"{status_text} {entry.status.title()}",
            font=ctk.CTkFont(size=11),
            text_color=status_color
        )
        status_label.pack(side="left")

        # File type
        type_label = ctk.CTkLabel(
            meta_frame,
            text=f"• {entry.file_type.upper()}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        type_label.pack(side="left", padx=5)

        # Timestamp
        try:
            dt = datetime.fromisoformat(entry.timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            time_str = "Unknown"

        time_label = ctk.CTkLabel(
            meta_frame,
            text=f"• {time_str}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        time_label.pack(side="left", padx=5)

        # Processing time
        if entry.processing_time > 0:
            time_label = ctk.CTkLabel(
                meta_frame,
                text=f"• {entry.processing_time:.1f}s",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            time_label.pack(side="left", padx=5)

        # Open button
        open_btn = ctk.CTkButton(
            entry_frame,
            text="Open",
            width=80,
            command=lambda: self._open_file(entry.path)
        )
        open_btn.pack(side="right", padx=10, pady=10)

    def _open_file(self, file_path: str):
        """Handle opening a file from history.

        Args:
            file_path: Path to the file to open
        """
        if self.on_file_selected:
            self.on_file_selected(file_path)
        self.destroy()

    def _clear_history(self):
        """Handle clearing the history."""
        import tkinter.messagebox as messagebox

        # Confirm
        result = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all recent files history?"
        )

        if result:
            self.history_manager.clear_history()
            self._refresh_history()

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

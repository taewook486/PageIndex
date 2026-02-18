"""
JSON Viewer Widgets for PageIndex GUI.

This module provides advanced JSON viewing components with syntax highlighting,
tree view visualization, and summary statistics.
"""

import json
from tkinter import messagebox
from typing import Any, Optional

import customtkinter as ctk


class SyntaxHighlightedTextbox(ctk.CTkTextbox):
    """A textbox with JSON syntax highlighting capabilities."""

    # Color scheme for JSON syntax highlighting
    COLORS = {
        'key': '#569CD6',        # Blue for keys
        'string': '#CE9178',     # Orange/brown for strings
        'number': '#B5CEA8',     # Light green for numbers
        'boolean': '#569CD6',    # Blue for booleans
        'null': '#569CD6',       # Blue for null
        'brace': '#FFD700',      # Gold for braces/brackets
        'default': '#D4D4D4',    # Light gray for default text
    }

    def __init__(self, *args, **kwargs):
        """Initialize the syntax highlighted textbox."""
        super().__init__(*args, **kwargs)
        self.configure(font=ctk.CTkFont(family="Consolas", size=11))

    def display_json(self, data: dict[str, Any]) -> None:
        """Display JSON data with syntax highlighting.

        Args:
            data: JSON data to display
        """
        self.delete("1.0", "end")
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self._insert_highlighted_json(json_str)
        self.configure(state="disabled")

    def _insert_highlighted_json(self, json_str: str) -> None:
        """Insert JSON string with syntax highlighting tags.

        Args:
            json_str: JSON string to highlight and insert
        """
        i = 0
        length = len(json_str)
        in_string = False
        escape_next = False

        while i < length:
            char = json_str[i]

            if escape_next:
                # Handle escaped characters inside strings
                self.insert("end", char)
                escape_next = False
                i += 1
                continue

            if char == '\\' and in_string:
                # Next character is escaped
                self.insert("end", char)
                escape_next = True
                i += 1
                continue

            if char == '"' and not escape_next:
                if in_string:
                    # Closing string
                    self.insert("end", char)
                    in_string = False
                else:
                    # Opening string - could be key or value
                    # Look backwards to determine if this is a key
                    start_pos = i - 1
                    while start_pos >= 0 and json_str[start_pos] in ' \t\n\r':
                        start_pos -= 1

                    if start_pos >= 0 and json_str[start_pos] in ':,([{':
                        # This is a value string
                        self.insert("end", char, ('string',))
                    else:
                        # This might be a key, look for colon after
                        temp_pos = i + 1
                        while temp_pos < length and json_str[temp_pos] not in ':':
                            if json_str[temp_pos] not in ' \t\n\r"':
                                break
                            temp_pos += 1

                        if temp_pos < length and json_str[temp_pos] == ':':
                            # This is a key
                            self.insert("end", char, ('key',))
                        else:
                            # This is a value
                            self.insert("end", char, ('string',))

                    in_string = True
                i += 1
                continue

            if in_string:
                # Inside a string
                self.insert("end", char, ('string',))
                i += 1
                continue

            # Outside of strings - handle other characters
            if char in '{}[]' or char in ':,':
                self.insert("end", char, ('brace',))
            elif char.isdigit() or char == '-':
                # Number
                start = i
                while i < length and (json_str[i].isdigit() or json_str[i] in '.-eE+'):
                    i += 1
                num_str = json_str[start:i]
                self.insert("end", num_str, ('number',))
                continue
            elif char.isalpha():
                # Boolean or null
                start = i
                while i < length and json_str[i].isalpha():
                    i += 1
                word = json_str[start:i]
                if word in ('true', 'false'):
                    self.insert("end", word, ('boolean',))
                elif word == 'null':
                    self.insert("end", word, ('null',))
                else:
                    self.insert("end", word, ('default',))
                continue
            elif not char.isspace():
                self.insert("end", char, ('default',))
            else:
                self.insert("end", char)

            i += 1

        # Apply colors to tags
        for tag_name, color in self.COLORS.items():
            self.tag_config(tag_name, foreground=color)


class TreeNode(ctk.CTkFrame):
    """A collapsible tree node for JSON visualization."""

    def __init__(
        self,
        parent,
        title: str,
        node_id: str = "",
        page_range: str = "",
        has_children: bool = False,
        level: int = 0,
        on_expand: Optional[callable] = None,
        on_collapse: Optional[callable] = None,
        **kwargs
    ):
        """Initialize a tree node.

        Args:
            parent: Parent widget
            title: Node title text
            node_id: Node identifier
            page_range: Page range string (e.g., "pp. 1-10")
            has_children: Whether this node has children
            level: Nesting level (for indentation)
            on_expand: Callback when node is expanded
            on_collapse: Callback when node is collapsed
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.level = level
        self.has_children = has_children
        self.on_expand = on_expand
        self.on_collapse = on_collapse
        self.is_expanded = False
        self.children_container = None

        # Indentation based on level
        indent = 20 * level

        # Main content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="x", padx=(indent, 0), pady=2)

        # Expand/Collapse button
        if has_children:
            self.expand_button = ctk.CTkButton(
                content_frame,
                text="▶",
                width=25,
                height=25,
                font=ctk.CTkFont(size=10),
                command=self._toggle_expand,
                fg_color="transparent",
                hover_color=("gray70", "gray30")
            )
            self.expand_button.pack(side="left", padx=(0, 5))
        else:
            # Leaf node - just an indicator
            leaf_label = ctk.CTkLabel(
                content_frame,
                text="•",
                width=25,
                font=ctk.CTkFont(size=14)
            )
            leaf_label.pack(side="left", padx=(0, 5))

        # Title label
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left")

        # Additional info labels
        if node_id:
            id_label = ctk.CTkLabel(
                content_frame,
                text=f"[{node_id}]",
                font=ctk.CTkFont(size=9),
                text_color="gray"
            )
            id_label.pack(side="left", padx=(5, 0))

        if page_range:
            page_label = ctk.CTkLabel(
                content_frame,
                text=page_range,
                font=ctk.CTkFont(size=9),
                text_color="gray"
            )
            page_label.pack(side="left", padx=(5, 0))

    def _toggle_expand(self):
        """Toggle the expand/collapse state."""
        if self.is_expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self):
        """Expand the node to show children."""
        if not self.has_children or self.is_expanded:
            return

        self.is_expanded = True
        self.expand_button.configure(text="▼")

        if self.on_expand:
            self.on_expand(self)

    def _collapse(self):
        """Collapse the node to hide children."""
        if not self.is_expanded:
            return

        self.is_expanded = False
        self.expand_button.configure(text="▶")

        # Remove children container if it exists
        if self.children_container:
            self.children_container.destroy()
            self.children_container = None

        if self.on_collapse:
            self.on_collapse(self)

    def add_children_container(self):
        """Create and return a container for child nodes."""
        if self.children_container is None:
            self.children_container = ctk.CTkFrame(self, fg_color="transparent")
            self.children_container.pack(fill="x", padx=(20 * (self.level + 1), 0), pady=(0, 5))
        return self.children_container

    def get_state(self) -> bool:
        """Get the current expanded state.

        Returns:
            True if expanded, False if collapsed
        """
        return self.is_expanded


class TreeView(ctk.CTkScrollableFrame):
    """A scrollable tree view for hierarchical JSON data."""

    def __init__(self, master, **kwargs):
        """Initialize the tree view.

        Args:
            master: Parent widget
        """
        super().__init__(master, **kwargs)
        self.nodes: list[TreeNode] = []
        self.expand_all_button = None
        self.collapse_all_button = None

    def load_tree_structure(self, structure: list[dict[str, Any]]) -> None:
        """Load and display a tree structure.

        Args:
            structure: List of node dictionaries
        """
        # Clear existing nodes
        for node in self.nodes:
            node.destroy()
        self.nodes.clear()

        # Create top-level nodes
        for node_data in structure:
            node = self._create_node(node_data, level=0)
            node.pack(fill="x", pady=2)
            self.nodes.append(node)

    def _create_node(self, node_data: dict[str, Any], level: int) -> TreeNode:
        """Create a tree node from data.

        Args:
            node_data: Node data dictionary
            level: Nesting level

        Returns:
            Created TreeNode widget
        """
        title = node_data.get('title', 'Untitled')
        node_id = node_data.get('node_id', '')
        start_idx = node_data.get('start_index', '')
        end_idx = node_data.get('end_index', '')

        page_range = ""
        if start_idx and end_idx:
            page_range = f"(pp. {start_idx}-{end_idx})"

        child_nodes = node_data.get('nodes', [])
        has_children = len(child_nodes) > 0

        def on_expand(node_widget):
            """Handle node expansion."""
            container = node_widget.add_children_container()
            for child_data in child_nodes:
                child = self._create_node(child_data, level=level + 1)
                child.pack(fill="x", pady=1)
                container.pack(fill="x")

        def on_collapse(node_widget):
            """Handle node collapse."""
            pass  # Container is automatically removed

        node = TreeNode(
            self,
            title=title,
            node_id=node_id,
            page_range=page_range,
            has_children=has_children,
            level=level,
            on_expand=on_expand,
            on_collapse=on_collapse
        )

        return node

    def expand_all(self) -> None:
        """Expand all collapsible nodes."""
        for node in self.nodes:
            self._expand_node_recursive(node)

    def collapse_all(self) -> None:
        """Collapse all expanded nodes."""
        for node in self.nodes:
            if node.is_expanded:
                node._collapse()

    def _expand_node_recursive(self, node: TreeNode) -> None:
        """Recursively expand a node and all its children.

        Args:
            node: TreeNode to expand
        """
        if node.has_children and not node.is_expanded:
            node._expand()

            # Expand children recursively
            if node.children_container:
                for child in node.children_container.winfo_children():
                    if isinstance(child, TreeNode):
                        self._expand_node_recursive(child)

    def search(self, query: str) -> int:
        """Search for nodes matching the query.

        Args:
            query: Search query string

        Returns:
            Number of matches found
        """
        if not query:
            return 0

        query_lower = query.lower()
        matches = 0

        for node in self.nodes:
            matches += self._search_node_recursive(node, query_lower)

        return matches

    def _search_node_recursive(self, node: TreeNode, query: str) -> int:
        """Recursively search for matching nodes.

        Args:
            node: TreeNode to search
            query: Lowercase search query

        Returns:
            Number of matches in this subtree
        """
        matches = 0

        # Check if this node matches
        for widget in node.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        text = child.cget("text").lower()
                        if query in text:
                            # Highlight the match
                            child.configure(text_color="#FFD700")
                            matches += 1
                            # Expand parent to show match
                            if node.has_children and not node.is_expanded:
                                node._expand()
                            break

        # Search children
        if node.children_container:
            for child in node.children_container.winfo_children():
                if isinstance(child, TreeNode):
                    matches += self._search_node_recursive(child, query)

        return matches


class SummaryView(ctk.CTkFrame):
    """A view showing summary statistics of JSON data."""

    def __init__(self, master, **kwargs):
        """Initialize the summary view.

        Args:
            master: Parent widget
        """
        super().__init__(master, **kwargs)
        self.summary_labels = {}

        # Create scrollable frame for content
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self, result: dict[str, Any]) -> None:
        """Load and analyze JSON data for summary.

        Args:
            result: Result dictionary containing JSON data
        """
        # Clear existing content
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        structure = result.get('result', {})

        # Document information section
        self._add_section_title("Document Information")

        doc_name = structure.get('doc_name', 'N/A')
        self._add_stat("Document Name", doc_name)

        doc_description = structure.get('doc_description')
        if doc_description:
            self._add_stat("Description", doc_description)

        # Structure statistics
        self._add_section_title("Structure Statistics")

        tree_structure = structure.get('structure', [])
        total_nodes = self._count_total_nodes(tree_structure)
        max_depth = self._calculate_max_depth(tree_structure)
        avg_children = self._calculate_avg_children(tree_structure)

        self._add_stat("Top-Level Nodes", len(tree_structure))
        self._add_stat("Total Nodes", total_nodes)
        self._add_stat("Maximum Depth", max_depth)
        self._add_stat("Avg Children/Node", f"{avg_children:.1f}")

        # Page range
        pages = self._get_page_range(tree_structure)
        if pages:
            self._add_stat("Page Range", f"{pages[0]} - {pages[1]}")
            self._add_stat("Total Pages", pages[1] - pages[0] + 1)

        # Node ID distribution
        self._add_section_title("Node Distribution")

        by_level = self._count_nodes_by_level(tree_structure)
        for level, count in sorted(by_level.items()):
            self._add_stat(f"Level {level}", f"{count} nodes")

        # File information
        self._add_section_title("File Information")

        self._add_stat("File Path", result.get('file_path', 'N/A'))
        self._add_stat("File Type", result.get('file_type', 'N/A').upper())
        self._add_stat("Output File", result.get('output_file', 'N/A'))

    def _add_section_title(self, title: str) -> None:
        """Add a section title.

        Args:
            title: Section title text
        """
        label = ctk.CTkLabel(
            self.scroll_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        label.pack(fill="x", pady=(15, 5))

        # Add separator line
        separator = ctk.CTkFrame(self.scroll_frame, height=2)
        separator.pack(fill="x", pady=(0, 5))

    def _add_stat(self, label: str, value: str) -> None:
        """Add a statistic label pair.

        Args:
            label: Statistic label
            value: Statistic value
        """
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame.pack(fill="x", pady=2)

        label_widget = ctk.CTkLabel(
            frame,
            text=f"{label}:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
            width=200
        )
        label_widget.pack(side="left")

        value_widget = ctk.CTkLabel(
            frame,
            text=str(value),
            anchor="w"
        )
        value_widget.pack(side="left", fill="x", expand=True)

    def _count_total_nodes(self, nodes: list[dict[str, Any]]) -> int:
        """Count total nodes recursively.

        Args:
            nodes: List of node dictionaries

        Returns:
            Total node count
        """
        count = len(nodes)
        for node in nodes:
            children = node.get('nodes', [])
            if children:
                count += self._count_total_nodes(children)
        return count

    def _calculate_max_depth(self, nodes: list[dict[str, Any]], current_depth: int = 1) -> int:
        """Calculate maximum tree depth.

        Args:
            nodes: List of node dictionaries
            current_depth: Current depth level

        Returns:
            Maximum depth
        """
        if not nodes:
            return current_depth

        max_child_depth = current_depth
        for node in nodes:
            children = node.get('nodes', [])
            if children:
                child_depth = self._calculate_max_depth(children, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _calculate_avg_children(self, nodes: list[dict[str, Any]]) -> float:
        """Calculate average number of children per node.

        Args:
            nodes: List of node dictionaries

        Returns:
            Average children count
        """
        total_children = 0
        total_parents = 0

        def count_recursive(node_list):
            nonlocal total_children, total_parents
            for node in node_list:
                children = node.get('nodes', [])
                if children:
                    total_parents += 1
                    total_children += len(children)
                    count_recursive(children)

        count_recursive(nodes)

        if total_parents == 0:
            return 0.0

        return total_children / total_parents

    def _count_nodes_by_level(self, nodes: list[dict[str, Any]], level: int = 0) -> dict[int, int]:
        """Count nodes at each level.

        Args:
            nodes: List of node dictionaries
            level: Current level

        Returns:
            Dictionary mapping level to count
        """
        counts = {level: len(nodes)}

        for node in nodes:
            children = node.get('nodes', [])
            if children:
                child_counts = self._count_nodes_by_level(children, level + 1)
                for level, count in child_counts.items():
                    counts[level] = counts.get(level, 0) + count

        return counts

    def _get_page_range(self, nodes: list[dict[str, Any]]) -> tuple | None:
        """Get overall page range from structure.

        Args:
            nodes: List of node dictionaries

        Returns:
            Tuple of (start_page, end_page) or None
        """
        all_pages = []

        def collect_pages(node_list):
            for node in node_list:
                start = node.get('start_index')
                end = node.get('end_index')
                if start is not None:
                    all_pages.append(start)
                if end is not None:
                    all_pages.append(end)

                children = node.get('nodes', [])
                if children:
                    collect_pages(children)

        collect_pages(nodes)

        if not all_pages:
            return None

        return (min(all_pages), max(all_pages))


class JsonViewerTabView(ctk.CTkTabview):
    """A tabbed view for displaying JSON in multiple formats."""

    def __init__(self, master, **kwargs):
        """Initialize the JSON viewer tab view.

        Args:
            master: Parent widget
        """
        super().__init__(master, **kwargs)

        # Create tabs
        self.add("Formatted JSON")
        self.add("Tree View")
        self.add("Summary")

        # Store references to tab widgets
        self.json_textbox = None
        self.tree_view = None
        self.summary_view = None
        self.search_entry = None

        # Initialize each tab
        self._init_json_tab()
        self._init_tree_tab()
        self._init_summary_tab()

    def _init_json_tab(self):
        """Initialize the formatted JSON tab."""
        self.set("Formatted JSON")

        # Create search/frame at top
        top_frame = ctk.CTkFrame(self.tab("Formatted JSON"))
        top_frame.pack(fill="x", padx=5, pady=5)

        # Copy button
        copy_btn = ctk.CTkButton(
            top_frame,
            text="Copy JSON",
            command=self._copy_json_to_clipboard,
            width=100
        )
        copy_btn.pack(side="right", padx=5)

        # Search label
        ctk.CTkLabel(top_frame, text="Search:").pack(side="left", padx=5)

        # Search entry
        self.search_entry = ctk.CTkEntry(top_frame, width=200)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", self._on_json_search)

        # Search button
        search_btn = ctk.CTkButton(
            top_frame,
            text="Find",
            command=self._on_json_search,
            width=60
        )
        search_btn.pack(side="left", padx=5)

        # JSON textbox with line numbers
        json_frame = ctk.CTkFrame(self.tab("Formatted JSON"))
        json_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.json_textbox = SyntaxHighlightedTextbox(json_frame)
        self.json_textbox.pack(fill="both", expand=True)

    def _init_tree_tab(self):
        """Initialize the tree view tab."""
        self.set("Tree View")

        # Control frame
        control_frame = ctk.CTkFrame(self.tab("Tree View"))
        control_frame.pack(fill="x", padx=5, pady=5)

        # Expand/Collapse buttons
        expand_btn = ctk.CTkButton(
            control_frame,
            text="Expand All",
            command=self._expand_all_tree_nodes,
            width=100
        )
        expand_btn.pack(side="right", padx=5)

        collapse_btn = ctk.CTkButton(
            control_frame,
            text="Collapse All",
            command=self._collapse_all_tree_nodes,
            width=100
        )
        collapse_btn.pack(side="right", padx=5)

        # Search
        ctk.CTkLabel(control_frame, text="Search:").pack(side="left", padx=5)
        tree_search_entry = ctk.CTkEntry(control_frame, width=200)
        tree_search_entry.pack(side="left", padx=5)
        tree_search_entry.bind("<Return>", lambda: self._on_tree_search(tree_search_entry.get()))

        search_btn = ctk.CTkButton(
            control_frame,
            text="Find",
            command=lambda: self._on_tree_search(tree_search_entry.get()),
            width=60
        )
        search_btn.pack(side="left", padx=5)

        # Tree view
        self.tree_view = TreeView(self.tab("Tree View"))
        self.tree_view.pack(fill="both", expand=True, padx=5, pady=5)

    def _init_summary_tab(self):
        """Initialize the summary tab."""
        self.set("Summary")

        # Summary view
        self.summary_view = SummaryView(self.tab("Summary"))
        self.summary_view.pack(fill="both", expand=True, padx=5, pady=5)

    def load_result(self, result: dict[str, Any]) -> None:
        """Load and display result data in all tabs.

        Args:
            result: Processing result dictionary
        """
        structure = result.get('result', {})

        # Load JSON tab
        if self.json_textbox:
            self.json_textbox.display_json(structure)

        # Load tree tab
        if self.tree_view:
            tree_structure = structure.get('structure', [])
            self.tree_view.load_tree_structure(tree_structure)

        # Load summary tab
        if self.summary_view:
            self.summary_view.load_data(result)

    def _copy_json_to_clipboard(self) -> None:
        """Copy JSON content to clipboard."""
        try:
            if self.json_textbox:
                content = self.json_textbox.get("1.0", "end")
                self.clipboard_clear()
                self.clipboard_append(content)
                messagebox.showinfo("Copy Successful", "JSON content copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Failed", f"Failed to copy: {e}")

    def _on_json_search(self, event=None) -> None:
        """Search for text in JSON view.

        Args:
            event: Tkinter event (optional)
        """
        if not self.search_entry or not self.json_textbox:
            return

        query = self.search_entry.get()
        if not query:
            return

        pos = self.json_textbox.search(query, "1.0", stopindex="end", nocase=True)
        if pos:
            self.json_textbox.tag_remove("sel", "1.0", "end")
            self.json_textbox.tag_add("sel", pos, f"{pos}+{len(query)}c")
            self.json_textbox.mark_set("insert", f"{pos}+{len(query)}c")
            self.json_textbox.see(pos)
            self.json_textbox.focus_set()
        else:
            messagebox.showinfo("Search", f"'{query}' not found")

    def _on_tree_search(self, query: str) -> None:
        """Search for nodes in tree view.

        Args:
            query: Search query string
        """
        if not self.tree_view or not query:
            return

        matches = self.tree_view.search(query)
        messagebox.showinfo("Search", f"Found {matches} nodes matching '{query}'")

    def _expand_all_tree_nodes(self) -> None:
        """Expand all nodes in tree view."""
        if self.tree_view:
            self.tree_view.expand_all()

    def _collapse_all_tree_nodes(self) -> None:
        """Collapse all nodes in tree view."""
        if self.tree_view:
            self.tree_view.collapse_all()

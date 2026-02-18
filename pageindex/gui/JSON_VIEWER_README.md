# JSON Viewer Implementation

## Overview

The PageIndex GUI now includes an advanced JSON result viewer with three viewing modes, syntax highlighting, and interactive tree navigation.

## Features

### 1. Formatted JSON View
- **Syntax Highlighting**: Color-coded JSON elements
  - Keys: Blue
  - Strings: Orange/Brown
  - Numbers: Light Green
  - Booleans/Null: Blue
  - Braces/Brackets: Gold

- **Search Functionality**: Find text within the JSON
- **Copy to Clipboard**: One-click JSON copy

### 2. Interactive Tree View
- **Collapsible/Expandable Nodes**: Click to expand or collapse nodes
- **Hierarchical Display**: Visual tree structure with indentation
- **Page Ranges**: Shows page ranges for each node (e.g., "pp. 1-10")
- **Node IDs**: Displays node identifiers
- **Search**: Search for nodes by title
- **Expand/Collapse All**: Bulk operations for all nodes

### 3. Summary View
Key statistics and information:
- Document Information
  - Document name and description
  - File path and type

- Structure Statistics
  - Total node count
  - Maximum depth
  - Average children per node
  - Page range and total pages

- Node Distribution
  - Nodes per level breakdown

## Usage

### In the Main Application

1. Process a document (PDF or Markdown)
2. Results automatically appear in the Results section
3. Click tabs to switch between views:
   - **Formatted JSON**: Syntax-highlighted raw JSON
   - **Tree View**: Interactive hierarchical view
   - **Summary**: Statistics and overview

### Tree View Navigation

- Click the ▶ button to expand a node
- Click the ▼ button to collapse a node
- Use "Expand All" to open entire tree
- Use "Collapse All" to close entire tree
- Use search to find specific nodes (matches are highlighted)

## Architecture

### Components

#### `SyntaxHighlightedTextbox`
Extends `CTkTextbox` with JSON syntax highlighting.

**Methods**:
- `display_json(data: Dict[str, Any])`: Display JSON with highlighting
- `_insert_highlighted_json(json_str: str)`: Internal highlighting logic

**Features**:
- Token-based parsing for accurate highlighting
- Custom color scheme via `COLORS` class attribute
- Preserves JSON formatting with 2-space indentation

#### `TreeNode`
Represents a single node in the tree view.

**Parameters**:
- `title`: Node title
- `node_id`: Node identifier
- `page_range`: Page range string
- `has_children`: Whether node has children
- `level`: Nesting depth (for indentation)
- `on_expand`: Callback when expanded
- `on_collapse`: Callback when collapsed

**Features**:
- Lazy loading of children (only loaded when expanded)
- Visual indicators for leaf nodes (•) vs parent nodes (▶/▼)
- Automatic indentation based on nesting level

#### `TreeView`
Scrollable container for tree nodes.

**Methods**:
- `load_tree_structure(structure: List[Dict])`: Load tree data
- `expand_all()`: Expand all nodes recursively
- `collapse_all()`: Collapse all nodes
- `search(query: str)`: Search and highlight matches

**Features**:
- Handles arbitrary depth nesting
- Efficient rendering with lazy loading
- Search highlighting with gold color

#### `SummaryView`
Displays statistics and metadata.

**Methods**:
- `load_data(result: Dict[str, Any])`: Analyze and display data
- Statistics calculation methods (private)

**Features**:
- Automatic analysis of tree structure
- Page range calculation
- Node distribution by level

#### `JsonViewerTabView`
Main tabbed interface combining all views.

**Tabs**:
1. Formatted JSON with search and copy
2. Tree View with expand/collapse controls
3. Summary statistics

**Methods**:
- `load_result(result: Dict[str, Any])`: Load data into all tabs
- Tab-specific search handlers
- Clipboard operations

## File Structure

```
pageindex/gui/
├── __init__.py           # Updated to export json_viewer
├── main_window.py        # Updated to use JsonViewerTabView
├── json_viewer.py        # NEW: All JSON viewer components
└── processing/           # Existing: Background processing
tests/
├── test_json_viewer.py   # NEW: Test/demo application
└── results/             # Existing: Sample JSON files
```

## Integration with Main Window

The `main_window.py` file was updated to use `JsonViewerTabView`:

**Before**:
```python
self.results_text = ctk.CTkTextbox(...)
self.results_text.insert("1.0", "Results will be displayed here...")
```

**After**:
```python
self.json_viewer = JsonViewerTabView(
    results_frame,
    width=700,
    height=200
)
self.json_viewer.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# Keep results_text for progress messages (hidden)
self.results_text = ctk.CTkTextbox(results_frame, height=0, ...)
```

**Display Logic**:
```python
def _display_result(self, result: Dict[str, Any]):
    """Display processing result in the improved JSON viewer."""
    # Load result into the JSON viewer tab view
    self.json_viewer.load_result(result)

    # Also show summary in hidden results_text
    self.results_text.configure(state="normal")
    self.results_text.delete("1.0", "end")
    # ... summary text ...
    self.results_text.configure(state="disabled")
```

## Performance Considerations

### Large JSON Files (~20KB)

**Optimizations Implemented**:
1. **Lazy Loading**: Tree nodes only create children when expanded
2. **Efficient Parsing**: Single-pass syntax highlighting
3. **Virtual Scrolling**: CustomTkinter's `CTkScrollableFrame` handles large content
4. **String Tags**: Efficient text coloring with tkinter tags

**Memory Usage**:
- Tree View: O(nodes) only for expanded nodes
- JSON View: O(1) with streaming insert
- Summary View: O(nodes) for statistics calculation

### Recommended Limits

- **Nodes**: < 10,000 nodes for smooth tree navigation
- **JSON Size**: < 1MB for syntax highlighting
- **Depth**: No hard limit, but > 10 levels may be hard to navigate

## Testing

Run the test application:

```bash
cd /path/to/PageIndex
python tests/test_json_viewer.py
```

**Test Features**:
- Tabbed viewer with all three views
- Individual component testing
- Sample data from test results
- Interactive controls

## Future Enhancements

Possible improvements:
1. **Export**: Export tree view as image or markdown
2. **Filtering**: Filter nodes by criteria
3. **Bookmarks**: Mark/favorite specific nodes
4. **Diff View**: Compare two JSON structures
5. **JSONPath/XPath**: Advanced query support
6. **Edit Mode**: Direct JSON editing with validation

## Compatibility

- **CustomTkinter**: Version 5.0.0+
- **Python**: 3.9+
- **Platform**: Windows, macOS, Linux
- **Display**: Minimum 800x600 resolution recommended

## Troubleshooting

### Issue: Tree view doesn't expand
**Solution**: Ensure nodes have `nodes` key with non-empty list

### Issue: Syntax highlighting missing
**Solution**: Check that CustomTkinter supports text tags

### Issue: Search doesn't work
**Solution**: Make sure to press Enter after typing search query

### Issue: Performance slow with large files
**Solution**: Consider expanding fewer nodes at a time, or use Summary view

## Code Style

Follows project conventions:
- Black formatting (line length 100)
- Type hints for all public methods
- Docstrings for all classes and methods
- PEP 8 naming conventions
- TRUST 5 quality principles

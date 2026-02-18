# ACCEPTANCE: PageIndex GUI Application

**Metadata**
- **SPEC ID**: SPEC-GUI-001
- **Document**: acceptance.md
- **Version**: 1.0
- **Last Updated**: 2025-02-18

---

## Acceptance Criteria

### Overview

All acceptance criteria follow the **Given-When-Then** format for clear test scenario definition.

---

## Functional Requirements Acceptance

### AC-001: File Selection

**Scenario 1: Drag & Drop PDF File**
```gherkin
GIVEN the GUI application is running
AND the main window is displayed
WHEN the user drags a PDF file onto the drop zone
THEN the file path should be displayed
AND the file should be validated as a valid PDF
AND the "Start Conversion" button should be enabled
```

**Scenario 2: Drag & Drop Markdown File**
```gherkin
GIVEN the GUI application is running
AND the main window is displayed
WHEN the user drags a Markdown file onto the drop zone
THEN the file path should be displayed
AND the file should be validated as a valid Markdown file
AND the "Start Conversion" button should be enabled
```

**Scenario 3: Invalid File Rejection**
```gherkin
GIVEN the GUI application is running
AND the main window is displayed
WHEN the user drags a file with invalid extension (e.g., .exe, .txt)
THEN an error message should be displayed
AND the file should not be accepted
AND the drop zone should show visual error feedback
```

**Scenario 4: Browse File Dialog**
```gherkin
GIVEN the GUI application is running
AND no file is currently selected
WHEN the user clicks the "Browse Files" button
THEN a file picker dialog should open
AND the dialog should filter for PDF and Markdown files
AND selecting a valid file should update the file path display
```

---

### AC-002: Configuration Management

**Scenario 1: Load Default Configuration**
```gherkin
GIVEN the GUI application is starting
AND a config.yaml file exists with default values
WHEN the main window is displayed
THEN all configuration fields should show default values
AND the values should match config.yaml settings
```

**Scenario 2: Save Configuration Changes**
```gherkin
GIVEN the GUI application is running
AND the user has modified configuration values
WHEN the user changes focus from a configuration field
THEN the new value should be validated
AND if valid, the value should be saved to gui_settings.yaml
```

**Scenario 3: Invalid Configuration Input**
```gherkin
GIVEN the GUI application is running
AND the user is editing a numeric configuration field
WHEN the user enters a value outside the valid range
THEN an inline error message should be displayed
AND the field should be highlighted in red
AND the "Start Conversion" button should be disabled
```

**Scenario 4: API Key Configuration**
```gherkin
GIVEN the GUI application is running
AND the user opens the Settings dialog
WHEN the user enters a new API key
AND clicks "Save"
THEN the new API key should be saved to .env file
AND a success message should be displayed
```

---

### AC-003: PDF Processing

**Scenario 1: Successful PDF Conversion**
```gherkin
GIVEN a valid PDF file is selected
AND valid configuration is set
WHEN the user clicks "Start Conversion"
THEN a progress bar should appear
AND the progress should update in real-time
AND upon completion, a success message should be displayed
AND the results should be displayed in the results viewer
```

**Scenario 2: PDF Processing with TOC**
```gherkin
GIVEN a PDF file with a table of contents is selected
AND the user has enabled "Add Node Summary"
WHEN the conversion completes
THEN the results should include a hierarchical tree structure
AND each node should have a summary
AND the structure should reflect the TOC hierarchy
```

**Scenario 3: PDF Processing without TOC**
```gherkin
GIVEN a PDF file without a table of contents is selected
WHEN the conversion completes
THEN the results should include an automatically generated tree structure
AND the structure should be based on content analysis
```

**Scenario 4: Large PDF Processing**
```gherkin
GIVEN a PDF file larger than 100MB is selected
WHEN the user attempts to start conversion
THEN a confirmation dialog should be displayed
AND the dialog should warn about processing time
AND the user can choose to continue or cancel
```

---

### AC-004: Markdown Processing

**Scenario 1: Successful Markdown Conversion**
```gherkin
GIVEN a valid Markdown file is selected
AND valid configuration is set
WHEN the user clicks "Start Conversion"
THEN the progress should be displayed
AND upon completion, the tree structure should reflect header hierarchy
AND results should be displayed in the results viewer
```

**Scenario 2: Markdown with Thinning Enabled**
```gherkin
GIVEN a Markdown file is selected
AND the user has enabled "Enable Thinning"
AND set "Min Threshold" to 5000
WHEN the conversion completes
THEN nodes with fewer than 5000 tokens should be merged with parents
AND the tree structure should be more compact
```

**Scenario 3: Invalid Markdown Structure**
```gherkin
GIVEN a Markdown file with no headers is selected
WHEN the conversion is attempted
THEN a warning should be displayed
AND the user should be informed about the lack of structure
AND the conversion should proceed with a flat structure
```

---

### AC-005: Progress Display

**Scenario 1: Progress Bar Updates**
```gherkin
GIVEN a file conversion is in progress
WHEN processing progresses
THEN the progress bar should reflect the percentage complete
AND the percentage should be displayed numerically
AND the progress should be smooth (no jumps)
```

**Scenario 2: Status Messages**
```gherkin
GIVEN a file conversion is in progress
WHEN different processing stages occur
THEN status messages should be displayed
AND messages should indicate current action (e.g., "Extracting text", "Building tree")
AND messages should be updated in real-time
```

**Scenario 3: Cancellation Support**
```gherkin
GIVEN a file conversion is in progress
WHEN the user clicks "Cancel"
THEN the conversion should stop gracefully
AND a cancellation message should be displayed
AND the GUI should return to ready state
AND any partial results should be cleaned up
```

---

### AC-006: Results Display

**Scenario 1: Tree View Display**
```gherkin
GIVEN a conversion has completed successfully
WHEN the results are displayed
THEN a tree view should show the document structure
AND nodes should be expandable/collapsible
AND node details should be visible on selection
```

**Scenario 2: JSON Viewer**
```gherkin
GIVEN a conversion has completed successfully
WHEN the user switches to JSON view
THEN the complete JSON structure should be displayed
AND the JSON should be properly formatted
AND sections should be collapsible
```

**Scenario 3: Export Results**
```gherkin
GIVEN results are displayed
WHEN the user clicks "Export"
THEN a file save dialog should appear
AND the user should be able to save as JSON
AND the exported file should match the results exactly
```

**Scenario 4: Open Results Folder**
```gherkin
GIVEN a conversion has completed successfully
WHEN the user clicks "Open Results Folder"
THEN the system file manager should open
AND the results directory should be displayed
AND the generated JSON file should be highlighted
```

---

## Non-Functional Requirements Acceptance

### AC-NFR-001: Performance

**Scenario 1: GUI Responsiveness**
```gherkin
GIVEN a file conversion is in progress
WHEN the user interacts with the GUI
THEN the GUI should respond immediately
AND no freezing should occur
AND window movements should be smooth
```

**Scenario 2: Processing Overhead**
```gherkin
GIVEN the same file is processed via CLI and GUI
WHEN comparing processing times
THEN the GUI overhead should be less than 10%
AND the results should be identical
```

---

### AC-NFR-002: Usability

**Scenario 1: Error Message Clarity**
```gherkin
GIVEN an error occurs during processing
WHEN the error is displayed
THEN the message should be in user-friendly language
AND the message should suggest corrective action
AND technical jargon should be minimized
```

**Scenario 2: Tooltips and Help**
```gherkin
GIVEN the user hovers over a configuration field
WHEN the cursor pauses on the field
THEN a tooltip should appear
AND the tooltip should explain the parameter
AND an example value should be shown
```

**Scenario 3: Keyboard Navigation**
```gherkin
GIVEN the GUI application is running
WHEN the user uses keyboard navigation (Tab, Enter, Escape)
THEN all controls should be accessible via keyboard
AND focus should be visible
AND Enter/Escape should work as expected
```

---

### AC-NFR-003: Reliability

**Scenario 1: Crash Recovery**
```gherkin
GIVEN the application crashes during processing
WHEN the user restarts the application
THEN the application should restart successfully
AND any unsaved configuration should be recoverable
AND a crash report should be generated
```

**Scenario 2: Configuration Corruption**
```gherkin
GIVEN the gui_settings.yaml file is corrupted
WHEN the application starts
THEN default values should be loaded
AND an error message should be displayed
AND the user should be prompted to reset configuration
```

**Scenario 3: Thread Safety**
```gherkin
GIVEN multiple operations are running in background threads
WHEN the threads update the GUI
THEN no race conditions should occur
AND the GUI should remain stable
AND all updates should be thread-safe
```

---

## Backward Compatibility Acceptance

### AC-BC-001: CLI Preservation

**Scenario 1: CLI Functionality Unchanged**
```gherkin
GIVEN the original CLI entry point (run_pageindex.py) exists
WHEN the user runs the CLI with existing arguments
THEN all CLI functionality should work as before
AND the output should be identical to pre-GUI version
AND no breaking changes should exist
```

**Scenario 2: Shared Configuration**
```gherkin
GIVEN both CLI and GUI use the same config.yaml
WHEN configuration is updated via GUI
THEN CLI should use the updated configuration
AND vice versa
```

---

## Security Acceptance

### AC-SEC-001: API Key Protection

**Scenario 1: API Key Not Logged**
```gherkin
GIVEN the application is processing files
WHEN logs are written
THEN the API key should not appear in any log file
AND the API key should be redacted from error messages
```

**Scenario 2: API Key Storage**
```gherkin
GIVEN the user enters an API key
WHEN the key is saved
THEN it should be stored in .env file only
AND the key should not be stored in gui_settings.yaml
AND file permissions should restrict access to owner only
```

---

## Definition of Done

A feature is considered complete when:

1. **Code Complete**
   - [ ] All implementation tasks are finished
   - [ ] Code follows project style guidelines
   - [ ] Code is reviewed and approved

2. **Testing Complete**
   - [ ] All acceptance criteria pass
   - [ ] Unit tests written (85%+ coverage for new code)
   - [ ] Integration tests pass
   - [ ] Manual testing completed

3. **Documentation Complete**
   - [ ] User documentation is written
   - [ ] API documentation is updated
   - [ ] Code comments are sufficient
   - [ ] README is updated

4. **Quality Gates Passed**
   - [ ] No critical bugs
   - [ ] No high-severity issues
   - [ ] Performance benchmarks met
   - [ ] Security review passed

5. **User Acceptance**
   - [ ] User testing completed
   - [ ] Feedback addressed
   - [ ] Stakeholder approval obtained

---

## Test Execution Record

| Test ID | Scenario | Status | Date | Tester | Notes |
|---------|----------|--------|------|--------|-------|
| AC-001-001 | Drag & Drop PDF | Pending | - | - | - |
| AC-001-002 | Drag & Drop MD | Pending | - | - | - |
| AC-001-003 | Invalid File | Pending | - | - | - |
| AC-002-001 | Load Defaults | Pending | - | - | - |
| AC-003-001 | PDF Conversion | Pending | - | - | - |
| AC-004-001 | MD Conversion | Pending | - | - | - |
| AC-005-001 | Progress Display | Pending | - | - | - |
| AC-006-001 | Results Display | Pending | - | - | - |
| AC-NFR-001-001 | GUI Responsiveness | Pending | - | - | - |
| AC-BC-001-001 | CLI Preservation | Pending | - | - | - |

---

**TAG**: SPEC-GUI-001
**Traceability**: All acceptance criteria map to requirements in spec.md and tasks in plan.md

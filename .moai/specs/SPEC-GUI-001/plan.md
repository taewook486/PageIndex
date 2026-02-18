# PLAN: PageIndex GUI Implementation

**Metadata**
- **SPEC ID**: SPEC-GUI-001
- **Document**: plan.md
- **Version**: 1.0
- **Last Updated**: 2025-02-18

---

## Implementation Strategy

### Development Approach

**Methodology**: Hybrid (TDD for new GUI components, DDD for existing CLI integration)

**Rationale**:
- GUI components are new → TDD approach with test-first UI automation
- Existing business logic → DDD approach with characterization tests
- Integration layer → Hybrid approach based on component type

---

## Milestones (Priority-Based)

### 🎯 Primary Goal: Core GUI Functionality

**M1. Basic GUI Framework Setup**
- Create `pageindex/gui/` package structure
- Implement main window with CustomTkinter
- Establish event handling architecture
- Set up thread pool for async operations

**Success Criteria**:
- [x] Application launches without errors
- [x] Main window displays correctly
- [x] Window can be closed cleanly
- [x] Theme switching works (light/dark)

**Dependencies**:
- CustomTkinter installation
- Existing pageindex package

**Estimated Complexity**: Medium

---

**M2. File Selection Interface**

**Tasks**:
1. Implement drag & drop file zone
2. Add file browser dialog
3. Create file validation logic
4. Implement file type detection

**Success Criteria**:
- [x] PDF files can be selected
- [x] Markdown files can be selected
- [x] Invalid files are rejected with clear error
- [x] Selected file path is displayed

**Dependencies**: M1

**Estimated Complexity**: Low

---

**M3. Configuration Panel**

**Tasks**:
1. Create parameter input widgets
2. Implement validation for all inputs
3. Add configuration persistence
4. Create defaults from `config.yaml`

**Success Criteria**:
- [x] All CLI parameters have GUI equivalents
- [x] Invalid inputs show inline errors
- [x] Configuration saves to `gui_settings.yaml`
- [x] Defaults load correctly on startup

**Dependencies**: M1

**Estimated Complexity**: Medium

---

**M4. Progress Display System**

**Tasks**:
1. Implement progress bar widget
2. Create status message callback system
3. Add cancellation support
4. Implement thread-safe GUI updates

**Success Criteria**:
- [x] Progress updates in real-time
- [x] Status messages are clear
- [x] Cancellation works safely
- [x] No GUI freezing during processing

**Dependencies**: M1, M3

**Estimated Complexity**: High (requires thread management)

---

**M5. Results Display**

**Tasks**:
1. Create tree view widget for document structure
2. Implement JSON viewer
3. Add export functionality
4. Create results folder access button

**Success Criteria**:
- [x] Tree structure displays hierarchically
- [x] JSON is properly formatted and collapsible
- [x] Results can be exported/copied
- [x] Results folder opens in file manager

**Dependencies**: M1, M2, M4

**Estimated Complexity**: Medium

---

### 🎯 Secondary Goal: Advanced Features

**M6. Recent Files Management**

**Tasks**:
1. Implement recent files tracking
2. Create recent files menu
3. Add file history persistence
4. Implement quick-open functionality

**Success Criteria**:
- [x] Last 10 files are tracked
- [x] Recent files persist across sessions
- [x] Quick-open works from menu

**Dependencies**: M2

**Estimated Complexity**: Low

---

**M7. Settings Management**

**Tasks**:
1. Create settings dialog
2. Implement API key management
3. Add theme selection
4. Create reset to defaults option

**Success Criteria**:
- [x] Settings dialog opens and closes properly
- [x] API key can be updated
- [x] Theme changes apply immediately
- [x] Reset works correctly

**Dependencies**: M1

**Estimated Complexity**: Medium

---

### 🎯 Final Goal: Polish & Documentation

**M8. Error Handling & User Feedback**

**Tasks**:
1. Implement comprehensive error dialogs
2. Add help tooltips
3. Create user documentation
4. Implement logging viewer

**Success Criteria**:
- [x] All errors have user-friendly messages
- [x] Tooltips explain all parameters
- [x] User guide is complete
- [x] Logs can be viewed in-app

**Dependencies**: All previous milestones

**Estimated Complexity**: Medium

---

### 🎯 Optional Goal: Nice-to-Have Features

**M9. Enhanced Visualizations**

**Tasks**:
1. Add document statistics dashboard
2. Create processing timeline view
3. Implement batch processing mode
4. Add result comparison tool

**Success Criteria**:
- [x] Statistics display accurately
- [x] Timeline shows processing steps
- [x] Multiple files can be queued
- [x] Results can be compared side-by-side

**Dependencies**: M5, M8

**Estimated Complexity**: High

---

## Technical Approach

### File Structure

```
pageindex/
├── __init__.py                 # (existing)
├── page_index.py               # (existing, reused)
├── page_index_md.py            # (existing, reused)
├── models.py                   # (existing, reused)
├── utils.py                    # (existing, reused)
├── constants.py                # (existing, reused)
├── config.yaml                 # (existing, reused)
│
├── gui/                        # NEW: GUI package
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── main_window.py          # Main window class
│   ├── widgets/                # Custom widgets
│   │   ├── __init__.py
│   │   ├── file_drop_zone.py
│   │   ├── config_panel.py
│   │   ├── progress_bar.py
│   │   └── results_viewer.py
│   ├── dialogs/                # Dialog windows
│   │   ├── __init__.py
│   │   ├── settings_dialog.py
│   │   └── error_dialog.py
│   ├── processing/             # Background processing
│   │   ├── __init__.py
│   │   ├── processor.py
│   │   └── progress_callback.py
│   ├── config/                 # GUI configuration
│   │   ├── __init__.py
│   │   └── gui_settings.py
│   └── themes/                 # Theme definitions
│       ├── __init__.py
│       └── colors.py
│
run_pageindex.py                # (existing, preserved for CLI)
run_pageindex_gui.py            # NEW: GUI entry point
```

### Key Design Decisions

**Decision 1: Thread Management**
- **Approach**: Separate thread for each processing job
- **Rationale**: Prevents GUI freezing, allows cancellation
- **Risk**: Thread safety for shared resources
- **Mitigation**: Thread-safe queues for callbacks

**Decision 2: Configuration Management**
- **Approach**: YAML-based settings with runtime defaults
- **Rationale**: Consistent with existing CLI config system
- **Risk**: Configuration drift between CLI and GUI
- **Mitigation**: Shared `config.yaml` base with GUI overrides

**Decision 3: Async/Await Integration**
- **Approach**: Run async functions in thread with new event loop
- **Rationale**: Existing business logic uses async/await
- **Risk**: Event loop conflicts
- **Mitigation**: Dedicated event loop per thread

**Decision 4: Error Handling**
- **Approach**: Try-catch with user-friendly dialogs
- **Rationale**: Non-technical users need clear guidance
- **Risk**: Over-generalization of errors
- **Mitigation**: Specific exception handling with context

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| GUI freezing during long operations | High | Medium | Thread pool with progress callbacks |
| Thread safety issues | High | Medium | Thread-safe queues, locks for shared state |
| Configuration conflicts with CLI | Medium | Low | Separate GUI settings file, merge on load |
| Async event loop conflicts | High | Medium | Dedicated event loop per processing thread |
| File path encoding issues (Windows) | Medium | Low | Use pathlib for cross-platform paths |
| API key exposure in logs | High | Low | Redact sensitive info in logging |

---

## Quality Assurance

### Testing Strategy

**Unit Tests** (TDD for new GUI components):
- Widget behavior tests
- Configuration validation tests
- File type detection tests
- Thread-safe callback tests

**Integration Tests** (DDD for CLI integration):
- End-to-end processing with GUI
- Configuration persistence tests
- Error handling integration tests

**UI Tests** (Manual/Automated):
- Visual regression tests
- User workflow tests
- Accessibility tests

### Coverage Targets

- New GUI code: 85%+ coverage
- Integration layer: 80%+ coverage
- Existing business logic: Preserve current coverage

---

## Rollout Strategy

**Phase 1: Alpha Release** (M1-M4)
- Core GUI functionality
- Basic file processing
- Internal testing

**Phase 2: Beta Release** (M5-M7)
- Results display
- Settings management
- User testing

**Phase 3: Stable Release** (M8-M9)
- Error handling polish
- Documentation complete
- Public release

---

## Success Metrics

- [ ] GUI processes PDF files correctly (parity with CLI)
- [ ] GUI processes Markdown files correctly (parity with CLI)
- [ ] User can process files without using CLI
- [ ] Processing time comparable to CLI (<10% overhead)
- [ ] Zero GUI freezing during operations
- [ ] Configuration persists across sessions
- [ ] Error messages are clear and actionable
- [ ] User satisfaction score >4/5

---

**TAG**: SPEC-GUI-001
**Traceability**: All requirements from spec.md are mapped to implementation tasks

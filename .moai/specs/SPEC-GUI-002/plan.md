# PLAN: PageIndex GUI Enhancements Implementation

**Metadata**
- **SPEC ID**: SPEC-GUI-002
- **Document**: plan.md
- **Version**: 1.0
- **Last Updated**: 2026-02-26

---

## Implementation Strategy

### Development Approach

**Methodology**: DDD (Domain-Driven Development)

**Rationale**:
- 기존 GUI 코드를 확장하는 작업
- 특성화 테스트로 현재 동작 보존
- 점진적 개선으로 회귀 방지

---

## Milestones (Priority-Based)

### 🎯 Primary Goal: Recent Files & Settings Management

**M6. Recent Files Management**

**Tasks**:
1. Create `HistoryManager` class
   - Implement JSON-based persistence
   - Add file tracking with metadata
   - Create FIFO queue (max 10 items)
2. Implement recent files menu
   - Add to main menu bar
   - Create dropdown with file list
   - Add status indicators (success/error)
3. Add quick-open functionality
   - Click to load file
   - Validate file existence
4. Implement clear history
   - Confirmation dialog
   - Empty state handling

**Success Criteria**:
- [ ] Last 10 files are tracked automatically
- [ ] Recent files persist across sessions
- [ ] Menu shows files with timestamps
- [ ] Clear history works with confirmation
- [ ] Non-existent files are removed automatically

**Dependencies**: M1-M5 (SPEC-GUI-001)

**Estimated Complexity**: Low

**File Structure**:
```
pageindex/gui/managers/history_manager.py
pageindex/gui/dialogs/history_dialog.py
```

---

**M7. Settings Management Dialog**

**Tasks**:
1. Create `SettingsManager` class
   - Implement encryption for API keys
   - Add settings persistence
   - Create validation layer
2. Implement settings dialog
   - API configuration section
   - Appearance section (theme, font size)
   - Defaults section
3. Add theme switching
   - Apply immediately on change
   - Save preference
4. Implement reset to defaults
   - Confirmation dialog
   - Restore all settings

**Success Criteria**:
- [ ] Settings dialog opens and closes properly
- [ ] API key is encrypted when saved
- [ ] Theme changes apply immediately
- [ ] Reset works with confirmation
- [ ] Invalid settings are rejected

**Dependencies**: M1 (SPEC-GUI-001)

**Estimated Complexity**: Medium

**File Structure**:
```
pageindex/gui/managers/settings_manager.py
pageindex/gui/dialogs/settings_dialog.py (enhanced)
```

---

### 🎯 Secondary Goal: Enhanced Visualization

**M9.1. Drag & Drop Enhancement**

**Tasks**:
1. Integrate `tkinterdnd2`
   - Add dependency
   - Enable drag & drop on file zone
2. Implement multi-file drop
   - Handle multiple files
   - Add to batch queue
3. Add visual feedback
   - Highlight on drag over
   - Error indicator for invalid files

**Success Criteria**:
- [ ] Single file drop works
- [ ] Multiple files can be dropped
- [ ] Invalid files are rejected with feedback
- [ ] Visual feedback is clear

**Dependencies**: M2 (SPEC-GUI-001)

**Estimated Complexity**: Medium

**File Structure**:
```
pageindex/gui/widgets/file_drop_zone.py (enhanced)
```

---

**M9.2. Batch Processing Mode**

**Tasks**:
1. Create `BatchProcessor` class
   - Implement file queue
   - Add sequential processing
   - Track individual results
2. Implement batch UI
   - Queue display widget
   - Progress indicator
   - Results summary
3. Add batch controls
   - Start/Stop/Pause buttons
   - Remove from queue
   - Clear queue

**Success Criteria**:
- [ ] Multiple files can be queued
- [ ] Files process sequentially
- [ ] Progress shows for each file
- [ ] Failure doesn't stop batch
- [ ] Summary shows at end

**Dependencies**: M9.1, M4 (SPEC-GUI-001)

**Estimated Complexity**: High

**File Structure**:
```
pageindex/gui/managers/batch_processor.py
pageindex/gui/widgets/batch_list_widget.py
```

---

**M9.3. Result Comparison View**

**Tasks**:
1. Create comparison widget
   - Side-by-side view
   - Diff highlighting
2. Add comparison mode
   - Select two results
   - Show differences
3. Implement navigation
   - Sync scrolling
   - Expand/collapse sync

**Success Criteria**:
- [ ] Two results can be compared
- [ ] Differences are highlighted
- [ ] Scrolling is synchronized
- [ ] View is responsive

**Dependencies**: M5 (SPEC-GUI-001)

**Estimated Complexity**: Medium

**File Structure**:
```
pageindex/gui/widgets/comparison_view.py
```

---

**M9.4. Export Functionality**

**Tasks**:
1. Create `ExportManager` class
   - PDF export (using fpdf)
   - HTML export (using jinja2)
   - Markdown export (native)
2. Implement export dialog
   - Format selection
   - Output path selection
   - Options (include metadata, etc.)
3. Add export button
   - In results viewer
   - In context menu

**Success Criteria**:
- [ ] PDF export produces formatted PDF
- [ ] HTML export produces styled HTML
- [ ] Markdown export produces valid MD
- [ ] Export options work correctly

**Dependencies**: M5 (SPEC-GUI-001)

**Estimated Complexity**: Medium

**File Structure**:
```
pageindex/gui/managers/export_manager.py
```

---

### 🎯 Optional Goal: Additional UX Enhancements

**Keyboard Shortcuts**

**Tasks**:
1. Create `KeyboardShortcuts` manager
   - Define all shortcuts
   - Register with main window
2. Implement key bindings
   - Ctrl+O: Open file
   - Ctrl+S: Save result
   - Ctrl+,: Open settings
   - F1: Help

**Success Criteria**:
- [ ] All shortcuts work
- [ ] Shortcuts are documented
- [ ] Conflicts are avoided

**Estimated Complexity**: Low

---

**Tooltips and Help System**

**Tasks**:
1. Create `TooltipHelper` class
   - Bind tooltips to widgets
   - Manage tooltip display
2. Add tooltips to all inputs
   - Parameter descriptions
   - Value ranges
3. Create help dialog
   - Context-sensitive help
   - "?" button handler

**Success Criteria**:
- [ ] Tooltips show on hover
- [ ] Tooltips are helpful
- [ ] Help dialog opens with F1

**Estimated Complexity**: Low

---

**Status Bar Enhancements**

**Tasks**:
1. Enhance status bar
   - Add progress display
   - Add processing time
   - Add file count
2. Update status dynamically
   - During processing
   - On completion
   - On errors

**Success Criteria**:
- [ ] Status bar shows current state
- [ ] Progress updates in real-time
- [ ] Times are accurate

**Estimated Complexity**: Low

---

**Log Viewer**

**Tasks**:
1. Create log viewer dialog
   - Text display with scroll
   - Log level filtering
2. Integrate with logging
   - Capture processing logs
   - Display errors
3. Add log controls
   - Clear logs
   - Export logs
   - Filter by level

**Success Criteria**:
- [ ] Logs are captured
- [ ] Viewer displays correctly
- [ ] Filtering works
- [ ] Export works

**Estimated Complexity**: Medium

---

## Technical Approach

### Dependencies

**New Dependencies**:
```toml
[tool.poetry.dependencies]
tkinterdnd2 = "^0.3.0"      # Drag & drop support
cryptography = "^41.0.0"     # API key encryption
fpdf = "^2.7.0"              # PDF export
jinja2 = "^3.1.0"            # HTML export
```

### Key Design Decisions

**Decision 1: API Key Encryption**
- **Approach**: Fernet symmetric encryption
- **Rationale**: Simple, secure, built-in key derivation
- **Risk**: Key loss if settings deleted
- **Mitigation**: Warn user before clearing settings

**Decision 2: Batch Processing Architecture**
- **Approach**: Queue-based sequential processing
- **Rationale**: Predictable resource usage, easier error handling
- **Risk**: Slower than parallel processing
- **Mitigation**: Document expected processing times

**Decision 3: Export Format Support**
- **Approach**: Plugin-style export managers
- **Rationale**: Extensible for future formats
- **Risk**: Added complexity
- **Mitigation**: Keep interface simple

**Decision 4: Drag & Drop Library**
- **Approach**: tkinterdnd2
- **Rationale**: Cross-platform, well-maintained
- **Risk**: May not work on all platforms
- **Mitigation**: Fallback to file browser

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| API key encryption breaks settings | High | Low | Backup/restore mechanism |
| Batch processing memory issues | Medium | Medium | Limit queue size, process sequentially |
| PDF export compatibility issues | Medium | Low | Test on common platforms |
| Drag & drop platform issues | Medium | Medium | Provide fallback file browser |
| Settings file corruption | Medium | Low | Validation + defaults fallback |
| History file grows too large | Low | Low | Hard limit of 10 items |

---

## Quality Assurance

### Testing Strategy

**Unit Tests**:
- `HistoryManager`: File tracking, persistence, FIFO logic
- `SettingsManager`: Encryption, validation, defaults
- `BatchProcessor`: Queue management, result tracking
- `ExportManager`: PDF/HTML generation

**Integration Tests**:
- Settings dialog integration
- Batch processing workflow
- Drag & drop to batch queue
- Export with actual results

**UI Tests**:
- Menu navigation
- Keyboard shortcuts
- Tooltip display
- Dialog interactions

### Coverage Targets

- New manager classes: 85%+ coverage
- Dialog classes: 80%+ coverage
- Widget enhancements: 75%+ coverage

---

## Rollout Strategy

**Phase 1: M6 + M7** (Primary Goal)
- Recent files tracking
- Settings management
- Internal testing

**Phase 2: M9.1 + M9.2** (Secondary Goal)
- Drag & drop enhancement
- Batch processing mode
- User testing

**Phase 3: M9.3 + M9.4** (Completion)
- Result comparison
- Export functionality
- Optional UX features

---

## Success Metrics

- [ ] Recent files tracked correctly
- [ ] Settings persist securely
- [ ] Drag & drop works for multiple files
- [ ] Batch processing completes successfully
- [ ] Results can be compared
- [ ] PDF export produces valid PDFs
- [ ] HTML export produces styled HTML
- [ ] Keyboard shortcuts work
- [ ] Tooltips display correctly
- [ ] Status bar shows accurate info
- [ ] Log viewer captures logs
- [ ] Zero crashes during normal operation
- [ ] Settings migration from v1 works

---

## Implementation Order

**Order** (based on dependencies and complexity):
1. M6: Recent files (foundation for other features)
2. M7: Settings management (enables other configuration)
3. M9.1: Drag & drop (enables batch processing)
4. M9.2: Batch processing (core enhancement)
5. M9.4: Export functionality (high value feature)
6. M9.3: Comparison view (nice-to-have)
7. Optional UX features (polish)

---

**TAG**: SPEC-GUI-002
**Traceability**: All requirements from spec.md are mapped to implementation tasks

# SPEC-GUI-002: PageIndex GUI Enhancements (Phase 2)

**Metadata**
- **Title**: PageIndex GUI Enhanced Features
- **ID**: SPEC-GUI-002
- **Status**: Planned
- **Priority**: High
- **Created**: 2026-02-26
- **Assigned**: manager-spec
- **Related SPECs**: SPEC-GUI-001 (Base GUI)

---

## Environment

### System Context
PageIndex GUI (SPEC-GUI-001)가 성공적으로 구현되었습니다. 기본 GUI 프레임워크, 파일 선택, 설정 패널, 진행률 표시, 결과 뷰어가 완료되었습니다. Phase 2에서는 사용자 경험을 향상시키는 고급 기능을 추가합니다.

### Current State
**Completed (M1-M5)**:
- M1: Basic GUI framework with CustomTkinter ✅
- M2: File selection interface (PDF/Markdown) ✅
- M3: Configuration panel with all parameters ✅
- M4: Progress display with cancellation support ✅
- M5: Results display with JSON viewer (3 tabs) ✅

**Pending (M6-M9)**:
- M6: Recent files management
- M7: Settings management dialog
- M8: Enhanced error handling (partially done)
- M9: Enhanced visualization features

### Target Users
- 빈번한 파일 처리를 수행하는 연구자
- 키보드 단축키를 선호하는 전력 사용자
- 배치 처리가 필요한 대량 문서 처리자
- 처리 결과를 비교/분석해야 하는 사용자

---

## Assumptions

### Technical Assumptions
- **Confidence: High** - Python 3.10+ 환경에서 실행됨
- **Confidence: High** - CustomTkinter 기반 GUI가 이미 구현됨
- **Confidence: Medium** - 사용자 시스템에 쓰기 권한이 있음 (설정 저장)
- **Confidence: High** - 기존 비즈니스 로직은 재사용 가능

### User Behavior Assumptions
- **Confidence: High** - 사용자는 최근 파일을 빠르게 다시 열고 싶어함
- **Confidence: Medium** - 사용자는 API 키를 안전하게 저장하고 싶어함
- **Confidence: High** - 사용자는 드래그 앤 드롭을 선호함
- **Confidence: Medium** - 일부 사용자는 여러 파일을 한 번에 처리하고 싶어함

### Risk if Wrong
- **Confidence: Low** - 설정 파일 형식 변경이 마이그레이션에 영향을 미칠 수 있음
- **Confidence: Medium** - 배치 처리 시 메모리 사용량이 급증할 수 있음
- **Confidence: Low** - PDF/HTML 내보내기 라이브러리 호환성 문제

---

## Requirements (EARS Format)

### M6: Recent Files Management

#### Ubiquitous Requirements
**REQ-U-001**: 시스템은 항상 최근 처리된 파일 목록을 유지해야 한다.

**REQ-U-002**: 시스템은 항상 최근 파일 데이터를 세션 간에 지속적으로 저장해야 한다.

#### Event-Driven Requirements
**REQ-E-001**: WHEN 파일 처리가 완료되면, 시스템은 해당 파일을 최근 파일 목록에 추가해야 한다.

**REQ-E-002**: WHEN 최근 파일 목록이 10개를 초과하면, 시스템은 가장 오래된 파일을 제거해야 한다.

**REQ-E-003**: WHEN 사용자가 최근 파일을 선택하면, 시스템은 해당 파일을 즉시 로드해야 한다.

**REQ-E-004**: WHEN 사용자가 히스토리 초기화를 요청하면, 시스템은 확인 후 히스토리를 비워야 한다.

#### State-Driven Requirements
**REQ-S-001**: IF 최근 파일 목록이 비어있으면, 시스템은 "최근 파일 없음" 메시지를 표시해야 한다.

**REQ-S-002**: IF 파일이 더 이상 존재하지 않으면, 시스템은 해당 항목을 목록에서 제거해야 한다.

#### Optional Requirements
**REQ-O-001**: 가능하면 최근 파일 항목에 파일 처리 결과 (성공/실패)를 표시해야 한다.

**REQ-O-002**: 가능하면 최근 파일 항목에 처리 시간을 표시해야 한다.

#### Unwanted Behavior Requirements
**REQ-N-001**: 시스템은 사용자 동의 없이 히스토리를 초기화하지 않아야 한다.

**REQ-N-002**: 시스템은 존재하지 않는 파일 경로를 히스토리에 유지하지 않아야 한다.

---

### M7: Settings Management Dialog

#### Ubiquitous Requirements
**REQ-U-003**: 시스템은 항상 설정을 파일 시스템에 안전하게 저장해야 한다.

**REQ-U-004**: 시스템은 항상 API 키를 암호화된 형태로 저장해야 한다.

#### Event-Driven Requirements
**REQ-E-005**: WHEN 사용자가 설정 대화상자를 열면, 시스템은 현재 설정을 로드해야 한다.

**REQ-E-006**: WHEN 사용자가 API 키를 변경하면, 시스템은 즉시 암호화하여 저장해야 한다.

**REQ-E-007**: WHEN 사용자가 테마를 변경하면, 시스템은 즉시 적용해야 한다.

**REQ-E-008**: WHEN 사용자가 "기본값 복원"을 클릭하면, 시스템은 확인 후 설정을 초기화해야 한다.

#### State-Driven Requirements
**REQ-S-003**: IF 저장된 API 키가 없으면, 시스템은 설정 대화상자에서 API 키 입력을 요구해야 한다.

**REQ-S-004**: IF 설정 파일이 손상되면, 시스템은 기본값으로 복구해야 한다.

#### Optional Requirements
**REQ-O-003**: 가능하면 설정을 가져오기/내보내기 기능을 제공해야 한다.

**REQ-O-004**: 가능하면 고급 설정 패널을 제공해야 한다.

#### Unwanted Behavior Requirements
**REQ-N-003**: 시스템은 API 키를 평문으로 저장하면 안 된다.

**REQ-N-004**: 시스템은 유효하지 않은 설정값을 저장하면 안 된다.

---

### M9: Enhanced Visualization Features

#### M9.1: Drag & Drop File Selection
**REQ-E-009**: WHEN 사용자가 파일을 드래그 앤 드롭하면, 시스템은 파일을 즉시 처리 준비 상태로 만들어야 한다.

**REQ-E-010**: WHEN 여러 파일을 동시에 드롭하면, 시스템은 모든 파일을 목록에 추가해야 한다.

**REQ-N-005**: 시스템은 지원되지 않는 파일 형식 드롭을 허용하지 않아야 한다.

#### M9.2: Batch Processing Mode
**REQ-E-011**: WHEN 배치 처리 모드가 활성화되면, 시스템은 파일 큐에 있는 모든 파일을 순차 처리해야 한다.

**REQ-E-012**: WHEN 배치 처리 중 파일이 실패하면, 시스템은 다음 파일을 계속 처리해야 한다.

**REQ-E-013**: WHEN 배치 처리가 완료되면, 시스템은 처리 요약을 표시해야 한다.

**REQ-S-005**: IF 배치 처리가 진행 중이면, 시스템은 전체 진행률을 표시해야 한다.

**REQ-O-005**: 가능하면 배치 처리 중단/재개 기능을 제공해야 한다.

#### M9.3: Result Comparison View
**REQ-E-014**: WHEN 두 개 이상의 처리 결과가 있으면, 시스템은 비교 뷰를 제공해야 한다.

**REQ-O-006**: 가능하면 사이드 바이 사이드 비교 뷰를 제공해야 한다.

#### M9.4: Export Functionality
**REQ-E-015**: WHEN 사용자가 내보내기를 요청하면, 시스템은 결과를 선택한 형식으로 내보내야 한다.

**REQ-E-016**: WHEN PDF 내보내기를 선택하면, 시스템은 포맷된 PDF를 생성해야 한다.

**REQ-E-017**: WHEN HTML 내보내기를 선택하면, 시스템은 인터랙티브한 HTML을 생성해야 한다.

**REQ-O-007**: 가능하면 Markdown 형식 내보내기를 지원해야 한다.

---

### Additional UX Enhancements

#### Keyboard Shortcuts
**REQ-E-018**: WHEN 사용자가 Ctrl+O를 누르면, 시스템은 파일 선택 대화상자를 열어야 한다.

**REQ-E-019**: WHEN 사용자가 Ctrl+S를 누르면, 시스템은 현재 결과를 저장해야 한다.

**REQ-E-020**: WHEN 사용자가 Ctrl+,를 누르면, 시스템은 설정 대화상자를 열어야 한다.

**REQ-E-021**: WHEN 사용자가 F1을 누르면, 시스템은 도움말을 표시해야 한다.

#### Tooltips and Help System
**REQ-E-022**: WHEN 사용자가 위젯 위에 마우스를 올리면, 시스템은 툴팁을 표시해야 한다.

**REQ-E-023**: WHEN 사용자가 "?" 버튼을 클릭하면, 시스템은 컨텍스트 도움말을 표시해야 한다.

#### Status Bar Enhancements
**REQ-U-005**: 시스템은 항상 현재 상태를 상태 바에 표시해야 한다.

**REQ-E-024**: WHEN 처리가 진행 중이면, 시스템은 상태 바에 진행률을 표시해야 한다.

**REQ-E-025**: WHEN 완료되면, 시스템은 상태 바에 처리 시간을 표시해야 한다.

#### Log Viewer
**REQ-E-026**: WHEN 로그 뷰어가 열리면, 시스템은 처리 로그를 표시해야 한다.

**REQ-E-027**: WHEN 에러가 발생하면, 시스템은 로그 뷰어에 에러 세부 정보를 표시해야 한다.

**REQ-O-008**: 가능하면 로그 필터링 기능을 제공해야 한다.

---

## Specifications

### M6: Recent Files Management

**Data Structure**:
```json
{
  "recent_files": [
    {
      "path": "/path/to/file.pdf",
      "timestamp": "2026-02-26T10:30:00",
      "status": "success",
      "processing_time": 45.2
    }
  ]
}
```

**Storage Location**: `~/.pageIndex/history.json`

**Key Features**:
- 최대 10개 파일 유지 (FIFO)
- 파일 존재 여부 자동 검증
- 빠른 액세스 메뉴 (File > Recent Files)
- 히스토리 초기화 기능

---

### M7: Settings Management Dialog

**Dialog Layout**:
```
┌─────────────────────────────────────────────┐
│  Settings                    [×]            │
├─────────────────────────────────────────────┤
│                                             │
│  API Configuration                          │
│  ┌─────────────────────────────────────┐    │
│  │ API Key: [•••••••••••••••••]        │    │
│  │ Base URL: [https://api.z.ai/...]    │    │
│  │ Model: [glm-5               ▼]      │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Appearance                                 │
│  ┌─────────────────────────────────────┐    │
│  │ Theme: ◉ Dark  ○ Light  ○ System   │    │
│  │ Font Size: [10        ▼]           │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Defaults                                   │
│  ┌─────────────────────────────────────┐    │
│  │ [Reset to Defaults]                 │    │
│  └─────────────────────────────────────┘    │
│                                             │
│           [Save]  [Cancel]  [Apply]         │
└─────────────────────────────────────────────┘
```

**API Key Encryption**:
```python
from cryptography.fernet import Fernet

class SettingsManager:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def save_api_key(self, api_key: str):
        encrypted = self.cipher.encrypt(api_key.encode())
        # Save to settings file
```

**Storage Location**: `~/.pageIndex/settings.json`

---

### M9: Enhanced Visualization

#### Drag & Drop
**Library**: `tkinterdnd2`

**Implementation**:
```python
from tkinterdnd2 import DND_FILES, TkinterDnD

class FileDropZone(ctk.CTkFrame):
    def enable_drag_drop(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)
```

#### Batch Processing
**Queue System**:
```python
from queue import Queue

class BatchProcessor:
    def __init__(self):
        self.queue = Queue()
        self.results = []

    def add_file(self, file_path: str):
        self.queue.put(file_path)

    def process_all(self):
        while not self.queue.empty():
            file_path = self.queue.get()
            result = self.process_file(file_path)
            self.results.append(result)
```

#### Export Functionality
**PDF Export** (using `fpdf`):
```python
from fpdf import FPDF

class PDFExporter:
    def export(self, result: dict, output_path: str):
        pdf = FPDF()
        pdf.add_page()
        # Format result as PDF
        pdf.output(output_path)
```

**HTML Export** (using `jinja2`):
```python
from jinja2 import Template

class HTMLExporter:
    def export(self, result: dict, output_path: str):
        template = Template(self._get_template())
        html = template.render(result=result)
        with open(output_path, 'w') as f:
            f.write(html)
```

---

### Architecture Updates

```
pageindex/
├── gui/
│   ├── main_window.py           # (existing, update)
│   ├── managers/                # NEW: Manager classes
│   │   ├── __init__.py
│   │   ├── history_manager.py   # M6: Recent files
│   │   ├── settings_manager.py  # M7: Settings management
│   │   ├── batch_processor.py   # M9: Batch processing
│   │   └── export_manager.py    # M9: Export functionality
│   ├── dialogs/
│   │   ├── settings_dialog.py   # (existing, enhance)
│   │   └── history_dialog.py    # NEW: Recent files dialog
│   ├── widgets/
│   │   ├── file_drop_zone.py    # (existing, enhance with dnd)
│   │   ├── batch_list_widget.py # NEW: Batch queue display
│   │   └── comparison_view.py   # NEW: Result comparison
│   └── utils/
│       ├── keyboard_shortcuts.py # NEW: Key bindings
│       └── tooltip_helper.py    # NEW: Tooltip management
```

---

## Traceability

**TAG**: SPEC-GUI-002

**Related Components**:
- SPEC-GUI-001: Base GUI implementation
- `pageindex/gui/main_window.py`: Main window updates
- `pageindex/gui/managers/`: New manager classes

**Dependencies**:
- CustomTkinter >= 5.2.0 (existing)
- tkinterdnd2 >= 0.3.0 (NEW)
- cryptography >= 41.0.0 (NEW)
- fpdf >= 2.7.0 (NEW for PDF export)
- jinja2 >= 3.1.0 (NEW for HTML export)

**Next Steps**: See `plan.md` for implementation approach

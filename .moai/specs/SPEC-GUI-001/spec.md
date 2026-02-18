# SPEC-GUI-001: PageIndex GUI Application

**Metadata**
- **Title**: PageIndex GUI Application Conversion
- **ID**: SPEC-GUI-001
- **Status**: Planned
- **Priority**: High
- **Created**: 2025-02-18
- **Assigned**: manager-spec

---

## Environment

### System Context
PageIndex는 현재 CLI 기반으로 작동하는 Python 애플리케이션입니다. 사용자는 명령줄 인자를 통해 PDF/Markdown 파일을 처리하고 계층적 트리 구조를 생성합니다.

### Current State
- **Entry Point**: `run_pageindex.py` (argparse-based CLI)
- **Core Modules**: `page_index.py`, `page_index_md.py`, `models.py`, `utils.py`, `constants.py`
- **Dependencies**: PyPDF2, PyMuPDF, OpenAI API, tiktoken, yaml, dotenv
- **Output**: JSON tree structure saved to `./results/{filename}_structure.json`

### Target Users
- 비기술적 사용자 (CLI 명령어에 익숙하지 않은 사용자)
- 대량 문서 처리를 해야 하는 연구자
- 문서 구조를 시각적으로 확인하고 싶은 사용자

---

## Assumptions

### Technical Assumptions
- **Confidence: High** - Python 3.10+ 환경에서 실행됨
- **Confidence: High** - 기존 비즈니스 로직(`pageindex` 패키지)은 재사용 가능
- **Confidence: Medium** - 사용자는 Windows/macOS/Linux 데스크톱 환경을 사용함
- **Confidence: High** - OpenAI API 호환 API Key가 `.env` 파일에 설정됨

### User Behavior Assumptions
- **Confidence: Medium** - 사용자는 drag & drop 파일 선택을 선호함
- **Confidence: Medium** - 사용자는 진행 상태를 시각적으로 확인하고 싶어함
- **Confidence: High** - 사용자는 CLI 파라미터 설정을 GUI 설정面板으로 대체하기를 원함

### Risk if Wrong
- **Confidence: Low** - GUI 프레임워크 선택이 프로젝트 유지보수에 영향을 미칠 수 있음
- **Confidence: Medium** - 비동기 API 호출을 GUI 스레드와 통합하는데 어려움이 있을 수 있음

---

## Requirements (EARS Format)

### Ubiquitous Requirements

**REQ-U-001**: 시스템은 항상 사용자의 API Key를 `.env` 파일에서 안전하게 로드해야 한다.

**REQ-U-002**: 시스템은 항상 PDF와 Markdown 파일 처리를 지원해야 한다.

**REQ-U-003**: 시스템은 항상 기존 CLI 기능을 완벽하게 보존해야 한다 (Backward Compatibility).

### Event-Driven Requirements

**REQ-E-001**: WHEN 사용자가 파일을 drag & drop 하면, 시스템은 즉시 파일 유효성을 검사해야 한다.

**REQ-E-002**: WHEN 사용자가 "변환 시작" 버튼을 클릭하면, 시스템은 진행률 표시줄을 표시해야 한다.

**REQ-E-003**: WHEN 변환이 완료되면, 시스템은 결과 파일 위치를 사용자에게 알려야 한다.

**REQ-E-004**: WHEN API 호출 중 오류가 발생하면, 시스템은 사용자에게 명확한 에러 메시지를 표시해야 한다.

**REQ-E-005**: WHEN 사용자가 설정값을 변경하면, 시스템은 설정을 즉시 저장해야 한다.

### State-Driven Requirements

**REQ-S-001**: IF 변환 중이면, 시스템은 "변환 시작" 버튼을 비활성화해야 한다.

**REQ-S-002**: IF 처리가 완료되면, 시스템은 결과 트리 구조를 트리 뷰로 표시해야 한다.

**REQ-S-003**: IF API Key가 설정되지 않았으면, 시스템은 설정 패널을 먼저 표시해야 한다.

**REQ-S-004**: IF 파일이 너무 크면(>100MB), 시스템은 사용자에게 확인을 요청해야 한다.

### Optional Requirements

**REQ-O-001**: 가능하면 다크 모드 테마를 지원해야 한다.

**REQ-O-002**: 가능하면 트리 구조를 JSON 뷰어로도 표시해야 한다.

**REQ-O-003**: 가능하면 최근 처리 파일 목록을 표시해야 한다.

**REQ-O-004**: 가능하면 변환 결과를 내보내기(Export) 기능을 제공해야 한다.

### Unwanted Behavior Requirements

**REQ-N-001**: 시스템은 변환 중 GUI를 멈추지 않아야 한다(Freezing prevention).

**REQ-N-002**: 시스템은 API Key를 로그 파일에 기록하지 않아야 한다.

**REQ-N-003**: 시스템은 잘못된 파일 형식을 허용하지 않아야 한다.

---

## Specifications

### GUI Framework Selection

**Framework Decision**: **CustomTkinter**

**Rationale**:
| Framework | Pros | Cons | Score |
|-----------|------|------|-------|
| CustomTkinter | • Modern, native look<br>• Built on Tkinter (standard library)<br>• Dark mode support<br>• Easy widget theming<br>• Cross-platform<br>• Lightweight | • Limited widget set<br>• Smaller community | **85** |
| PyQt6/PySide6 | • Professional widgets<br>• Excellent documentation<br>• Large ecosystem<br>• Qt Designer | • Heavy weight (~50MB)<br>• Complex licensing<br>• Steep learning curve | 75 |
| PySimpleGUI | • Very simple API<br>• Rapid development | • Commercial license for business<br>• Limited customization<br>• Not actively maintained | 60 |
| tkinter | • Built-in | • Dated look<br>• No modern widgets<br>• Limited styling | 45 |

**Selected Framework**: CustomTkinter (`/tomschimansky/customtkinter`)
- **Benchmark Score**: 75.7 (High)
- **Source Reputation**: High
- **Code Snippets**: 223

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│  PageIndex GUI                              [- □ ×]          │
├─────────────────────────────────────────────────────────────┤
│  File | Settings | Help                                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  📄 Drag & Drop PDF/Markdown file here              │    │
│  │                                                      │    │
│  │          or                                          │    │
│  │                                                      │    │
│  │  [Browse Files]                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  Selected File: example.pdf                               │
│                                                               │
│  ┌─ Configuration ─────────────────────────────────────┐    │
│  │                                                       │    │
│  │  AI Model: [glm-5              ▼]                   │    │
│  │  Base URL:  [https://api.z.ai/...   ]              │    │
│  │                                                       │    │
│  │  PDF Options:                                        │    │
│  │    TOC Check Pages: [20        ]                    │    │
│  │    Max Pages/Node:  [10        ]                    │    │
│  │    Max Tokens/Node: [20000     ]                    │    │
│  │                                                       │    │
│  │  Output Options:                                     │    │
│  │    ☑ Add Node ID        ☑ Add Summary               │    │
│  │    ☐ Add Doc Description ☐ Add Node Text             │    │
│  │                                                       │    │
│  │  Markdown Options (when MD selected):                │    │
│  │    ☐ Enable Thinning    Min Threshold: [5000]         │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                               │
│  [Start Conversion]  [Clear]  [Open Results Folder]         │
│                                                               │
│  Progress: [████████████░░░░░░░] 60% (Processing...)         │
│                                                               │
│  Status: Processing page 15 of 25...                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI Application                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐    │
│  │ Main Window   │───▶│ Config Panel  │    │ File Handler  │    │
│  │               │    │               │    │               │    │
│  │ - Layout      │    │ - Parameters  │    │ - Validation  │    │
│  │ - Events      │    │ - Persistence │    │ - Drag & Drop │    │
│  └───────────────┘    └───────────────┘    └───────────────┘    │
│           │                     │                     │           │
│           └─────────────────────┴─────────────────────┘           │
│                                 │                                 │
│                                 ▼                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    Processing Layer                        │   │
│  │                                                           │   │
│  │  ┌──────────────┐      ┌──────────────┐                   │   │
│  │  │ Thread Pool  │─────▶│ Progress     │                   │   │
│  │  │              │      │ Callback     │                   │   │
│  │  └──────────────┘      └──────────────┘                   │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                 │                                 │
│                                 ▼                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                  Business Logic Layer                      │   │
│  │                                                           │   │
│  │  pageindex/ package (reused from CLI)                     │   │
│  │  - page_index.py (PDF processing)                         │   │
│  │  - page_index_md.py (Markdown processing)                 │   │
│  │  - models.py (Data models)                               │   │
│  │  - utils.py (API calls, utilities)                       │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Component Specifications

**Main Window Components**:

1. **File Drop Zone**
   - Drag & drop support for PDF/MD files
   - File validation on drop
   - Visual feedback (highlight, error indicators)

2. **Configuration Panel**
   - Grouped sections (PDF, Markdown, Output)
   - Input validation (numeric ranges, required fields)
   - Save/Load configuration

3. **Progress Display**
   - Progress bar with percentage
   - Status message updates
   - Cancellation support

4. **Results Display**
   - Tree view for document structure
   - JSON viewer (collapsible sections)
   - Export functionality

### Thread Management Strategy

```python
# Async/await integration pattern
class ProcessingThread(threading.Thread):
    def __init__(self, file_path, config, callback):
        super().__init__()
        self.file_path = file_path
        self.config = config
        self.callback = callback
        self.daemon = True

    def run(self):
        try:
            # Run async processing in separate thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            if self.file_path.endswith('.pdf'):
                result = loop.run_until_complete(
                    self._process_pdf()
                )
            else:
                result = loop.run_until_complete(
                    self._process_markdown()
                )

            self.callback('success', result)
        except Exception as e:
            self.callback('error', str(e))
        finally:
            loop.close()
```

### Configuration Persistence

```yaml
# config/gui_settings.yaml
gui:
  theme: dark
  window:
    width: 800
    height: 700
    resizable: true
  recent_files:
    - path: ./documents/example.pdf
      timestamp: 2025-02-18T10:30:00
```

---

## Traceability

**TAG**: SPEC-GUI-001

**Related Components**:
- `run_pageindex.py` - Original CLI entry point (to be preserved)
- `pageindex/` - Business logic package (reused)
- `pageindex/gui/` - New GUI package

**Dependencies**:
- CustomTkinter >= 5.2.0
- Existing pageindex dependencies

**Next Steps**: See `plan.md` for implementation approach

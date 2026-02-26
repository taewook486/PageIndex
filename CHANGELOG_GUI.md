# PageIndex GUI 구현 - 변경 사항

## 날짜
2026-02-26 (성능 최적화 업데이트)
2026-02-19 (초기 구현)

## 개요
PageIndex CLI 애플리케이션을 GUI 애플리케이션으로 변환

---

## 주요 변경사항

### 1. GUI 패키지 구현
- **위치**: `pageindex/gui/`
- **프레임워크**: CustomTkinter (현대적 다크 모드 지원)
- **주요 파일**:
  - `main.py` - GUI 진입점
  - `main_window.py` - 메인 윈도 (700+ 라인)
  - `processing/processor.py` - 백그라운드 처리 (250+ 라인)

### 2. 핵심 기능

#### 파일 선택
- 파일 브라우저 대화상자
- PDF/Markdown 파일 유형 검증

#### 설정 패널
- AI 모델 선택
- Base URL 설정
- PDF 옵션 (TOC 확인 페이지, 최대 페이지/노드, 최대 토큰/노드)
- 출력 옵션 (노드 ID, 요약, 문서 설명, 노드 텍스트)

#### 진행률 표시
- 실시간 진행률 바 (0-100%)
- 상태 메시지 업데이트
- 취소 버튼 지원

#### 결과 표시
- **JSON 뷰어 개선** (3개 탭):
  - Formatted JSON: 문법 강조
  - Tree View: 대화형 트리 구조
  - Summary: 통계 정보
- 검색 기능
- 확장/축소 기능
- 클립보드 복사

### 3. 백그라운드 처리
- 스레드 기반 비동기 처리
- PDF 처리 (동기): `asyncio.run()` 내부 사용을 위해 별도 처리
- Markdown 처리 (비동기): 이벤트 루프 사용

### 4. 오류 처리
- 개선된 오류 표시 (상태 라벨 + 결과창 + 메시지박스)
- 전체 스택 트레이스 표시
- 취소 기능

---

## 수정된 파일

### 기존 파일 수정
| 파일 | 변경사항 |
|------|----------|
| `README.md` | GUI 사용 방법 추가 |
| `requirements.txt` | CustomTkinter 의존성 추가 |

---

## 새로운 파일

### GUI 구현
- `pageindex/gui/__init__.py`
- `pageindex/gui/main.py`
- `pageindex/gui/main_window.py`
- `pageindex/gui/processing/__init__.py`
- `pageindex/gui/processing/processor.py`
- `pageindex/gui/json_viewer.py`
- `pageindex/gui/JSON_VIEWER_README.md`

### 실행 스크립트
- `run_pageindex_gui.py`

### 테스트
- `tests/characterization/test_cli_characterization.py`
- `tests/test_json_viewer.py`

### 문서
- `.moai/specs/SPEC-GUI-001/spec.md`
- `.moai/specs/SPEC-GUI-001/plan.md`
- `.moai/specs/SPEC-GUI-001/acceptance.md`

---

## 해결된 문제

### 1. CustomTkinter 호환성
- **문제**: `CTkLabelFrame` 클래스가 존재하지 않음
- **해결**: `CTkFrame` + 레이블로 대체

### 2. asyncio 이벤트 루프 충돌
- **문제**: `asyncio.run()`을 백그라운드 스레드의 이벤트 루프 내에서 호출 불가
- **해결**: PDF 처리를 동기식으로 분리 (`_process_pdf_sync`)

### 3. CustomTkinter API 오류
- **문제**: `create_tab()`, `set_tab()` 메서드가 존재하지 않음
- **해결**: `add()`, `set()`로 수정

---

## 사용 방법

### GUI 실행
```bash
python run_pageindex_gui.py
```

### CLI 실행 (기존 방식, 100% 호환)
```bash
python run_pageindex.py --pdf_path document.pdf
```

---

## 2026-02-26 성능 최적화

### 문제
- PDF 처리 속도가 너무 느림
- API 요청 병목 현상

### 해결
**Rate Limiting 설정 최적화** ([pageindex/constants.py](pageindex/constants.py#L50-L51))

| 설정 | 이전 값 | 새 값 | 향상 |
|------|---------|-------|------|
| MAX_CONCURRENT_REQUESTS | 3 | 20 | 6.7x |
| RATE_LIMIT_DELAY | 0.5초 | 0.05초 | 10x |

### 예상 성능 향상
- **100페이지 PDF 처리**: 최소 대기 시간 17초 → 0.25초
- **종합 성능 향상**: 5-10배 빠른 처리 (API 서버 한도 내)

---

## 다음 단계 (향후 개선사항)

1. 최근 파일 관리
2. 설정 관리 대화상자 (API 키, 테마)
3. Drag & Drop 파일 선택
4. 배치 처리 모드
5. 결과 비교 기능

---

## 기술 스택
- Python 3.10+
- CustomTkinter 5.2+
- tkinter (표준 라이브러리)
- Pydantic 2.0+

---
id: SPEC-GUI-003
version: 1.0.0
status: completed
created: 2026-02-27
updated: 2026-02-27
author: taewook486
priority: high
---

## HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-27 | taewook486 | 초기 SPEC 작성 |
| 1.1.0 | 2026-02-27 | taewook486 | 구현 완료 및 상태 업데이트 |

---

# SPEC-GUI-003: GUI 진행률 표시 및 취소 기능 개선

## 환경 (Environment)

### 시스템 환경
- **운영체제**: Windows, macOS, Linux (크로스 플랫폼)
- **Python 버전**: 3.9+
- **GUI 프레임워크**: CustomTkinter

### 기술 환경
- **PDF 처리**: PyMuPDF (fitz)
- **비동기 처리**: asyncio
- **쓰레딩**: threading 모듈
- **데이터 검증**: Pydantic

### 관련 컴포넌트
- `pageindex.gui.main_window.MainWindow`: 메인 GUI 윈도우
- `pageindex.gui.processing.processor.Processor`: 문서 처리 프로세서
- `pageindex.page_index.page_index_main()`: PDF 처리 함수
- `pageindex.page_index_md.md_to_tree()`: Markdown 처리 함수

---

## 가정 (Assumptions)

### 기술적 가정
1. **CustomTkinter UI 업데이트**: 모든 UI 업데이트는 메인 쓰레드에서 `after()` 메서드를 통해 수행됨
2. **비동기 처리**: PDF 처리는 `asyncio.run()`을 사용하여 동기 쓰레드에서 실행됨
3. **취소 신호**: 현재 `threading.Event()`를 사용하지만 실제 처리 중에는 확인되지 않음

### 사용자 가정
1. **사용자 기대**: 사용자는 진행률이 실시간으로 업데이트될 것으로 기대함
2. **취소 반응**: 사용자는 취소 요청 후 1초 이내에 반응을 기대함
3. **부분 결과 보존**: 취소 시 사용자는 이미 완료된 작업의 결과를 보존하기를 원함

### 제약 사항
1. **성능 오버헤드**: 진행률 추적은 처리 성능에 5% 이상의 영향을 주어서는 안 됨
2. **스레드 안전성**: UI 업데이트는 반드시 메인 쓰레드에서 수행되어야 함
3. **데이터 무결성**: 취소 시 출력 파일이 손상되지 않아야 함

---

## 요구사항 (Requirements)

### REQ-1: 실제 동작하는 취소 기능

**[Ubiquitous]** 시스템은 **항상** 사용자 요청 시 처리 중인 작업을 취소할 수 있어야 한다.

**[Event-Driven]** WHEN 사용자가 취소 버튼을 클릭하면, 시스템은 **SHALL** 현재 실행 중인 문서 처리 작업을 중단하고 취소 상태로 전환해야 한다.

**[State-Driven]** WHILE 처리가 진행 중일 때, 시스템은 **SHALL** 주기적으로 취소 신호를 확인하고 취소 요청이 있으면 즉시 처리를 중단해야 한다.

**[Unwanted]** 시스템은 취소 신호를 무시하거나 사용자가 취소를 요청한 후에도 처리를 계속해서는 안 된다.

**Rationale**: 현재 취소 기능이 실제로 동작하지 않아 사용자 경험이 저하됨

**Acceptance Criteria**:
- 취소 버튼 클릭 후 1초 이내에 처리 중단
- 모든 처리 단계에서 취소 신호 확인 (PDF/Markdown 처리, AI 추론)
- 취소 시 적절한 리소스 정리 및 종료

### REQ-2: 세분화된 진행률 표시

**[Ubiquitous]** 시스템은 **항상** 사용자에게 처리 진행 상태를 명확하게 표시해야 한다.

**[Event-Driven]** WHEN 각 처리 단계가 완료되면, 시스템은 **SHALL** 진행률 바와 상태 메시지를 업데이트해야 한다.

**[State-Driven]** IF 문서 처리가 진행 중이면, 시스템은 **SHALL** 최소 5% 단위 또는 주요 단계마다 진행률을 업데이트해야 한다.

**Rationale**: 현재 3단계(10%, 20%, 100%)만 표시되어 사용자가 실제 진행 상황을 파악하기 어려움

**Acceptance Criteria**:
- 진행률 업데이트는 최소 5% 단위 또는 주요 처리 단계마다 수행
- 각 단계에서 의미 있는 상태 메시지 표시 (예: "페이지 3/10 처리 중...", "AI 추론 진행 중...")
- 대용량 문서 처리 시 예상 남은 시간 표시 (선택사항)

### REQ-3: 취소 시 데이터 무결성 보장

**[Event-Driven]** WHEN 사용자가 작업을 취소하면, 시스템은 **SHALL** 출력 파일의 데이터 무결성을 보장해야 한다.

**[State-Driven]** IF 취소 요청이 발생하면, 시스템은 **SHALL** 부분적으로 완성된 결과를 안전하게 정리하거나 임시 파일로 보존해야 한다.

**[Unwanted]** 시스템은 취소 시 출력 파일이 손상되거나 불완전한 상태로 남겨두어서는 안 된다.

**Rationale**: 취소 시 불완전한 파일이 남아 문제를 일으킬 수 있음

**Acceptance Criteria**:
- 취소 시 불완전한 출력 파일 삭제 또는 임시 파일로 이동
- 부분 완료 결과를 보존할 경우 명시적인 사용자 알림
- 파일 쓰기 중 원자적 연산 보장

### REQ-4: 처리 단계별 상태 메시지

**[Event-Driven]** WHEN 각 처리 단계가 시작되거나 완료되면, 시스템은 **SHALL** 사용자에게 명확한 상태 메시지를 표시해야 한다.

**[State-Driven]** IF 특정 처리 단계가 진행 중이면, 시스템은 **SHALL** 현재 수행 중인 작업에 대한 문맥 정보를 제공해야 한다.

**Rationale**: 현재 "Loading [file type]...", "Extracting text..."만 표시되어 실제 진행 상황 파악이 어려움

**Acceptance Criteria**:
- PDF 처리: 페이지 수 및 현재 페이지 표시
- 텍스트 추출: 추출 진행률 표시
- 구조 분석: 섹션 분석 진행률 표시
- AI 추론: 추론 호출 횟수 및 진행률 표시

### REQ-5: 일관된 취소 처리 아키텍처

**[Ubiquitous]** 시스템은 **항상** PDF와 Markdown 처리 경로 모두에서 동일한 취소 메커니즘을 사용해야 한다.

**[Event-Driven]** WHEN 취소가 요청되면, 시스템은 **SHALL** 비동기 및 동기 처리 경로 모두에서 취소 신호를 확인하고 중단해야 한다.

**[State-Driven]** IF 비동기 처리가 진행 중이면, 시스템은 **SHALL** `asyncio.CancelledError`를 적절히 처리하여 정상적으로 종료해야 한다.

**Rationale**: 현재 PDF와 Markdown 처리가 서로 다른 취소 동작을 보임

**Acceptance Criteria**:
- PDF와 Markdown 처리 모두에서 동일한 취소 인터페이스 사용
- 비동기 처리 경로에서 `asyncio.CancelledError` 적절한 처리
- 취소 시 모든 리소스(파일 핸들, 네트워크 연결 등) 적절한 정리

---

## 명세 (Specifications)

### SPEC-1: 취소 메커니즘 개선

#### 현재 구현 분석
- `main_window.py:474-496`: 취소 버튼이 `processor.stop()`를 호출
- `processor.py:87-89`: `threading.Event()` 기본 stop 이벤트 설정
- **문제점**: 실제 처리 중에는 stop 이벤트가 확인되지 않음

#### 개선 사항
1. **Stop Event 체크 통합**
   - `page_index_main()` 함수에 주기적 stop event 확인 추가
   - `md_to_tree()` 함수에 async 취소 지원 추가
   - AI 추론 호출 중 취소 확인

2. **비동기 취소 처리**
   - `asyncio.run()` 대신 async context 사용
   - `asyncio.CancelledError` 예외 처리
   - Task 취소 전파 메커니즘

3. **리소스 정리**
   - 취소 시 열린 파일 핸들 정리
   - 진행 중인 API 요청 취소
   - 백그라운드 쓰레드 안전 종료

### SPEC-2: 진행률 체크포인트 추가

#### 현재 진행률 구현
```python
# main_window.py:294-312
# 10%, 20%, 100%만 표시
```

#### 개선 사항
1. **PDF 처리 진행률**
   - 페이지 단위 진행률 (예: 10~60% 구간)
   - 텍스트 추출 진행률 (예: 60~80% 구간)
   - 구조 분석 진행률 (예: 80~95% 구간)

2. **Markdown 처리 진행률**
   - 파일 파싱 진행률 (예: 10~30% 구간)
   - 섹션 분석 진행률 (예: 30~70% 구간)
   - 트리 구성 진행률 (예: 70~95% 구간)

3. **AI 추론 진행률**
   - 추론 호출 횟수 기반 진행률 (예: 95~100% 구간)
   - 현재 처리 중인 항목 표시

### SPEC-3: UI 업데이트 최적화

#### 스레드 안전성
- 모든 UI 업데이트는 `after()` 메서드를 통해서만 수행
- 진행률 업데이트 쓰로틀링 (최대 10회/초)
- UI 응답성 유지를 위한 비동기 업데이트

#### 상태 메시지 형식
```
[파일명] 처리 중... (페이지 3/10)
텍스트 추출 중... (30%)
구조 분석 중... (섹션 5/15)
AI 추론 진행 중... (7/10 완료)
```

### SPEC-4: 배치 처리 진행률

**[Optional]** WHERE 배치 처리 모드인 경우, 시스템은 **SHALL** 전체 배치 진행률과 현재 파일 진행률을 모두 표시해야 한다.

#### 배치 처리 UI
- 전체 진행률 바: 완료된 파일 / 전체 파일
- 현재 파일 진행률 바: 현재 파일 처리 진행률
- 배치 상태 메시지: "파일 3/10 처리 중..."

---

## 추적 가능성 (Traceability)

| 요구사항 | 명세 | 테스트 시나리오 |
|---------|------|---------------|
| REQ-1 | SPEC-1 | TC-CANCEL-001, TC-CANCEL-002 |
| REQ-2 | SPEC-2, SPEC-3 | TC-PROGRESS-001, TC-PROGRESS-002 |
| REQ-3 | SPEC-1 | TC-CANCEL-003 |
| REQ-4 | SPEC-2, SPEC-3 | TC-PROGRESS-003 |
| REQ-5 | SPEC-1 | TC-CANCEL-004 |

---

## 참조

- Research Document: `.moai/specs/SPEC-GUI-003/research.md`
- Related Code:
  - `pageindex/gui/main_window.py`
  - `pageindex/gui/processing/processor.py`
  - `pageindex/page_index.py`
  - `pageindex/page_index_md.py`

---

**End of SPEC Document**

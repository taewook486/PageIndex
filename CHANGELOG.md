# Change Log
All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-02-27

### Added (SPEC-GUI-003)
- [x] 실제 동작하는 취소 기능 구현
- [x] 세분화된 진행률 표시 (5% 단위 또는 주요 단계마다)
- [x] 취소 시 데이터 무결성 보장 (임시 파일 관리)
- [x] 처리 단계별 상태 메시지 개선
- [x] 일관된 취소 처리 아키텍처 (PDF/Markdown 공통 인터페이스)

### Implementation Details
- Created 5 new utility modules:
  - `pageindex/gui/processing/stop_event_checker.py`: 취소 신호 확인 (85 lines)
  - `pageindex/gui/processing/progress_calculator.py`: 진행률 계산 (146 lines)
  - `pageindex/gui/processing/progress_updater.py`: 진행률 업데이트 스로틀링 (99 lines)
  - `pageindex/gui/processing/temp_file_manager.py`: 원자적 파일 쓰기 (159 lines)
  - `pageindex/gui/processing/status_formatter.py`: 상태 메시지 형식화 (215 lines)
- Modified `pageindex/gui/processing/processor.py`: 취소 처리 통합
- Added 38 comprehensive unit tests (100% pass rate)
- Test coverage: 85%+ for new modules

### Quality Assurance
- TRUST 5 Framework: PASS
- Ruff Linting: PASS
- Test Results: 38/38 passed
- Code Quality: Clean, well-documented, type-safe

## Beta - 2025-04-23

### Added
- [x] Add node_id, node summary
- [x] Add document discription

### Changed
- [x] Change "child_nodes" -> "nodes" to simplify the structure

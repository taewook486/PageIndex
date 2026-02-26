# ACCEPTANCE: PageIndex GUI Enhancements

**Metadata**
- **SPEC ID**: SPEC-GUI-002
- **Document**: acceptance.md
- **Version**: 1.0
- **Last Updated**: 2026-02-26

---

## Acceptance Criteria

### M6: Recent Files Management

#### Scenario 1: File Added to Recent Files
**Given** 사용자가 파일 처리를 완료했을 때
**When** 처리가 성공적으로 완료되면
**Then** 파일이 최근 파일 목록에 추가되어야 한다
**And** 목록에 타임스탬프가 표시되어야 한다
**And** 목록에 파일 이름이 표시되어야 한다

#### Scenario 2: Recent Files Limit
**Given** 최근 파일 목록에 10개의 파일이 있을 때
**When** 11번째 파일이 처리되면
**Then** 가장 오래된 파일이 목록에서 제거되어야 한다
**And** 목록은 최대 10개를 유지해야 한다

#### Scenario 3: Recent Files Persistence
**Given** 사용자가 3개의 파일을 처리했을 때
**When** 애플리케이션을 종료하고 다시 시작하면
**Then** 최근 파일 목록이 복원되어야 한다
**And** 3개의 파일이 모두 표시되어야 한다

#### Scenario 4: Open Recent File
**Given** 최근 파일 목록에 파일이 있을 때
**When** 사용자가 목록에서 파일을 선택하면
**Then** 해당 파일이 로드되어야 한다
**And** 설정값이 자동으로 로드되어야 한다

#### Scenario 5: Clear Recent Files
**Given** 최근 파일 목록에 파일이 있을 때
**When** 사용자가 "히스토리 초기화"를 선택하면
**Then** 확인 대화상자가 표시되어야 한다
**And** 확인을 누르면 목록이 비워야 한다

#### Scenario 6: Non-existent File Removal
**Given** 최근 파일 목록에 파일이 있을 때
**When** 해당 파일이 삭제되고 목록을 새로고침하면
**Then** 존재하지 않는 파일이 목록에서 제거되어야 한다

#### Scenario 7: Empty Recent Files
**Given** 최근 파일 목록이 비어있을 때
**When** 사용자가 "최근 파일" 메뉴를 열면
**Then** "최근 파일 없음" 메시지가 표시되어야 한다
**And** 메뉴 항목이 비활성화되어야 한다

---

### M7: Settings Management

#### Scenario 1: Open Settings Dialog
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 Ctrl+,를 누르거나 "설정" 메뉴를 선택하면
**Then** 설정 대화상자가 열려야 한다
**And** 현재 설정값이 표시되어야 한다

#### Scenario 2: Save API Key
**Given** 설정 대화상자가 열려있을 때
**When** 사용자가 API 키를 입력하고 "저장"을 누르면
**Then** API 키가 암호화되어 저장되어야 한다
**And** 평문으로 저장되지 않아야 한다
**And** 대화상자가 닫혀야 한다

#### Scenario 3: Load Saved API Key
**Given** 저장된 API 키가 있을 때
**When** 사용자가 설정 대화상자를 열면
**Then** API 키가 마스킹되어 표시되어야 한다 (예: ••••••••)
**And** 기능이 정상 작동해야 한다

#### Scenario 4: Change Theme
**Given** 설정 대화상자가 열려있을 때
**When** 사용자가 테마를 "Light"로 변경하고 "적용"을 누르면
**Then** 테마가 즉시 변경되어야 한다
**And** 대화상자가 열려있어야 한다

#### Scenario 5: Reset to Defaults
**Given** 사용자 정의 설정값이 있을 때
**When** 사용자가 "기본값 복원"을 누르면
**Then** 확인 대화상자가 표시되어야 한다
**And** 확인을 누르면 모든 설정이 기본값으로 복원되어야 한다

#### Scenario 6: Validate Settings
**Given** 설정 대화상자가 열려있을 때
**When** 사용자가 유효하지 않은 URL을 입력하고 "저장"을 누르면
**Then** 에러 메시지가 표시되어야 한다
**And** 설정이 저장되지 않아야 한다

#### Scenario 7: Corrupted Settings Recovery
**Given** 설정 파일이 손상되었을 때
**When** 애플리케이션이 시작되면
**Then** 기본값으로 자동 복구되어야 한다
**And** 사용자에게 알림이 표시되어야 한다

---

### M9: Enhanced Visualization

#### M9.1: Drag & Drop

**Scenario 1: Single File Drop**
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 PDF 파일을 드래그 앤 드롭하면
**Then** 파일이 로드되어야 한다
**And** 파일 경로가 표시되어야 한다

**Scenario 2: Multiple Files Drop**
**Given** 배치 처리 모드가 활성화되어 있을 때
**When** 사용자가 3개의 파일을 동시에 드롭하면
**Then** 모든 파일이 배치 큐에 추가되어야 한다
**And** 큐 목록에 3개의 파일이 표시되어야 한다

**Scenario 3: Invalid File Drop**
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 .exe 파일을 드롭하면
**Then** 거부 피드백이 표시되어야 한다
**And** 파일이 로드되지 않아야 한다

**Scenario 4: Drag Over Feedback**
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 파일을 드래그 영역 위로 가져가면
**Then** 드롭 영역이 하이라이트되어야 한다

---

#### M9.2: Batch Processing

**Scenario 1: Start Batch Processing**
**Given** 배치 큐에 3개의 파일이 있을 때
**When** 사용자가 "일괄 처리 시작"을 누르면
**Then** 첫 번째 파일 처리가 시작되어야 한다
**And** 진행률이 표시되어야 한다

**Scenario 2: Batch Progress**
**Given** 3개 파일 중 2번째가 처리 중일 때
**When** 처리가 진행되면
**Then** 전체 진행률이 표시되어야 한다 (예: "2/3 완료")
**And** 현재 파일의 진행률도 표시되어야 한다

**Scenario 3: Batch Error Handling**
**Given** 3개 파일 배치 처리 중일 때
**When** 두 번째 파일에서 에러가 발생하면
**Then** 에러가 기록되어야 한다
**And** 세 번째 파일 처리가 계속되어야 한다

**Scenario 4: Batch Completion**
**Given** 3개 파일 배치 처리가 완료되면
**When** 모든 처리가 끝나면
**Then** 처리 요약이 표시되어야 한다
**And** 성공/실패 수가 표시되어야 한다
**And** 총 처리 시간이 표시되어야 한다

**Scenario 5: Remove from Queue**
**Given** 배치 큐에 3개의 파일이 있을 때
**When** 사용자가 두 번째 파일을 제거하면
**Then** 해당 파일이 큐에서 제거되어야 한다
**And** 남은 파일이 2개여야 한다

---

#### M9.3: Result Comparison

**Scenario 1: Open Comparison View**
**Given** 두 개의 처리 결과가 있을 때
**When** 사용자가 "비교"를 선택하면
**Then** 사이드 바이 사이드 뷰가 열려야 한다
**And** 두 결과가 나란히 표시되어야 한다

**Scenario 2: Sync Scrolling**
**Given** 비교 뷰가 열려있을 때
**When** 사용자가 한 쪽을 스크롤하면
**Then** 다른 쪽도 동기화되어 스크롤되어야 한다

**Scenario 3: Diff Highlighting**
**Given** 비교 뷰가 열려있을 때
**When** 두 결과에 차이가 있으면
**Then** 차이가 하이라이트되어야 한다

---

#### M9.4: Export Functionality

**Scenario 1: PDF Export**
**Given** 처리 결과가 있을 때
**When** 사용자가 "PDF로 내보내기"를 선택하면
**Then** 파일 저장 대화상자가 열려야 한다
**And** PDF 파일이 생성되어야 한다
**And** PDF가 정상적으로 열려야 한다

**Scenario 2: HTML Export**
**Given** 처리 결과가 있을 때
**When** 사용자가 "HTML로 내보내기"를 선택하면
**Then** 스타일된 HTML 파일이 생성되어야 한다
**And** HTML이 브라우저에서 정상적으로 표시되어야 한다

**Scenario 3: Markdown Export**
**Given** 처리 결과가 있을 때
**When** 사용자가 "Markdown으로 내보내기"를 선택하면
**Then** 유효한 Markdown 파일이 생성되어야 한다

**Scenario 4: Export with Options**
**Given** 내보내기 대화상자가 열려있을 때
**When** 사용자가 "메타데이터 포함"을 선택하고 내보내면
**Then** 메타데이터가 포함된 파일이 생성되어야 한다

---

### Additional UX Enhancements

#### Keyboard Shortcuts

**Scenario 1: Ctrl+O Open File**
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 Ctrl+O를 누르면
**Then** 파일 선택 대화상자가 열려야 한다

**Scenario 2: Ctrl+S Save Result**
**Given** 처리 결과가 있을 때
**When** 사용자가 Ctrl+S를 누르면
**Then** 결과 저장 대화상자가 열려야 한다

**Scenario 3: Ctrl+, Open Settings**
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 Ctrl+,를 누르면
**Then** 설정 대화상자가 열려야 한다

**Scenario 4: F1 Help**
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 F1을 누르면
**Then** 도움말 대화상자가 열려야 한다

---

#### Tooltips

**Scenario 1: Parameter Tooltip**
**Given** 설정 패널이 표시되어 있을 때
**When** 사용자가 "Max Pages/Node" 입력 위에 마우스를 올리면
**Then** 툴팁이 표시되어야 한다
**And** 설명이 명확해야 한다

**Scenario 2: Button Tooltip**
**Given** 메인 창이 표시되어 있을 때
**When** 사용자가 "일괄 처리" 버튼 위에 마우스를 올리면
**Then** 기능 설명 툴팁이 표시되어야 한다

---

#### Status Bar

**Scenario 1: Idle Status**
**Given** 애플리케이션이 실행 중일 때
**When** 처리가 진행 중이 아니면
**Then** 상태 바에 "대기 중" 메시지가 표시되어야 한다

**Scenario 2: Processing Status**
**Given** 파일 처리 중일 때
**When** 처리가 진행되면
**Then** 상태 바에 진행률이 표시되어야 한다
**And** "처리 중: 60%"와 같은 메시지가 표시되어야 한다

**Scenario 3: Completion Status**
**Given** 파일 처리가 완료되면
**When** 처리가 끝나면
**Then** 상태 바에 완료 메시지가 표시되어야 한다
**And** 처리 시간이 표시되어야 한다 (예: "완료 (45초)")

---

#### Log Viewer

**Scenario 1: Open Log Viewer**
**Given** 애플리케이션이 실행 중일 때
**When** 사용자가 "로그 보기"를 선택하면
**Then** 로그 뷰어 대화상자가 열려야 한다
**And** 처리 로그가 표시되어야 있다

**Scenario 2: Error Log Display**
**Given** 처리 중 에러가 발생했을 때
**When** 사용자가 로그 뷰어를 열면
**Then** 에러 세부 정보가 표시되어야 한다
**And** 에러가 빨간색으로 하이라이트되어야 한다

**Scenario 3: Filter Logs**
**Given** 로그 뷰어가 열려있을 때
**When** 사용자가 "ERROR"만 필터링하면
**Then** 에러 로그만 표시되어야 한다

**Scenario 4: Export Logs**
**Given** 로그 뷰어가 열려있을 때
**When** 사용자가 "로그 내보내기"를 누르면
**Then** 로그 파일이 저장되어야 한다

---

## Quality Gates

### TRUST 5 Framework

**Tested**:
- [ ] Unit tests for all new manager classes
- [ ] Integration tests for batch processing
- [ ] UI tests for dialogs and menus
- [ ] Minimum 85% code coverage for new code

**Readable**:
- [ ] Clear naming conventions
- [ ] Code comments in English
- [ ] Documentation for new classes
- [ ] User guide for new features

**Unified**:
- [ ] Consistent with existing GUI style
- [ ] Follows project coding standards
- [ ] Black/ruff formatting applied

**Secured**:
- [ ] API key encryption verified
- [ ] No secrets in logs
- [ ] Input validation on all user inputs
- [ ] Settings file permissions checked

**Trackable**:
- [ ] Conventional commit messages
- [ ] SPEC reference in commits
- [ ] CHANGELOG updated
- [ ] Version number incremented

---

## Definition of Done

A feature is considered complete when:
- [ ] All acceptance criteria pass
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] No critical bugs
- [ ] Performance acceptable (<10% overhead)
- [ ] User testing completed (for major features)

---

**TAG**: SPEC-GUI-002
**Traceability**: All acceptance criteria map to requirements in spec.md

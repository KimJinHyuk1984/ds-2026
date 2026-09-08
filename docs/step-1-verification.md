# 1단계 검증 보고서

실행일: 2026-09-08 (Asia/Seoul). 최초 실행 기록이며 기존 보고서는 없었다.

**최종 판정: 미완료·중단. 원본 SHA-256 불일치(`SRC-001`)와 브라우저 실측 불가(`ENV-001`)로 1단계를 통과 처리하지 않는다.** 개인정보 관련 관측의 재공개 범위(`PRIV-001`)도 미결정이다. 2단계는 수행하지 않았다.

## 실행 범위와 환경

- 저장소: `D:/000vibecoding/ds-2026`; `git rev-parse --show-toplevel`로 확인.
- 사용자 지시: “WORKFLOW.md 를 읽고 1단계를 수행한다. 원본 자료는 source/ 에 있다.”
- README, DESIGN.md, WORKFLOW.md를 읽었다. 적용할 AGENTS.md는 저장소 및 확인한 상위 경로에 없었다. 기존 `docs/`와 상태 파일, `.gitignore`도 없었다.
- 시작 `git status --short --untracked-files=all`: 원본 PDF 1개만 미추적. 시작 추적 파일 diff는 0건. 원본은 사용자 제공 파일이며 이번 작업의 신규 작성물이 아니다.
- PowerShell 5.1.26100.9168, Node.js v22.22.2, Git 2.54.0.windows.1, PDF.js 6.3.289, Windows.Data.Pdf 및 Windows.Media.Ocr(`ko`).
- `python`, `python3`, Poppler, Tesseract는 PATH에서 찾지 못했다. `py -0p`와 `py -3`는 설치 Python 없음으로 응답했다. 일부 표준 Python 설치 경로 조회는 접근 거부로 확인하지 못했다. 시스템 전체를 검색하거나 Python이 컴퓨터 전체에 없다고 단정하지 않았다.
- PDF.js는 `work-temp/step-1/` 아래에만 임시 설치했다. 웹 런타임에 npm 의존성을 추가하지 않았다. 원본 전송·온라인 OCR·원본 내 링크 방문은 0건.
- 브라우저 도구로 `file:///D:/000vibecoding/ds-2026/index.html` 검증을 준비했지만 `No browser is available` 응답을 받았다. 페이지 진입 성공으로 세지 않았다. viewport·브라우저 버전·테마·모션 설정의 실측값은 없음.

## 원본 변경 발견

| 시점 | 크기 | SHA-256 |
| --- | ---: | --- |
| 시작 기준 | 80321983 | `AA77C8A411D6D58ABFAF513D9725ED1BDD43BB54A906B245894FAAFBE3073881` |
| 22:58:20 +09:00 종료 대조 | 27401216 | `188AB7701BA40291E1E60F1CD01A808EF38305A8BB71C706741016787E77C56B` |
| 후속 재확인 | 27401216 | `188AB7701BA40291E1E60F1CD01A808EF38305A8BB71C706741016787E77C56B` |

현재 파일의 생성 시각은 22:57:16.4851303, 수정 시각은 22:57:16.0417985(+09:00)로 관측했다. 변경 주체·원인은 확인하지 못했다. 이번 검사 스크립트의 원본 경로 접근은 읽기이며, 텍스트·JSON·PNG·연락시트 쓰기 대상은 모두 `work-temp/step-1/`였다. 현재 원본을 수정·복원·덮어쓰기하지 않았다.

종료 시 동일성 조건이 깨졌으므로, 216쪽 텍스트/OCR 검사를 현재 파일의 검사 결과로 인증하지 않는다. 정본 선택 전에는 현재 PDF의 내용 검사로 자동 재시작하지 않는다.

## 공통 검증 C01~C15

최초 실행이어서 이전 통과 증거를 재사용한 항목은 없다. 기존 예시 페이지도 검사 대상이며, 웹 파일을 수정하지 않았다는 이유로 동작 검증을 `해당 없음`으로 처리하지 않았다.

| ID | 결과 | 대상·개수 | 방법·실측값·증거와 제한 |
| --- | --- | --- | --- |
| C01 변경 범위 | 실패 | 보호 파일 4개, 원본 1개, JS 3개 | `Get-FileHash -LiteralPath ... -Algorithm SHA256`: 보호 파일 4/4 동일, 원본 1/1 불일치. `node --check`로 shared.js·widgets.js·site.js 오류 0. `git diff --check` 오류 0, 추적 웹 파일 diff 0. 위 원본 관측 표 및 상태 파일의 최초 해시 참조 |
| C02 개인정보·추적 | 미실행 | 원본 1개, 새 문서 3개와 .gitignore, 기존 instructor 필드 | 제외·추적 검사는 통과: 실제 원본/임시 파일 `git check-ignore -v` 적중, `git ls-files source work-temp .venv venv` 0건. 신규 보고서의 실제 이름·연락처 재인용 0. 원본의 이전 텍스트 216쪽·OCR 216쪽 검사 결과는 source-inventory.md 참조. **현재 원본은 교체되어 개인정보 검사 미실행**, 공개 처리도 미결정. C02 전체 통과 아님 |
| C03 코드 정본 | 통과 | 기존 템플릿 개념 예제 3블록; 원본 실습 파일 0개 | `index.html` 소스에서 3개 모두 121자·7줄, 끝 줄바꿈 없음, 서로 문자 단위 동일. 정본 파일이 없는 TODO 함수 예제로 원문·들여쓰기·None 반환·호출의 소스 일관성을 확인. 정규화 없이 비교. Python 실행·새 강의 정본 검증을 했다는 뜻은 아님 |
| C04 실제 복사 | 미실행 | 기존 코드 3블록, 발표 코드 참조 1개 | ENV-001: 실제 클릭·OS/브라우저 클립보드 읽기 불가. 복사 성공 배지나 모의 API로 대체하지 않음 |
| C05 전체 발표 순회 | 미실행 | index.html 1개, 소스상 기본 14/전체 15마커 | ENV-001. skip 1개 제목 `추가 주의사항`은 소스 관측값. P·방향키·PageUp/Down·Shift·B·S·Esc 실제 입력 결과가 아님. 허브 대상 0개이나 강의 대상은 존재 |
| C06 조각 넘침 | 미실행 | 강의 1개, 기본/S 포함 합계 29개 검사 예정 | 1920×950 설정 및 `.presentation-viewport` 측정, `reportPresentationOverflow()` 실행 모두 불가. 넘침 0건이나 `[]`로 기록하지 않음. 실측 CSV를 만들지 않음 |
| C07 크기·복원 | 미실행 | 강의 1개, 코드 3개·그림 1개·위젯 1개 | 표시 배율·변환 후 글자 크기·종료 후 DOM/스타일/상태 복원 실측 없음 |
| C08 테마·AA | 미실행 | 예시 페이지 1개, 두 테마 | computed 색 수집·알파 합성·텍스트/포커스 대비 측정 불가. CSS 토큰만 보고 통과시키지 않음 |
| C09 모바일 | 미실행 | 예시 페이지 1개, 두 테마 | 375×812에서 scrollWidth/clientWidth 및 메뉴·모달·이미지·입력 실측 불가 |
| C10 HTTP·file | 미실행 | index.html 1개 | 사용 가능한 Python 3 경로를 확보하지 못했고 연결 브라우저도 없음. Python HTTP 서버 미시작, 하위 경로·file 직접 열기·왕복 이동 미실행 |
| C11 오류·오프라인 | 미실행 | HTML 1개·JS 3개 | `rg`/Node 소스 검사에서 fetch/XMLHttpRequest 호출 0개. 실행 오류·요청 실패는 실측 불가. `instructor.photo`의 `assets/img/instructor.jpg`는 파일이 없어 정상 HTTP 실행 시 실패 요청 가능성이 있음(소스 관측; 재현 미실행). README의 이니셜 폴백을 실측 결과로 사용하지 않음 |
| C12 모션 감소 | 미실행 | 강의·공통 reveal·발표·위젯 | reduce/일반 모드 에뮬레이션과 최종 결과·키보드 동작 대조 불가 |
| C13 다운로드·이미지 | 미실행 | 다운로드 0개, 기존 본문 이미지 1개·선택 사진 경로 1개 | 다운로드만 대상 0개. example-image.webp는 파일 헤더상 1600×900, HTML width/height와 일치; alt·lazy·캡션 존재, 로컬 이미지 육안 확인. 브라우저 naturalWidth·로딩·사진 폴백 검증은 미실행이므로 전체 통과 아님 |
| C14 공통 UI | 미실행 | 메뉴·진도·모달·키보드, 3섹션 | 소스상 진도 키 `lecture-progress:lecture-template:lecture-title`, 테마 키 `lecture-template-theme`. 클릭·포커스 트랩·Esc·복귀·새로고침 복원·단축키 충돌 검증 불가 |
| C15 위젯 회귀 | 미실행 | 기존 `value-slider` 1개 | 입력 경계·키보드·마우스/터치·발표 축소·스크립트 차단/생성 예외의 브라우저 검증 불가. 원본 실습 프로그램·장치 실행 대상은 0개 |

합계: 통과 1, 실패 1, 미실행 13, 해당 없음 0. C01의 부분 통과와 C02의 Git 검사 통과를 항목 전체 통과와 혼동하지 않는다.

## 제외·추적 및 마무리 확인

실제 실행한 주요 명령:

```powershell
git status --short --untracked-files=all
git diff --stat
git diff --check
git ls-files
git ls-files source work-temp .venv venv
git check-ignore -v -- 'source/데이터 과학-240710.pdf' work-temp/step-1/read-pdf.mjs
node --check assets/js/shared.js
node --check assets/js/widgets.js
node --check data/site.js
Get-FileHash -LiteralPath 'source/데이터 과학-240710.pdf' -Algorithm SHA256
```

원본은 `.gitignore:1:/source/`, 실제 임시 스크립트는 `.gitignore:2:/work-temp/`에 적중했다. .venv·venv·__pycache__·pyc 규칙은 가상 경로로도 적중 여부를 확인했으며, 실제 해당 원본/가상환경 신규 추적은 0건이었다. `files/` 전체 제외 규칙은 추가하지 않았다. 원본의 기존 추적 0건으로, 추적 해제나 Git 이력 수정은 하지 않았다.

작업 임시물은 이번에 만든 `work-temp/step-1/`에만 두었다. 해당 폴더의 재귀 삭제 명령은 자동 승인 검토에서 `rejected: blocked by policy`로 차단되어 실행되지 않았다(`TMP-001`). 따라서 **`D:/000vibecoding/ds-2026/work-temp/step-1/`가 남아 있다.** Git 제외 상태를 재확인했다. 세부 차단 사유는 도구가 제공하지 않았다. 다른 수단으로 삭제를 우회하지 않았다.

남은 임시물은 PDF 렌더 PNG 216개, OCR 텍스트·위치 JSON, 본문 추출 텍스트, PDF 속성/주석 검사 JSON, 페이지 연락시트 18개, 검사 스크립트·로그, PDF.js 도구와 npm 캐시다. 검사 텍스트·이미지에 실제 식별 정보가 있으므로 공개 보고서·웹 자산으로 옮기지 않는다. 2단계 이미지 추출물로 사용하지 않는다. 서버는 시작하지 않아 종료할 서버 프로세스가 없다.

## 단계 종료 기록

- 수행한 단계/회차 → **1단계만 수행, 완료 판정 보류**.
- 변경 파일 → `.gitignore`, `docs/source-inventory.md`, `docs/step-1-verification.md`, `docs/workflow-state.md`. 작업 중 관측한 원본 교체는 이 보고서의 검사 스크립트 작성 변경과 구분한다.
- 산출물 → 자료 1개 목록, 두 시점의 원본 해시, 보호 파일 최초 기준, 마스킹한 식별 정보 관측, C01~C15 결과와 미실행 원인.
- 검사별 결과 → 통과 1 / 실패 1 / 미실행 13. 실습 배포 복사 0개.
- 미해결 선택지 → SRC-001의 현 파일/최초 파일 정본 선택을 우선 확인. PRIV-001의 공개 범위는 정본 재검사 후 확정. ENV-001은 연결 브라우저와 Python HTTP 검사 환경 확보 필요. TMP-001은 정책상 차단된 임시 폴더 정리 미완료.
- 수행하지 않은 범위 → 현재 교체본 내용 검사, 원본 비식별 수정, 공개 실습 복사, 이미지 자산 추출, 코드 복원, 내용 분석·섹션 설계·HTML 제작, 2~7단계, 커밋·푸시·배포.
- 다음 실행 조건 → 사용자가 정본을 지정한 뒤 1단계 재검사를 지시한다. 공개 차단 결정과 필요한 공통 검증을 마치기 전에는 2단계 진입 불가. 승인만으로 다음 단계가 자동 실행되지 않는다.

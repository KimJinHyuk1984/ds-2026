# 사용자 지정 2단계 — 학기 사이트 뼈대 검증

작업일: 2026-09-08. 사용자 확정 B안과 이번 메시지의 2단계 범위만 적용했다.
기존 WORKFLOW.md의 이미지 추출 2단계와 다른 작업이다. 3단계 본문 작성·ready 전환·커밋·푸시·배포는 실행하지 않았다.

## 결과

- 구현: 학기 홈 1개 + 준비 중 주차 HTML 15개. 전 주차 coming, 개념 설명·실습·코드·본문 이미지·CSV·수집 스크립트 0개.
- 정적 검사와 메모리 내 주차 이동 검사, 로컬 HTTP 경로 검사 통과.
- 브라우저 화면 검증은 **미실행**. CUA 검색 결과 apps/browsers가 비어 있었고, iab 페이지 열기도 'Browser is not available: iab'로 실패했다. 모바일·테마·실제 클릭·file:// 실행을 통과로 선언하지 않는다.
- 현재 Python은 설치되어 있지 않다(`py --list`: No installed Pythons found). Node 내장 HTTP 서버로 경로를 검사했다. 빌드·번들러·npm 의존성·GitHub Actions를 추가하지 않았다.

## 실행한 검사

| 항목 | 결과·범위 |
|---|---|
| JavaScript 구문 | `node --check data/site.js`, `node --check assets/js/widgets.js` 통과 |
| 공백 오류 | `git diff --check` 오류 0건. Git의 LF→CRLF 안내는 오류가 아님 |
| 파일·메타 일치 | HTML 16개, levels 15개, coming 15개, 학습목표 32개, 사용자 제공 교재 단원 쪽수 21개 대조 |
| 링크·구조 | 정적 상대 파일 링크 141개 실재 확인, 내부 앵커와 ID 중복 검사 통과 |
| 내용 범위 | HTML에서 pre/code/template/data-slide/발표 버튼/TODO/예시 위젯·이미지 참조 0개 |
| 주차 이동 | 실제 widgets.js의 week-navigation 함수를 Node VM의 DOM 대역에서 실행. 11개 상태 시나리오 통과. 실제 브라우저 입력 검사가 아님 |
| 이동 상태 시나리오 | ready 0개, 1개, 중간 coming을 포함한 1·4·9주 공개, 전체 공개. 첫/중간/마지막 ready와 coming 직접 접근 검사. coming 선택을 강제로 submit해도 이동 0건 |
| HTTP | 임시 서버의 /ds-2026/와 /ds-2026/week-01/ ~ week-15/ 및 참조 파일 157회 응답 200 확인. 렌더링·클릭 검사가 아님 |
| 공통 자산 | base.css·tokens.css·shared.js·DESIGN.md·sync-shared.ps1·sync-shared.sh 6개 시작/종료 SHA-256 일치 |
| 강사 정보 | Git HEAD의 SITE.instructor와 현재 객체 동일 |
| 자료 폴더 | data/neis, data/weather-bike, data/kbo, scripts는 각각 .gitkeep만 있음 |
| 임시 검사 | work-temp/stage-2-checks/check.cjs를 실행 후 정리. 상태 변경은 메모리에서만 수행; 배포 메타는 전부 coming 유지 |

## WORKFLOW 공통 검사와 이번 범위

| ID | 상태 | 근거·남은 확인 |
|---|---|---|
| C01 | 통과 | 위 구문·diff·공통 6개 해시 비교. 이번 작업에 원본 자료 사용 없음 |
| C02 | 부분 검사 | 신규 페이지는 목표와 안내만 포함. 강사 데이터 동일. 기존 로컬 PDF가 있는 docs/reference/를 .gitignore에 추가하고 제외·미추적 상태 확인. PDF 내용 검사를 재실행한 것은 아님 |
| C03·C04 | 해당 없음 | 학습용 코드블록·복사 버튼 대상 0개 |
| C05·C06·C07 | 해당 없음 | 이번 안내 페이지의 발표 버튼·발표 조각 대상 0개 |
| C08 | 미실행 | 브라우저 부재: 라이트/다크 실제 대비·렌더 검사 필요 |
| C09 | 미실행 | 브라우저 부재: 375×812 양 테마와 가로 넘침 검사 필요 |
| C10 | 부분 검사 | Node HTTP 요청 157건 확인. file:// 실행과 브라우저 왕복 이동 미실행 |
| C11 | 부분 검사 | 사이트의 fetch/XMLHttpRequest·추가 외부 런타임 의존성 없음. 실제 브라우저 콘솔·네트워크는 미실행 |
| C12 | 미실행 | 브라우저 부재: 모션 감소 설정 확인 필요 |
| C13 | 부분 검사 | CSV 다운로드·본문 이미지 대상 0개. 기존 강사 사진/이니셜의 실제 표시 검사는 미실행 |
| C14 | 미실행 | 브라우저 부재: 기존 메뉴·현재 위치·열람 기록·강사 모달·포커스 검사 필요 |
| C15 | 부분 검사 | 주차 이동 상태 11개 통과. 실제 키보드·선택·반응형·스크립트 차단 검사는 미실행 |

## 생성·수정 파일

수정: index.html, data/site.js, assets/js/widgets.js, assets/css/lecture.css, docs/CURRICULUM.md, docs/workflow-state.md, .gitignore.

생성: week-01/index.html ~ week-15/index.html, data/README.md, data/neis/.gitkeep, data/weather-bike/.gitkeep, data/kbo/.gitkeep, scripts/.gitkeep, 이 검증 문서.

.gitignore에는 /docs/reference/만 추가하여 로컬 교재 PDF를 공개 커밋 후보에서 제외했다. PDF 자체와 이전 source-inventory.md·step-1-verification.md는 수정하지 않았다. 공통 자산과 instructor는 그대로 유지했다.

## 로컬 확인 방법

1. 빠른 확인은 저장소의 index.html과 각 week-XX/index.html을 브라우저로 직접 연다. JavaScript가 켜져 있어야 동적 목록·공통 메뉴·주차 이동을 확인할 수 있다. 새 수정이 보이지 않으면 Ctrl+F5를 누른다.
2. HTTP 확인은 저장소 루트의 PowerShell에서 아래 명령을 실행한다. 설치된 Node의 내장 모듈만 사용한다. 서버는 127.0.0.1에만 연결되며 Ctrl+C로 종료한다.

```powershell
@'
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const types = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8" };
http.createServer((request, response) => {
  let urlPath = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
  if (urlPath.endsWith("/")) urlPath += "index.html";
  const file = path.resolve(root, "." + urlPath);
  if (!file.startsWith(root + path.sep)) { response.writeHead(403).end(); return; }
  fs.readFile(file, (error, content) => {
    response.writeHead(error ? 404 : 200, { "Content-Type": types[path.extname(file)] || "application/octet-stream" });
    response.end(error ? "Not found" : content);
  });
}).listen(8000, "127.0.0.1", () => console.log("http://127.0.0.1:8000/"));
'@ | node
```

브라우저에서 http://127.0.0.1:8000/ 와 http://127.0.0.1:8000/week-01/ ~ week-15/ 를 확인한다. 위 PowerShell 명령은 실제 실행해 홈·1주·15주·위젯 JS의 200 응답과 Content-Type을 확인한 뒤 서버를 종료했다. file://의 폴더 이동은 브라우저에 따라 디렉터리 표시가 될 수 있으므로 HTTP 확인을 우선한다.

## 배포 후 체크리스트

- [ ] /ds-2026/ 에 데이터 과학 제목과 15개 coming 카드가 표시되고 링크가 비활성이다.
- [ ] /ds-2026/week-01/ ~ week-15/ 를 각각 직접 열면 해당 주차 번호·제목·차시·목표·데이터·제공된 쪽수·준비 중 안내가 보인다.
- [ ] 직접 URL에서 미완성 원고·예시 코드·실습·미존재 CSV 다운로드 링크가 노출되지 않는다.
- [ ] 각 페이지의 학기 홈 링크가 /ds-2026/ 의 홈으로 돌아간다.
- [ ] 전 주차 coming 상태에서 주차 선택·이동 버튼과 이전/다음이 비활성이고 공개된 주차가 없다는 안내가 보인다.
- [ ] 향후 ready 전환 후 선택 목록은 ready만 이동 가능하고, 이전/다음은 coming을 건너뛴다. 첫/마지막 ready에서는 해당 방향이 비활성이다.
- [ ] coming 직접 접근 페이지의 이전/다음은 계속 비활성이고, 선택 목록으로는 ready 주차에만 이동한다.
- [ ] 375×812 모바일과 데스크톱에서 가로 넘침·잘린 버튼·긴 제목/데이터 이름·선택 목록을 확인한다. 라이트/다크 모두 확인한다.
- [ ] 공통 목차·강사 소개·테마·키보드 포커스가 작동하며 자산 경로가 저장소 하위 경로에서 유지된다.

## 3단계 전에 결정할 사항

- 1주차 따릉이 CSV의 대상 기간과 집계 범위(예: 서울 전체 일별 대여 건수).
- 기존 CSV를 사용할지, 3단계에서 교사 배포용 CSV 수집·집계를 함께 진행할지.

주차 slug·공개 방식·데이터 종류·교재 쪽수는 이미 확정되었으므로 다시 결정할 필요가 없다. 3단계 진행 지시 전에는 본문이나 실습 자료를 만들지 않는다.

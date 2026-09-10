# 4주차 작성 검증 — 2026-09-10

## 승인 범위와 산출물

사용자가 3주차 검증 완료 후 4주차 완성·ready 전환과 정제 CSV 생성 스크립트 작성(실행 금지)을 지시했다. 메뉴 분리·알레르기 처리·파생변수·편향은 5주차로 배치한다. 공통 파일과 기존 CSV는 변경하지 않는다.

| 파일 | 변경 내용 |
|---|---|
| week-04/index.html | 10~12차시 본문, 완성 코드, 비교·과제, 수업 후 공개 안내 |
| scripts/build-bike-daily-clean.py | 원본 검증 후 강수량 공백만 0으로 바꾸는 별도 결과 생성기 |
| .gitignore | bike-daily-clean.csv·meals-parsed.csv 허용 명시 |
| data/site.js | 4주차 ready 및 4/5주차 데이터·목표·5주차 제목 |
| week-05/index.html | 확정된 제목·목표·데이터만 동기화, coming 안내 유지 |
| docs/CURRICULUM.md | 4/5주차 배치·실측 근거·결과 배포 정책 |
| data/README.md | 원본/정제 결과 구분, 교사 실행법·검증 기준 |
| docs/workflow-state.md, 이 문서 | 승인·작업·검증·미실행 기록 |

## 콘텐츠와 실측 대조

- 세 차시 모두 질문 → Orange3 → 개념 → Python → 비교 순서다. Python 문법 강의 없이 컬럼·날짜·학교·IQR 배수를 바꿀 수 있는 완성 코드 12셀을 제공했다.
- Impute는 10차시 Don't Impute로 원본을 유지한다. 11차시는 같은 원본에서 세 갈래로 평균 대체·행 삭제·0 대체를 비교한다. 메뉴는 처리할 대상으로 관찰만 한다.
- PowerShell Import-Csv로 기존 확정 CSV를 읽어 강수량 공백 200개·명시적 0 51개, 관측된 값 평균 8.12091503267974mm, 합계를 353으로 나눈 평균 3.51983002832861mm를 대조했다. 새 CSV를 만들지 않았다.
- 대여건수의 기본 선형 보간 사분위 Q1=78,186, Q3=164,906, IQR=86,720과 1.5×IQR 후보 0건을 대조했다. 극단값을 억지로 이상치로 표시하지 않는다.
- 최소 14,293건은 2024-05-05, 평균기온 17.8°C·강수량 48.3mm·공휴일여부 1이다. 폭설·한파로 설명하지 않는다. 최대 194,244건은 2024-06-04다. 원인에 대한 가설과 실제 관측을 구별하며 두 행 모두 남긴다.
- 명덕고 2024-03-05의 60/1,005/55명을 원본과 대조했다. 2주차 2024-03-04의 60/759/55명을 변경하지 않았다. 기숙사생 등 이용 대상 차이는 추가 운영 정보로 확인할 해석이다.
- Orange 공식 Impute·Box Plot·Outliers 문서를 확인했다. LOF와 IQR을 서로 다른 탐지 기준으로 구분했다. Outliers는 대여건수만 Features로 분석하고 전체 Data를 유지한다. Orange Box Plot과 matplotlib의 수염 표시가 동일하다고 설명하지 않는다.
- 교재는 p.67 (Ⅱ-1-2) 참조만 제공했다. 교재 문장·이미지·도표·레이아웃을 재사용하지 않았다.

## 정적 검증 결과

| 항목 | 결과 |
|---|---|
| HTML 구조 | 태그 짝·중복 ID·ARIA·로컬 링크·내부 앵커 오류 0건 |
| 섹션·ID | 8섹션, 34개 ID |
| 발표 조각 | 중첩 0개, 기본 29개·보충 포함 31개 |
| 코드 | pre[data-code] 12개, 최대 10줄, 모든 셀이 발표 조각 안에 있음 |
| 학습 경계 | 메뉴 분리·정규식·CSV 쓰기 코드 없음, 기존 폰트 설치 방식 없음 |
| 공개 링크 | 원본 2개만 다운로드, 정제 결과·생성기 직접 링크 없음 |
| 공개 상태 | 15개 level 유지, 1~4주 ready·5~15주 coming |
| 변경 경계 | 4/5주차 외 level과 instructor 불변, 15개 주차 파일 존재 |
| JS·공백 | node --check data/site.js, git diff --check 통과 |
| Git 예외 | 두 정제 CSV 허용, 다른 weather-bike CSV·source/ 제외 유지 |
| 원본 추적 | git ls-files source work-temp 결과 0개 |
| 보호 해시 | 아래 10개 모두 시작·종료 일치 |
| 결과 파일 | bike-daily-clean.csv·meals-parsed.csv 모두 미생성 |

발표 중 본문 앵커 처리는 기존 widgets.js의 비활성화·복원 로직을 그대로 사용한다. 실제 클릭 검증으로 확대해 보고하지 않는다.

## 생성기 검토 — 실행하지 않음

- 외부 의존성은 pandas뿐이며 수집/API 요청은 없다.
- 원본의 컬럼 순서·353행·기간·날짜 연속성·강수량 공백 200개·그 외 공백 0개·수치 형식을 저장 전에 확인한다.
- 문자열로 읽어 기존 셀 표기를 보존한다. 강수량 공백만 0으로 바꾸고 관측 강수량과 다른 7개 컬럼의 동일성을 검사한다.
- 원본과 같은 경로/파일 거절, 기존 결과는 기본 중단, --overwrite는 결과에만 적용한다.
- UTF-8 BOM·인덱스 없이 별도 저장하고 전후 결측·행 수·기간·강수량 평균·대여건수 최소/최대를 출력한다.
- 소스를 검토했으며 Python 실행·import·구문 컴파일·CSV 생성은 하지 않았다. 생성기 실행 성공과 출력 검증은 사용자 로컬 실행 후 확인해야 한다.

## 보호 파일 SHA-256

| 파일 | 시작·종료 동일 해시 |
|---|---|
| assets/js/shared.js | E74FACE44F5B81E6A96CFA500CA616A089975EB85EF5EF985CE05DB182D75569 |
| assets/css/base.css | 2B1D4CFCF12DC00C9A65A288D106BB1F6E9C75AB14D900CA24095738B35B25CB |
| assets/css/tokens.css | 6C3EEDE764AE1875570731BA175D569DA58030C7FDA96669FCED3FE36DEB8590 |
| DESIGN.md | C473FCA5C871CAB360DAE65320E6A38189D7E987857CC53700C69E9606A40100 |
| week-01/index.html | 69412065CBC9696A4C4BD89F47AB668A3D317A1F1AAAE38C2994F2B543F0D4FD |
| week-02/index.html | 68ED59C0C937D3CAE475F5DCDC646D4783B806F18A27B70E64EFADDCBFB9AC4E |
| week-03/index.html | F46A724D26F100D7AE7D0165E10565ECCB13F654103D22D14BA3B41E2A7F8F40 |
| data/neis/schools.csv | 6D83C06A150A534EF912D86688F18593F0A65ACD783974F837C030BF663731D8 |
| data/neis/meals.csv | 74D2A209A4DEC8B8BD8017BB7E25B102637FBB582A4721C08E4CFCC84FF47C75 |
| data/weather-bike/bike-daily.csv | 4F3E86DC8F2D39D924DE4B5DD42AE1669AC214FBBA576D1F9984E6860344B3DC |

## 미실행 항목과 다음 확인

CUA 상태가 apps=[]·browsers=[]여서 실제 Orange3·발표·모바일·코드 복사·다운로드 UI 검증을 할 수 없었다. Colab/Python 셀도 실행하지 않았다. 커밋·배포는 수행하지 않았다.

- 사용자가 Orange3의 Impute 세 분기와 Outliers 전체 Data 출력을 확인한다.
- Colab 셀 1~12 순차 실행과 폰트, 수치·학교/날짜 변경을 확인한다.
- 일반 화면 앵커·목차, 발표 29개/S 포함 31개, 좁은 화면의 표·코드 스크롤을 확인한다.
- 생성기를 로컬 실행하고 README의 결과 기준을 대조한 뒤 수업 후 참고 영역에 링크를 추가한다.
- 5주차 본문은 사용자 진행 지시 후 작성한다. 메뉴 결과의 행 단위와 구체 컬럼은 그때 확정한다.

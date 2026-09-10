# 9주차 작성·정적 검증 — 2026-09-10

## 승인과 변경 범위

사용자가 8주차 완료를 확인하고 9주차 25~27차시 상관분석·인과 구별·회귀 개념 작성과 ready 전환을 지시했다. 입력은 기존 bike-daily-clean.csv, 관련 교재 p.95 (Ⅱ-2-3)·p.107 (Ⅲ-1-1)이다. 시작 Git 상태는 깨끗했다.

| 파일 | 변경 |
|---|---|
| week-09/index.html | 세 차시 본문·Orange3 안내·Colab 코드 10셀·결과 비교 |
| data/site.js | week-09 ready, 정제본 표시·세 학습목표 |
| docs/CURRICULUM.md | 확정 수업 구성·실측 상관·인과/회귀 범위·상태 |
| data/README.md | 정제본 9주차 사용·계산 범위·상관계수·활동값 구별 |
| docs/workflow-state.md, 이 문서 | 승인·검증·미실행·보호 해시 |

공통 자산·강사 정보·기존 주차·수집기·CSV를 변경하지 않았다. 원본·교재 이미지·문장을 사용하거나 새 실습 데이터 파일을 만들지 않았다. 커밋·푸시·배포는 수행하지 않았다.

## 읽기 전용 계산

스프레드시트 스킬의 읽기 전용 분석 지침을 적용했다. PowerShell Import-Csv로 실제 bike-daily-clean.csv를 읽고 JavaScript로 계산했다. 워크북/CSV를 작성하거나 Python/pandas가 실행된 것으로 보고하지 않는다.

- 입력 353행 × 8열, 2024-03-01~2025-02-16. 다섯 분석 컬럼의 빈 값/비수치 값 0개.
- 평균기온·최고기온·최저기온·강수량·대여건수만 사용하며 모든 쌍의 관측 수가 353이다. 강수량은 4주차 정제 결과로 계산한다.
- Pearson 계산 1: 중심화한 편차의 곱 합을 각 편차 제곱합의 기하평균으로 나눈다.
- 독립 대조 계산 2: 원자료의 합·제곱합·곱 합과 n을 사용하는 Pearson 식으로 계산했다. 7쌍의 최대 차이는 4.440892098500626e-15, 소수 넷째 자리 표시값 불일치 0개다.

| 변수 쌍 | 계산값 (소수 12자리) | 페이지 표시 |
|---|---:|---:|
| 평균기온–대여건수 | 0.616984970704 | 0.6170 |
| 최고기온–대여건수 | 0.671238771677 | 0.6712 |
| 최저기온–대여건수 | 0.555449301744 | 0.5554 |
| 강수량–대여건수 | -0.293127518126 | -0.2931 |
| 평균기온–최고기온 | 0.988919195474 | 0.9889 |
| 평균기온–최저기온 | 0.989810760802 | 0.9898 |
| 최고기온–최저기온 | 0.961280738848 | 0.9613 |

계수의 부호와 절댓값을 구별하며 r를 증가율·정확도·인과 효과로 읽지 않는다. 기온끼리 높은 상관은 정보가 많이 겹친다는 관찰로 설명한다.

## 실제 사례와 활동값

| 확인 항목 | 결과 |
|---|---|
| 평균기온 20~21°C 조건 | 16일 |
| 2024-06-01 | 토, 평균기온 20.7°C, 강수량 0mm, 대여 167881건 |
| 2024-06-08 | 토, 평균기온 20.3°C, 강수량 16.9mm, 대여 108164건 |
| 2024년 8월 | 31일, 평균기온–대여건수 r=−0.23372377900939986 |
| 전체 같은 쌍 | 353일, r=0.6169849707039784 |
| 회귀 도입 실제 날짜 2025-01-10 | 평균기온 −7.3°C, 대여 54566건 |
| 회귀 도입 실제 날짜 2024-06-01 | 평균기온 20.7°C, 대여 167881건 |

기간별 비교는 인과 효과의 분리나 증명이 아니다. 반례는 “기온이 높으면 언제나 대여가 더 많다”는 주장과 대조하며, 기온의 인과 영향 자체가 없음을 증명한다고 설명하지 않는다. 아이스크림·익사 사례는 생각 실험이며 숫자나 별도 데이터셋을 추가하지 않았다.

학생이 고치는 기본 예측값은 위 실제 두 날짜 순으로 50000·150000건이다. 자동으로 학습한 값이 아니며 노트북 사본에만 둔다. 실제−예측 오차는 4566·17881건, 대체 예측 60000·180000건에서는 −5434·−12119건이다. 코드는 두 기온 사이의 선분과 두 날짜의 세로 차이를 표시한다. 두 날만 잘 맞는 것을 나머지 351일의 적합성으로 일반화하지 않는다.

## 도구·코드 검토

- 세 차시는 질문→Orange3→개념→Python→비교 순서다. 25차시 Correlations는 다섯 Numeric Features, Target 없음, Pearson 설정을 명시하고 Data/Features 출력을 Scatter Plot으로 연결한다.
- 26차시 Select Rows의 평균기온 20~21°C 조건과 날짜 2024-08-01~08-31 조건을 각각 Python으로 재현한다. 월 조건은 이 파일에 각 월이 한 번씩만 있는 기간 안에서 사용한다.
- 27차시는 손으로 그린 직선·입력·예측·실제·오차 개념에 한정한다. 자동 학습/추정 호출, 회귀 계수 해석, 다중회귀, MSE, R²는 페이지와 코드에 없다. 모델 학습 방법은 10주차에 남긴다.
- Colab 코드는 자체 작성 개념 예제다. 별도 정본 스크립트는 없으며 컬럼·변수 의존 순서·날짜 조회·계산 근거·차트 표시를 소스로 검토했다. Python 실행 통과로 처리하지 않는다.
- 모든 코드는 pre[data-code]이며 HTML 엔티티를 복원해 검사했다. 한글 폰트는 koreanize-matplotlib 표준 설치/import를 적용했다. 그림 2개에 한글 제목·축·단위, 직선/점/오차 구별 범례를 넣었다.

기능 확인 출처:

- [Orange3 Correlations](https://orangedatamining.com/widget-catalog/unsupervised/correlations/): Pearson/Spearman, 수치 Features, 선택 쌍과 Data/Features 출력.
- [Orange3 Scatter Plot](https://orangedatamining.com/widget-catalog/visualize/scatterplot/): 축·색·범례·Jittering과 선택 데이터 출력. 회귀선 자동 표시는 끄도록 안내했다.
- [pandas DataFrame.corr](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html): 기본 Pearson, 쌍별 유효 관측과 수치 컬럼 선택. 이번 자료는 선택 컬럼에 결측이 없다.

공식 문서의 예제 데이터·이미지는 수업에 넣지 않았다.

## 검증 결과

| ID | 상태 | 근거·제한 |
|---|---|---|
| C01 | 통과 | node --check data/site.js, git diff --check, 보호/기존 주차/CSV 해시 19/19 일치. 다른 14개 level·instructor 동일. |
| C02 | 통과 | 이번 공개 변경에 학생 개인정보·인증키 없음. source/·work-temp/ ignore 매칭과 추적 0개 확인. |
| C03 | 통과 — 정적 | 자체 작성 개념 코드 10셀·최대 9줄. 실제 데이터·두 상관 계산·조건별 일수·오차·코드 의존 순서 대조. Python 실행 미실행. |
| C04 | 미실행 | 실제 복사 버튼·클립보드 검사 가능한 브라우저 없음. |
| C05 | 미실행 | 실제 발표 순회 불가. 소스는 기본 33개/S 포함 34개, 중첩 0건. |
| C06 | 미실행 | 1920×950 presentation-viewport 넘침 실측 불가. |
| C07 | 미실행 | 실제 표시 배율·본문/코드 크기·발표 종료 복원 검사 불가. |
| C08 | 미실행 | 라이트/다크 computed 색 대비 측정 불가. |
| C09 | 미실행 | 375×812 두 테마 화면 확인 불가. 기존 표 스크롤·코드 스타일 사용. |
| C10 | 미실행 | HTTP/file 브라우저 이동 미실행. 홈+15주차 태그·ID/ARIA·내부 파일/앵커 정적 오류 0건. |
| C11 | 미실행 | 실제 콘솔·네트워크 검사 불가. 새 JS·CDN·fetch 추가 없음. |
| C12 | 미실행 | 모션 감소 실제 에뮬레이션 불가. |
| C13 | 미실행 | 다운로드 클릭 후 바이트 대조 불가. 로컬 파일 존재·해시 확인. |
| C14 | 미실행 | 공통 메뉴·모달·현재 위치·진도 실제 UI 조작 불가. 공통 파일 동일. |
| C15 | 미실행 | 주차 선택·이전/다음 조작 불가. 1~9 ready·10~15 coming; 9주차 이전은 8주차, 다음 없음. |

9주차는 7섹션(objectives, materials, lesson-1, lesson-2, lesson-3, assignment, references)·32 ID다. 3개 차시 단계 순서와 HTML·SITE·CURRICULUM의 목표 일치를 확인했다. 보충 발표 조각은 ‘공식 도구 문서’ 하나다.

현재 CUA 상태는 apps=[]·browsers=[]이다. PATH에 Python이 없고 앞서 지정한 실행 경로도 접근이 거부된 환경이다. Python/Colab 실행·설치·실제 Orange3/UI 검증은 수행하지 않았다. 상관계수 계산과 소스 검토를 코드 실행·화면 검증과 구별한다.

## 보호 SHA-256

| 파일 | 시작·종료 동일 해시 |
|---|---|
| assets/js/shared.js | E74FACE44F5B81E6A96CFA500CA616A089975EB85EF5EF985CE05DB182D75569 |
| assets/css/base.css | 2B1D4CFCF12DC00C9A65A288D106BB1F6E9C75AB14D900CA24095738B35B25CB |
| assets/css/tokens.css | 6C3EEDE764AE1875570731BA175D569DA58030C7FDA96669FCED3FE36DEB8590 |
| DESIGN.md | C473FCA5C871CAB360DAE65320E6A38189D7E987857CC53700C69E9606A40100 |
| assets/js/widgets.js | 9106FC437726C110AD8AD1BA15F3EC714F6E1412B4D234E33EEB078BFD6B5046 |
| assets/css/lecture.css | FBE43EB60DBA45C4E36E6428E5F3E06609073705097B137E681DB55C4C58C39D |
| week-01/index.html | 69412065CBC9696A4C4BD89F47AB668A3D317A1F1AAAE38C2994F2B543F0D4FD |
| week-02/index.html | 68ED59C0C937D3CAE475F5DCDC646D4783B806F18A27B70E64EFADDCBFB9AC4E |
| week-03/index.html | F46A724D26F100D7AE7D0165E10565ECCB13F654103D22D14BA3B41E2A7F8F40 |
| week-04/index.html | 683630EAE31B86AD5DB1E7BFC0856992767E4BC92BCD6E0DC0AABECEAE727CAD |
| week-05/index.html | A73B8F599256EBA66D90C4CBF3A22FF0C269DC834F698C608CB1C2599719E58D |
| week-06/index.html | E9383B172F00C69C3D173D3B912A0F119C19FDAC74DC837BC2F75F9C14B51492 |
| week-07/index.html | 41FA6FAE4AE7A86A370A46DE810B5EE97AC0A7D24A4A6D25B90406E66375F4DD |
| week-08/index.html | E3F758F15DF8D7E6C02EFE776856B97B96A880DC56C01873AE0E184BDDCA7298 |
| data/weather-bike/bike-daily.csv | 4F3E86DC8F2D39D924DE4B5DD42AE1669AC214FBBA576D1F9984E6860344B3DC |
| data/weather-bike/bike-daily-clean.csv | 0F427AF3C01E0E6749141F9350AA36EA7D2A535D200250C2D0A052937CC32897 |
| data/neis/meals.csv | 74D2A209A4DEC8B8BD8017BB7E25B102637FBB582A4721C08E4CFCC84FF47C75 |
| data/neis/schools.csv | 6D83C06A150A534EF912D86688F18593F0A65ACD783974F837C030BF663731D8 |
| data/neis/meals-parsed.csv | 843FD66777C7FDFCF46A51BE54B030B998244A100DD5F63A11914E06AFE627C5 |

## 남은 검증과 다음 범위

- W09-PY: 사용자 Colab에서 셀 1~10 순서 실행, shape·7쌍의 상관·20~21°C의 16일·8월 31일간 자료·직선 후보·오차·한글 표시를 확인한다.
- W09-UI: Orange3의 Pearson·Features·선택 조건과 산점도를 대조한다. 홈 ready 카드·8↔9 이동·9주차 다음 없음, 발표 33/34조각·모바일·복사·다운로드를 실제 브라우저에서 확인한다.
- 10주차는 사용자 진행 지시 후 작성한다.

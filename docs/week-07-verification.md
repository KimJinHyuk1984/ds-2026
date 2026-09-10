# 7주차 작성·정적 검증 — 2026-09-10

## 승인과 작성

사용자가 6주차 완료와 7주차 작성을 지시했다. 4주차 정제 파일을 기본으로 사용하고, 추론통계는 모집단·표본·반복 표본 통계량 비교까지로 확정했다. 페이지에 신뢰구간·표준오차·가설검정을 넣지 않는다.

| 파일 | 변경 |
|---|---|
| week-07/index.html | 19~21차시 본문·Orange3 안내·완성 Python 코드·학습 기록 |
| data/site.js | week-07 ready, 정제본 데이터 표시와 세 목표 |
| docs/CURRICULUM.md | 7주차 미확정 제안 해소와 확정 수업·통계 기준 |
| data/README.md | 정제본의 7주차 사용·실측 통계량·표본 실습 범위 |
| docs/workflow-state.md, 이 문서 | 승인·검증·미실행·보호 해시 |

시작 Git 상태는 깨끗했다. CSV·수집기·기존 주차·공통 CSS/JS·강사 정보는 변경하지 않았다. 학생용 새 데이터 파일이나 교재 이미지·문장을 추가하지 않았다. 커밋·푸시·배포는 수행하지 않았다.

## 입력과 계산 확인

기존 UTF-8 BOM CSV를 PowerShell Import-Csv로 읽었고, JavaScript로 평균·중앙값·표준편차·기간별 집계도 독립 대조했다. 스프레드시트 스킬은 읽기 전용 데이터 확인에 적용했으며 워크북·CSV를 작성하거나 변환 저장하지 않았다. 아래는 Python/Colab 실행 결과가 아니다.

| 항목 | 확인한 값 |
|---|---|
| 입력 | bike-daily-clean.csv, 353행 × 8열, 모든 컬럼 빈 값 0개 |
| 기간 | 2024-03-01~2025-02-16 |
| 대여건수 평균 | 119,927.78186968839건 → 119,928건 표시 |
| 중앙값 | 126,749건 |
| 표준편차 n−1 기준 | 49,525.53445676132건 → 49,526건 표시 |
| 분산 n−1 기준 | 2,452,778,563.227853건² |
| 표준편차 n 기준 | 49,455.335223097085건 |
| 표준편차 / 평균 | 약 41.3% |
| 최빈값 해석 | 대여건수는 353개 모두 다름; 요일은 금·토·일 각 51개 |
| 겨울(12~2월) | 78일 평균 61,294.294871794875건 |
| 그 외 기간 | 275일 평균 136,558.3709090909건 |
| 2025년 1월 표준편차 | 20,963.542052401252건 (31일, n−1 기준) |
| 2024년 5월 표준편차 | 54,670.78543456512건 (31일, n−1 기준) |
| 월별 예외 | 11개월은 전체보다 작지만 2024년 5월은 더 큼 |
| 5월 범위 | 14,293~193,336건 |
| 강수량 처리 후 평균 | 3.5198300283286112mm → 3.52mm 표시 |

겨울 값들이 전체 평균을 낮추는 근거를 제시하되 최저일 2024-05-05를 함께 확인한다. 계절만으로 모든 저조일의 원인을 확정하지 않는다. 강수량 8.12mm는 결측을 제외한 153개 기록, 3.52mm는 0 처리 후 353일을 대상으로 한 평균이다.

## 내용·코드 검토

- 19차시: Feature Statistics(버전에 따라 Column Statistics), Box Plot과 겨울 Select Rows로 확인한 뒤 대표값·분산·표준편차에 이름을 붙이고 describe·mode·var·std·기간별 집계로 재현한다.
- 20차시: 전체와 한 달의 Box Plot·Distributions를 비교하고 groupby().describe와 두 종류의 그래프를 제공한다. 날짜 범위·일수·구간 폭을 맞추고 월별 표준편차가 항상 작아지는 것은 아니라는 관찰을 담았다.
- 21차시: 월별 필터를 거치지 않은 353행을 모집단으로 사용한다. Data Sampler는 Fixed sample size, 중복·Replicable·Stratify 해제, Data Sample 출력으로 연결한다.
- Python 첫 표본 셀은 다시 실행할 때 새 표본을 뽑는다. 크기별 반복 코드는 n=30/100/200, repeats=100이며 반복마다 random_state가 달라진다. seed_start를 유지하면 재현하고 바꾸면 새 실험을 비교한다.
- 반복 평균의 평균·최솟값·최댓값과 박스플롯을 비교하며 표준오차를 계산하지 않는다. 그림의 값이 하루 대여건수가 아니라 표본 평균임을 명시한다. 표본 크기와 반복 횟수를 구별한다.
- 한 번의 큰 표본이 언제나 더 가까운 것은 아니며, 모집단은 이 파일의 353일로 한정한다. 미래 날짜까지의 자동 일반화는 하지 않는다.
- 한글 폰트 셀은 koreanize-matplotlib 설치와 import뿐이다. 설치 순서, import 유지, 재시작 불필요, 새 런타임 재설치를 명시했다.
- 코드는 Colab용 자체 작성 예제다. 독립 배포 스크립트 정본은 없으며 입력 URL·컬럼·의존 순서·수치 해석을 소스로 검토했다. 실행 통과로 표시하지 않는다.

## 도구 설명 확인 근거

- [Orange3 Feature Statistics / Column Statistics](https://orangedatamining.com/widget-catalog/data/featurestatistics/): 최신 표시 이름과 Mean·Mode·Dispersion의 의미. Dispersion을 분산으로 안내하지 않는다.
- [Orange3 Box Plot](https://orangedatamining.com/widget-catalog/visualize/boxplot/)과 [공식 구현](https://raw.githubusercontent.com/biolab/orange3/master/Orange/widgets/visualize/owboxplot.py): BoxData의 np.nanvar와 제곱근으로 n 기준 표준편차를 확인했다.
- [Orange3 Distributions](https://orangedatamining.com/widget-catalog/visualize/distributions/): Bin width와 히스토그램 안내. [Select Rows 공식 구현](https://raw.githubusercontent.com/biolab/orange3/master/Orange/widgets/data/owselectrows.py)에서 TimeVariable의 기간 조건 지원을 확인했다.
- [Orange3 Data Sampler](https://orangedatamining.com/widget-catalog/transform/datasampler/): Fixed sample size, Sample with replacement, Replicable sampling, Data Sample 출력과 Sample Data 버튼.
- [pandas describe](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html), [std](https://pandas.pydata.org/docs/reference/api/pandas.Series.std.html), [sample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sample.html): 기본 통계·ddof=1/0·중복 없는 추출과 random_state 의미.

자료는 도구 동작 확인에만 사용했고 문서의 예제 데이터·이미지는 수업에 넣지 않았다. 로컬 Orange3 설치 버전의 실제 UI는 미확인이다.

## 정적 검증과 미실행

| ID | 상태 | 근거·제한 |
|---|---|---|
| C01 | 통과 | node --check data/site.js, git diff --check, 보호 해시 17/17 일치. 다른 14개 level·instructor 동일. |
| C02 | 통과 | 공개 변경에 학생 개인정보·인증키 없음. source/·work-temp/ 추적 0개와 ignore 매칭 확인. |
| C03 | 통과 — 정적 | 자체 작성 Colab 코드 13개: 본편 12/보충 1, 최대 10줄. 실측 입력·변수 순서·계산 기준 대조. Python 실행은 미실행. |
| C04 | 미실행 | 실제 복사 버튼·클립보드 검사 가능한 브라우저 없음. |
| C05 | 미실행 | 실제 발표 순회 불가. 소스 집계는 기본 36개/S 포함 38개. |
| C06 | 미실행 | 1920×950 presentation-viewport 넘침 실측 불가. |
| C07 | 미실행 | 실제 본문·코드 크기·발표 종료 복원 검사 불가. |
| C08 | 미실행 | 라이트/다크 computed 색 대비 측정 불가. |
| C09 | 미실행 | 375×812 두 테마 화면 확인 불가. 기존 표 스크롤·코드 스타일 재사용. |
| C10 | 미실행 | HTTP/file 실제 브라우저 이동 미실행. 홈+15주차 태그·ID/ARIA·로컬 파일/앵커 정적 오류 0건. |
| C11 | 미실행 | 콘솔·네트워크 검사 불가. 새 JS·CDN·fetch 추가 없음. |
| C12 | 미실행 | 실제 모션 감소 에뮬레이션 불가. |
| C13 | 미실행 | 다운로드 클릭 후 바이트 대조 불가. 로컬 파일 존재·해시 확인. |
| C14 | 미실행 | 공통 메뉴·모달·현재 위치·진도 조작 불가. 공통 파일 동일. |
| C15 | 미실행 | 주차 선택·이전/다음 실제 UI 조작 불가. 상태는 1~7 ready·8~15 coming, 7주차 이전은 6주차/다음 없음. |

7주차는 7섹션(objectives, materials, lesson-1, lesson-2, lesson-3, assignment, references), 32개 ID다. 각 차시의 question→orange→concept→python→compare 순서와 HTML·SITE·CURRICULUM의 세 목표 일치를 확인했다. 보충 발표 조각은 ‘도구 비교 보충 · 표준편차의 계산 기준’과 ‘공식 도구 문서’다.

지정 Python 실행 경로 접근이 거부되었고 PATH에 Python이 없다. 생성기·Python/Colab 셀 실행은 수행하지 않았다. CUA 상태는 apps=[]·browsers=[]여서 실제 Orange3·Colab·페이지 UI 검증은 남아 있다. 전체 브라우저 검증을 통과했다고 판정하지 않는다.

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
| data/weather-bike/bike-daily.csv | 4F3E86DC8F2D39D924DE4B5DD42AE1669AC214FBBA576D1F9984E6860344B3DC |
| data/weather-bike/bike-daily-clean.csv | 0F427AF3C01E0E6749141F9350AA36EA7D2A535D200250C2D0A052937CC32897 |
| data/neis/meals.csv | 74D2A209A4DEC8B8BD8017BB7E25B102637FBB582A4721C08E4CFCC84FF47C75 |
| data/neis/schools.csv | 6D83C06A150A534EF912D86688F18593F0A65ACD783974F837C030BF663731D8 |
| data/neis/meals-parsed.csv | 843FD66777C7FDFCF46A51BE54B030B998244A100DD5F63A11914E06AFE627C5 |

## 다음 확인

사용자가 Orange3의 통계 위젯 명칭과 셀 1~12·보충 셀을 확인하고, 월별 예외·반복 표본 평균 그림·발표·모바일·복사·다운로드·주차 이동을 검증한다. 8주차는 별도 지시 후 작성한다.

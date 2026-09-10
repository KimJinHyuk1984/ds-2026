# 8주차 작성·정적 검증 — 2026-09-10

## 승인과 변경 범위

사용자가 7주차 완료를 확인하고 8주차 22~24차시 데이터 시각화 작성과 ready 전환을 지시했다. 입력은 기존 bike-daily-clean.csv, 교재는 관련 교재 p.88 (Ⅱ-2-2) 참조다. 시작 Git 상태는 깨끗했다.

| 파일 | 변경 |
|---|---|
| week-08/index.html | 분포·관계·그래프 선택·축 절단·색/크기 활동, 완성 Colab 코드 10셀 |
| data/site.js | week-08 ready, 정제본 표시와 세 학습목표 |
| docs/CURRICULUM.md | 8주차 입력·목표·세 차시·시각화 품질 기준과 상태 |
| data/README.md | 같은 정제본의 8주차 사용, 분포·요일별 평균 검산 근거 |
| docs/workflow-state.md, 이 문서 | 승인·검증·미실행·보호 해시 기록 |

공통 CSS/JS·강사 정보·기존 주차·CSV·수집기를 변경하지 않았다. 교재 문장·이미지를 사용하거나 새 데이터 파일을 만들지 않았다. 커밋·푸시·배포는 수행하지 않았다.

## 내용과 수치 대조

- 세 차시 모두 질문→Orange3→개념→Python→비교 순서다. 22차시는 7주차 요약값을 그림으로 재확인하고, 23차시는 1주차 산점도를 경향·퍼짐·예외·한계로 설명하며, 24차시는 변수의 유형/개수와 질문에 맞는 표현을 선택한다.
- 7주차에 읽기 전용으로 확인한 353행 데이터를 재사용해 JavaScript로 추가 집계했다. 현재 CSV 해시가 그 입력과 동일함을 확인했다. 이는 Python/Colab 셀 실행 결과가 아니다.
- 대여건수 평균 119,927.78186968839건, 중앙값 126,749건, pandas 기본 n−1 기준 표준편차 49,525.53445676132건이다. 페이지는 각각 119,928 / 126,749 / 49,526으로 표시한다.
- 히스토그램 너비 5000·10000·20000 모두 353개 값을 빠짐없이 포함한다. 1만 건 구간의 18만 이상 19만 미만에는 35일이 있다. 좌우 비대칭과 적은 값 쪽 꼬리를 관찰하되 평균/중앙값 관계만으로 전체 모양을 단정하지 않는다.
- 강수량 0은 251일이고 실제 범위는 0~128.8mm다. 산점도의 점 겹침과 색 범위 설정에 사용한다. 진하기가 날짜 수와 정확히 비례한다고 안내하지 않는다.
- 요일별 산점도는 353일을 모두 표시한다. 축 절단용 막대는 아래 평균 7개를 사용한다.

| 요일 | 날짜 수 | 평균 대여건수(건, 소수 둘째 자리 표시) |
|---|---:|---:|
| 월 | 50 | 127129.94 |
| 화 | 50 | 123569.42 |
| 수 | 50 | 126836.26 |
| 목 | 50 | 129076.56 |
| 금 | 51 | 131410.57 |
| 토 | 51 | 104281.94 |
| 일 | 51 | 97717.25 |

요일 평균을 한 번만 계산해 같은 값·색·제목·그림 크기로 표시하며 y축만 0~140000 / 90000~140000으로 바꾼다. 모든 막대 윗부분은 두 범위 안에 있다. 오른쪽의 0 기준 부분 절단을 오해 분석 활동으로 명시했다. Orange3의 영역 확대는 이 y축만의 통제 비교와 구별했다.

모든 그래프 셀에 제목·축 이름이 있고 수치 축에 단위를 넣었다. 평균/중앙값은 범례, 강수량 색은 단위 있는 컬러바를 제공한다. 요일은 범주로 표시하며 범주 사이 기울기로 해석하지 않는다. 크기에 변수를 담는 경우 면적·범례·겹침·0 값 소실을 확인하도록 안내했다. 한글 폰트는 koreanize-matplotlib 설치/import 한 셀이다.

## 도구 설명 근거

- [Orange3 Distributions](https://orangedatamining.com/widget-catalog/visualize/distributions/), [Box Plot](https://orangedatamining.com/widget-catalog/visualize/boxplot/): 기존 수업과 같은 분포 위젯 설정을 사용한다.
- [Orange3 Scatter Plot](https://orangedatamining.com/widget-catalog/visualize/scatterplot/): 축·색·크기·투명도·Jittering·범례·확대/복구 기능을 확인했다.
- [matplotlib hist](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hist.html): 구간 경계·빈도 표시.
- [matplotlib boxplot](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.boxplot.html): 기본 IQR 수염·showmeans·반환한 평균/중앙값 객체를 범례에 사용한다.
- [matplotlib scatter](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html): s의 면적 단위, 색·투명도·컬러맵 설정.

공식 문서는 기능 확인용이며 문서의 예제 데이터·이미지는 수업에 넣지 않았다. 실제 설치 버전의 Orange3 UI와 Colab 실행은 미확인이다.

## 검증 결과

| ID | 상태 | 근거·제한 |
|---|---|---|
| C01 | 통과 | node --check data/site.js, git diff --check, 보호/기존 주차/CSV 해시 18/18 일치. 다른 14개 level·instructor 동일. |
| C02 | 통과 | 이번 공개 변경에 학생 개인정보·인증키 없음. source/·work-temp/ ignore 매칭 및 추적 0개 확인. |
| C03 | 통과 — 정적 | 자체 작성 Colab 예제 10개, 최대 11줄. 입력 URL·컬럼·셀 순서·그래프 제목/축/범례와 수치 근거를 소스로 대조. 독립 스크립트 정본은 없으며 Python 실행은 미실행. |
| C04 | 미실행 | 실제 복사 버튼·클립보드 검사 가능한 브라우저 없음. |
| C05 | 미실행 | 발표 순회 불가. 소스 집계는 기본 32개/S 포함 33개, 중첩 0건. |
| C06 | 미실행 | 1920×950 presentation-viewport 넘침 실측 불가. |
| C07 | 미실행 | 실제 표시 배율·본문/코드 크기·발표 종료 복원 검사 불가. |
| C08 | 미실행 | 라이트/다크 computed 색 대비 측정 불가. |
| C09 | 미실행 | 375×812 두 테마 화면 확인 불가. 기존 표 스크롤·코드 스타일 재사용. |
| C10 | 미실행 | HTTP/file 브라우저 이동 미실행. 홈+15주차 태그·ID/ARIA·로컬 파일/앵커 정적 오류 0건. |
| C11 | 미실행 | 콘솔·네트워크 검사 불가. 새 JS·CDN·fetch 추가 없음. |
| C12 | 미실행 | 실제 모션 감소 에뮬레이션 불가. |
| C13 | 미실행 | 다운로드 클릭 후 바이트 대조 불가. 로컬 파일 존재·해시 확인. |
| C14 | 미실행 | 공통 메뉴·모달·현재 위치·진도 UI 조작 불가. 공통 파일 동일. |
| C15 | 미실행 | 주차 선택·이전/다음 실제 조작 불가. 상태는 1~8 ready·9~15 coming; 8주차 이전은 7주차, 다음 없음. |

8주차는 7섹션(objectives, materials, lesson-1, lesson-2, lesson-3, assignment, references)·32 ID다. 3개 차시의 단계 순서와 HTML·SITE·CURRICULUM의 목표 일치를 확인했다. 그래프 셀 7개에서 총 8개 그래프 영역을 만들도록 작성했다. 보충 발표 조각은 ‘공식 도구 문서’ 하나다.

현재 CUA는 apps=[]·browsers=[]이다. PATH에 Python이 없고 앞서 지정된 실행 파일도 접근이 거부되어 Python/Colab 실행·패키지 설치를 하지 않았다. 정적 검사 통과를 실제 UI·코드 실행 통과로 판정하지 않는다.

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
| data/weather-bike/bike-daily.csv | 4F3E86DC8F2D39D924DE4B5DD42AE1669AC214FBBA576D1F9984E6860344B3DC |
| data/weather-bike/bike-daily-clean.csv | 0F427AF3C01E0E6749141F9350AA36EA7D2A535D200250C2D0A052937CC32897 |
| data/neis/meals.csv | 74D2A209A4DEC8B8BD8017BB7E25B102637FBB582A4721C08E4CFCC84FF47C75 |
| data/neis/schools.csv | 6D83C06A150A534EF912D86688F18593F0A65ACD783974F837C030BF663731D8 |
| data/neis/meals-parsed.csv | 843FD66777C7FDFCF46A51BE54B030B998244A100DD5F63A11914E06AFE627C5 |

## 남은 검증과 다음 범위

- W08-PY: 사용자 Colab에서 셀 1~10 순서 실행, (353, 8)과 그래프 8개 영역·한글·범례 확인. 히스토그램 너비·투명도·축 하한·점 크기 변경 활동을 실행한다.
- W08-UI: Orange3 분포·산점도 설정과 비교, 학기 홈 ready 카드·7↔8 이동·8주차 다음 없음, 발표 32/33조각·모바일·복사·다운로드를 실제 브라우저에서 확인한다.
- 9주차는 사용자 진행 지시 후 작성한다.

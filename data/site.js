/* ★ 공통 관리 파일: instructor는 템플릿 원본에서만 수정해 모든 강의에 반영합니다.
 * site, levels와 otherLectures는 각 강의 저장소에서 수정합니다.
 * 동기화 스크립트는 이 파일을 덮어쓰지 않습니다. instructor 변경은 수동으로 병합합니다.
 */
window.SITE = {
  site: {
    title: "데이터 과학",
    subtitle: "고등학교 데이터 과학 · 주 3차시 × 15주 · 총 45차시 · Orange3와 Python으로 함께 배우는 한 학기",
    repo: "ds-2026" // 진행 기록을 구분하는 이름. 복제한 저장소 이름으로 변경합니다.
  },
  // ── 이 아래 instructor 블록은 모든 강의 저장소에서 동일하게 유지한다 ──
  instructor: {
    name: "김진혁",
    affiliation: "동양고등학교 · 수학, 정보",
    email: "kimjh0630@naver.com",
    photo: "assets/img/instructor.jpg",
    credentials: [
      "동양고등학교 교사(수학, 정보)",
      "성균관대학교 일반대학원 수학교육전공 박사 수료",
      "서울시교육청 초중등 AI교육 연구회 부회장",
      "(2022개정 교육과정) 『데이터 과학』 교과서 집필진(올드앤뉴)",
      "(2022개정 교육과정) 『논리와 사고』 교과서 집필진(세종)",
      "AIEDAP마스터 교원(서울, 경기, 인천, 제주 권역)",
      "서울시교육청 AI융합교육 선도교사(2023~)",
      "2026학년도 서울시교육청 AI중점학교 지원단",
      "『인공지능 진로진학 교육자료』 집필진(서울시교육청, 2022)",
      "『면접보고 대학가자』 집필진(올드앤뉴, 2023)"
    ]
  },

  // CURRICULUM.md의 15주 구조를 반영합니다. 폴더명과 body[data-level]은 slug와 같습니다.
  // textbook은 사용자 지정 인쇄 쪽수이며 범위를 추정하지 않습니다.
  // 본문을 완성한 주차만 ready로 전환합니다. 나머지는 coming 안내 페이지를 유지합니다.
  levels: [
    {
      "slug": "week-01",
      "week": 1,
      "badge": "1주차",
      "title": "오리엔테이션과 Orange3·Colab 시작",
      "subtitle": "1–3차시",
      "kicker": "1주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "따릉이 일별 대여 건수 CSV"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "ready",
      "lessons": "1–3차시",
      "dataName": "따릉이 일별 대여 건수 CSV",
      "textbook": [
        {
          "unit": "Ⅰ-1-1",
          "page": 11
        }
      ],
      "objectives": [
        "Orange3와 Google Colab을 함께 열어 실습을 시작할 수 있다.",
        "따릉이 일별 대여 건수 CSV를 두 도구에서 불러와 같은 데이터를 확인할 수 있다.",
        "기본 워크플로우를 실행하며 데이터 과학의 활동을 살펴볼 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-02",
      "week": 2,
      "badge": "2주차",
      "title": "데이터의 형태·속성과 NEIS 데이터 수집",
      "subtitle": "4–6차시",
      "kicker": "2주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "NEIS 학교기본정보·급식식단정보"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "4–6차시",
      "dataName": "NEIS 학교기본정보·급식식단정보",
      "textbook": [
        {
          "unit": "Ⅰ-1-2",
          "page": 16
        },
        {
          "unit": "Ⅱ-1-1",
          "page": 59
        }
      ],
      "objectives": [
        "데이터의 형태와 속성을 구분하고 수집 방법을 설명할 수 있다.",
        "Python으로 NEIS API를 호출하고 응답을 데이터프레임으로 구성할 수 있다.",
        "수집한 데이터를 Orange3와 Python에서 확인할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-03",
      "week": 3,
      "badge": "3주차",
      "title": "빅데이터·데이터베이스와 데이터 통합",
      "subtitle": "7–9차시",
      "kicker": "3주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "NEIS + 기상"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "7–9차시",
      "dataName": "NEIS + 기상",
      "textbook": [
        {
          "unit": "Ⅰ-2-1",
          "page": 23
        },
        {
          "unit": "Ⅰ-2-2",
          "page": 29
        }
      ],
      "objectives": [
        "빅데이터·데이터베이스·데이터셋의 의미를 설명할 수 있다.",
        "Orange3의 Merge Data·Concatenate와 Python의 merge·concat으로 데이터를 통합할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-04",
      "week": 4,
      "badge": "4주차",
      "title": "결측치·이상치 탐지와 처리",
      "subtitle": "10–12차시",
      "kicker": "4주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "기상·따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "10–12차시",
      "dataName": "기상·따릉이",
      "textbook": [
        {
          "unit": "Ⅱ-1-2",
          "page": 67
        }
      ],
      "objectives": [
        "기상·따릉이 데이터에서 결측치와 이상치를 찾아낼 수 있다.",
        "Orange3와 Python으로 결측치·이상치를 처리하고 결과를 비교할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-05",
      "week": 5,
      "badge": "5주차",
      "title": "정규화·파생변수와 데이터 편향",
      "subtitle": "13–15차시",
      "kicker": "5주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "기상·따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "13–15차시",
      "dataName": "기상·따릉이",
      "textbook": [
        {
          "unit": "Ⅱ-1-2",
          "page": 67
        }
      ],
      "objectives": [
        "Orange3와 Python으로 데이터를 정규화하고 파생변수를 만들 수 있다.",
        "전처리 과정에서 데이터 편향을 살펴보고 결과에 미치는 영향을 설명할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-06",
      "week": 6,
      "badge": "6주차",
      "title": "미니 프로젝트 1 — 전처리 보고서",
      "subtitle": "16–18차시",
      "kicker": "6주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "기상·따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "16–18차시",
      "dataName": "기상·따릉이",
      "textbook": [],
      "objectives": [
        "기상·따릉이 데이터의 전처리 방법을 선택하고 적용할 수 있다.",
        "전처리 과정과 결과를 근거와 함께 보고서로 정리할 수 있다."
      ],
      "compressible": true
    },
    {
      "slug": "week-07",
      "week": 7,
      "badge": "7주차",
      "title": "기술통계와 추론통계",
      "subtitle": "19–21차시",
      "kicker": "7주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "19–21차시",
      "dataName": "따릉이",
      "textbook": [
        {
          "unit": "Ⅱ-2-1",
          "page": 82
        }
      ],
      "objectives": [
        "기술통계와 추론통계의 역할을 구분할 수 있다.",
        "Orange3와 Python으로 따릉이 데이터의 통계량을 구하고 해석할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-08",
      "week": 8,
      "badge": "8주차",
      "title": "데이터 시각화 — 분포·산점도·박스플롯",
      "subtitle": "22–24차시",
      "kicker": "8주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "22–24차시",
      "dataName": "따릉이",
      "textbook": [
        {
          "unit": "Ⅱ-2-2",
          "page": 88
        }
      ],
      "objectives": [
        "분포·산점도·박스플롯으로 따릉이 데이터를 시각화할 수 있다.",
        "Orange3와 Python의 시각화 결과를 비교하고 데이터의 특징을 설명할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-09",
      "week": 9,
      "badge": "9주차",
      "title": "상관분석과 회귀 모델의 개념",
      "subtitle": "25–27차시",
      "kicker": "9주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "25–27차시",
      "dataName": "따릉이",
      "textbook": [
        {
          "unit": "Ⅱ-2-3",
          "page": 95
        },
        {
          "unit": "Ⅲ-1-1",
          "page": 107
        }
      ],
      "objectives": [
        "속성 간 관계를 상관분석으로 살펴볼 수 있다.",
        "따릉이 대여 건수 예측에서 회귀 모델의 입력과 출력을 설명할 수 있다."
      ],
      "compressible": true
    },
    {
      "slug": "week-10",
      "week": 10,
      "badge": "10주차",
      "title": "선형 회귀와 학습·테스트 데이터 분리",
      "subtitle": "28–30차시",
      "kicker": "10주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "28–30차시",
      "dataName": "따릉이",
      "textbook": [
        {
          "unit": "Ⅲ-1-2",
          "page": 118
        }
      ],
      "objectives": [
        "학습 데이터와 테스트 데이터를 나누어 회귀 모델을 구성할 수 있다.",
        "Orange3와 Python으로 따릉이 대여 건수를 예측하는 선형 회귀를 구현할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-11",
      "week": 11,
      "badge": "11주차",
      "title": "회귀 모델 평가와 미니 프로젝트 2",
      "subtitle": "31–33차시",
      "kicker": "11주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "따릉이"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "31–33차시",
      "dataName": "따릉이",
      "textbook": [
        {
          "unit": "Ⅲ-1-2",
          "page": 118
        }
      ],
      "objectives": [
        "MSE와 R²로 회귀 모델을 평가하고 입력 변수에 따른 변화를 비교할 수 있다.",
        "회귀 모델의 예측 결과와 평가 결과를 해석하여 정리할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-12",
      "week": 12,
      "badge": "12주차",
      "title": "분류 모델과 평가",
      "subtitle": "34–36차시",
      "kicker": "12주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "KBO 선수 기록"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "34–36차시",
      "dataName": "KBO 선수 기록",
      "textbook": [
        {
          "unit": "Ⅲ-2-1",
          "page": 133
        },
        {
          "unit": "Ⅲ-2-2",
          "page": 141
        }
      ],
      "objectives": [
        "Orange3와 Python으로 KBO 선수 기록의 분류 모델을 구성할 수 있다.",
        "혼동행렬과 정확도·정밀도·재현율을 이용해 분류 결과를 평가할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-13",
      "week": 13,
      "badge": "13주차",
      "title": "군집 모델과 급식 메뉴 연관분석",
      "subtitle": "37–39차시",
      "kicker": "13주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "KBO 선수 기록·NEIS 급식식단정보"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "37–39차시",
      "dataName": "KBO 선수 기록·NEIS 급식식단정보",
      "textbook": [
        {
          "unit": "Ⅲ-3-1",
          "page": 147
        },
        {
          "unit": "Ⅲ-3-2",
          "page": 161
        }
      ],
      "objectives": [
        "KBO 선수 기록을 군집화하고 선수 유형을 해석할 수 있다.",
        "NEIS 급식 메뉴를 장바구니 형태로 변환하여 연관 규칙을 도출할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-14",
      "week": 14,
      "badge": "14주차",
      "title": "데이터 과학의 진로·전망과 프로젝트 설계",
      "subtitle": "40–42차시",
      "kicker": "14주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "NEIS / 기상·따릉이 / KBO 중 택1 또는 공공데이터포털 직접 수집"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "40–42차시",
      "dataName": "NEIS / 기상·따릉이 / KBO 중 택1 또는 공공데이터포털 직접 수집",
      "textbook": [
        {
          "unit": "Ⅰ-3-1",
          "page": 42
        },
        {
          "unit": "Ⅰ-3-2",
          "page": 46
        },
        {
          "unit": "Ⅳ-1-1",
          "page": 173
        },
        {
          "unit": "Ⅳ-1-2",
          "page": 179
        }
      ],
      "objectives": [
        "데이터 과학의 사회적 변화·진로·전망과 필요한 역량을 설명할 수 있다.",
        "허용된 데이터 범위에서 프로젝트 주제를 정하고 탐색적 데이터 분석을 수행할 수 있다."
      ],
      "compressible": false
    },
    {
      "slug": "week-15",
      "week": 15,
      "badge": "15주차",
      "title": "최종 프로젝트 수행과 발표",
      "subtitle": "43–45차시",
      "kicker": "15주차",
      "duration": "3차시",
      "target": "고등학교",
      "difficulty": "",
      "tags": [
        "NEIS / 기상·따릉이 / KBO 중 택1 또는 공공데이터포털 직접 수집"
      ],
      "accent": "neon-green",
      "emoji": "",
      "cover": "",
      "status": "coming",
      "lessons": "43–45차시",
      "dataName": "NEIS / 기상·따릉이 / KBO 중 택1 또는 공공데이터포털 직접 수집",
      "textbook": [
        {
          "unit": "Ⅳ-2-1",
          "page": 187
        },
        {
          "unit": "Ⅳ-2-2",
          "page": 197
        }
      ],
      "objectives": [
        "선정한 주제와 데이터로 분석 프로젝트를 수행할 수 있다.",
        "분석 과정과 결과를 근거와 함께 발표할 수 있다."
      ],
      "compressible": false
    }
  ],

  // 다른 강의로 이동하는 링크 (전부 외부 절대 주소)
  otherLectures: [
    {
      title: "딥러닝 CNN으로 포트홀을 찾아라",
      url: "https://kimjinhyuk1984.github.io/pothole/",
      emoji: ""
    }
  ]
};

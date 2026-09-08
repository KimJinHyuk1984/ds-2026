/* ★ 공통 관리 파일: instructor는 템플릿 원본에서만 수정해 모든 강의에 반영합니다.
 * site, levels와 otherLectures는 각 강의 저장소에서 수정합니다.
 * 동기화 스크립트는 이 파일을 덮어쓰지 않습니다. instructor 변경은 수동으로 병합합니다.
 */
window.SITE = {
  site: {
    title: "강의 모음",
    subtitle: "배울 강의를 선택하세요.",
    repo: "lecture-template" // 진행 기록을 구분하는 이름. 복제한 저장소 이름으로 변경합니다.
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

  // ── 이 아래는 강의마다 교체한다 ──
  // 원소가 1개이면 루트가 강의 페이지, 2개 이상이면 루트가 허브입니다.
  // 단일 강의의 badge는 비워 둡니다. 번호가 필요 없으므로 표시하지 않습니다.
  // 단일 강의의 slug는 폴더/URL 선택에는 무시하지만 진행 기록의 고정 ID로 사용합니다.
  // 다중 강의에서는 slug와 하위 폴더명, 하위 HTML의 body[data-level]을 일치시킵니다.
  levels: [{
    slug: "lecture-title",
    badge: "",
    title: "강의 제목",
    subtitle: "한 줄 부제",
    kicker: "TOPIC",
    duration: "2시간",
    target: "고등학교",
    difficulty: "입문",
    tags: ["Python"],
    accent: "neon-green", // neon-green | violet | amber
    emoji: "",
    cover: "", // 선택 사항: 사이트 루트 기준 상대 경로, 예: assets/img/cover.webp
    status: "ready" // ready | coming: 다중 강의 허브에서 링크 공개 여부를 결정합니다.
  }],

  // 다른 강의로 이동하는 링크 (전부 외부 절대 주소)
  otherLectures: [
    {
      title: "딥러닝 CNN으로 포트홀을 찾아라",
      url: "https://kimjinhyuk1984.github.io/pothole/",
      emoji: ""
    }
  ]
};

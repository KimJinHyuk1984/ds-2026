"""기상·대여 일별 결과를 날짜 기준으로 결합하고 학기 공통 CSV를 저장한다."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from csvtools import (
    ROOT, INTERMEDIATE_DIR, parse_dates, parse_numbers,
    check_unique_dates, report, write_csv,
)

START_DATE = "2024-03-01"
# 202502 따릉이 원본은 재다운로드해도 2월 16일까지만 존재하므로 최종 기간을 줄인다.
END_DATE = "2025-02-16"

WEATHER_COLUMNS = ("날짜", "평균기온", "최고기온", "최저기온", "강수량")
BIKE_COLUMNS = ("날짜", "대여건수")
OUTPUT_COLUMNS = ("날짜", "요일", "공휴일여부", "평균기온", "최고기온", "최저기온", "강수량", "대여건수")
WEEKDAY_NAMES = ("월", "화", "수", "목", "금", "토", "일")
HOLIDAY_COVERAGE = ("2024-03-01", "2025-02-16")
# 아래 날짜는 해당 기간에 한정한다. 현재/미래 연도 규칙을 소급 적용하지 않는다.
# 출처: KASI 2024·2025 월력요항, 정책브리핑 임시공휴일 공고 안내.
# https://www.kasi.re.kr/kor/publication/post/newsMaterial/29633?cPage=7
# https://www.kasi.re.kr/publication/post/newsMaterial?cPage=10
# https://www.korea.kr/news/policyNewsView.do?newsId=148933400
# https://www.korea.kr/news/policyNewsView.do?newsId=148938559
HOLIDAYS = {
    "2024-03-01": "삼일절",
    "2024-04-10": "제22대 국회의원 선거일",
    "2024-05-05": "어린이날",
    "2024-05-06": "어린이날 대체공휴일",
    "2024-05-15": "부처님오신날",
    "2024-06-06": "현충일",
    "2024-08-15": "광복절",
    "2024-09-16": "추석 전날",
    "2024-09-17": "추석",
    "2024-09-18": "추석 다음 날",
    "2024-10-01": "국군의 날 임시공휴일",
    "2024-10-03": "개천절",
    "2024-10-09": "한글날",
    "2024-12-25": "기독탄신일",
    "2025-01-01": "새해 첫날",
    "2025-01-27": "설 연휴 임시공휴일",
    "2025-01-28": "설날 전날",
    "2025-01-29": "설날",
    "2025-01-30": "설날 다음 날",
}


def read_prepared(path: Path, expected: tuple) -> pd.DataFrame:
    if not path.is_file():
        raise ValueError(f"중간 결과가 없습니다: {path}. 앞 단계 스크립트를 먼저 실행하세요.")
    frame = pd.read_csv(path, encoding="utf-8-sig", dtype="string", keep_default_na=False, on_bad_lines="error")
    if set(frame.columns) != set(expected):
        raise ValueError(f"{path.name}: 기대 컬럼 {expected}, 실제 컬럼 {list(frame.columns)}")
    frame["날짜"] = parse_dates(frame["날짜"], f"{path.name}/날짜")
    # 기존 중간 파일은 2월 28일까지 포함할 수 있다. 최종 기간만 선택하고 값은 보정하지 않는다.
    inside = frame["날짜"].between(pd.Timestamp(START_DATE), pd.Timestamp(END_DATE))
    print(f"[기간] {path.name}: 최종 기간 밖 {int((~inside).sum())}행 제외")
    frame = frame.loc[inside].copy()
    check_unique_dates(frame, path.name)
    for column in expected[1:]:
        frame[column] = parse_numbers(frame[column], f"{path.name}/{column}", integer=column == "대여건수")
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weather", type=Path, default=INTERMEDIATE_DIR / "weather-daily.csv")
    parser.add_argument("--bike", type=Path, default=INTERMEDIATE_DIR / "bike-counts-daily.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "weather-bike" / "bike-daily.csv")
    args = parser.parse_args()
    if (START_DATE, END_DATE) != HOLIDAY_COVERAGE:
        raise ValueError("기간을 바꾸려면 해당 기간의 HOLIDAYS와 HOLIDAY_COVERAGE도 확인·갱신하세요.")
    weather = read_prepared(args.weather, WEATHER_COLUMNS)
    bike = read_prepared(args.bike, BIKE_COLUMNS)
    # 날짜 목록은 관측값이 아니다. 원본 행이 없는 날도 유지하고 관측값은 비워 둔다.
    calendar = pd.DataFrame({"날짜": pd.date_range(START_DATE, END_DATE, freq="D")})
    print(f"[병합] 날짜 기준표 {len(calendar)}일")
    print(f"[원본 누락] 기상 행 없는 날짜 {len(calendar) - len(weather)}일, 대여 행 없는 날짜 {len(calendar) - len(bike)}일")
    result = calendar.merge(weather, how="left", on="날짜", validate="one_to_one")
    result = result.merge(bike, how="left", on="날짜", validate="one_to_one")
    result["요일"] = result["날짜"].dt.dayofweek.map(dict(enumerate(WEEKDAY_NAMES)))
    # 일요일 자체는 추가하지 않고 사용자가 확인한 HOLIDAYS 19개 날짜만 표시한다.
    is_holiday = result["날짜"].dt.strftime("%Y-%m-%d").isin(HOLIDAYS)
    result["공휴일여부"] = is_holiday.astype("Int64")
    result = result.loc[:, list(OUTPUT_COLUMNS)]
    report(result, "학기 공통 bike-daily.csv", start_date=START_DATE, end_date=END_DATE)
    print(f"공휴일 표시: {int(result['공휴일여부'].sum())}일 (HOLIDAYS 목록 기준)")
    missing_bike_dates = result.loc[result["대여건수"].isna(), "날짜"].dt.strftime("%Y-%m-%d").tolist()
    print(f"[최종 대여건수 결측 날짜/원본 없는 날 포함] {missing_bike_dates if missing_bike_dates else '없음'}")
    if not result.loc[:, list(WEATHER_COLUMNS[1:]) + ["대여건수"]].isna().any().any():
        print("[수업 준비 확인] 원본에서 보존된 결측이 없습니다. 결측을 인위적으로 만들지 않았습니다.")
    write_csv(result, args.output, [args.weather, args.bike])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError, pd.errors.ParserError) as error:
        raise SystemExit(f"처리 중단: {error}") from error

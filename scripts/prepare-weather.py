"""서울(108) ASOS 일자료를 정리한다. 원본 준비 후 사용자가 실행한다."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from csvtools import (
    ROOT, INTERMEDIATE_DIR, csv_files, find_layout, read_options, rename_columns,
    parse_dates, parse_numbers, select_period, check_unique_dates, report, write_csv,
)

# 날짜·지점은 이름 후보와 비교하고 기상 4개 열은 아래 부분 문자열로 찾는다.
# 원본의 최저/최고기온 위치나 단위의 ° 문자가 달라도 이름으로 구분한다.
COLUMN_MAP = {
    "날짜": ("일시", "날짜", "관측일자"),
    "평균기온": ("평균기온",),
    "최저기온": ("최저기온",),
    "최고기온": ("최고기온",),
    "강수량": ("일강수량",),
    "지점": ("지점", "지점번호", "관측지점번호"),  # 있으면 서울(108) 검증에 사용
}
SUBSTRING_COLUMNS = ("평균기온", "최저기온", "최고기온", "강수량")
REQUIRED_COLUMNS = ("날짜", "평균기온", "최고기온", "최저기온", "강수량")
STATION_ID = 108
ENCODING = None      # 자동: UTF-8 BOM / cp949 / euc-kr. 예: "cp949"
HEADER_ROW = None    # 자동: 앞 100행. 직접 지정하면 0부터 세는 물리 행 번호.
DELIMITER = None     # 자동: 쉼표 / 탭 / 세미콜론


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="생략하면 source/weather/의 CSV 1개")
    parser.add_argument("--output", type=Path, default=INTERMEDIATE_DIR / "weather-daily.csv")
    args = parser.parse_args()
    if args.input is None:
        candidates = csv_files(ROOT / "source" / "weather")
        if len(candidates) != 1:
            raise ValueError(f"source/weather/에는 ASOS CSV 1개가 필요합니다. 현재 {len(candidates)}개")
        source = candidates[0]
    else:
        source = args.input
    layout = find_layout(
        source, COLUMN_MAP, REQUIRED_COLUMNS, ENCODING, HEADER_ROW, DELIMITER,
        substring_columns=SUBSTRING_COLUMNS,
    )
    frame = rename_columns(pd.read_csv(source, **read_options(layout)), layout)
    if "지점" in frame:
        station = parse_numbers(frame["지점"], f"{source.name}/지점", integer=True)
        if station.isna().any():
            raise ValueError("관측지점이 비어 있습니다. 서울(108) 자료인지 확인하세요.")
        selected = station.eq(STATION_ID)
        print(f"[지점] 서울({STATION_ID}) 외 {int((~selected).sum())}행 제외")
        frame = frame.loc[selected].copy()
    else:
        print("[확인 필요] 지점 컬럼 없음. 내려받은 파일이 서울(108) 자료인지 원본에서 확인하세요.")
    frame["날짜"] = parse_dates(frame["날짜"], f"{source.name}/날짜")
    frame = select_period(frame, source.name)
    check_unique_dates(frame, "ASOS")
    for column in REQUIRED_COLUMNS[1:]:
        frame[column] = parse_numbers(frame[column], f"{source.name}/{column}")
    frame = frame.loc[:, list(REQUIRED_COLUMNS)].sort_values("날짜").reset_index(drop=True)
    # 강수량이 공백인 날은 0으로 바꾸지 않는다. 수치형 이상치도 그대로 둔다.
    report(frame, "ASOS 정리 결과")
    write_csv(frame, args.output, [source])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError, pd.errors.ParserError) as error:
        raise SystemExit(f"처리 중단: {error}") from error

"""시간대별 이용정보 월별 CSV 12개를 파일·청크 단위로 읽어 일별 전체 건수를 합산한다."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from csvtools import (
    ROOT, START_DATE, END_DATE, INTERMEDIATE_DIR, csv_files, find_layout,
    read_options, rename_columns, parse_dates, parse_numbers, report, write_csv,
)

# 행 1개를 대여 1건으로 세지 않는다. 시간대별 통계의 '이용건수'를 합산한다.
# 현재 12개 원본의 헤더는 '대여일자', '이용건수'와 일치한다. 전체 행은 미검증이다.
COLUMN_MAP = {
    "날짜": ("대여일자", "대여일시", "기준일자", "날짜"),
    "대여건수": ("이용건수", "대여건수", "이용 건수", "대여 건수"),
}
# 월마다 헤더/인코딩이 다르면 정확한 파일명을 키로 설정한다.
FILE_OVERRIDES = {
    # "실제-월별-파일명.csv": {
    #     "columns": {"날짜": ("실제 날짜 컬럼",), "대여건수": ("실제 건수 컬럼",)},
    #     "encoding": "cp949", "header_row": 0, "delimiter": ",",
    # },
}
EXPECTED_FILE_COUNT = 12
CHUNK_SIZE = 100_000


def aggregate_file(source: Path) -> tuple[pd.DataFrame, str, int, int]:
    overrides = FILE_OVERRIDES.get(source.name, {})
    mapping = {**COLUMN_MAP, **overrides.get("columns", {})}
    layout = find_layout(source, mapping, ("날짜", "대여건수"),
                         overrides.get("encoding"), overrides.get("header_row"),
                         overrides.get("delimiter"))
    # 매월 작은 일별 누계만 유지한다. 원본 청크를 리스트에 쌓지 않는다.
    day_sums: dict = {}
    months = set()
    total_rows = skipped_rows = negative_counts = 0
    with pd.read_csv(source, chunksize=CHUNK_SIZE, **read_options(layout)) as reader:
        for raw in reader:
            chunk = rename_columns(raw, layout)
            chunk["날짜"] = parse_dates(chunk["날짜"], f"{source.name}/날짜")
            outside = ~chunk["날짜"].between(pd.Timestamp(START_DATE), pd.Timestamp(END_DATE))
            if outside.any():
                raise ValueError(f"{source.name}: 지정 기간 밖 날짜가 있습니다. 요청한 12개 월별 CSV인지 확인하세요.")
            months.update(chunk["날짜"].dt.strftime("%Y-%m").unique())
            if len(months) > 1:
                raise ValueError(f"{source.name}: 한 파일에 여러 달 {sorted(months)}이 있습니다. 월별 파일 구성부터 확인하세요.")
            counts = parse_numbers(chunk["대여건수"], f"{source.name}/대여건수", integer=True)
            chunk["대여건수"] = counts
            total_rows += len(chunk)
            skipped_rows += int(counts.isna().sum())
            negative_counts += int(counts.lt(0).sum())
            # 결측 행은 합산에서 제외한다. 청크의 모든 행이 결측이면 소계도 결측이다.
            grouped = chunk.groupby("날짜")["대여건수"].sum(min_count=1)
            for date, subtotal in grouped.items():
                # None은 지금까지 이 날짜의 유효한 건수를 한 번도 읽지 않았다는 뜻이다.
                day_sums.setdefault(date, None)
                if pd.notna(subtotal):
                    previous = day_sums[date]
                    day_sums[date] = (0 if previous is None else previous) + int(subtotal)
    if not day_sums or len(months) != 1:
        raise ValueError(f"{source.name}: 유효한 월별 자료가 없습니다.")
    daily = pd.DataFrame({
        "날짜": sorted(day_sums),
        "대여건수": pd.array(
            [day_sums[date] for date in sorted(day_sums)],
            dtype="Int64",
        ),
    })
    month = next(iter(months))
    print(f"[집계] {source.name}: {total_rows:,}행 → {len(daily)}일, 음수 {negative_counts:,}개")
    print(f"[결측 행 제외/{month}] 이용건수가 결측인 {skipped_rows:,}행을 합산에서 제외")
    report(daily, f"{source.name} 일별 합계")
    return daily, month, total_rows, skipped_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "source" / "bike")
    parser.add_argument("--output", type=Path, default=INTERMEDIATE_DIR / "bike-counts-daily.csv")
    args = parser.parse_args()
    sources = csv_files(args.input_dir)
    if len(sources) != EXPECTED_FILE_COUNT:
        raise ValueError(f"월별 CSV {EXPECTED_FILE_COUNT}개가 필요합니다. 현재 {len(sources)}개")
    expected_months = set(pd.period_range(START_DATE, END_DATE, freq="M").astype(str))
    observed_months = set()
    daily_frames = []  # 집계가 끝난 월별 최대 31행만 보관한다.
    total_rows = total_skipped_rows = 0
    for source in sources:
        daily, month, month_rows, month_skipped_rows = aggregate_file(source)
        if month in observed_months:
            raise ValueError(f"{month} 자료가 여러 파일에 있습니다. 중복 집계를 막기 위해 중단합니다.")
        observed_months.add(month)
        daily_frames.append(daily)
        total_rows += month_rows
        total_skipped_rows += month_skipped_rows
    if observed_months != expected_months:
        raise ValueError(f"월 구성 불일치. 필요한 월: {sorted(expected_months - observed_months)}")
    result = pd.concat(daily_frames, ignore_index=True).sort_values("날짜").reset_index(drop=True)
    if result["날짜"].duplicated().any():
        raise ValueError("일별 합계에 중복 날짜가 있습니다.")
    report(result, "12개월 따릉이 일별 전체 합계")
    skipped_ratio = total_skipped_rows / total_rows
    print(f"[전체 결측 행 제외] {total_skipped_rows:,}/{total_rows:,}행 ({skipped_ratio:.6%})")
    missing_dates = result.loc[result["대여건수"].isna(), "날짜"].dt.strftime("%Y-%m-%d").tolist()
    print(f"[대여건수 결측 날짜/모든 행 결측] {missing_dates if missing_dates else '없음'}")
    write_csv(result, args.output, sources)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError, pd.errors.ParserError) as error:
        raise SystemExit(f"처리 중단: {error}") from error

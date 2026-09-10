"""4주차 수업 후 참고용 CSV 생성. 원본을 보존하고 강수량 공백만 0으로 바꾼다.

실행: python scripts/build-bike-daily-clean.py
기존 결과를 다시 만들 때만 --overwrite를 지정한다. 외부 의존성: pandas.
학생용 페이지에는 이 스크립트를 직접 링크하지 않는다.
"""

import argparse
import math
import os
from pathlib import Path
import tempfile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data/weather-bike/bike-daily.csv"
OUTPUT_PATH = ROOT / "data/weather-bike/bike-daily-clean.csv"
START_DATE = "2024-03-01"
# 원본 따릉이 202502 파일에 2월 16일 이후 기록이 없어 확정한 수업 기간이다.
END_DATE = "2025-02-16"
EXPECTED_ROWS = 353
EXPECTED_RAIN_MISSING = 200
EXPECTED_COLUMNS = [
    "날짜", "요일", "공휴일여부", "평균기온", "최고기온", "최저기온", "강수량", "대여건수",
]
NUMERIC_COLUMNS = EXPECTED_COLUMNS[2:]


def build_clean(*, overwrite: bool = False) -> None:
    if not INPUT_PATH.is_file():
        raise ValueError(f"확정된 실습 원본이 없습니다: {INPUT_PATH}")
    if INPUT_PATH.resolve() == OUTPUT_PATH.resolve():
        raise ValueError("출력 경로는 실습 원본과 달라야 합니다.")
    if OUTPUT_PATH.exists():
        if OUTPUT_PATH.samefile(INPUT_PATH):
            raise ValueError("출력이 원본과 같은 파일을 가리킵니다.")
        if not overwrite:
            raise ValueError("결과가 이미 있습니다. 검토 후 --overwrite로 재생성하세요.")

    # 숫자도 문자열로 읽어, 바꾸지 않는 셀의 표기와 원래 컬럼·행 순서를 보존한다.
    original = pd.read_csv(INPUT_PATH, encoding="utf-8-sig", dtype=str,
                           keep_default_na=False)
    if original.columns.tolist() != EXPECTED_COLUMNS or len(original) != EXPECTED_ROWS:
        raise ValueError("실습 원본은 지정 컬럼 순서의 353행 × 8열이어야 합니다.")
    expected_dates = pd.date_range(START_DATE, END_DATE).strftime("%Y-%m-%d").tolist()
    if original["날짜"].tolist() != expected_dates:
        raise ValueError("날짜 범위·순서·연속성 또는 중복을 확인하세요.")
    missing = original.apply(lambda column: column.str.strip().eq(""))
    if int(missing["강수량"].sum()) != EXPECTED_RAIN_MISSING:
        raise ValueError("원본 강수량 공백은 200개여야 합니다. 이미 처리한 파일인지 확인하세요.")
    if missing.drop(columns="강수량").any().any():
        raise ValueError("강수량 외 컬럼에 빈 값이 있습니다. 원본을 먼저 확인하세요.")
    for column in NUMERIC_COLUMNS:
        values = pd.to_numeric(original.loc[~missing[column], column], errors="raise")
        if not all(math.isfinite(value) for value in values):
            raise ValueError(f"{column}에 유한한 수가 아닌 값이 있습니다.")

    # 사용자 원본 검토로 확인된 의미: 이 파일의 강수량 공백은 무강수(0 mm).
    # 평균 대체·행 삭제·이상치 제거·클리핑은 하지 않는다. 다른 자료에 일반화하지 않는다.
    cleaned = original.copy(deep=True)
    cleaned.loc[missing["강수량"], "강수량"] = "0"
    other_columns = [column for column in EXPECTED_COLUMNS if column != "강수량"]
    if not cleaned[other_columns].equals(original[other_columns]):
        raise ValueError("강수량 외 값이 변경되었습니다. 저장하지 않습니다.")
    observed = ~missing["강수량"]
    if not cleaned.loc[observed, "강수량"].equals(original.loc[observed, "강수량"]):
        raise ValueError("관측된 강수량이 변경되었습니다. 저장하지 않습니다.")
    after_missing = cleaned.apply(lambda column: column.str.strip().eq("")).sum()
    if after_missing.any():
        raise ValueError("처리 후 빈 값이 남았습니다. 저장하지 않습니다.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=OUTPUT_PATH.parent, suffix=".tmp",
                                         delete=False) as temporary:
            temporary_path = Path(temporary.name)
        cleaned.to_csv(temporary_path, index=False, encoding="utf-8-sig")
        if overwrite:
            os.replace(temporary_path, OUTPUT_PATH)
        else:
            # 새 파일은 배타적으로 생성한다. 검증 도중 생긴 결과도 덮어쓰지 않는다.
            created = False
            try:
                with OUTPUT_PATH.open("xb") as output:
                    created = True
                    output.write(temporary_path.read_bytes())
            except OSError:
                if created:
                    OUTPUT_PATH.unlink(missing_ok=True)
                raise
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    rentals = pd.to_numeric(cleaned["대여건수"], errors="raise")
    rain = pd.to_numeric(cleaned["강수량"], errors="raise")
    print(f"저장: {OUTPUT_PATH} (UTF-8 BOM, 인덱스 열 없음)")
    print(f"크기: {len(cleaned)}행 × {len(cleaned.columns)}열")
    print(f"기간: {START_DATE} ~ {END_DATE}; 날짜 누락·중복 0일")
    print("컬럼별 빈 값 — 처리 전 / 처리 후")
    print(pd.DataFrame({"처리 전": missing.sum(), "처리 후": after_missing}).to_string())
    print(f"강수량 공백 → 0: {EXPECTED_RAIN_MISSING}개; 강수량 평균: {rain.mean():.6f} mm")
    print(f"대여건수 최소 / 최대: {rentals.min():,} / {rentals.max():,}")
    print("353행 및 극단값 보존. 강수량의 기존 관측값과 다른 7개 컬럼은 셀 단위 동일.")
    print("원본 bike-daily.csv는 변경하지 않았습니다. 결과 검토 후 수업 후 참고용으로 공개하세요.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true", help="기존 정제 결과만 덮어쓰기")
    args = parser.parse_args()
    try:
        build_clean(overwrite=args.overwrite)
    except (OSError, ValueError) as error:
        parser.exit(1, f"생성 중단: {error}\n")


if __name__ == "__main__":
    main()

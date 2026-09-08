"""공공 CSV 읽기와 결측 보존을 위한 공통 함수. 외부 의존성은 pandas뿐이다."""
from __future__ import annotations

import csv
import os
from pathlib import Path
import re
import tempfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
# 원본 준비 범위. 최종 배포 기간은 build-bike-daily.py 상단에서 별도로 지정한다.
START_DATE = "2024-03-01"
END_DATE = "2025-02-28"
INTERMEDIATE_DIR = ROOT / "work-temp" / "data-preparation"
ENCODINGS = ("utf-8-sig", "cp949", "euc-kr")
DELIMITERS = (",", "\t", ";")
HEADER_SCAN_LINES = 100
# 숫자 0, -999, -9999 및 '-'는 결측으로 간주하지 않는다.
# 원본의 특수 결측 부호는 제공 기관 정의를 확인한 뒤에만 추가한다.
MISSING_TOKENS = {"", "na", "n/a", "nan", "null", "none"}
NUMBER_PATTERN = r"[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


def csv_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise ValueError(f"원본 폴더가 없습니다: {directory}")
    return sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".csv")


def normalize_header(value: str) -> str:
    return re.sub(r"\s+", "", value.replace("\ufeff", "")).casefold()


def find_layout(path: Path, mapping: dict, required: tuple,
                encoding: str | None = None, header_row: int | None = None,
                delimiter: str | None = None, *, substring_columns: tuple = ()) -> dict:
    """앞쪽 안내 행을 건너뛰고 필수 컬럼이 모두 있는 실제 헤더를 찾는다.

    header_row는 0부터 시작하는 물리 행 번호. 잘못된 컬럼을 위치로 추측하지 않는다.
    substring_columns에 지정한 항목만 이름의 부분 문자열로 찾는다.
    큰 파일 전체를 메모리에 읽지 않으며 손상된 인코딩을 replace로 숨기지 않는다.
    """
    if not path.is_file():
        raise ValueError(f"원본 파일이 없습니다: {path}")
    if header_row is not None and header_row < 0:
        raise ValueError("header_row는 0 이상이어야 합니다.")
    with path.open("rb") as handle:
        bom = handle.read(4)
    encodings = (encoding,) if encoding else (
        ("utf-16",) if bom.startswith((b"\xff\xfe", b"\xfe\xff")) else ENCODINGS
    )
    separators = (delimiter,) if delimiter else DELIMITERS
    limit = max(HEADER_SCAN_LINES, (header_row or 0) + 1)
    for codec in encodings:
        for separator in separators:
            try:
                with path.open("r", encoding=codec, errors="strict", newline="") as handle:
                    reader = csv.reader(handle, delimiter=separator)
                    while reader.line_num < limit:
                        row_number = reader.line_num
                        row = next(reader, None)
                        if row is None:
                            break
                        if header_row is not None and row_number != header_row:
                            continue
                        normalized = [normalize_header(cell) for cell in row]
                        selected = {}
                        ambiguous = []
                        for target, aliases in mapping.items():
                            aliases = (aliases,) if isinstance(aliases, str) else aliases
                            candidates = {normalize_header(alias) for alias in aliases}
                            if target in substring_columns:
                                matches = [raw for raw in row if any(
                                    token in normalize_header(raw) for token in candidates
                                )]
                            else:
                                matches = [raw for raw in row if normalize_header(raw) in candidates]
                            if len(matches) == 1:
                                selected[target] = matches[0]
                            elif len(matches) > 1:
                                ambiguous.append(target)
                        if all(key in selected or key in ambiguous for key in required):
                            if ambiguous:
                                raise ValueError(f"{path.name}: 컬럼 후보가 여러 개입니다: {ambiguous}. COLUMN_MAP을 좁히세요.")
                            nonempty = [name for name in normalized if name]
                            if len(nonempty) != len(set(nonempty)):
                                raise ValueError(f"{path.name}: 중복 헤더를 확인하세요.")
                            print(f"[입력] {path.name}: encoding={codec}, 헤더={row_number + 1}행, 구분자={separator!r}")
                            print(f"[매핑] {selected}")
                            return {"encoding": codec, "separator": separator,
                                    "header_row": row_number, "columns": selected}
            except (UnicodeError, csv.Error):
                continue
    raise ValueError(
        f"{path.name}: 필수 컬럼 {required}을 찾지 못했습니다. "
        "COLUMN_MAP, 인코딩, header_row(0부터), 구분자와 원본 CSV 여부를 확인하세요."
    )


def read_options(layout: dict) -> dict:
    return {
        "encoding": layout["encoding"], "encoding_errors": "strict",
        "sep": layout["separator"], "skiprows": layout["header_row"], "header": 0,
        "usecols": list(layout["columns"].values()), "dtype": "string",
        "keep_default_na": False, "on_bad_lines": "error",
    }


def rename_columns(frame: pd.DataFrame, layout: dict) -> pd.DataFrame:
    return frame.rename(columns={raw: target for target, raw in layout["columns"].items()})


def parse_dates(series: pd.Series, label: str) -> pd.Series:
    text = series.astype("string").str.strip()
    text = text.str.replace(r"[./]", "-", regex=True)
    # 날짜 열과 선택적 시각만 허용한다. 빈 날짜·소계·각주를 조용히 버리지 않는다.
    date_part = text.str.extract(
        r"^(\d{4}-\d{1,2}-\d{1,2}|\d{8})(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?$",
        expand=False,
    )
    result = pd.to_datetime(date_part, format="%Y-%m-%d", errors="coerce")
    compact = pd.to_datetime(date_part, format="%Y%m%d", errors="coerce")
    result = result.where(result.notna(), compact)
    if result.isna().any():
        raise ValueError(f"{label}: 해석할 수 없거나 빈 날짜 {int(result.isna().sum())}개. 날짜 형식·각주 행을 확인하세요.")
    return result.dt.normalize()


def parse_numbers(series: pd.Series, label: str, integer: bool = False) -> pd.Series:
    text = series.astype("string").str.strip()
    missing = text.isna() | text.str.casefold().isin(MISSING_TOKENS)
    valid = text.str.fullmatch(NUMBER_PATTERN, na=False)
    if (~missing & ~valid).any():
        raise ValueError(f"{label}: 숫자 또는 정의된 결측 부호가 아닌 값 {int((~missing & ~valid).sum())}개. 단위·기호·결측 표기를 확인하세요.")
    numbers = pd.to_numeric(text.mask(missing).str.replace(",", "", regex=False), errors="coerce")
    invalid = (~missing & numbers.isna()) | numbers.isin([float("inf"), -float("inf")])
    if invalid.any():
        raise ValueError(f"{label}: 숫자 표현 범위를 벗어난 값이 있습니다.")
    if integer:
        fractional = numbers.notna() & numbers.mod(1).ne(0)
        if fractional.any():
            raise ValueError(f"{label}: 정수가 아닌 건수가 있습니다. 반올림하지 않고 중단합니다.")
    # 음수나 큰 수는 그대로 보존한다. 범위 밖 기온·강수량을 자르지 않는다.
    return numbers.astype("Int64" if integer else "Float64")


def select_period(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    inside = frame["날짜"].between(pd.Timestamp(START_DATE), pd.Timestamp(END_DATE))
    if (~inside).any():
        print(f"[기간] {label}: 지정 기간 밖 {int((~inside).sum())}행 제외")
    return frame.loc[inside].copy()


def check_unique_dates(frame: pd.DataFrame, label: str) -> None:
    if frame.empty:
        raise ValueError(f"{label}: 지정 기간의 데이터가 없습니다.")
    duplicated = frame["날짜"].duplicated(keep=False)
    if duplicated.any():
        raise ValueError(f"{label}: 중복 날짜 {int(duplicated.sum())}행. 중복을 평균·제거하지 않고 원본 확인을 요청합니다.")


def report(frame: pd.DataFrame, label: str, *,
           start_date: str = START_DATE, end_date: str = END_DATE) -> None:
    print(f"\n[{label}] {len(frame):,}행 × {len(frame.columns)}열")
    print("\n컬럼별 자료형 / 결측 개수")
    print(pd.DataFrame({"자료형": frame.dtypes.astype(str), "결측": frame.isna().sum()}).to_string())
    print("\n컬럼별 요약")
    print(frame.describe(include="all").to_string())
    if "날짜" in frame:
        missing_days = pd.date_range(start_date, end_date).difference(pd.DatetimeIndex(frame["날짜"]))
        print(f"\n현재 결과에 날짜 행이 없는 날: {len(missing_days)}일")
    print("결측 채움·이상치 제거·보정: 수행하지 않음")


def write_csv(frame: pd.DataFrame, destination: Path, inputs: list[Path]) -> None:
    """원본 경로에는 쓰지 않고, 저장 성공 후에만 기존 출력 파일을 교체한다."""
    destination = destination.resolve()
    if destination in {source.resolve() for source in inputs} or (ROOT / "source").resolve() in destination.parents:
        raise ValueError("출력 경로를 원본 파일 또는 source/ 아래로 지정할 수 없습니다.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".csv-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
        frame.to_csv(temporary, index=False, encoding="utf-8-sig", na_rep="", date_format="%Y-%m-%d")
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    print(f"\n[저장] {destination} (UTF-8 BOM, 결측은 빈 필드)")

"""5주차 수업 후 참고용 long CSV 생성. 교사가 검토 후 직접 실행한다.

python scripts/build-meals-parsed.py
기존 결과 재생성: --overwrite. 외부 의존성은 pandas뿐이다.
생성 스크립트는 학생 페이지에서 직접 링크하지 않는다.
"""

import argparse
from collections import Counter
import math
import os
from pathlib import Path
import re
import tempfile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data/neis/meals.csv"
OUTPUT_PATH = ROOT / "data/neis/meals-parsed.csv"
MENU_SEPARATOR = "<br/>"
SOURCE_MENU_COLUMN = "요리명"
META_COLUMNS = ["학교명", "표준학교코드", "급식일자", "요일", "식사종류", "급식인원"]
OUTPUT_COLUMNS = META_COLUMNS + ["메뉴명", "알레르기번호"]
MEAL_KEY = ["표준학교코드", "급식일자", "식사종류"]
EXPECTED_MEALS = 1504
# 원문 구간을 읽기 전용으로 센 예상치. 출력에 맞추려고 행을 추가/삭제하지 않는다.
EXPECTED_MENU_ROWS = 10274
ALLOWED_ALLERGENS = frozenset(range(1, 20))
NUMERIC_BODY = re.compile(r"[0-9]+(?:\.[0-9]+)*")
PARENTHESES = re.compile(r"\(([^()]*)\)")
ALLERGEN_TAIL = re.compile(r"\(([0-9]+(?:\.[0-9]+)*)\)\s*$")


def parse_menu(raw: str) -> tuple[str, str]:
    text = raw.strip()
    if not text:
        raise ValueError("빈 메뉴 구간: 자동으로 버리지 않습니다.")
    if re.search(r"<[^>]*>|&(?:[A-Za-z]+|#[0-9]+|#x[0-9A-Fa-f]+);", text):
        raise ValueError("예상 밖 HTML 태그/엔티티: 구분자와 원문을 확인하세요.")
    depth = 0
    for character in text:
        if character == "(":
            depth += 1
            if depth > 1:
                raise ValueError("중첩 괄호: 단순 패턴으로 해석하지 않습니다.")
        elif character == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("닫는 괄호의 짝이 없습니다.")
    if depth:
        raise ValueError("열린 괄호의 짝이 없습니다.")
    for group in PARENTHESES.finditer(text):
        inside = group[1]
        if re.fullmatch(r"[0-9.,\s]+", inside) and not NUMERIC_BODY.fullmatch(inside):
            raise ValueError("쉼표·공백·연속 점 등 비표준 숫자 괄호를 확인하세요.")

    match = ALLERGEN_TAIL.search(text)
    numbers = []
    name = text
    if match:
        numbers = [int(value) for value in match[1].split(".")]
        if not all(value in ALLOWED_ALLERGENS for value in numbers):
            raise ValueError("끝의 숫자 괄호가 1~19 밖입니다. 설명/규격인지 확인하세요.")
        name = text[:match.start()].strip()
    # 앞쪽 (24.03), (23.06), (100)은 메뉴 정보로 보존한다.
    # 앞에도 1~19만 있는 괄호가 있다면 여러 번호 묶음인지 모호하므로 검토한다.
    for group in PARENTHESES.finditer(name):
        if NUMERIC_BODY.fullmatch(group[1]):
            values = [int(value) for value in group[1].split(".")]
            if all(value in ALLOWED_ALLERGENS for value in values):
                raise ValueError("메뉴 중간의 번호 후보: 설명인지 알레르기인지 확인하세요.")
    if not name:
        raise ValueError("알레르기 표시를 제거한 뒤 메뉴명이 비었습니다.")
    # 설명 괄호, 별표, 내부 공백과 문장부호는 임의로 삭제/분리하지 않는다.
    codes = ",".join(str(value) for value in dict.fromkeys(numbers))
    return name, codes


def build(*, overwrite: bool = False) -> None:
    if not INPUT_PATH.is_file():
        raise ValueError(f"확정된 원본이 없습니다: {INPUT_PATH}")
    if INPUT_PATH.resolve() == OUTPUT_PATH.resolve():
        raise ValueError("출력 경로가 원본과 같습니다.")
    if OUTPUT_PATH.exists():
        if OUTPUT_PATH.samefile(INPUT_PATH):
            raise ValueError("출력이 원본과 같은 파일을 가리킵니다.")
        if not overwrite:
            raise ValueError("결과가 이미 있습니다. 검토 후 --overwrite를 사용하세요.")
    source = pd.read_csv(INPUT_PATH, encoding="utf-8-sig", dtype=str,
                         keep_default_na=False)
    required = META_COLUMNS + [SOURCE_MENU_COLUMN]
    if not set(required).issubset(source.columns) or len(source) != EXPECTED_MEALS:
        raise ValueError("원본 필수 컬럼 또는 확정된 1,504개 급식 행을 확인하세요.")
    if source[required].apply(lambda column: column.str.strip().eq("")).any().any():
        raise ValueError("원본 필수 컬럼에 빈 값이 있습니다.")
    if source.duplicated(MEAL_KEY).any():
        raise ValueError("학교코드·날짜·식사종류 키가 중복됩니다.")
    dates = pd.to_datetime(source["급식일자"], format="%Y-%m-%d", errors="raise")
    if dates.dt.strftime("%Y-%m-%d").tolist() != source["급식일자"].tolist():
        raise ValueError("급식일자는 YYYY-MM-DD 형식이어야 합니다.")
    people = pd.to_numeric(source["급식인원"], errors="raise")
    if not all(math.isfinite(value) and value >= 0 for value in people):
        raise ValueError("급식인원의 수치 형식을 확인하세요. 자동 보정하지 않습니다.")

    records, failures = [], []
    counts = Counter()
    for source_index, row in source.iterrows():
        for item_index, raw in enumerate(row[SOURCE_MENU_COLUMN].split(MENU_SEPARATOR), 1):
            try:
                name, codes = parse_menu(raw)
            except ValueError as error:
                failures.append(
                    f"원본 행 {source_index + 1}, {row['학교명']} {row['급식일자']} "
                    f"{row['식사종류']}, 메뉴 {item_index}: {error}\n  원문: {raw!r}"
                )
                continue
            records.append({**{column: row[column] for column in META_COLUMNS},
                            "메뉴명": name, "알레르기번호": codes})
            counts["번호 없음"] += not bool(codes)
            counts["별표 보존"] += "*" in name
            counts["설명 괄호 보존"] += "(" in name
            counts["숫자 설명 괄호 보존"] += bool(re.search(r"\([0-9.]+\)", name))
    if failures:
        print(f"검토 필요 {len(failures)}개. 출력 파일을 저장하지 않습니다.")
        for failure in failures:
            print(failure)
        raise ValueError("위 원문을 확인한 뒤 패턴/예외 정책을 수정하세요.")
    result = pd.DataFrame(records, columns=OUTPUT_COLUMNS)
    expected_count = source[SOURCE_MENU_COLUMN].map(
        lambda value: len(value.split(MENU_SEPARATOR))).sum()
    if len(result) != expected_count:
        raise ValueError("메뉴 구간 수와 출력 행 수가 다릅니다.")
    if len(result) != EXPECTED_MENU_ROWS:
        raise ValueError(f"예상 {EXPECTED_MENU_ROWS}행과 다릅니다. 실제 {len(result)}행을 검토하세요.")
    unique_meals = result[META_COLUMNS].drop_duplicates().reset_index(drop=True)
    if unique_meals.to_dict("records") != source[META_COLUMNS].to_dict("records"):
        raise ValueError("급식 메타데이터 또는 원본 순서가 변경되었습니다.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=OUTPUT_PATH.parent, suffix=".tmp",
                                         delete=False) as temporary:
            temporary_path = Path(temporary.name)
        result.to_csv(temporary_path, index=False, encoding="utf-8-sig")
        if overwrite:
            os.replace(temporary_path, OUTPUT_PATH)
        else:
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
    print(f"저장: {OUTPUT_PATH} · UTF-8 BOM · 인덱스 열 없음")
    print(f"원본 {len(source):,}급식 → {len(result):,}메뉴 × {len(result.columns)}열")
    print(result.groupby("학교명", sort=False).size().rename("메뉴 행 수").to_string())
    print("컬럼별 빈 값:")
    print(result.apply(lambda column: column.eq("")).sum().to_string())
    print("파싱 관찰:", dict(counts))
    print("급식인원은 메뉴마다 반복됩니다. 합산하지 마세요.")
    print("알레르기번호 빈 값은 번호 미표기이며 유발 성분이 없다는 뜻이 아닙니다.")
    print("원본 보존. 수업 후 참고용 공개 전에 사례와 빈도/비율을 대조하세요.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true", help="기존 결과만 재생성")
    args = parser.parse_args()
    try:
        build(overwrite=args.overwrite)
    except (OSError, ValueError) as error:
        parser.exit(1, f"생성 중단: {error}\n")


if __name__ == "__main__":
    main()

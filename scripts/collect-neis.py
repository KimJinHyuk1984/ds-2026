"""NEIS 학교·급식 정보를 수집한다. 교사가 로컬에서 실행하며 키는 저장하지 않는다.

Python 3.10 이상, 표준 라이브러리만 사용한다. 실행 방법은 data/README.md 참조.
"""
from __future__ import annotations

import argparse
import csv
import getpass
import html
import json
import math
import os
import re
import sys
import time
from collections import Counter
from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone
from http.client import HTTPException, IncompleteRead
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.parse import quote, quote_plus, urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
API_BASE = "https://open.neis.go.kr/hub/"
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
OFFICE_CODE = "B10"  # 서울특별시교육청
ADDRESS_PREFIX = "서울특별시 "  # 승인된 후보를 구 경계로 제외하지 않는다.
# 사용자 --check 결과로 확정한 기본 4개교. 코드는 재조회 결과와 대조한다.
CONFIRMED_SCHOOL_CODES = {
    "동양고등학교": "7010965",
    "명덕고등학교": "7010158",
    "영일고등학교": "7010216",
    "세현고등학교": "7010764",
}
DEFAULT_SCHOOLS = tuple(CONFIRMED_SCHOOL_CODES)
RESERVE_SCHOOLS = ("대일고등학교",)
CANDIDATE_SCHOOLS = DEFAULT_SCHOOLS + RESERVE_SCHOOLS
# 마포고등학교는 사용자 확인에서 2024-03-06 급식이 없어 대상에서 제외했다.
# 각 월의 수요일 하루만 확인한다. 해당 날짜의 부재는 월 전체의 부재가 아니다.
CHECK_DATES = ("2024-03-06", "2024-09-04", "2025-01-08")
START_DATE = "2024-03-01"
END_DATE = "2025-02-28"  # 2024학년도. 따릉이 데이터의 축소 기간과 구분한다.
PAGE_SIZE = 1000  # 전체 급식 수집의 기본 페이지 크기
SCHOOL_PAGE_SIZE = 10  # 일반 schoolInfo 요청은 인증 여부와 무관하게 10건 요청
MINIMAL_SCHOOL = "동양고등학교"
REQUEST_INTERVAL = 1.0  # 이전 요청 종료 후 최소 대기 시간(초)
TIMEOUT = 30
MAX_RETRIES = 3  # 타임아웃·JSON 응답의 429/503만 최대 3회 추가, 2·4·8초 후 재시도
MIN_MEAL_DAYS = 150
KEY_ENV = "NEIS_API_KEY"
EXPECTED_KEY_LENGTH = 32  # 보통 32자. 길이는 경고 기준이며 유효성 보장은 아니다.
WEEKDAY_NAMES = ("월", "화", "수", "목", "금", "토", "일")  # 기존 기상·따릉이 파일과 같은 표기

# API 원본 이름 -> 배포 컬럼. 명세/실물 확인 후 이 상수에서 수정한다.
SCHOOL_COLUMNS = {
    "ATPT_OFCDC_SC_CODE": "시도교육청코드",
    "SD_SCHUL_CODE": "표준학교코드",
    "SCHUL_NM": "학교명",
    "SCHUL_KND_SC_NM": "학교종류",
    "LCTN_SC_NM": "시도명",
    "FOND_SC_NM": "설립구분",
    "ORG_RDNMA": "도로명주소",
    "HMPG_ADRES": "홈페이지",
}
MEAL_COLUMNS = {
    "ATPT_OFCDC_SC_CODE": "시도교육청코드",
    "SD_SCHUL_CODE": "표준학교코드",
    "SCHUL_NM": "학교명",
    "MLSV_YMD": "급식일자",
    "MMEAL_SC_CODE": "식사코드",
    "MMEAL_SC_NM": "식사종류",
    "MLSV_FGR": "급식인원",
    "DDISH_NM": "요리명",
    "ORPLC_INFO": "원산지정보",
    "CAL_INFO": "칼로리정보",
    "NTR_INFO": "영양정보",
}
MEAL_OUTPUT_COLUMNS = (*MEAL_COLUMNS.values(), "요일")  # 요일은 급식일자에서 추가
REQUIRED_SCHOOL = ("ATPT_OFCDC_SC_CODE", "SD_SCHUL_CODE", "SCHUL_NM",
                   "SCHUL_KND_SC_NM", "ORG_RDNMA")
REQUIRED_MEAL = ("ATPT_OFCDC_SC_CODE", "SD_SCHUL_CODE", "SCHUL_NM",
                "MLSV_YMD", "MMEAL_SC_CODE", "MMEAL_SC_NM", "DDISH_NM")


class CollectionError(Exception):
    """실제 인증키를 포함하지 않는 사용자용 오류."""


class RequestFailure(CollectionError):
    """재시도 불가 또는 한도 초과. --check의 다음 학교/날짜 요청도 중단한다."""


def api_code(result: dict) -> str:
    if not isinstance(result, dict):
        raise CollectionError("RESULT가 객체 형식이 아닙니다. 응답 본문을 확인하세요.")
    code = str(result.get("CODE", ""))
    return code if re.fullmatch(r"[A-Z]+-\d+", code) else "UNKNOWN"


def redact_key(value: str, key: str) -> str:
    """URL뿐 아니라 오류 본문·메시지에 되돌아온 키도 가린다."""
    if not key:
        return value
    masked = key[:3] + "..." + key[-3:] if len(key) > 6 else "***"
    variants = {key, quote(key, safe=""), quote_plus(key, safe=""),
                json.dumps(key, ensure_ascii=True)[1:-1],
                json.dumps(key, ensure_ascii=False)[1:-1], html.escape(key)}
    for secret in sorted(variants, key=len, reverse=True):
        value = value.replace(secret, masked)
    return value


def decode_body(body: bytes, charset: str | None) -> str:
    """전체 바이트를 디코딩한다. 서버 지정 인코딩 다음 UTF-8·CP949를 시도한다."""
    for encoding in dict.fromkeys((charset, "utf-8-sig", "cp949")):
        if not encoding:
            continue
        try:
            return body.decode(encoding)
        except (LookupError, UnicodeError):
            continue
    return body.decode("utf-8", errors="backslashreplace")


def result_fields(body_text: str) -> list[tuple[object, object]]:
    """JSON의 최상위/head RESULT와, 오류가 XML로 온 경우의 RESULT를 찾는다."""
    found = []
    try:
        payload = json.loads(body_text.lstrip("\ufeff"))
    except json.JSONDecodeError:
        try:
            root = ElementTree.fromstring(body_text)
        except (ElementTree.ParseError, ValueError):
            return found
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "RESULT":
                fields = {child.tag.rsplit("}", 1)[-1]: child.text for child in element}
                found.append((fields.get("CODE"), fields.get("MESSAGE")))
        return found

    def visit(value: object) -> None:
        if isinstance(value, dict):
            result = value.get("RESULT")
            if isinstance(result, dict):
                found.append((result.get("CODE"), result.get("MESSAGE")))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    return found


def report_failure(request: Request, key: str, status: int | None,
                   body: bytes | None, charset: str | None, attempt: int,
                   reason: str) -> None:
    """본문은 길이 제한 없이 출력한다. 인증키만 마스킹하며 파일에는 기록하지 않는다."""
    print(f"\n[요청 실패] HTTP {status if status is not None else '응답 없음'}, "
          f"시도 {attempt + 1}/{MAX_RETRIES + 1}: {redact_key(reason, key)}")
    print("[요청 URL · 인증키 마스킹] " + redact_key(request.full_url, key))
    body_text = decode_body(body, charset) if body is not None else ""
    print("[응답 본문 시작 · 인증키만 마스킹]")
    print(redact_key(body_text, key) if body_text else
          ("(응답 본문을 수신하지 못했습니다.)" if body is None else "(빈 응답 본문)"))
    print("[응답 본문 끝]")
    results = result_fields(body_text) if body_text else []
    if not results:
        print("RESULT.CODE: (찾을 수 없음)")
        print("RESULT.MESSAGE: (찾을 수 없음 — 위 원문 확인)")
    for index, (code, message) in enumerate(results, start=1):
        print(f"[RESULT {index}]")
        print("RESULT.CODE: " + redact_key(str(code) if code is not None else "(없음)", key))
        print("RESULT.MESSAGE: " + redact_key(str(message) if message is not None else "(없음)", key))
    sys.stdout.flush()


def unpack_page(payload: dict, service: str) -> tuple[list[dict], int]:
    """HTTP 200 응답 안의 NEIS 오류와 head/row를 따로 확인한다."""
    if not isinstance(payload, dict):
        raise CollectionError(f"{service}: JSON 최상위 형식을 확인하세요.")
    if "RESULT" in payload:
        code = api_code(payload["RESULT"])
        if code == "INFO-200":
            return [], 0
        raise CollectionError(f"{service}: NEIS 응답 코드 {code}. 인증키·명세·서비스 상태를 확인하세요.")
    blocks = payload.get(service)
    if not isinstance(blocks, list):
        raise CollectionError(f"{service}: 응답에 서비스 목록이 없습니다.")
    total = None
    rows = None
    for block in blocks:
        if not isinstance(block, dict):
            raise CollectionError(f"{service}: 응답 블록 형식이 다릅니다.")
        heads = block.get("head", [])
        if not isinstance(heads, list) or not all(isinstance(head, dict) for head in heads):
            raise CollectionError(f"{service}: head 형식이 다릅니다.")
        for head in heads:
            if "RESULT" in head and api_code(head["RESULT"]) != "INFO-000":
                raise CollectionError(f"{service}: NEIS 응답 코드 {api_code(head['RESULT'])}.")
            if "list_total_count" in head:
                try:
                    total = int(head["list_total_count"])
                except (TypeError, ValueError):
                    raise CollectionError(f"{service}: 전체 건수가 정수가 아닙니다.") from None
        if "row" in block:
            rows = block["row"]
    if total is None or total < 0 or not isinstance(rows, list):
        raise CollectionError(f"{service}: head의 전체 건수 또는 row 목록이 없습니다.")
    if not all(isinstance(row, dict) for row in rows):
        raise CollectionError(f"{service}: 행 형식이 다릅니다.")
    return rows, total


class NeisClient:
    def __init__(self, key: str, page_size: int, interval: float):
        self.key = key
        self.page_size = page_size
        self.interval = interval
        self.next_request_at = 0.0
        self.calls = 0

    def page(self, service: str, filters: dict, page_index: int,
             *, page_size: int | None = None) -> tuple[list[dict], int]:
        # dict 삽입 순서를 urlencode가 유지하도록 학교 요청의 순서를 명시한다.
        params = {"Type": "json"}
        for name in ("ATPT_OFCDC_SC_CODE", "SCHUL_NM", "SCHUL_KND_SC_NM"):
            if name in filters:
                params[name] = filters[name]
        for name, value in filters.items():
            if name not in params and name not in {"KEY", "pIndex", "pSize"}:
                params[name] = value
        if self.key:
            params["KEY"] = self.key
        elif page_index != 1:
            raise RequestFailure("무인증 조회는 첫 페이지만 허용합니다. 전체 수집에는 인증키가 필요합니다.")
        params["pIndex"] = page_index
        if service == "schoolInfo":
            params["pSize"] = SCHOOL_PAGE_SIZE
        elif not self.key:
            params["pSize"] = 5
        else:
            params["pSize"] = self.page_size if page_size is None else page_size
        return self._request_page(service, params)

    def minimal_school(self) -> tuple[list[dict], int]:
        # page()를 거치지 않아 학교급·pIndex·pSize가 자동으로 추가되지 않는다.
        params = {
            "Type": "json",
            "ATPT_OFCDC_SC_CODE": OFFICE_CODE,
            "SCHUL_NM": MINIMAL_SCHOOL,
        }
        if self.key:
            params["KEY"] = self.key
        return self._request_page("schoolInfo", params, show_response=True)

    def _request_page(self, service: str, params: dict,
                      *, show_response: bool = False) -> tuple[list[dict], int]:
        # 한글 학교명도 urlencode로 인코딩한다. 실패 진단에는 마스킹한 URL만 출력한다.
        request = Request(API_BASE + service + "?" + urlencode(params),
                          headers=REQUEST_HEADERS)
        if show_response:
            print("[요청 URL · 인증키 마스킹] " + redact_key(request.full_url, self.key))
        for attempt in range(MAX_RETRIES + 1):
            time.sleep(max(0.0, self.next_request_at - time.monotonic()))
            self.calls += 1
            retry_reason = ""
            status = None
            body = None
            charset = None
            try:
                with urlopen(request, timeout=TIMEOUT) as response:
                    status = response.status
                    charset = response.headers.get_content_charset()
                    body = response.read()
                    payload = json.loads(decode_body(body, charset).lstrip("\ufeff"))
                result = unpack_page(payload, service)
                if show_response:
                    print(f"[최소 요청 응답] HTTP {status}")
                    print("[응답 본문 시작 · 인증키만 마스킹]")
                    print(redact_key(decode_body(body, charset), self.key))
                    print("[응답 본문 끝]")
                return result
            except HTTPError as error:
                status = error.code
                charset = error.headers.get_content_charset() if error.headers is not None else None
                detail = f"HTTP {status}"
                try:
                    # HTTPError도 응답 스트림이다. close 전에 끝까지 읽어 원인을 보존한다.
                    body = error.read()
                except IncompleteRead as read_error:
                    body = read_error.partial
                    detail += " — 연결이 끊겨 수신된 본문 일부만 표시"
                except (OSError, HTTPException):
                    detail += " — 응답 본문 읽기 실패"
                finally:
                    error.close()
                report_failure(request, self.key, status, body, charset, attempt, detail)
                # 429/503이어도 HTML·XML·빈 본문 등 JSON이 아닌 응답은 즉시 중단한다.
                if body is not None:
                    try:
                        json.loads(decode_body(body, charset).lstrip("\ufeff"))
                    except (UnicodeError, json.JSONDecodeError):
                        raise RequestFailure(f"{service}: HTTP {status}, JSON이 아닌 응답입니다. 재시도 없이 중단합니다.") from None
                if status not in {429, 503}:
                    raise RequestFailure(f"{service}: HTTP {status}. 재시도 대상이 아닙니다. 위 진단을 확인하세요.") from None
                retry_reason = f"HTTP {status}"
            except IncompleteRead as error:
                body = error.partial
                retry_reason = "응답 본문 수신 중 연결 끊김"
                report_failure(request, self.key, status, body, charset, attempt,
                               retry_reason + " — 수신된 본문 일부만 표시")
                raise RequestFailure(f"{service}: 불완전한 응답입니다. 재시도 없이 중단합니다.") from None
            except TimeoutError:
                retry_reason = "네트워크 타임아웃"
                report_failure(request, self.key, status, body, charset, attempt, retry_reason)
            except URLError as error:
                # DNS·인증서·연결 거부 등의 오류를 타임아웃으로 오인하지 않는다.
                timed_out = isinstance(error.reason, TimeoutError)
                retry_reason = "네트워크 타임아웃" if timed_out else "네트워크 연결 실패"
                report_failure(request, self.key, status, body, charset, attempt, retry_reason)
                if not timed_out:
                    raise RequestFailure(f"{service}: 타임아웃 이외의 연결 오류입니다. 재시도 없이 중단합니다.") from None
            except (OSError, HTTPException):
                report_failure(request, self.key, status, body, charset, attempt, "연결·응답 읽기 실패")
                raise RequestFailure(f"{service}: 재시도 대상이 아닌 연결·응답 오류입니다.") from None
            except (UnicodeError, json.JSONDecodeError):
                report_failure(request, self.key, status, body, charset, attempt, "JSON 해석 실패")
                raise RequestFailure(f"{service}: JSON이 아닌 응답입니다. 재시도 없이 중단합니다.") from None
            except CollectionError as error:
                # HTTP 200이어도 RESULT 업무 오류·응답 형식 오류이면 원문을 표시한다.
                report_failure(request, self.key, status, body, charset, attempt, str(error))
                raise RequestFailure(str(error)) from None
            finally:
                self.next_request_at = time.monotonic() + self.interval
            if attempt == MAX_RETRIES:
                raise RequestFailure(f"{service}: {retry_reason}, 재시도 한도에 도달했습니다.") from None
            delay = max(self.interval, 2 ** (attempt + 1))
            print(f"[재시도] {service}, {retry_reason}, {delay:g}초 후 ({attempt + 1}/{MAX_RETRIES})")
            self.next_request_at = time.monotonic() + delay
        raise CollectionError("요청을 완료하지 못했습니다.")

    def iter_pages(self, service: str, filters: dict, label: str) -> Iterator[list[dict]]:
        """페이지 누계를 검증하며 한 페이지씩 전달한다. 전체 원문을 누적하지 않는다."""
        if not self.key:
            raise CollectionError("기간 전체 조회에는 인증키가 필요합니다. 무인증 표본으로 건수를 확정하지 않습니다.")
        count = 0
        expected = None
        page_index = 1
        page_size = SCHOOL_PAGE_SIZE if service == "schoolInfo" else self.page_size
        while True:
            rows, total = self.page(service, filters, page_index, page_size=page_size)
            if expected is None:
                expected = total
            elif total != expected:
                raise CollectionError(f"{label}: 수집 중 전체 건수가 바뀌었습니다. 나중에 다시 실행하세요.")
            if len(rows) > page_size:
                raise CollectionError(f"{label}: 요청 크기보다 많은 행이 반환되었습니다.")
            count += len(rows)
            if count > expected or (not rows and count != expected):
                raise CollectionError(f"{label}: 전체 건수와 페이지 누계가 일치하지 않습니다.")
            if count < expected and len(rows) < page_size:
                raise CollectionError(f"{label}: 전체 건수 전에 짧은 페이지가 왔습니다. 키와 pSize 제한을 확인하세요.")
            print(f"[조회] {label}, 페이지 {page_index}, {len(rows)}행, 누계 {count}/{expected}")
            yield rows
            if count == expected:
                return
            page_index += 1

    def all_rows(self, service: str, filters: dict, label: str) -> list[dict]:
        return [row for page in self.iter_pages(service, filters, label) for row in page]


def text_value(row: dict, field: str) -> str:
    value = row.get(field)
    return "" if value is None else str(value)


def require_fields(row: dict, fields: tuple[str, ...], label: str) -> None:
    missing = [name for name in fields if not text_value(row, name).strip()]
    if missing:
        raise CollectionError(f"{label}: 필수 컬럼이 없거나 비어 있습니다: {', '.join(missing)}")


def find_school(client: NeisClient, name: str, *, single_page: bool = False) -> dict:
    filters = {"ATPT_OFCDC_SC_CODE": OFFICE_CODE,
               "SCHUL_NM": name, "SCHUL_KND_SC_NM": "고등학교"}
    if single_page:
        limit = SCHOOL_PAGE_SIZE if client.key else 5
        rows, total = client.page("schoolInfo", filters, 1, page_size=SCHOOL_PAGE_SIZE)
        if len(rows) != total or total > limit:
            raise CollectionError(f"{name}: 학교 조회 한 페이지가 완전하지 않습니다. 키·학교명을 확인하세요.")
    else:
        rows = client.all_rows("schoolInfo", filters, name + " 학교 조회")
    matches = [row for row in rows if text_value(row, "SCHUL_NM").strip() == name
               and text_value(row, "ATPT_OFCDC_SC_CODE") == OFFICE_CODE
               and text_value(row, "SCHUL_KND_SC_NM") == "고등학교"
               and text_value(row, "ORG_RDNMA").startswith(ADDRESS_PREFIX)]
    if len(matches) != 1:
        raise CollectionError(f"{name}: 서울 고등학교의 정확한 후보가 {len(matches)}개입니다. 학교명을 확인하세요.")
    require_fields(matches[0], REQUIRED_SCHOOL, name)
    expected_code = CONFIRMED_SCHOOL_CODES.get(name)
    if expected_code and text_value(matches[0], "SD_SCHUL_CODE") != expected_code:
        raise CollectionError(f"{name}: 사용자 확정 학교코드 {expected_code}와 다릅니다. 학교 조회 결과를 확인하세요.")
    return matches[0]


def prepare_meals(rows: list[dict], school: dict, start: date, end: date) -> list[dict]:
    result = []
    seen = set()
    name = school["SCHUL_NM"]
    for row in rows:
        require_fields(row, REQUIRED_MEAL, name)
        code = text_value(row, "SD_SCHUL_CODE")
        meal_code = text_value(row, "MMEAL_SC_CODE")
        if (text_value(row, "ATPT_OFCDC_SC_CODE") != OFFICE_CODE
                or code != text_value(school, "SD_SCHUL_CODE")
                or text_value(row, "SCHUL_NM") != name):
            raise CollectionError(f"{name}: 다른 학교의 급식 행이 반환되었습니다.")
        if meal_code not in {"1", "2", "3"}:
            raise CollectionError(f"{name}: 식사코드가 1·2·3 이외의 값입니다. 명세를 확인하세요.")
        try:
            day = datetime.strptime(text_value(row, "MLSV_YMD"), "%Y%m%d").date()
        except ValueError:
            raise CollectionError(f"{name}: 급식일자는 YYYYMMDD여야 합니다.") from None
        if not start <= day <= end:
            raise CollectionError(f"{name}: 요청 기간 밖의 급식이 반환되었습니다. 날짜 필터를 확인하세요.")
        identity = (OFFICE_CODE, code, day, meal_code)
        if identity in seen:
            raise CollectionError(f"{name}: {day} 식사코드 {meal_code} 중복. 임의 삭제하지 않고 중단합니다.")
        seen.add(identity)
        record = {public: text_value(row, source) for source, public in MEAL_COLUMNS.items()}
        record["급식일자"] = day.isoformat()
        record["요일"] = WEEKDAY_NAMES[day.weekday()]
        # DDISH_NM은 문자열 원문 그대로 둔다. 태그 제거·알레르기 번호 분리·메뉴 분할은 4~5주차 학생 실습이다.
        # 학교별 식사/방학 운영 차이를 통합하거나 중식만 남기는 필터도 적용하지 않는다.
        result.append(record)
    return result


def check_availability(client: NeisClient) -> bool:
    """학교 1회 + 지정 날짜별 1회만 요청한다. 파일 생성·저장·추가 날짜 조회 없음."""
    days = [date.fromisoformat(value) for value in CHECK_DATES]
    started = time.monotonic()
    errors = []
    school_codes = set()
    print(f"[사전 확인] 현재 후보 {len(CANDIDATE_SCHOOLS)}개교(기본 4개교+예비), 날짜별 하루만 조회, CSV 저장 없음")
    print("[기준] 있음(조·중·석)은 해당 날짜에 반환된 식사 종류입니다.")
    print("[주의] 없음은 해당 날짜의 응답 0건입니다. 방학·급식 미운영 가능성이 있어 월 전체 부재로 판단하지 않습니다.")
    print("| 학교명 | 코드 조회 성공 | 표준학교코드 | " + " | ".join(CHECK_DATES) + " |", flush=True)
    print("| --- | --- | --- | " + " | ".join("---" for _ in days) + " |", flush=True)
    for name in CANDIDATE_SCHOOLS:
        try:
            school = find_school(client, name, single_page=True)
            code = text_value(school, "SD_SCHUL_CODE")
            if code in school_codes:
                raise CollectionError(f"{name}: 다른 후보와 표준학교코드가 같습니다.")
            school_codes.add(code)
        except RequestFailure:
            raise
        except CollectionError as error:
            errors.append(str(error))
            print(f"| {name} | 실패 | — | " + " | ".join("조회 안 함" for _ in days) + " |", flush=True)
            continue
        results = []
        for day in days:
            try:
                # FROM=TO로 정확히 하루만 요청한다. 식사코드를 제한하지 않아 조·중·석을 함께 확인한다.
                rows, total = client.page("mealServiceDietInfo", {
                    "ATPT_OFCDC_SC_CODE": OFFICE_CODE, "SD_SCHUL_CODE": code,
                    "MLSV_FROM_YMD": day.strftime("%Y%m%d"),
                    "MLSV_TO_YMD": day.strftime("%Y%m%d"),
                }, 1, page_size=3)
                if len(rows) != total or total > 3:
                    raise CollectionError("하루 조회 건수가 3건을 초과하거나 응답이 불완전합니다. 날짜 필터·명세를 확인하세요.")
                prepared = prepare_meals(rows, school, day, day)
                meal_codes = {row["식사코드"] for row in prepared}
                kinds = "·".join(label for meal_code, label in (("1", "조"), ("2", "중"), ("3", "석"))
                                 if meal_code in meal_codes)
                results.append(f"있음({kinds})" if prepared else "없음")
            except RequestFailure:
                raise
            except CollectionError as error:
                results.append("확인 실패")
                errors.append(f"{name} {day}: {error}")
        print(f"| {name} | 성공 | {code} | " + " | ".join(results) + " |", flush=True)
    for error in errors:
        print(f"[확인 실패] {error}")
    print(f"[사전 확인 완료] HTTP 요청 {client.calls}회, {time.monotonic() - started:.1f}초. CSV를 저장하지 않았습니다.")
    print("[다음] --count로 확정한 4개교의 기간 전체 고유 급식일을 확인하세요. 하루 조회로 150일 이상을 보장할 수는 없습니다.")
    return not errors


def count_meals(client: NeisClient, names: list[str], start: date, end: date) -> None:
    """전체 기간을 조회하되 날짜·식별키·건수만 누적하고 파일은 저장하지 않는다."""
    started = time.monotonic()
    summaries = []
    school_codes = set()
    print(f"[규모 확인] {start} ~ {end}, {len(names)}개교, 모든 식사 종류, CSV 저장 없음")
    for name in names:
        school = find_school(client, name)
        code = text_value(school, "SD_SCHUL_CODE")
        if code in school_codes:
            raise CollectionError("서로 다른 학교에 같은 코드가 반환되었습니다. 건수를 확정하지 않습니다.")
        school_codes.add(code)
        days, seen = set(), set()
        by_meal, by_month = Counter(), Counter()
        total = 0
        # 식사코드를 요청 조건에 넣지 않는다. 조·중·석을 모두 조회한다.
        for page in client.iter_pages("mealServiceDietInfo", {
            "ATPT_OFCDC_SC_CODE": OFFICE_CODE, "SD_SCHUL_CODE": code,
            "MLSV_FROM_YMD": start.strftime("%Y%m%d"),
            "MLSV_TO_YMD": end.strftime("%Y%m%d"),
        }, name + " 급식 규모"):
            for row in prepare_meals(page, school, start, end):
                day, meal = row["급식일자"], row["식사코드"]
                identity = (day, meal)
                if identity in seen:
                    raise CollectionError(f"{name}: {day} 식사코드 {meal}가 페이지 간 중복입니다. 건수를 확정하지 않습니다.")
                seen.add(identity)
                days.add(day)
                by_meal[meal] += 1
                by_month[day[:7]] += 1
                total += 1
        summaries.append({"name": name, "code": code, "total": total,
                          "days": len(days), "meals": by_meal, "months": by_month})

    print("\n| 학교명 | 학교코드 | 총 건수 | 고유 급식일 수 | 조식 건수 | 중식 건수 | 석식 건수 | 150일 기준 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in summaries:
        meals = item["meals"]
        verdict = "충족" if item["days"] >= MIN_MEAL_DAYS else "미달"
        print(f"| {item['name']} | {item['code']} | {item['total']} | {item['days']} | "
              f"{meals['1']} | {meals['2']} | {meals['3']} | {verdict} |")

    print("\n[월별 건수] 모든 식사 행의 수이며, 조회 결과 0건인 달도 표시합니다.")
    print("| 월 | " + " | ".join(item["name"] for item in summaries) + " |")
    print("| --- | " + " | ".join("---" for _ in summaries) + " |")
    month = start.replace(day=1)
    while month <= end:
        label = month.strftime("%Y-%m")
        print(f"| {label} | " + " | ".join(str(item["months"][label]) for item in summaries) + " |")
        month = date(month.year + 1, 1, 1) if month.month == 12 else date(month.year, month.month + 1, 1)

    below = [item["name"] for item in summaries if item["days"] < MIN_MEAL_DAYS]
    if below:
        print(f"[확인 필요] 고유 급식일 {MIN_MEAL_DAYS}일 미달: {', '.join(below)}. 기간 또는 대상 학교 조정을 검토하세요.")
    else:
        print(f"[기준 충족] 모든 대상 학교의 고유 급식일이 {MIN_MEAL_DAYS}일 이상입니다.")
    print("[해석] 같은 날 조·중·석식 3건이 있어도 고유 급식일은 1일입니다. 월별 0건의 원인은 별도 확인하세요.")
    print(f"[규모 확인 완료] HTTP 요청 {client.calls}회, {time.monotonic() - started:.1f}초. 파일을 저장하지 않았습니다.")


def report_meals(name: str, rows: list[dict]) -> None:
    days = sorted({row["급식일자"] for row in rows})
    print(f"[요약] {name}: {len(rows)}행, 고유 급식일 {len(days)}일, {days[0]} ~ {days[-1]}")
    for code, label in (("1", "조식"), ("2", "중식"), ("3", "석식")):
        count = len({row["급식일자"] for row in rows if row["식사코드"] == code})
        print(f"  {label}: {count}일")
    by_month = Counter(row["급식일자"][:7] for row in rows)
    print("  월별 행 수: " + ", ".join(f"{month}={count}" for month, count in sorted(by_month.items())))
    if len(days) < MIN_MEAL_DAYS:
        print(f"[확인 필요] {name}: {MIN_MEAL_DAYS}일 미만입니다. 13주차 사용 전 제공 기간과 누락을 확인하세요.")
    print("  빈 값: " + ", ".join(f"{col}={sum(not row[col].strip() for row in rows)}"
          for col in MEAL_OUTPUT_COLUMNS))


def write_outputs(output_dir: Path, schools: list[dict], meals: list[dict], overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = (("schools.csv", schools, list(SCHOOL_COLUMNS.values())),
               ("meals.csv", meals, list(MEAL_OUTPUT_COLUMNS)))
    if not overwrite and any((output_dir / name).exists() for name, _, _ in outputs):
        raise CollectionError("출력 파일이 이미 있습니다. 검토 후 --overwrite로 다시 실행하세요.")
    # 두 파일을 모두 인코딩·작성한 다음 배치한다. 수집 실패 중에는 기존 CSV를 건드리지 않는다.
    with TemporaryDirectory(prefix="neis-", dir=output_dir) as temporary:
        for name, records, columns in outputs:
            with (Path(temporary) / name).open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=columns)
                writer.writeheader()
                writer.writerows(records)
        for name, _, _ in outputs:
            os.replace(Path(temporary) / name, output_dir / name)


def clean_key(value: str) -> str:
    """복사 중 섞인 공백·개행·탭·따옴표·BOM을 제거한다."""
    copy_marks = {"'", '"', "‘", "’", "“", "”", "\ufeff"}
    return "".join(char for char in value if not char.isspace() and char not in copy_marks)


def read_key() -> str:
    key = clean_key(os.environ.get(KEY_ENV, ""))
    if not key:
        if not sys.stdin.isatty():
            raise CollectionError(f"대화형 터미널에서 실행하거나 환경변수 {KEY_ENV}를 설정하세요.")
        key = clean_key(getpass.getpass("NEIS 교사 인증키 (화면에 표시하지 않음): "))
    print(f"[인증키] 정제 후 길이: {len(key)}자 (값은 출력하지 않습니다)")
    if len(key) != EXPECTED_KEY_LENGTH:
        print(f"[경고] 인증키는 보통 {EXPECTED_KEY_LENGTH}자입니다. 복사한 내용을 확인하세요.")
    if not key or key.lower() in {"sample", "samplekey"} or "여기에" in key:
        raise CollectionError("유효한 교사 인증키를 입력하거나 --check --no-key로 사전 확인하세요.")
    return key


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="현재 후보(기본 4개교+예비)·CHECK_DATES만 조회, CSV 저장 없음")
    mode.add_argument("--minimal", action="store_true",
                      help="동양고 학교정보에 Type·교육청·학교명·KEY만 전송, 응답 출력 후 종료")
    mode.add_argument("--count", action="store_true",
                      help="4개교의 기간 전체 건수·고유 급식일·식사별/월별 건수만 출력, 파일 저장 없음")
    parser.add_argument("--no-key", action="store_true",
                        help="--check/--minimal 전용: 키 입력·환경변수 읽기·KEY 전송 없이 조회")
    parser.add_argument("--schools", nargs="+", default=list(DEFAULT_SCHOOLS), metavar="학교명",
                        help="규모 확인/전체 수집: 현재 후보 중 동양고를 포함한 4개교")
    parser.add_argument("--start", default=START_DATE, help="YYYY-MM-DD")
    parser.add_argument("--end", default=END_DATE, help="YYYY-MM-DD")
    parser.add_argument("--page-size", type=int, default=PAGE_SIZE, help="전체 급식 수집 1~1000, 학교 조회는 10")
    parser.add_argument("--interval", type=float, default=REQUEST_INTERVAL, help="요청 종료 후 간격(초), 최소 1")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "neis")
    parser.add_argument("--overwrite", action="store_true", help="검토한 기존 두 CSV를 교체")
    args = parser.parse_args()
    if not math.isfinite(args.interval) or args.interval < 1:
        raise CollectionError("interval은 유한한 1초 이상이어야 합니다.")
    if args.no_key and not (args.check or args.minimal):
        raise CollectionError("--no-key는 --check 또는 --minimal과 함께 사용하세요. --count와 전체 수집에는 인증키가 필요합니다.")
    if args.minimal:
        key = "" if args.no_key else read_key()
        if args.no_key:
            print("[무인증 최소 요청] KEY를 제외한 3개 파라미터만 전송합니다.")
        else:
            print("[최소 요청] Type·ATPT_OFCDC_SC_CODE·SCHUL_NM·KEY만 전송합니다.")
        client = NeisClient(key, SCHOOL_PAGE_SIZE, args.interval)
        rows, total = client.minimal_school()
        print(f"[최소 요청 완료] {MINIMAL_SCHOOL}, 반환 {len(rows)}행, 응답 전체 건수 {total}, HTTP 요청 {client.calls}회")
        print("[종료] 다른 학교·급식은 요청하지 않았으며 CSV를 저장하지 않았습니다.")
        return
    if args.check:
        # 전체 수집의 학교/기간/페이지/출력 옵션과 무관하게 후보 전체를 확인한다.
        # 기존 CSV 존재 여부도 확인하지 않으며, 아래 저장 경로로 진행하지 않는다.
        key = "" if args.no_key else read_key()
        if args.no_key:
            print("[무인증] 키를 읽거나 입력받지 않으며 KEY 파라미터를 전송하지 않습니다. 최대 5건만 확인합니다.")
        client = NeisClient(key, PAGE_SIZE, args.interval)
        if not check_availability(client):
            raise CollectionError("사전 확인 표에 실패 항목이 있습니다. 위 오류를 확인하세요. CSV는 저장하지 않았습니다.")
        return
    try:
        start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    except ValueError:
        raise CollectionError("기간은 YYYY-MM-DD 형식이어야 합니다.") from None
    if start > end:
        raise CollectionError("시작일이 종료일보다 늦습니다.")
    if not 1 <= args.page_size <= 1000:
        raise CollectionError("page-size는 1~1000이어야 합니다.")
    if (len(args.schools) != 4 or len(set(args.schools)) != 4
            or "동양고등학교" not in args.schools
            or not set(args.schools) <= set(CANDIDATE_SCHOOLS)):
        raise CollectionError("현재 후보 중 중복 없이 동양고등학교를 포함한 4개교를 지정하세요.")
    if args.count:
        client = NeisClient(read_key(), args.page_size, args.interval)
        count_meals(client, args.schools, start, end)
        return  # 출력 파일 존재 검사·폴더/CSV 생성 경로로 진행하지 않는다.
    if not args.overwrite and any((args.output_dir / name).exists() for name in ("schools.csv", "meals.csv")):
        raise CollectionError("기존 출력이 있습니다. 검토 후 --overwrite를 지정하세요. API 요청 전 중단합니다.")
    client = NeisClient(read_key(), args.page_size, args.interval)
    started = time.monotonic()
    print(f"[범위] {start} ~ {end}, {len(args.schools)}개교, 전체 식사 종류")
    print("[주의] 공식 급식 안내는 현재년도 자료입니다. 과거 기간의 제공 여부를 확인합니다.")
    schools, meals = [], []
    school_codes = set()
    for name in args.schools:
        school = find_school(client, name)
        code = text_value(school, "SD_SCHUL_CODE")
        if code in school_codes:
            raise CollectionError("서로 다른 학교 이름에 같은 표준학교코드가 반환되었습니다.")
        school_codes.add(code)
        print(f"[학교] {name}, {OFFICE_CODE}/{code}")
        records = client.all_rows("mealServiceDietInfo", {
            "ATPT_OFCDC_SC_CODE": OFFICE_CODE, "SD_SCHUL_CODE": code,
            "MLSV_FROM_YMD": start.strftime("%Y%m%d"),
            "MLSV_TO_YMD": end.strftime("%Y%m%d"),
        }, name + " 급식")
        if not records:
            raise CollectionError(f"{name}: 기간 내 급식이 없습니다. 과거 자료 제공 여부를 확인하세요. CSV는 저장하지 않습니다.")
        prepared = prepare_meals(records, school, start, end)
        report_meals(name, prepared)
        schools.append({public: text_value(school, source) for source, public in SCHOOL_COLUMNS.items()})
        meals.extend(prepared)
    schools.sort(key=lambda row: row["표준학교코드"])
    meals.sort(key=lambda row: (row["표준학교코드"], row["급식일자"], row["식사코드"]))
    write_outputs(args.output_dir, schools, meals, args.overwrite)
    collected_at = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")
    print(f"[저장] schools.csv {len(schools)}행 × {len(SCHOOL_COLUMNS)}열 / meals.csv {len(meals)}행 × {len(MEAL_OUTPUT_COLUMNS)}열")
    print(f"[완료] {collected_at}, HTTP 요청 {client.calls}회, {time.monotonic() - started:.1f}초")
    print("[확인] 학교별 150일·중식 일수·월별 범위를 검토하고 data/README.md에 실측 결과를 기록하세요.")


if __name__ == "__main__":
    try:
        main()
    except CollectionError as error:
        raise SystemExit(f"수집 중단: {error}") from None
    except (OSError, EOFError, KeyboardInterrupt):
        raise SystemExit("수집 중단: 연결·파일 접근·입력 상태를 확인하세요. 진단 출력의 인증키는 마스킹합니다.") from None

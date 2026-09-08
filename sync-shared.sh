#!/usr/bin/env bash
# 템플릿의 공통 파일만 강의 저장소에 복사합니다. Bash / Git Bash에서 실행하세요.
# 사용법: ./sync-shared.sh ../ai-squat-king
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf '사용법: %s ../<강의저장소>\n' "$0" >&2
  exit 1
fi

if [[ ! -d "$1" ]]; then
  printf '오류: 대상 디렉터리가 없습니다: %s\n' "$1" >&2
  exit 1
fi

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
target_dir="$(cd -- "$1" && pwd -P)"
if [[ "$source_dir" == "$target_dir" ]]; then
  printf '오류: 템플릿 자신을 동기화 대상으로 지정할 수 없습니다.\n' >&2
  exit 1
fi

# 이 목록에 강의별 파일을 추가하지 않습니다. data/site.js는 수동 병합 대상입니다.
shared_files=(
  "DESIGN.md"
  "assets/css/tokens.css"
  "assets/css/base.css"
  "assets/js/shared.js"
)
changed_files=()

# 대상 안의 링크를 통해 다른 저장소로 쓰지 않도록 복사 전 경로를 확인합니다.
for directory in "assets" "assets/css" "assets/js"; do
  if [[ -L "$target_dir/$directory" || ( -e "$target_dir/$directory" && ! -d "$target_dir/$directory" ) ]]; then
    printf '오류: 대상 경로가 일반 디렉터리가 아닙니다: %s\n' "$target_dir/$directory" >&2
    exit 1
  fi
done

for file in "${shared_files[@]}"; do
  if [[ ! -f "$source_dir/$file" ]]; then
    printf '오류: 공통 원본 파일이 없습니다: %s\n' "$source_dir/$file" >&2
    exit 1
  fi
  if [[ -L "$target_dir/$file" || ( -e "$target_dir/$file" && ! -f "$target_dir/$file" ) ]]; then
    printf '오류: 대상이 일반 파일이 아닙니다: %s\n' "$target_dir/$file" >&2
    exit 1
  fi
done

printf '템플릿: %s\n대상: %s\n' "$source_dir" "$target_dir"
for file in "${shared_files[@]}"; do
  old_file="$target_dir/$file"
  [[ -f "$old_file" ]] || old_file="/dev/null"
  diff_status=0
  diff -u -- "$old_file" "$source_dir/$file" || diff_status=$?
  case "$diff_status" in
    0) ;;
    1) changed_files+=("$file") ;;
    *) printf '오류: diff 실행 실패: %s\n' "$file" >&2; exit "$diff_status" ;;
  esac
done

if [[ ${#changed_files[@]} -eq 0 ]]; then
  printf '이미 최신 상태입니다. 변경할 파일이 없습니다.\n'
  exit 0
fi

printf '\n위 diff의 공통 파일 %s개를 복사할까요? [y/n] ' "${#changed_files[@]}"
answer=""
if ! IFS= read -r answer; then
  printf '\n입력이 없어 취소했습니다. 파일을 변경하지 않았습니다.\n'
  exit 0
fi
case "$answer" in
  y|Y)
    for file in "${changed_files[@]}"; do
      mkdir -p -- "$(dirname -- "$target_dir/$file")"
      cp -- "$source_dir/$file" "$target_dir/$file"
      printf '복사 완료: %s\n' "$file"
    done
    ;;
  *) printf '취소했습니다. 파일을 변경하지 않았습니다.\n' ;;
esac

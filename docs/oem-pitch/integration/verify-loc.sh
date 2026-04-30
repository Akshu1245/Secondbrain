#!/usr/bin/env bash
# Reproduce the "drops in under 150 LOC" pitch number.
#
# Output is the total *semantic* lines of code an OEM integration team
# adds to their AI-assistant launcher to ship AOL — i.e. AolClient.kt
# (Kotlin) plus IAolMiddleware.aidl (AIDL). Block comments and the
# end-of-file usage example are excluded; that matches how a code-review
# tool like `cloc` counts.
#
# Usage: ./verify-loc.sh        (from this directory or the repo root)
#
# Numbers as of last verification:
#   AolClient.kt        : 125 code  (cloc)
#   IAolMiddleware.aidl :   6 code  (manual; cloc has no AIDL grammar)
#   Total integration   : 131 LOC
set -euo pipefail

dir="$(cd "$(dirname "$0")" && pwd)"
kt="${dir}/AolClient.kt"
aidl="${dir}/IAolMiddleware.aidl"

count_aidl_code() {
  # Strip /* ... */ block comments, then drop blank + // line-comment lines.
  python3 - "$1" <<'PY'
import re, sys
src = open(sys.argv[1]).read()
src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
code = sum(
    1
    for ln in src.splitlines()
    if ln.strip() and not ln.strip().startswith("//")
)
print(code)
PY
}

if command -v cloc >/dev/null 2>&1; then
  kt_code="$(cloc --csv --quiet "$kt" 2>/dev/null | awk -F, '/Kotlin/ {print $5}')"
else
  kt_code="$(count_aidl_code "$kt")"
fi
aidl_code="$(count_aidl_code "$aidl")"
total="$(( kt_code + aidl_code ))"

printf '%-32s %s\n' "AolClient.kt"        "$kt_code"
printf '%-32s %s\n' "IAolMiddleware.aidl" "$aidl_code"
printf '%-32s %s\n' "Total integration LOC" "$total"

if [ "$total" -lt 150 ]; then
  echo "OK: under 150 LOC."
  exit 0
fi
echo "WARNING: integration LOC is no longer under 150 (total ${total})."
exit 1

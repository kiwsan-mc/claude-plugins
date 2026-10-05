#!/usr/bin/env bash
# Resolve a Python interpreter and run the answer-term guard.
#
# FAIL OPEN. Every path out of this script that is not a clean run exits 0, so a
# missing or broken interpreter lets the answer through instead of stalling it.
#
# Interpreter order matters on Windows: `python` and `python3` are often the
# Microsoft Store stub, which can hang. The `py` launcher is the reliable one
# there. Set ANSWER_GUARD_PYTHON to pin a specific interpreter (for example the
# one shipped under C:\ProgramData\McGroup\Claude\mcp\python3-standalone).

set -u

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="$here/check_answer_terms_stop.py"

run_with() {
    "$@" "$target"
}

for candidate in "${ANSWER_GUARD_PYTHON:-}" py python3 python; do
    [ -n "$candidate" ] || continue
    command -v "$candidate" >/dev/null 2>&1 || continue
    if [ "$candidate" = "py" ]; then
        run_with py -3 && exit 0
    else
        run_with "$candidate" && exit 0
    fi
    exit 0
done

exit 0

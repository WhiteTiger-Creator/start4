#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Step 1: recover the authoritative registry index (#REG-7170) -----------
# The migration left /app/data/registry_index.json truncated. Merge the
# pre-migration snapshot with the replay journal and write the result back to
# that path; nothing the reconciler emits is correct until this is done.

python3 "${SCRIPT_DIR}/recover_index.py"

# --- Step 2: restore the reconciler and produce the install artifacts -------

cp "${SCRIPT_DIR}/resolver_fixed.py" /app/workflow/resolver.py
python3 /app/workflow/resolver.py --output-dir /app/output

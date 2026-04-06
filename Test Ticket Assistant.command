#!/bin/bash

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 was not found on this Mac."
  echo "Install Python 3 and try again."
  read -r -p "Press Enter to close this window..."
  exit 1
fi

python3 senior_cruise_assistant.py --dry-run
STATUS=$?

echo
if [ "$STATUS" -eq 0 ]; then
  echo "Dry run finished."
else
  echo "Dry run ended with an error."
fi

read -r -p "Press Enter to close this window..."

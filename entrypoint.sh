#!/usr/bin/env bash
set -e
source /opt/pydozor/.venv/bin/activate
if [ -z "$*" ]; then
  exec bash
else
  python /opt/pydozor/dozor_offline.py "$@"
fi

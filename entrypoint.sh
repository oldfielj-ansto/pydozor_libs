#!/usr/bin/env bash
set -e
source /opt/pydozor/.venv/bin/activate
if [ -z "$*" ]; then
  exec bash --login
else
  python /opt/pydozor/dozor_offline.py "$@"
fi

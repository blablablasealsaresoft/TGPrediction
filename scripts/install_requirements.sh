#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
REQ_FILE="${1:-requirements/dev.lock}"
REQ_PATH="${ROOT_DIR}/${REQ_FILE}"
WHEEL_DIR="${ROOT_DIR}/vendor"

if [[ ! -f "${REQ_PATH}" ]]; then
  echo "Requested requirements file '${REQ_PATH}' does not exist" >&2
  exit 1
fi

PIP_ARGS=("-r" "${REQ_PATH}")

if [[ -d "${WHEEL_DIR}" ]] && [[ $(ls -A "${WHEEL_DIR}" 2>/dev/null) ]]; then
  echo "Installing dependencies from vendored wheelhouse at ${WHEEL_DIR}" >&2
  python -m pip install --no-index --find-links "${WHEEL_DIR}" "${PIP_ARGS[@]}"
else
  echo "Vendored wheelhouse empty; falling back to PyPI" >&2
  python -m pip install "${PIP_ARGS[@]}"
fi

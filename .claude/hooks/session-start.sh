#!/bin/bash
# Installs the lightweight test/lint dependencies so that `pytest` and
# `flake8` work in Claude Code on the web sessions. This intentionally uses
# the offline `requirements-test.txt` stack (no Azure/AWS/audio/ML), which is
# all that is needed to run the unit tests and linter.
set -euo pipefail

# Only run in the remote (Claude Code on the web) environment.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# Install the test/lint requirements. Fall back to --break-system-packages
# for externally-managed (PEP 668) Python environments.
python -m pip install -r requirements-test.txt \
  || python -m pip install --break-system-packages -r requirements-test.txt

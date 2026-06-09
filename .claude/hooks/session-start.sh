#!/bin/bash
# Installs the package with its test extras so that `pytest` and `flake8` work
# in Claude Code on the web sessions. The `[test]` extra pulls only the core
# (no Azure/AWS/audio/ML) stack needed to run the unit tests and linter.
set -euo pipefail

# Only run in the remote (Claude Code on the web) environment.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# Install the package + test extras. Fall back to --break-system-packages for
# externally-managed (PEP 668) Python environments.
python -m pip install -e ".[test]" \
  || python -m pip install --break-system-packages -e ".[test]"

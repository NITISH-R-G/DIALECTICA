"""Shim for OpenEnv manifest: `server.contract_app:app`."""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(__file__))
_SRC = os.path.join(_ROOT, "src")
if os.path.isdir(_SRC) and _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from contract_env.server.app import app, main  # noqa: E402,F401


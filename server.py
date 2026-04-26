"""
Compatibility shim for running with:

  uvicorn server:app --reload

The upstream Space uses `server/app.py` and runs `uvicorn server.app:app`.
Your workflow asked specifically for `server.py`, so this file re-exports
the FastAPI `app` from `server.app`.
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(__file__)
_SRC = os.path.join(_ROOT, "src")
if os.path.isdir(_SRC) and _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from echo_env.server.app import app  # noqa: E402


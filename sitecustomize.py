"""
Automatically add the repository's `src/` directory to `sys.path`.

This enables `src`-layout imports (e.g. `import echo_env`) when running code
directly from the repo without installing the package.

Python imports `sitecustomize` automatically when it is present on `sys.path`.
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(__file__)
_SRC = os.path.join(_ROOT, "src")

if os.path.isdir(_SRC) and _SRC not in sys.path:
    sys.path.insert(0, _SRC)


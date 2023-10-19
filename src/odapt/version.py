from __future__ import annotations

import re

__version__ = "1.0.1"
VERSION = __version__ #noqa: C0103
version_info = tuple(re.split(r"[-\.]", __version__))

del re

from __future__ import annotations

import re

__version__ = "1.0.1"
VERSION = __version__ # pylint: disable=invalid-name
version_info = tuple(re.split(r"[-\.]", __version__))

del re

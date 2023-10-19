import re

__version__ = "1.0.1"
version = __version__
version_info = tuple(re.split(r"[-\.]", __version__))

del re

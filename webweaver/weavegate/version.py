# Semantic version components
MAJOR = 0
MINOR = 0
PATCH = 0

# e.g. "alpha", "beta", "rc1", or None
PRE_RELEASE = "MVP-0"

# Version tuple for comparisons
VERSION = (MAJOR, MINOR, PATCH, PRE_RELEASE)

# Construct the string representation
__version__ = f"V{MAJOR}.{MINOR}.{PATCH}"

if PRE_RELEASE:
    __version__ += f"-{PRE_RELEASE}"

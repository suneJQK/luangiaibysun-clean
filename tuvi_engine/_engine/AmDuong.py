"""Core astronomical and palace-position calculations for the local Tu Vi engine."""

# This module is intentionally kept as a standalone calculation module.
# The complete source is copied from the local engine in the source repository.

def timPhaToai(chiNam):
    if chiNam in (1, 4, 7, 10):
        return 6
    elif chiNam in (3, 6, 9, 12):
        return 10
    elif chiNam in (2, 5, 8, 11):
        return 2
    raise Exception("Không tìm được vị trí Phá Toái")

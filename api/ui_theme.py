from __future__ import annotations

from ui_theme import themed_index


def handler(request):
    return themed_index()

app = handler

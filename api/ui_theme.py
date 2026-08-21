from __future__ import annotations

from fastapi import FastAPI

from ui_theme import themed_index

app = FastAPI(title="TV AI themed UI")


@app.get("/")
def root():
    return themed_index()

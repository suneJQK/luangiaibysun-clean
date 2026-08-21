from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from ui_theme import themed_index

app = FastAPI(title="TV AI Root UI")


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    return themed_index()

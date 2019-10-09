"""Application definition."""
from fastapi import FastAPI, Query
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from stilio.frontend import settings as project_settings
from stilio.frontend.pagination import get_pages
from stilio.persistence.torrents import Torrent

app = FastAPI()

app.mount("/static", StaticFiles(directory="stilio/frontend/static"), name="static")
templates = Jinja2Templates(directory="stilio/frontend/templates")


@app.get("/")
async def index(request: Request):
    count = await Torrent.total_torrent_count()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "count": count
    })


@app.get("/search")
async def search(request: Request, query: str = Query(None, max_length=50), page: int = Query(1, gt=0)):
    if not query:
        return RedirectResponse("/")

    torrents, count = await Torrent.search_by_name(
        query,
        limit=project_settings.PAGE_SIZE,
        offset=project_settings.PAGE_SIZE * (page - 1),
    )
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": query,
            "torrents": torrents,
            "count": count,
            "pages": get_pages(count, page),
            "current_page": page
        }
    )

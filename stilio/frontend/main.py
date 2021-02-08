from fastapi import Depends, FastAPI, Query
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from stilio.frontend import settings as project_settings
from stilio.frontend.pagination import get_pages
from stilio.persistence.database import db, db_state_default
from stilio.persistence.torrents.models import Torrent


async def reset_db_state():
    db._state._state.set(db_state_default.copy())
    db._state.reset()


def get_db(db_state=Depends(reset_db_state)):
    try:
        db.connect()
        yield
    finally:
        if not db.is_closed():
            db.close()


app = FastAPI()

app.mount("/static", StaticFiles(directory="stilio/frontend/static"), name="static")
templates = Jinja2Templates(directory="stilio/frontend/templates")


@app.on_event("startup")
def startup():
    db.connect(reuse_if_open=True)


@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()


@app.get("/", dependencies=[Depends(get_db)])
async def index(request: Request):
    count = Torrent.total_torrent_count()
    return templates.TemplateResponse(
        "index.html", {"request": request, "count": count}
    )


@app.get("/search", dependencies=[Depends(get_db)])
async def search(
    request: Request,
    query: str = Query(None, max_length=50),
    page: int = Query(1, gt=0),
):
    if not query or not query.strip():
        return RedirectResponse("/")

    torrents, count = Torrent.search_by_name(
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
            "current_page": page,
        },
    )

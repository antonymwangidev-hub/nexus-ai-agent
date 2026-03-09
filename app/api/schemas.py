from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router

app = FastAPI(
    title="SocialFusion Agent API",
    description="API for generating social media content packs",
    version="1.0.0",
)

app.include_router(router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/ui")
def frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

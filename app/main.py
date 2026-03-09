from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

from app.api.routes import router as api_router
from app.api.live_routes import router as live_router

app = FastAPI(
    title="NEXUS AI Agent API",
    description="Multimodal social content generation platform",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(api_router, prefix="/api")
app.include_router(live_router)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("app/static/nexus-logo.png")


@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/ui")
def frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

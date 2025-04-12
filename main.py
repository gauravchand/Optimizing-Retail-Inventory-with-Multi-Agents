from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.api.routes import router
from app.models.database import init_db
from app.config.constants import CURRENT_USER, CURRENT_DATETIME
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting application as {CURRENT_USER} at {CURRENT_DATETIME}")
    await init_db()
    yield
    # Shutdown
    print("Shutting down application")

app = FastAPI(
    title="Retail Inventory AI",
    description="Multi-agent AI system for retail inventory management",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": CURRENT_USER,
            "current_datetime": CURRENT_DATETIME
        }
    )

# Include API routes
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
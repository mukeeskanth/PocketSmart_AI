from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.routes.page_routes import router as page_router
from app.routes.auth_routes import router as auth_router
from app.routes.planner_routes import router as planner_router

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app=FastAPI(title="PocketSmart AI",
            description="Smart Budget & Recommendation Assistant",
            version="1.0.0",lifespan=lifespan)

app.add_middleware(CORSMiddleware,allow_origins=["*"],
                   allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

app.mount("/static",StaticFiles(directory="app/static"),name="static")
app.include_router(page_router)
app.include_router(auth_router,prefix="/api")
app.include_router(planner_router,prefix="/api")

@app.get("/health")
def health():
    return {"status":"healthy","service":"PocketSmart AI"}

from fastapi import FastAPI
from app.routers.search import router as search_router
from app.routers.sources import router as sources_router

app = FastAPI(title="LifeScience API")

app.include_router(search_router)
app.include_router(sources_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI

from app.routers import auth, dashboard, analysis

app = FastAPI(title="Life Science Data Platform", version="1")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(analysis.router)


@app.get("/")
def root():
    return {"message": "Life Science Data Platform API v1"}

from fastapi import FastAPI

from app.routers import alerts, reports, dashboard, analysis, auth, sources

app = FastAPI(title="Life Science Data Platform", version="1")

app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(auth.router)
app.include_router(sources.router)


@app.get("/")
def root():
    return {"message": "Life Science Data Platform API v1"}

app.include_router(dashboard.router)
app.include_router(analysis.router)

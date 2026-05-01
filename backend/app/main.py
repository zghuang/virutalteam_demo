from fastapi import FastAPI

from app.routers import alerts, reports

app = FastAPI(title="Life Science Data Platform", version="1")

app.include_router(alerts.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"message": "Life Science Data Platform API v1"}

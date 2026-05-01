from fastapi import FastAPI

app = FastAPI(title="Life Science Data Platform", version="1")


@app.get("/")
def root():
    return {"message": "Life Science Data Platform API v1"}

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text

from edge_lab.db import DbSession
from edge_lab.routes import router

app = FastAPI(title="edge-lab", version="0.2.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz(db: DbSession) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "db unavailable") from exc
    return {"status": "ready"}


app.include_router(router)

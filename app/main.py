from fastapi import FastAPI
from .api.routes_health import router as health_router

app = FastAPI(title="Flyswatter API")
app.include_router(health_router)

@app.get("/")
def root():
    return {"ok": True}
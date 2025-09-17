from fastapi import FastAPI
from .api.routes_health import router as health_router
from .api.routes_user import router as user_router

app = FastAPI(title="Flyswatter API")
app.include_router(health_router)
app.include_router(user_router)

@app.get("/")
def root():
    return {"ok": True}
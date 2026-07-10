from fastapi import FastAPI
from app.modules.auth.router import router as auth_router

app = FastAPI()
app.include_router(auth_router)

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

from app.modules.organization.router import router as org_router

app.include_router(org_router)

from app.modules.service.router import router as service_router

app.include_router(service_router)
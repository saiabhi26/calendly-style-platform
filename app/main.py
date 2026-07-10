from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.modules.auth.router import router as auth_router
from app.modules.organization.router import router as org_router
from app.modules.service.router import router as service_router
from app.modules.availability.router import router as availability_router
from app.modules.slot.router import router as slot_router
from app.modules.booking.router import router as booking_router
from app.modules.public.router import router as public_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(org_router)
app.include_router(service_router)
app.include_router(availability_router)
app.include_router(slot_router)
app.include_router(booking_router)
app.include_router(public_router)


@app.get("/health-check")
def health_check():
    return {"status": "ok"}


# --- Static frontend ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("app/static/index.html")


@app.get("/book", include_in_schema=False)
def booking_page():
    return FileResponse("app/static/booking.html")

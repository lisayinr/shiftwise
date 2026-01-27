from fastapi import FastAPI
from app.workers import router as workers_router
from app.shifts import router as shifts_router
from app.availability import router as availability_router

app = FastAPI(title="ShiftWise API")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(workers_router)
app.include_router(shifts_router)
app.include_router(availability_router)

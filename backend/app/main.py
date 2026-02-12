from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.workers import router as workers_router
from app.shifts import router as shifts_router
from app.availability import router as availability_router
from app.schedules import router as schedules_router

app = FastAPI(title="ShiftWise API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(workers_router)
app.include_router(shifts_router)
app.include_router(availability_router)
app.include_router(schedules_router)
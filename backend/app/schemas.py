from pydantic import BaseModel

# -------- Workers --------
class WorkerCreate(BaseModel):
    first_name: str
    last_name: str
    max_shifts_per_week: int
    active: int = 1  # 0 or 1

class WorkerOut(WorkerCreate):
    worker_id: int

# -------- Shifts --------
class ShiftCreate(BaseModel):
    shift_name: str
    start_time: str   # "08:00:00"
    end_time: str     # "12:00:00"
    required_workers: int
    undesirable: int = 0  # 0 or 1

class ShiftOut(ShiftCreate):
    shift_id: int

# -------- Availability --------
class AvailabilityCreate(BaseModel):
    worker_id: int
    day_of_week: int
    start_time: str
    end_time: str

class AvailabilityOut(AvailabilityCreate):
    availability_id: int

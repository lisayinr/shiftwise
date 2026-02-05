from fastapi import APIRouter
from pydantic import BaseModel
from app.database import get_conn
from app.scheduler import generate_schedule

router = APIRouter(prefix="/schedules", tags=["Schedules"])


class GenerateRequest(BaseModel):
    week_start_date: str  # "YYYY-MM-DD" (should be Monday)


@router.post("/generate")
def generate(req: GenerateRequest):
    return generate_schedule(req.week_start_date)


@router.get("/{schedule_id}/assignments")
def list_assignments(schedule_id: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT assignment_id, assigned_date, schedule_id, shift_id, worker_id
        FROM assignments
        WHERE schedule_id=%s
        ORDER BY assigned_date, shift_id, worker_id
        """,
        (schedule_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

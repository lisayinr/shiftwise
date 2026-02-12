from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_conn
from app.scheduler import generate_schedule

router = APIRouter(prefix="/schedules", tags=["Schedules"])


class GenerateRequest(BaseModel):
    week_start_date: str  # "YYYY-MM-DD" (should be Monday)


@router.post("/generate")
def generate(req: GenerateRequest):
    result = generate_schedule(req.week_start_date)

    if result["assignments_created"] == 0:
        raise HTTPException(
            status_code=400,
            detail="No valid schedule could be generated for that week. Check worker availability and max shifts per week."
        )

    return result


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

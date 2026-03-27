from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_conn
from app.scheduler import generate_schedule
from app.repair import repair_schedule

router = APIRouter(prefix="/schedules", tags=["Schedules"])


class GenerateRequest(BaseModel):
    week_start_date: str  # "YYYY-MM-DD"


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


@router.get("/{schedule_id}/assignments/detail")
def list_assignments_detail(schedule_id: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT
            a.assignment_id,
            a.assigned_date,
            a.schedule_id,
            a.shift_id,
            s.shift_name,
            s.start_time,
            s.end_time,
            a.worker_id,
            CONCAT(w.first_name, ' ', w.last_name) AS worker_name
        FROM assignments a
        JOIN shifts s ON s.shift_id = a.shift_id
        JOIN workers w ON w.worker_id = a.worker_id
        WHERE a.schedule_id=%s
        ORDER BY a.assigned_date, s.start_time, w.worker_id
        """,
        (schedule_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@router.post("/{schedule_id}/repair")
def repair(schedule_id: int):
    return repair_schedule(schedule_id)
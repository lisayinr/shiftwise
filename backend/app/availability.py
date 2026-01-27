from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.schemas import AvailabilityCreate, AvailabilityOut

router = APIRouter(prefix="/availability", tags=["Availability"])

def _fix_availability_row(row: dict):
    if row is None:
        return None
    row["start_time"] = str(row["start_time"])
    row["end_time"] = str(row["end_time"])
    return row


@router.get("", response_model=list[AvailabilityOut])
def list_all():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT availability_id, worker_id, day_of_week, start_time, end_time FROM availability")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_fix_availability_row(r) for r in rows]

@router.get("/worker/{worker_id}", response_model=list[AvailabilityOut])
def list_for_worker(worker_id: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT availability_id, worker_id, day_of_week, start_time, end_time FROM availability WHERE worker_id=%s",
        (worker_id,),
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_fix_availability_row(r) for r in rows]

@router.post("", response_model=AvailabilityOut)
def create(a: AvailabilityCreate):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "INSERT INTO availability (worker_id, day_of_week, start_time, end_time) VALUES (%s, %s, %s, %s)",
            (a.worker_id, a.day_of_week, a.start_time, a.end_time),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Invalid worker_id or availability data")

    new_id = cur.lastrowid
    cur.execute(
        "SELECT availability_id, worker_id, day_of_week, start_time, end_time FROM availability WHERE availability_id=%s",
        (new_id,),
    )
    row = cur.fetchone()
    cur.close(); conn.close()
    return _fix_availability_row(row)

@router.put("/{availability_id}", response_model=AvailabilityOut)
def update(availability_id: int, a: AvailabilityCreate):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "UPDATE availability SET worker_id=%s, day_of_week=%s, start_time=%s, end_time=%s WHERE availability_id=%s",
        (a.worker_id, a.day_of_week, a.start_time, a.end_time, availability_id),
    )
    conn.commit()
    cur.execute(
        "SELECT availability_id, worker_id, day_of_week, start_time, end_time FROM availability WHERE availability_id=%s",
        (availability_id,),
    )
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Availability not found")
    return _fix_availability_row(row)

@router.delete("/{availability_id}")
def delete(availability_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM availability WHERE availability_id=%s", (availability_id,))
    conn.commit()
    deleted = cur.rowcount
    cur.close(); conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Availability not found")
    return {"deleted": True}

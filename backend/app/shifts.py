from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.schemas import ShiftCreate, ShiftOut

router = APIRouter(prefix="/shifts", tags=["Shifts"])

def _fix_shift_row(row: dict):
    if row is None:
        return None
    # MySQL TIME may come back as timedelta; convert to "HH:MM:SS"
    row["start_time"] = str(row["start_time"])
    row["end_time"] = str(row["end_time"])
    return row


@router.get("", response_model=list[ShiftOut])
def list_shifts():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT shift_id, shift_name, start_time, end_time, required_workers, undesirable FROM shifts")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_fix_shift_row(r) for r in rows]

@router.post("", response_model=ShiftOut)
def create_shift(shift: ShiftCreate):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "INSERT INTO shifts (shift_name, start_time, end_time, required_workers, undesirable) VALUES (%s, %s, %s, %s, %s)",
        (shift.shift_name, shift.start_time, shift.end_time, shift.required_workers, shift.undesirable),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.execute("SELECT shift_id, shift_name, start_time, end_time, required_workers, undesirable FROM shifts WHERE shift_id=%s", (new_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return _fix_shift_row(row)


@router.get("/{shift_id}", response_model=ShiftOut)
def get_shift(shift_id: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT shift_id, shift_name, start_time, end_time, required_workers, undesirable FROM shifts WHERE shift_id=%s", (shift_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Shift not found")
    return _fix_shift_row(row)


@router.put("/{shift_id}", response_model=ShiftOut)
def update_shift(shift_id: int, shift: ShiftCreate):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "UPDATE shifts SET shift_name=%s, start_time=%s, end_time=%s, required_workers=%s, undesirable=%s WHERE shift_id=%s",
        (shift.shift_name, shift.start_time, shift.end_time, shift.required_workers, shift.undesirable, shift_id),
    )
    conn.commit()
    cur.execute("SELECT shift_id, shift_name, start_time, end_time, required_workers, undesirable FROM shifts WHERE shift_id=%s", (shift_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Shift not found")
    return _fix_shift_row(row)


@router.delete("/{shift_id}")
def delete_shift(shift_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM shifts WHERE shift_id=%s", (shift_id,))
    conn.commit()
    deleted = cur.rowcount
    cur.close(); conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Shift not found")
    return {"deleted": True}

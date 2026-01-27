from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.schemas import WorkerCreate, WorkerOut

router = APIRouter(prefix="/workers", tags=["Workers"])

@router.get("", response_model=list[WorkerOut])
def list_workers():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT worker_id, first_name, last_name, max_shifts_per_week, active FROM workers")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

@router.post("", response_model=WorkerOut)
def create_worker(worker: WorkerCreate):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "INSERT INTO workers (first_name, last_name, max_shifts_per_week, active) VALUES (%s, %s, %s, %s)",
        (worker.first_name, worker.last_name, worker.max_shifts_per_week, worker.active),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.execute("SELECT worker_id, first_name, last_name, max_shifts_per_week, active FROM workers WHERE worker_id=%s", (new_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

@router.get("/{worker_id}", response_model=WorkerOut)
def get_worker(worker_id: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT worker_id, first_name, last_name, max_shifts_per_week, active FROM workers WHERE worker_id=%s", (worker_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Worker not found")
    return row

@router.put("/{worker_id}", response_model=WorkerOut)
def update_worker(worker_id: int, worker: WorkerCreate):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "UPDATE workers SET first_name=%s, last_name=%s, max_shifts_per_week=%s, active=%s WHERE worker_id=%s",
        (worker.first_name, worker.last_name, worker.max_shifts_per_week, worker.active, worker_id),
    )
    conn.commit()
    cur.execute("SELECT worker_id, first_name, last_name, max_shifts_per_week, active FROM workers WHERE worker_id=%s", (worker_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Worker not found")
    return row

@router.delete("/{worker_id}")
def delete_worker(worker_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM workers WHERE worker_id=%s", (worker_id,))
    conn.commit()
    deleted = cur.rowcount
    cur.close(); conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {"deleted": True}

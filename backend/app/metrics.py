from fastapi import APIRouter
from app.database import get_conn

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/schedule/{schedule_id}")
def schedule_metrics(schedule_id: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # total assignments per worker
    cur.execute(
        """
        SELECT w.worker_id,
               CONCAT(w.first_name, ' ', w.last_name) AS worker_name,
               COUNT(a.assignment_id) AS total_assignments,
               SUM(CASE WHEN s.undesirable = 1 THEN 1 ELSE 0 END) AS undesirable_assignments
        FROM workers w
        LEFT JOIN assignments a
               ON a.worker_id = w.worker_id AND a.schedule_id = %s
        LEFT JOIN shifts s
               ON s.shift_id = a.shift_id
        WHERE w.active = 1
        GROUP BY w.worker_id, worker_name
        ORDER BY w.worker_id
        """,
        (schedule_id,),
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows
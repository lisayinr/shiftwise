from app.database import get_conn

def repair_schedule(schedule_id: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Find assignments where the assigned worker is now inactive
    cur.execute("""
        SELECT a.assignment_id, a.assigned_date, a.shift_id, a.worker_id
        FROM assignments a
        JOIN workers w ON a.worker_id = w.worker_id
        WHERE a.schedule_id = %s
          AND w.active = 0
    """, (schedule_id,))
    broken_assignments = cur.fetchall()

    repaired_count = 0

    for broken in broken_assignments:
        assigned_date = broken["assigned_date"]
        shift_id = broken["shift_id"]
        old_worker_id = broken["worker_id"]

        # Get shift info
        cur.execute("""
            SELECT shift_id, start_time, end_time
            FROM shifts
            WHERE shift_id = %s
        """, (shift_id,))
        shift = cur.fetchone()

        if not shift:
            continue

        # Find active workers who are available that day
        day_of_week = assigned_date.weekday() + 1  # Monday=1

        cur.execute("""
            SELECT DISTINCT w.worker_id
            FROM workers w
            JOIN availability a ON w.worker_id = a.worker_id
            WHERE w.active = 1
              AND a.day_of_week = %s
              AND a.start_time <= %s
              AND a.end_time >= %s
              AND w.worker_id != %s
        """, (day_of_week, shift["start_time"], shift["end_time"], old_worker_id))
        candidates = cur.fetchall()

        if candidates:
            new_worker_id = candidates[0]["worker_id"]

            # Update the old assignment instead of deleting/reinserting
            cur.execute("""
                UPDATE assignments
                SET worker_id = %s
                WHERE assignment_id = %s
            """, (new_worker_id, broken["assignment_id"]))

            repaired_count += 1

    conn.commit()
    cur.close()
    conn.close()

    return {"schedule_id": schedule_id, "repaired_assignments": repaired_count}
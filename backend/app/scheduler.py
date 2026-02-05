from datetime import datetime, timedelta, date
from app.database import get_conn

# Hard constraints:
# 1) Worker must be available for the full shift window on that day.
# 2) Worker cannot exceed max_shifts_per_week.
# 3) Each shift needs required_workers (best effort if not enough people).
# 4) Worker cannot be double-booked on overlapping shifts on the same day.


def _to_minutes(t) -> int:
    """
    mysql-connector can return TIME as timedelta.
    Accepts timedelta, string 'HH:MM:SS', or datetime.time.
    Returns minutes since midnight.
    """
    if hasattr(t, "seconds") and hasattr(t, "days"):  # timedelta
        return int(t.total_seconds() // 60)
    if isinstance(t, str):
        h, m, s = t.split(":")
        return int(h) * 60 + int(m)
    # datetime.time
    return t.hour * 60 + t.minute


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end


def generate_schedule(week_start_date: str) -> dict:
    """
    Creates (or reuses) a schedule row for the given week_start_date (YYYY-MM-DD),
    deletes old assignments for that schedule, then generates new assignments.
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # 1) Find or create schedule row
    cur.execute("SELECT schedule_id FROM schedules WHERE week_start_date=%s", (week_start_date,))
    row = cur.fetchone()
    if row:
        schedule_id = row["schedule_id"]
        cur.execute("DELETE FROM assignments WHERE schedule_id=%s", (schedule_id,))
        conn.commit()
    else:
        cur.execute("INSERT INTO schedules (week_start_date) VALUES (%s)", (week_start_date,))
        conn.commit()
        schedule_id = cur.lastrowid

    # 2) Load data
    cur.execute("SELECT worker_id, max_shifts_per_week FROM workers WHERE active=1")
    workers = cur.fetchall()

    cur.execute("SELECT shift_id, start_time, end_time, required_workers FROM shifts")
    shifts = cur.fetchall()

    cur.execute("SELECT availability_id, worker_id, day_of_week, start_time, end_time FROM availability")
    availability = cur.fetchall()

    # Build availability lookup: avail_by_worker_day[(worker_id, day_of_week)] -> list of (start_min, end_min)
    avail_by_worker_day = {}
    for a in availability:
        key = (a["worker_id"], a["day_of_week"])
        avail_by_worker_day.setdefault(key, []).append((_to_minutes(a["start_time"]), _to_minutes(a["end_time"])))

    # Track counts for max shifts constraint
    max_by_worker = {w["worker_id"]: int(w["max_shifts_per_week"]) for w in workers}
    assigned_count = {w["worker_id"]: 0 for w in workers}

    # Track assignments per worker per date for overlap check:
    # worker_day_assigned[(worker_id, assigned_date)] = list of (start_min, end_min)
    worker_day_assigned = {}

    # Convert week_start_date string to date
    ws = datetime.strptime(week_start_date, "%Y-%m-%d").date()

    total_assignments = 0

    # 3) Loop 7 days: Monday..Sunday
    for day_index in range(7):
        assigned_date = ws + timedelta(days=day_index)
        day_of_week = day_index + 1  # 1=Mon .. 7=Sun

        # For each shift, assign required_workers
        for sh in shifts:
            shift_start = _to_minutes(sh["start_time"])
            shift_end = _to_minutes(sh["end_time"])
            needed = int(sh["required_workers"])

            # Candidate workers = available + under max + no overlap
            candidates = []
            for worker_id in assigned_count.keys():
                # Max shifts constraint
                if assigned_count[worker_id] >= max_by_worker[worker_id]:
                    continue

                # Availability constraint
                windows = avail_by_worker_day.get((worker_id, day_of_week), [])
                is_available = any(w_start <= shift_start and w_end >= shift_end for (w_start, w_end) in windows)
                if not is_available:
                    continue

                # No overlap constraint
                taken = worker_day_assigned.get((worker_id, assigned_date), [])
                if any(_overlaps(shift_start, shift_end, t_start, t_end) for (t_start, t_end) in taken):
                    continue

                candidates.append(worker_id)

            # Simple fairness: fewest assignments so far first
            candidates.sort(key=lambda wid: assigned_count[wid])

            chosen = candidates[:needed]

            # Insert assignments
            for worker_id in chosen:
                cur.execute(
                    "INSERT INTO assignments (assigned_date, schedule_id, shift_id, worker_id) VALUES (%s, %s, %s, %s)",
                    (assigned_date, schedule_id, sh["shift_id"], worker_id),
                )
                total_assignments += 1
                assigned_count[worker_id] += 1
                worker_day_assigned.setdefault((worker_id, assigned_date), []).append((shift_start, shift_end))

    conn.commit()
    cur.close()
    conn.close()

    return {"schedule_id": schedule_id, "assignments_created": total_assignments}

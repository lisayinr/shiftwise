from datetime import datetime, timedelta
from app.database import get_conn


def _to_minutes(t) -> int:
    if hasattr(t, "seconds") and hasattr(t, "days"):  # timedelta
        return int(t.total_seconds() // 60)
    if isinstance(t, str):
        h, m, s = t.split(":")
        return int(h) * 60 + int(m)
    return t.hour * 60 + t.minute


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end


def generate_schedule(week_start_date: str) -> dict:
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # 1) Find or create schedule row (reuse week)
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

    cur.execute("SELECT shift_id, start_time, end_time, required_workers, undesirable FROM shifts")
    shifts = cur.fetchall()

    cur.execute("SELECT availability_id, worker_id, day_of_week, start_time, end_time FROM availability")
    availability = cur.fetchall()

    # availability lookup
    avail_by_worker_day = {}
    for a in availability:
        key = (a["worker_id"], a["day_of_week"])
        avail_by_worker_day.setdefault(key, []).append((_to_minutes(a["start_time"]), _to_minutes(a["end_time"])))

    # max shifts per week (hard constraint)
    max_by_worker = {w["worker_id"]: int(w["max_shifts_per_week"]) for w in workers}

    # WEEK counters (for constraints)
    week_assigned = {w["worker_id"]: 0 for w in workers}
    week_undesirable = {w["worker_id"]: 0 for w in workers}

    # HISTORY counters (for fairness memory)
    hist_total = {w["worker_id"]: 0 for w in workers}
    hist_undesirable = {w["worker_id"]: 0 for w in workers}

    # --- Fairness: initialize from history (past total + past undesirable) ---
    cur.execute(
        """
        SELECT a.worker_id,
               COUNT(*) AS total_hist,
               SUM(CASE WHEN s.undesirable = 1 THEN 1 ELSE 0 END) AS undesirable_hist
        FROM assignments a
        JOIN shifts s ON s.shift_id = a.shift_id
        GROUP BY a.worker_id
        """
    )
    for r in cur.fetchall():
        wid = r["worker_id"]
        if wid in hist_total:
            hist_total[wid] = int(r["total_hist"] or 0)
            hist_undesirable[wid] = int(r["undesirable_hist"] or 0)

    # overlap tracking
    worker_day_assigned = {}

    ws = datetime.strptime(week_start_date, "%Y-%m-%d").date()
    total_assignments = 0

    for day_index in range(7):
        assigned_date = ws + timedelta(days=day_index)
        day_of_week = day_index + 1

        for sh in shifts:
            shift_start = _to_minutes(sh["start_time"])
            shift_end = _to_minutes(sh["end_time"])
            needed = int(sh["required_workers"])
            is_undesirable_shift = int(sh["undesirable"]) == 1

            candidates = []
            for wid in week_assigned.keys():
                # Hard constraint: max shifts per week
                if week_assigned[wid] >= max_by_worker[wid]:
                    continue

                # Hard constraint: availability
                windows = avail_by_worker_day.get((wid, day_of_week), [])
                if not any(w_start <= shift_start and w_end >= shift_end for (w_start, w_end) in windows):
                    continue

                # Hard constraint: no overlap same day
                taken = worker_day_assigned.get((wid, assigned_date), [])
                if any(_overlaps(shift_start, shift_end, t_start, t_end) for (t_start, t_end) in taken):
                    continue

                candidates.append(wid)

            # Fairness-aware sorting with history + this week
            # score = (hist_total + week_total) + 2*(hist_undesirable + week_undesirable)
            def fairness_key(wid: int):
                total = hist_total[wid] + week_assigned[wid]
                undes = hist_undesirable[wid] + week_undesirable[wid]
                score = total + (2 * undes)
                return (score, undes, total, wid)

            candidates.sort(key=fairness_key)

            chosen = candidates[:needed]

            for wid in chosen:
                cur.execute(
                    "INSERT INTO assignments (assigned_date, schedule_id, shift_id, worker_id) VALUES (%s, %s, %s, %s)",
                    (assigned_date, schedule_id, sh["shift_id"], wid),
                )
                total_assignments += 1
                week_assigned[wid] += 1
                if is_undesirable_shift:
                    week_undesirable[wid] += 1
                worker_day_assigned.setdefault((wid, assigned_date), []).append((shift_start, shift_end))

    conn.commit()
    cur.close()
    conn.close()

    return {"schedule_id": schedule_id, "assignments_created": total_assignments}
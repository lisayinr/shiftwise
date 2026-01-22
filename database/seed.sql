INSERT INTO workers (first_name, last_name, max_shifts_per_week, active)
VALUES
('Alex', 'Garcia', 4, 1),
('Maya', 'Lopez', 3, 1),
('Jordan', 'Kim', 5, 1),
('Taylor', 'Smith', 2, 1);


INSERT INTO shifts (shift_name, start_time, end_time, required_workers, undesirable)
VALUES
('Morning',  '08:00:00', '12:00:00', 2, 0),
('Afternoon','12:00:00', '16:00:00', 2, 0),
('Evening',  '16:00:00', '20:00:00', 2, 1);


INSERT INTO schedules (week_start_date)
VALUES ('2026-01-26');


-- Alex (worker_id = 1) available Mon–Fri 8–20
INSERT INTO availability (day_of_week, start_time, end_time, worker_id)
VALUES
(1, '08:00:00', '20:00:00', 1),
(2, '08:00:00', '20:00:00', 1),
(3, '08:00:00', '20:00:00', 1),
(4, '08:00:00', '20:00:00', 1),
(5, '08:00:00', '20:00:00', 1);

-- Maya (worker_id = 2) available Mon–Fri 8–16
INSERT INTO availability (day_of_week, start_time, end_time, worker_id)
VALUES
(1, '08:00:00', '16:00:00', 2),
(2, '08:00:00', '16:00:00', 2),
(3, '08:00:00', '16:00:00', 2),
(4, '08:00:00', '16:00:00', 2),
(5, '08:00:00', '16:00:00', 2);

-- Jordan (worker_id = 3) available Mon–Fri 12–20
INSERT INTO availability (day_of_week, start_time, end_time, worker_id)
VALUES
(1, '12:00:00', '20:00:00', 3),
(2, '12:00:00', '20:00:00', 3),
(3, '12:00:00', '20:00:00', 3),
(4, '12:00:00', '20:00:00', 3),
(5, '12:00:00', '20:00:00', 3);

-- Taylor (worker_id = 4) available Tue/Thu 8–20
INSERT INTO availability (day_of_week, start_time, end_time, worker_id)
VALUES
(2, '08:00:00', '20:00:00', 4),
(4, '08:00:00', '20:00:00', 4);


INSERT INTO assignments (assigned_date, schedule_id, shift_id, worker_id)
VALUES ('2026-01-26', 1, 1, 1);



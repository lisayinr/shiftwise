# ShiftWise

ShiftWise is a scheduling system that generates weekly employee schedules based on worker availability, max shifts per week, and shift staffing needs. It also shows fairness metrics and supports CSV export.

## Features
- Worker management
- Shift management
- Availability tracking
- Weekly schedule generation
- Fairness metrics
- No-valid-schedule error handling
- Schedule repair after worker unavailability
- CSV export

## Tech Stack
- FastAPI
- Python
- MySQL
- HTML/CSS/JavaScript

## How to Run

### Backend
1. Go to the backend folder
2. Activate the virtual environment
3. Run:
   uvicorn app.main:app --reload

### Frontend
1. Go to the frontend folder
2. Run:
   python3 -m http.server 5500

3. Open:
   http://127.0.0.1:5500

## Main API Endpoints
- POST /schedules/generate
- GET /schedules/{schedule_id}/assignments
- GET /schedules/{schedule_id}/assignments/detail
- GET /metrics/schedule/{schedule_id}
- POST /schedules/{schedule_id}/repair

## Project Status
ShiftWise currently supports schedule generation, fairness display, repair after worker unavailability, and CSV export.

## Fairness Logic
The scheduler uses total assignments and undesirable assignments to help distribute work more evenly.

## Repair Logic
If a worker becomes unavailable after scheduling, the system replaces only the affected assignments instead of rebuilding the whole schedule.
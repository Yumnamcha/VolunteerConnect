# VolunteerConnect — Full Stack MVP

A modern NGO volunteer and campaign management portal.

## Stack

- Frontend: React + Vite + Axios + React Router + Recharts + Lucide React
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: PostgreSQL
- Authentication: JWT
- Password hashing: bcrypt
- Local database: Docker Compose

## Features

### Volunteers
- Register/login
- Browse and search campaigns
- View campaign details
- Apply for campaigns
- Track application status
- Send/read campaign messages
- Volunteer dashboard with statistics

### Coordinators
- Login/register
- Create, edit and delete campaigns
- View applicants
- Approve/reject applications
- View campaign statistics
- Send/read campaign messages

## 1. Requirements

Install:

- Python 3.11+
- Node.js 20+
- Docker Desktop

Check:

```bash
python --version
node --version
docker --version
```

## 2. Start PostgreSQL

From the project root:

```bash
docker compose up -d
```

PostgreSQL will run on port 5432.

## 3. Start backend

Open Terminal 1:

```bash
cd backend
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend:
http://127.0.0.1:8000

Swagger API documentation:
http://127.0.0.1:8000/docs

## 4. Start frontend

Open Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally:

http://localhost:5173

## Demo coordinator

Email:
admin@volunteerconnect.com

Password:
admin123

The backend automatically creates this account and several demo campaigns on first startup.

## API structure

```text
/api/auth
/api/campaigns
/api/applications
/api/messages
/api/dashboard
```

## Important

This is a college-project-ready MVP. Before public deployment, change the JWT secret, database password, CORS settings, and add production HTTPS/security controls.

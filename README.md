# IRIS: IUT Repository and Information System

[![DP-I Project](https://img.shields.io/badge/Project-DP--I%20(Team%207)-blue)](documents%20&%20artifacts/PROJECT_PLAN_AND_ARCHITECTURE.md)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Tailwind-61DAFB?logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791?logo=postgresql)](https://www.postgresql.org/)

IRIS is an authenticated, AI-augmented, permanent institutional repository for notices, circulars, and academic documents at the Islamic University of Technology (IUT).

---

## 🏛️ Project Information
- **Department:** Computer Science and Technology, IUT
- **Course:** Project Proposal (DP-I)
- **Team 7:**
  - Ashfaque Sadad (ID: 230042102)
  - Md Rufayed Ul Alam (ID: 230042121)
  - MD Zahin Uddin Nirob (ID: 230042160)

---

## 🚀 Key Features
- **Permanent Archival:** Digital PDFs and physical notice board photos are preserved permanently even after removal from official websites.
- **Hybrid Ingestion:** Manual uploads by Class Representatives (CRs) & departmental officials + automated scheduled crawler for `iutoic-dhaka.edu`.
- **Hybrid OCR & Vision Pipeline:** PyMuPDF for native text, OpenCV preprocessing + Tesseract OCR for physical photos, and Google Gemini for structured extraction.
- **In-Flight Uploader Verification:** Real-time preview with color-coded confidence indicators so uploaders can confirm/edit extracted metadata immediately.
- **PostgreSQL Relational + JSONB Architecture:** Rock-solid relational integrity for users, roles, and review audit trails, combined with native `JSONB` for flexible AI-extracted metadata.
- **Interactive Deadlines Hub:** Dedicated timeline view of upcoming dues/registrations with 1-click Google Calendar & `.ics` export.
- **Role-Based Access Control:** Google OAuth restricted to `@iut-dhaka.edu` accounts with role assignment (Student, CR, Faculty, Admin).

---

## 📁 Repository Structure
```
IRIS-IUT-Repository-and-Information-System/
├── backend/                  # FastAPI async backend service
│   ├── app/
│   │   ├── api/v1/           # API routes (auth, documents, deadlines)
│   │   ├── core/             # Configuration & JWT security
│   │   ├── db/               # PostgreSQL async connection (SQLAlchemy + asyncpg)
│   │   ├── models/           # SQLAlchemy ORM models (User, NoticeDocument)
│   │   ├── schemas/          # Pydantic data schemas
│   │   └── services/         # Storage, OCR pipeline, Gemini, scraper
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React + Tailwind CSS client
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── documents & artifacts/     # Architecture, specifications, and project plan
│   └── PROJECT_PLAN_AND_ARCHITECTURE.md
└── docker-compose.yml        # Multi-container orchestration (PostgreSQL + Backend + Frontend)
```

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (or local Docker)

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation is live at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Client is live at `http://localhost:5173`.

### 4. Running via Docker Compose
```bash
docker compose up --build
```
This automatically boots PostgreSQL 16, creates the database tables, starts FastAPI on port 8000, and starts React on port 5173.

---



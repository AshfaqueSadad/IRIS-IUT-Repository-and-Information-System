# IRIS: IUT Repository and Information System

[![DP-I Project](https://img.shields.io/badge/Project-DP--I%20(Team%207)-blue)](documents%20&%20artifacts/PROJECT_PLAN_AND_ARCHITECTURE.md)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Tailwind-61DAFB?logo=react)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?logo=mongodb)](https://www.mongodb.com/)

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
- **Typo-Tolerant Search:** MongoDB Atlas Search (Lucene) with fuzzy search over OCR text and faceted filtering (Category, Department, Batch, Sender).
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
│   │   ├── db/               # MongoDB Motor connection
│   │   ├── models/ & schemas/# Pydantic data models
│   │   └── services/         # Storage, OCR pipeline, Gemini, scraper
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React + Tailwind CSS client
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── documents & artifacts/     # Architecture, specifications, and project plan
│   └── PROJECT_PLAN_AND_ARCHITECTURE.md
└── docker-compose.yml        # Multi-container orchestration (Mongo + Backend + Frontend)
```

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB (or MongoDB Atlas account)
- Tesseract OCR (optional for local image OCR)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Client will be live at `http://localhost:5173`.

### 4. Running via Docker Compose
```bash
docker compose up --build
```

---

## 📖 Documentation
Detailed architectural blueprints, database schemas, and the 10-week development roadmap are located in [`documents & artifacts/PROJECT_PLAN_AND_ARCHITECTURE.md`](documents%20&%20artifacts/PROJECT_PLAN_AND_ARCHITECTURE.md).

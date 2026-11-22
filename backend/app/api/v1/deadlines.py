from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Response, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from icalendar import Calendar, Event

from app.db.database import get_db
from app.models.document import NoticeDocument

router = APIRouter()


@router.get("/")
async def list_upcoming_deadlines(
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all upcoming deadlines extracted from active notices in PostgreSQL."""
    query = select(NoticeDocument).where(NoticeDocument.status == "APPROVED")
    if department and department != "All":
        query = query.where(NoticeDocument.department.in_([department, "All"]))

    result = await db.execute(query)
    docs = result.scalars().all()

    deadlines = []
    now_iso = datetime.utcnow().isoformat()

    for doc in docs:
        doc_metadata = doc.notice_metadata or {}
        extracted_deadlines = doc_metadata.get("deadlines", [])
        for dl in extracted_deadlines:
            due_date = dl.get("dueDate")
            if due_date and due_date >= now_iso:
                deadlines.append({
                    "noticeId": str(doc.id),
                    "noticeTitle": doc.title,
                    "department": doc.department,
                    "category": doc.category,
                    "deadline": dl
                })

    # Sort deadlines by due date ascending
    deadlines.sort(key=lambda x: x["deadline"].get("dueDate", ""))
    return deadlines


@router.get("/export.ics")
async def export_calendar_ics(
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Download an iCalendar (.ics) file with all upcoming university deadlines."""
    cal = Calendar()
    cal.add("prodid", "-//IRIS - IUT Repository and Information System//EN")
    cal.add("version", "2.0")

    query = select(NoticeDocument).where(NoticeDocument.status == "APPROVED")
    result = await db.execute(query)
    docs = result.scalars().all()

    for doc in docs:
        doc_metadata = doc.notice_metadata or {}
        for deadline in doc_metadata.get("deadlines", []):
            event = Event()
            event.add("summary", f"[IUT Deadline] {deadline.get('title', doc.title)}")
            due_str = deadline.get("dueDate")
            try:
                dt = datetime.fromisoformat(due_str.replace("Z", "+00:00")) if due_str else datetime.utcnow()
            except Exception:
                dt = datetime.utcnow()
            event.add("dtstart", dt)
            event.add("description", f"{deadline.get('actionRequired', '')}\nNotice: {doc.title}")
            cal.add_component(event)

    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=iut_deadlines.ics"}
    )

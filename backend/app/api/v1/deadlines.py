from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Response, Query
from icalendar import Calendar, Event
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/")
async def list_upcoming_deadlines(
    department: Optional[str] = Query(None),
    batch: Optional[str] = Query(None)
):
    """Retrieve all upcoming deadlines extracted from active notices."""
    db = get_database()
    if db is None:
        return []

    now = datetime.utcnow()
    pipeline = [
        {"$match": {"status": "APPROVED", "deadlines": {"$exists": True, "$ne": []}}},
        {"$unwind": "$deadlines"},
        {"$match": {"deadlines.dueDate": {"$gte": now}}},
        {"$sort": {"deadlines.dueDate": 1}},
        {"$project": {
            "_id": 1,
            "noticeId": "$_id",
            "noticeTitle": "$title",
            "department": "$department",
            "category": "$category",
            "deadline": "$deadlines"
        }}
    ]

    cursor = db.documents.aggregate(pipeline)
    deadlines = []
    async for item in cursor:
        item["_id"] = str(item["_id"])
        item["noticeId"] = str(item["noticeId"])
        deadlines.append(item)

    return deadlines


@router.get("/export.ics")
async def export_calendar_ics(
    department: Optional[str] = Query(None)
):
    """Download an iCalendar (.ics) file with all upcoming university deadlines."""
    cal = Calendar()
    cal.add("prodid", "-//IRIS - IUT Repository and Information System//EN")
    cal.add("version", "2.0")

    db = get_database()
    if db is not None:
        cursor = db.documents.find({"status": "APPROVED", "deadlines": {"$exists": True, "$ne": []}})
        async for doc in cursor:
            for deadline in doc.get("deadlines", []):
                event = Event()
                event.add("summary", f"[IUT Deadline] {deadline.get('title', doc.get('title'))}")
                event.add("dtstart", deadline.get("dueDate", datetime.utcnow()))
                event.add("description", f"{deadline.get('actionRequired', '')}\nNotice: {doc.get('title')}")
                cal.add_component(event)

    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=iut_deadlines.ics"}
    )

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from auth.permissions import require_roles
from crud.log_processing.service import process_log
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from models.event import Event
from models.helper import get_db
from schemas.log_processing import ProcessLogRequest, ProcessLogResponse

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/view", response_class=HTMLResponse)
async def view_logs(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    result = await db.execute(select(Event).order_by(Event.id.desc()).limit(50))
    events = result.scalars().all()

    html = """
    <html>
    <head>
        <title>Logs Viewer</title>
        <style>
            body { font-family: Arial; background: #f5f5f5; }
            .log { background: white; margin: 10px; padding: 10px; border-radius: 8px; }
            .low { border-left: 5px solid green; }
            .medium { border-left: 5px solid orange; }
            .high { border-left: 5px solid red; }
        </style>
    </head>
    <body>
        <h2>Logs Analysis</h2>
    """

    for e in events:
        html += f"""
        <div class="log {e.severity}">
            <b>Severity:</b> {e.severity}<br>
            <b>Category:</b> {e.category}<br>
            <b>Message:</b> {e.message}<br>
            <b>Service:</b> {e.service}<br>
            <b>Time:</b> {e.timestamp}<br>
            <b>Raw:</b> {e.raw_message}
        </div>
        """

    html += "</body></html>"
    return html

@router.post("/upload")
async def upload_logs(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    content = await file.read()
    lines = content.decode("utf-8").splitlines()

    results = []

    for line in lines:
        if not line.strip():
            continue

        result = await process_log(
            db=db,
            user_id=current_user.id,
            raw_log=line,
            source=file.filename,
            host="upload",
        )

        if result is not None:
            results.append({
                "incident_id": result["incident"].id,
                "event_id": result["event"].id,
                "severity": result["analysis_result"]["severity"],
                "category": result["analysis_result"]["category"],
                "message": result["analysis_result"]["message"],
            })

    return {
        "status": "ok",
        "processed": len(results),
        "results": results,
    }

@router.post("/process", response_model=ProcessLogResponse)
async def process_log_endpoint(
    payload: ProcessLogRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    result = await process_log(
        db=db,
        user_id=current_user.id,
        raw_log=payload.raw_log,
        source=payload.source,
        host=payload.host,
        timestamp=payload.timestamp,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No active analysis pattern matched the provided log",
        )

    incident = result["incident"]
    event = result["event"]
    analysis = result["analysis_result"]

    return ProcessLogResponse(
        incident_id=incident.id,
        event_id=event.id,
        pattern_key=analysis["pattern_key"],
        severity=analysis["severity"],
        category=analysis["category"],
        service=analysis.get("service"),
        message=analysis["message"],
        extracted_fields=result["extracted_fields"],
        rule_metadata=result["rule_metadata"],
        event_context=result["event_context"],
        incident_context=result["incident_context"],
        confidence=result["confidence"],
        explanation=result["explanation"],
    )
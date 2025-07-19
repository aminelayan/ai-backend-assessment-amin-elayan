from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from app.services.docx_report_service import generate_docx_report

router = APIRouter(prefix="/api/report", tags=["Report"])

class ReportRequest(BaseModel):
    title: str
    sections: list[str]
    prompt_context: str
    tenant: str

@router.post("/generate")
def generate_report(request: ReportRequest):
    report_id, path = generate_docx_report(
        title=request.title,
        sections=request.sections,
        prompt_context=request.prompt_context,
        tenant=request.tenant
    )
    return {"report_id": report_id, "download_url": f"/api/report/{report_id}/download"}

@router.get("/{report_id}/download")
def download_report(report_id: str):
    path = f"generated_reports/{report_id}.docx"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=f"{report_id}.docx")

"""
Procurement Planning Microservice.
Provides REST endpoints for APP-CSE upload, parsing, budget validation, and an interactive Web Portal.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.parser import parse_app_cse_excel
from app.models import AppCseSubmissionResponse
import uuid
import os
from typing import Dict

app = FastAPI(
    title="mPhilGEPS Procurement Planning Service",
    description="Microservice responsible for APP-CSE submission, parsing, and budget validation.",
    version="1.0.0"
)

# In-memory store for local testing
submissions_db: Dict[str, AppCseSubmissionResponse] = {}

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def get_portal_ui():
    """Serves the interactive browser-based APP-CSE Submission Portal."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to mPhilGEPS Procurement Planning Service. Visit /docs for Swagger UI."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "procurement-planning", "environment": "local"}

@app.post("/api/v1/app-cse/upload", response_model=AppCseSubmissionResponse)
async def upload_app_cse(
    agency_id: str = Form(..., description="Government Agency Identifier, e.g. NGA-DEPED-001"),
    fiscal_year: int = Form(2026, description="Fiscal Year for the procurement plan"),
    allocated_budget: float = Form(1000000.0, description="Approved agency budget ceiling for CSE"),
    file: UploadFile = File(..., description="PS-DBM APP-CSE Excel workbook (.xlsx)")
):
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only Excel workbooks (.xlsx, .xlsm) are currently supported.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    items, errors = parse_app_cse_excel(file_bytes)
    total_budget = round(sum(item.total_amount for item in items), 2)
    budget_status = "WITHIN_LIMIT" if total_budget <= allocated_budget else "EXCEEDS_BUDGET"

    submission_id = f"cse-{fiscal_year}-{uuid.uuid4().hex[:8]}"
    
    response = AppCseSubmissionResponse(
        submission_id=submission_id,
        agency_id=agency_id,
        fiscal_year=fiscal_year,
        status="VALIDATED" if not errors else "VALIDATED_WITH_WARNINGS",
        total_items=len(items),
        total_estimated_budget=total_budget,
        allocated_budget=allocated_budget,
        budget_status=budget_status,
        items=items,
        validation_errors=errors
    )
    
    submissions_db[submission_id] = response
    return response

@app.get("/api/v1/app-cse/{submission_id}", response_model=AppCseSubmissionResponse)
def get_submission(submission_id: str):
    if submission_id not in submissions_db:
        raise HTTPException(status_code=404, detail=f"Submission '{submission_id}' not found.")
    return submissions_db[submission_id]

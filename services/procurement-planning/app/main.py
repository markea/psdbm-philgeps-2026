"""
Procurement Planning & Multi-Agent Intelligence Microservice (mPhilGEPS Demo Sandbox).
Provides REST endpoints for:
  1. APP-CSE upload, Dual-Pass UNSPSC classification, and BigQuery ML demand stream
  2. Multi-Agent Conversational Ecosystem (BAC Advisor, COA Auditor, Merchant Help, Supervisor Router) + Model Armor
  3. Cloud Spanner Graph Cartel & BigQuery ML Collusion Probability Index (CPI) Visualizer
  4. 4-Tier Anti-Scraping Perimeter Simulator & OCDS v1.1 Open Data Bulk Export
  5. Golden Dataset Evaluation Runner & Live Scorecard
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agents import (
    get_spanner_graph_collusion_data,
    run_agent_turn,
    simulate_anti_scraping_decision,
)
from app.eval_runner import EVAL_RESULTS_PATH, run_golden_evaluation
from app.models import AppCseSubmissionResponse
from app.parser import parse_app_cse_excel

app = FastAPI(
    title="mPhilGEPS Modernization Demo Portal & Multi-Agent Sandbox",
    description=(
        "DEMO ENVIRONMENT ONLY: Interactive PS-DBM / PhilGEPS Modernization Sandbox featuring "
        "Dual-Pass AI UNSPSC Classification, 3 Specialized AI Agents + Supervisor Router, "
        "Spanner Graph Cartel Detection, Anti-Scraping Defense, and Golden Dataset Evaluations."
    ),
    version="2.0.0-DEMO",
)

# In-memory store for session submissions
submissions_db: Dict[str, AppCseSubmissionResponse] = {}

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User query to the mPhilGEPS AI Agent Hub")
    agent: Optional[str] = Field(
        default="auto",
        description="Target agent ('auto', 'bac', 'coa', or 'merchant')",
    )


class SecuritySimulationRequest(BaseModel):
    profile: str = Field(
        default="shared_lgu_nat",
        description="Traffic profile ('shared_lgu_nat', 'ambiguous_crawler', or 'commercial_scraper_bot')",
    )


@app.get("/")
def get_portal_ui():
    """Serves the interactive browser-based mPhilGEPS Modernization Demo Portal."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to mPhilGEPS Demo Portal. Visit /docs for Swagger UI."}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "procurement-planning",
        "environment": "DEMO_SANDBOX",
        "demo_notice": "Non-production PS-DBM / PhilGEPS Modernization Sandbox",
        "capabilities": [
            "app_cse_dual_pass_unspsc",
            "multi_agent_ecosystem_bac_coa_merchant",
            "model_armor_ra10173_dlp",
            "spanner_graph_cartel_detection",
            "anti_scraping_ocds_open_data",
            "golden_dataset_agent_evals",
        ],
    }


@app.post("/api/v1/app-cse/upload", response_model=AppCseSubmissionResponse)
async def upload_app_cse(
    agency_id: str = Form(..., description="Government Agency Identifier, e.g. NGA-DEPED-001"),
    fiscal_year: int = Form(2026, description="Fiscal Year for the procurement plan"),
    allocated_budget: float = Form(1000000.0, description="Approved agency budget ceiling for CSE"),
    file: UploadFile = File(..., description="PS-DBM APP-CSE Excel workbook (.xlsx)"),
):
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(
            status_code=400,
            detail="Only Excel workbooks (.xlsx, .xlsm) are currently supported.",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    items, errors = parse_app_cse_excel(file_bytes)
    total_budget = round(sum(item.total_amount for item in items), 2)
    budget_status = "WITHIN_LIMIT" if total_budget <= allocated_budget else "EXCEEDS_BUDGET"

    submission_id = f"cse-{fiscal_year}-{uuid.uuid4().hex[:8]}"

    # Generate BigQuery ML in-database demand stream records (TDD §5.2)
    bq_records = [
        {
            "procurement_date": f"{fiscal_year}-01-15",
            "unspsc_commodity_code": item.unspsc_code,
            "total_expenditure": item.total_amount,
            "holiday_region": "PH",
        }
        for item in items
    ]

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
        bigquery_demand_stream=bq_records,
        validation_errors=errors,
    )

    submissions_db[submission_id] = response
    return response


@app.get("/api/v1/app-cse/{submission_id}", response_model=AppCseSubmissionResponse)
def get_submission(submission_id: str):
    if submission_id not in submissions_db:
        raise HTTPException(status_code=404, detail=f"Submission '{submission_id}' not found.")
    return submissions_db[submission_id]


@app.get("/api/v1/app-cse/{submission_id}/bigquery-stream")
def get_bigquery_demand_stream(submission_id: str):
    """
    Returns the BigQuery ML ARIMA_PLUS streaming records for this submission,
    formatted for mphilgeps_analytics.app_demand_forecast with holiday_region = 'PH'.
    """
    if submission_id not in submissions_db:
        raise HTTPException(status_code=404, detail=f"Submission '{submission_id}' not found.")
    sub = submissions_db[submission_id]
    return {
        "submission_id": sub.submission_id,
        "target_table": "mphilgeps_analytics.app_demand_forecast",
        "holiday_region": "PH",
        "stream_records_count": len(sub.bigquery_demand_stream),
        "records": sub.bigquery_demand_stream,
    }


# ==============================================================================
# OPTION 1: LIVE MULTI-AGENT CONVERSATIONAL ECOSYSTEM + MODEL ARMOR
# ==============================================================================
@app.post("/api/v1/agents/chat")
def chat_with_agent(req: AgentChatRequest) -> Dict[str, Any]:
    """
    Executes an interactive turn with the mPhilGEPS Multi-Agent Ecosystem:
      - Pre-screens prompt with Google Cloud Model Armor (RA 10173 PII DLP + Jailbreak Block)
      - Routes via Supervisor Intent Classifier ('bac', 'coa', 'merchant', or 'auto')
      - Injects live session APP-CSE context if a workbook was uploaded
    """
    portal_context = None
    if submissions_db:
        latest_sub = list(submissions_db.values())[-1]
        portal_context = {
            "submission_id": latest_sub.submission_id,
            "agency_id": latest_sub.agency_id,
            "fiscal_year": latest_sub.fiscal_year,
            "total_items": latest_sub.total_items,
            "total_estimated_budget": latest_sub.total_estimated_budget,
            "allocated_budget": latest_sub.allocated_budget,
            "budget_status": latest_sub.budget_status,
        }

    return run_agent_turn(
        user_message=req.message,
        requested_agent=req.agent,
        portal_context=portal_context,
    )


@app.get("/api/v1/agents/eval-report")
def get_agent_evaluation_report() -> Dict[str, Any]:
    """Returns the 15-case Golden Dataset evaluation report and rubric scorecard."""
    if EVAL_RESULTS_PATH.exists():
        try:
            with open(EVAL_RESULTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return run_golden_evaluation(save_artifacts=True)


@app.post("/api/v1/agents/run-eval")
def trigger_live_agent_evaluation() -> Dict[str, Any]:
    """Re-executes all 15 Golden Dataset test cases live and returns the updated scorecard."""
    return run_golden_evaluation(save_artifacts=True)


# ==============================================================================
# OPTION 2: CLOUD SPANNER GRAPH CARTEL & BIGQUERY ML COLLUSION VISUALIZER
# ==============================================================================
@app.get("/api/v1/collusion/graph")
def get_collusion_graph() -> Dict[str, Any]:
    """
    Returns the Cloud Spanner Graph (`MPhilGepsProcurementGraph`) topology,
    GQL query, BigQuery ML Collusion Probability Index (CPI = 0.942), and Benford's Law distribution.
    """
    return get_spanner_graph_collusion_data()


# ==============================================================================
# OPTION 3: 4-TIER ANTI-SCRAPING SIMULATOR & OCDS v1.1 OPEN DATA BULK EXPORT
# ==============================================================================
@app.post("/api/v1/security/simulate-request")
def simulate_security_request(req: SecuritySimulationRequest) -> Dict[str, Any]:
    """
    Simulates Cloud Armor JA3 + reCAPTCHA Enterprise Frictionless Edge Scoring + Apigee Quotas
    across Shared LGU NAT IPs, Ambiguous Crawlers, and Commercial Scraper Bots.
    """
    return simulate_anti_scraping_decision(req.profile)


@app.get("/api/v1/open-data/ocds-export")
def export_ocds_open_data(format: str = Query("json", enum=["json", "csv"])):
    """
    Publishes standardized Open Contracting Data Standard (OCDS v1.1) bulk data
    (as served via gs://mphilgeps-open-data-ocds + Cloud CDN) to de-monetize commercial scrapers.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    releases = [
        {
            "ocid": "ocds-mphilgeps-2026-DPWH-R3-004",
            "id": "release-2026-001",
            "date": now_iso,
            "tag": ["tender", "award", "auditWarning"],
            "initiationType": "tender",
            "buyer": {
                "id": "PH-NGA-DPWH-R3",
                "name": "Department of Public Works and Highways - Region III",
            },
            "tender": {
                "id": "ITB-2026-DPWH-R3-004",
                "title": "Construction of Flood Control Dike & Pumping Station - Pampanga River Basin (Package 4)",
                "status": "underAuditReview",
                "procurementMethod": "open",
                "procurementMethodDetails": "RA 12009 Competitive Bidding (Most Advantageous Bid - MAB)",
                "value": {"amount": 145000000.00, "currency": "PHP"},
                "unspscCode": "72141120",
            },
            "auditTelemetry": {
                "spannerGraphCollusionProbabilityIndex": 0.942,
                "riskClassification": "CRITICAL_CARTEL_ALERT",
                "wormStorageBucket": "gs://mphilgeps-audit-worm-10yr/2026/ITB-2026-DPWH-R3-004",
            },
        },
        {
            "ocid": "ocds-mphilgeps-2026-DEPED-NCR-019",
            "id": "release-2026-002",
            "date": now_iso,
            "tag": ["planning", "tender"],
            "initiationType": "tender",
            "buyer": {
                "id": "PH-NGA-DEPED-NCR",
                "name": "Department of Education - National Capital Region",
            },
            "tender": {
                "id": "APP-CSE-2026-DEPED-NCR",
                "title": "FY 2026 Common-Use Supplies and Equipment (APP-CSE) Consolidated Plan",
                "status": "active",
                "procurementMethod": "selective",
                "procurementMethodDetails": "PS-DBM Virtual Store / eMarketplace",
                "value": {"amount": 2849983.50, "currency": "PHP"},
                "unspscCode": "43211503",
            },
            "auditTelemetry": {
                "spannerGraphCollusionProbabilityIndex": 0.041,
                "riskClassification": "LOW_RISK_NORMAL",
                "wormStorageBucket": "gs://mphilgeps-audit-worm-10yr/2026/APP-CSE-2026-DEPED-NCR",
            },
        },
    ]

    # Append any dynamically uploaded session APP-CSE submissions
    for idx, sub in enumerate(submissions_db.values(), start=3):
        releases.append(
            {
                "ocid": f"ocds-mphilgeps-{sub.fiscal_year}-{sub.submission_id}",
                "id": f"release-2026-00{idx}",
                "date": now_iso,
                "tag": ["planning"],
                "initiationType": "tender",
                "buyer": {"id": sub.agency_id, "name": sub.agency_id},
                "tender": {
                    "id": sub.submission_id,
                    "title": f"Uploaded APP-CSE Plan ({sub.total_items} Line Items)",
                    "status": sub.status,
                    "procurementMethodDetails": "RA 12009 Sec. 7 APP-CSE Consolidation",
                    "value": {"amount": sub.total_estimated_budget, "currency": "PHP"},
                },
            }
        )

    if format == "csv":
        csv_lines = [
            "ocid,release_id,buyer_id,tender_id,title,amount_php,currency,status,cpi_score,risk_level"
        ]
        for r in releases:
            t = r.get("tender", {})
            val = t.get("value", {})
            aud = r.get("auditTelemetry", {})
            title_clean = str(t.get("title", "")).replace(",", " ")
            csv_lines.append(
                f"{r['ocid']},{r['id']},{r['buyer']['id']},{t.get('id','')},"
                f"\"{title_clean}\",{val.get('amount',0)},{val.get('currency','PHP')},"
                f"{t.get('status','')},{aud.get('spannerGraphCollusionProbabilityIndex',0.0)},"
                f"{aud.get('riskClassification','NORMAL')}"
            )
        return PlainTextResponse("\n".join(csv_lines), media_type="text/csv")

    return {
        "uri": "https://storage.googleapis.com/mphilgeps-open-data-ocds/releases/2026-daily-ocds.json",
        "version": "1.1",
        "publishedDate": now_iso,
        "publisher": {
            "name": "Procurement Service - Department of Budget and Management (PS-DBM) mPhilGEPS Open Data Portal",
            "scheme": "PH-PSDBM-OCDS",
        },
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "antiScrapingOffloadPolicy": "Served via Google Cloud CDN from gs://mphilgeps-open-data-ocds ($0.00 origin database impact)",
        "releases": releases,
    }

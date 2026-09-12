from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "procurement-planning"

def test_upload_app_cse_within_budget(sample_app_cse_bytes):
    response = client.post(
        "/api/v1/app-cse/upload",
        data={
            "agency_id": "NGA-DEPED-001",
            "fiscal_year": 2026,
            "allocated_budget": 100000.00
        },
        files={
            "file": ("app_cse_2026.xlsx", sample_app_cse_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agency_id"] == "NGA-DEPED-001"
    assert data["fiscal_year"] == 2026
    assert data["total_items"] == 4
    assert data["total_estimated_budget"] == 80700.00
    assert data["budget_status"] == "WITHIN_LIMIT"
    assert data["status"] == "VALIDATED"
    
    # Verify retrieval
    sub_id = data["submission_id"]
    get_res = client.get(f"/api/v1/app-cse/{sub_id}")
    assert get_res.status_code == 200
    assert get_res.json()["submission_id"] == sub_id

def test_upload_app_cse_exceeds_budget(sample_app_cse_bytes):
    response = client.post(
        "/api/v1/app-cse/upload",
        data={
            "agency_id": "LGU-QUEZON-001",
            "fiscal_year": 2026,
            "allocated_budget": 50000.00 # Lower than total 80700.00
        },
        files={
            "file": ("app_cse_2026.xlsx", sample_app_cse_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_estimated_budget"] == 80700.00
    assert data["budget_status"] == "EXCEEDS_BUDGET"

def test_portal_ui_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "mPhilGEPS" in response.text
    assert "Annual Procurement Plan" in response.text

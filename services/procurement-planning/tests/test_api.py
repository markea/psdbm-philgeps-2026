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

def test_dual_pass_unspsc_hierarchy_and_confidence(sample_app_cse_bytes):
    response = client.post(
        "/api/v1/app-cse/upload",
        data={"agency_id": "NGA-DEPED-001", "fiscal_year": 2026, "allocated_budget": 500000.00},
        files={"file": ("app_cse_2026.xlsx", sample_app_cse_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    items = data["items"]
    assert len(items) > 0
    
    first_item = items[0]
    assert "hierarchy" in first_item and first_item["hierarchy"] is not None
    assert "segment" in first_item["hierarchy"]
    assert "family" in first_item["hierarchy"]
    assert "class" in first_item["hierarchy"]
    assert "commodity" in first_item["hierarchy"]
    assert first_item["confidence_score"] >= 0.90
    assert first_item["standardized_description"] is not None

def test_bigquery_demand_stream_endpoint(sample_app_cse_bytes):
    upload_res = client.post(
        "/api/v1/app-cse/upload",
        data={"agency_id": "NGA-DEPED-001", "fiscal_year": 2026, "allocated_budget": 500000.00},
        files={"file": ("app_cse_2026.xlsx", sample_app_cse_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    sub_id = upload_res.json()["submission_id"]
    
    bq_res = client.get(f"/api/v1/app-cse/{sub_id}/bigquery-stream")
    assert bq_res.status_code == 200
    bq_data = bq_res.json()
    assert bq_data["target_table"] == "mphilgeps_analytics.app_demand_forecast"
    assert bq_data["holiday_region"] == "PH"
    assert len(bq_data["records"]) == upload_res.json()["total_items"]
    for rec in bq_data["records"]:
        assert rec["holiday_region"] == "PH"
        assert len(rec["unspsc_commodity_code"]) == 8
        assert rec["total_expenditure"] > 0

def test_upload_actual_sample_file_on_disk():
    import os
    sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sample_app_cse_2026.xlsx"))
    assert os.path.exists(sample_path)
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/app-cse/upload",
        data={"agency_id": "NGA-DEPED-001", "fiscal_year": 2026, "allocated_budget": 500000.00},
        files={"file": ("sample_app_cse_2026.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 7
    assert data["total_estimated_budget"] == 262850.00
    assert data["budget_status"] == "WITHIN_LIMIT"
    
    # Assert all 7 items have full 4-tier UNSPSC hierarchy
    for item in data["items"]:
        assert item["hierarchy"] is not None
        assert item["confidence_score"] >= 0.90
        assert item["standardized_description"] is not None


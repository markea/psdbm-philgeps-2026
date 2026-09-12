# Modernized Philippine Government Electronic Procurement System (mPhilGEPS)

[![Architecture](https://img.shields.io/badge/Architecture-Google_Cloud-4285F4?logo=googlecloud&logoColor=white)](./mPhilGEPS_GoogleCloud_TDD.md)
[![AI Stack](https://img.shields.io/badge/AI-Gemini_%26_Vertex_AI-8E75B2?logo=google&logoColor=white)](./mPhilGEPS_GoogleCloud_BRD.md)
[![Status](https://img.shields.io/badge/Status-Phase_1:_Localhost-success)](./mPhilGEPS_Implementation_Plan.md)

Modernized electronic procurement platform for the Republic of the Philippines (Procurement Service - Department of Budget and Management / PS-DBM), designed to comply with the **New Government Procurement Act (RA 12009)**.

---

## 📚 Architectural & Delivery Documentation

*   📄 **[Business Requirements Document (BRD)](./mPhilGEPS_GoogleCloud_BRD.md):** Detailed mapping of procurement workflows, legal mandates, and AI requirements to the Google Cloud stack.
*   📄 **[Technical Design Document (TDD)](./mPhilGEPS_GoogleCloud_TDD.md):** Engineering blueprint detailing microservices, database schemas, Model Armor, and progressive deployment paths (Localhost $\rightarrow$ GCP Demo $\rightarrow$ Production GKE).
*   📄 **[Master Implementation & Delivery Plan](./mPhilGEPS_Implementation_Plan.md):** Phased execution roadmap, Work Breakdown Structure (WBS), risk registry, and environment promotion matrix.

---

## 🚀 Quickstart: Running the APP-CSE Service Locally

The **APP-CSE (Annual Procurement Plan - Common-Use Supplies and Equipment)** service is currently available to run and test locally with **zero external cloud dependencies**.

### Prerequisites
*   Python 3.11+
*   *(Optional)* Docker & Docker Compose

---

### Option 1: Run via Python Virtualenv (Fastest)

1. Navigate to the service directory:
   ```bash
   cd services/procurement-planning
   ```

2. Start the FastAPI development server:
   ```bash
   .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```
   *(Note: If creating a fresh virtualenv, run `uv venv && uv pip install -r requirements.txt`)*

3. Open your web browser and visit:
   👉 **[http://localhost:8001/](http://localhost:8001/)**

4. **Test with Sample Data:**
   * A pre-generated sample procurement workbook is located at the project root:
     `sample_app_cse_2026.xlsx`
   * Drag and drop this file into the web portal upload area and click **"Process & Validate APP-CSE"**.
   * Inspect the extracted line items, UNSPSC classifications, and budget ceiling validation badge.

5. **Interactive Swagger API Documentation:**
   * Visit **[http://localhost:8001/docs](http://localhost:8001/docs)** to test the REST API directly.

---

### Option 2: Run via Docker Compose

1. From the repository root:
   ```bash
   docker compose -f docker-compose.local.yml up --build
   ```

2. Access the portal at:
   👉 **[http://localhost:8001/](http://localhost:8001/)**

---

## 🧪 Running Automated Tests

To execute the unit and integration test suite (`pytest`):

```bash
cd services/procurement-planning
.venv/bin/pytest -v
```

### Current Test Coverage
*   `test_health_check`: Verifies service liveness.
*   `test_upload_app_cse_within_budget`: Tests valid spreadsheet upload and `WITHIN_LIMIT` status.
*   `test_upload_app_cse_exceeds_budget`: Tests budget ceiling overflow detection.
*   `test_portal_ui_served`: Asserts the static HTML portal is rendered at root `/`.
*   `test_parse_valid_app_cse`: Tests openpyxl spreadsheet parsing and UNSPSC classification.
*   `test_parse_arithmetic_mismatch`: Detects intentional arithmetic discrepancies in workbook formulas.

---

## 📁 Repository Structure

```
psdbm-philgeps-2026/
├── mPhilGEPS_GoogleCloud_BRD.md          # Business Requirements Document
├── mPhilGEPS_GoogleCloud_TDD.md          # Technical Design Document
├── mPhilGEPS_Implementation_Plan.md      # Master Implementation & Delivery Plan
├── README.md                             # Project overview and local run instructions
├── docker-compose.local.yml              # Local container orchestration
├── sample_app_cse_2026.xlsx              # Sample procurement workbook for testing
└── services/
    └── procurement-planning/             # APP-CSE Microservice (FastAPI)
        ├── Dockerfile
        ├── requirements.txt
        ├── app/
        │   ├── main.py                   # REST endpoints & web portal handler
        │   ├── models.py                 # Pydantic data schemas
        │   ├── parser.py                 # openpyxl spreadsheet parser
        │   ├── classifier.py             # UNSPSC categorization engine
        │   └── static/
        │       └── index.html            # Web UI dashboard
        └── tests/
            ├── conftest.py               # In-memory Excel fixtures
            ├── test_api.py               # FastAPI integration tests
            └── test_parser.py            # Workbook parsing tests
```

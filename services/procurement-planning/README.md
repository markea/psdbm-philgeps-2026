# APP-CSE Procurement Planning Microservice

Microservice responsible for ingesting, validating, and extracting line items from Annual Procurement Plan (APP-CSE) spreadsheets submitted by Philippine government agencies.

---

## Quickstart

### 1. Start Server
```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

*   **Web Portal UI:** [http://localhost:8001/](http://localhost:8001/)
*   **Swagger API Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)

### 2. Run Tests
```bash
.venv/bin/pytest -v
```

### 3. Key Endpoints
*   `GET /`: Serves the interactive browser dashboard.
*   `GET /health`: Health check.
*   `POST /api/v1/app-cse/upload`: Multipart upload endpoint accepting `.xlsx` files with `agency_id`, `fiscal_year`, and `allocated_budget`.
*   `GET /api/v1/app-cse/{submission_id}`: Retrieves parsed submission by ID.

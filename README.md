# Modernized Philippine Government Electronic Procurement System (mPhilGEPS) Phase 2

[![Architecture](https://img.shields.io/badge/Architecture-Google_Cloud_%26_Spanner_Graph-4285F4?logo=googlecloud&logoColor=white)](./mPhilGEPS_GoogleCloud_TDD.md)
[![AI Stack](https://img.shields.io/badge/AI-Gemini_3.1_Pro_%26_3.7_Flash-8E75B2?logo=google&logoColor=white)](./mPhilGEPS_GoogleCloud_BRD.md)
[![BOM & Cost](https://img.shields.io/badge/BOM-3--Year_TCO_₱34.3M-34A853?logo=googlecloud&logoColor=white)](./mPhilGEPS_Production_BOM.md)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Cloud_Run-0F9D58?logo=googlecloud&logoColor=white)](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/)

Modernized electronic procurement platform for the Republic of the Philippines (Procurement Service - Department of Budget and Management / PS-DBM), engineered to comply with the **New Government Procurement Act (RA 12009 / NGPA)** and the **Data Privacy Act (RA 10173)**.

---

## 📚 Architectural, Delivery & Financial Documentation

*   📄 **[Business Requirements Document (BRD)](./mPhilGEPS_GoogleCloud_BRD.md):** Detailed mapping of procurement workflows, legal mandates, and next-generation AI requirements to the Google Cloud stack.
*   📄 **[Technical Design Document (TDD)](./mPhilGEPS_GoogleCloud_TDD.md):** Engineering blueprint detailing in-database AI processing (Spanner Graph & BigQuery ML), dual-pass UNSPSC classification, Document AI verification matrix, Confidential Space Bid Vault, and progressive deployment paths (Localhost $\rightarrow$ GCP Demo $\rightarrow$ Production GKE).
*   📊 **[Production Bill of Materials (BOM) & 3-Year TCO (Markdown)](./mPhilGEPS_Production_BOM.md):** Itemized production-grade cost model across 8 architectural categories, multi-environment distribution, CUD optimizations (-35.1%), and 3-year lifecycle projection ($1.00 USD = ₱65.00 PHP).
*   📑 **[Production Bill of Materials (BOM) & 3-Year TCO (Executive PDF)](./mPhilGEPS_Production_BOM.pdf):** 14-page styled executive report with line-item SKU rates, subtotals, and budgetary recommendations for PS-DBM leadership.
*   📄 **[Master Implementation & Delivery Plan](./mPhilGEPS_Implementation_Plan.md):** Phased execution roadmap, Work Breakdown Structure (WBS), risk registry, and environment promotion matrix.
*   📄 **[PS-DBM Gemini Requirements Architecture v1.0](./PS-DBM%20-%20Gemini%20Reqs%20-%20v1.0.pdf):** Foundational architectural specifications and Terms of Reference (TOR) analysis.

---

## 💰 Production Bill of Materials (BOM) & Sizing Summary

*   **Primary Region:** Singapore (`asia-southeast1`) | **Disaster Recovery Region:** Jakarta (`asia-southeast2`)
*   **Currency Benchmark:** $1.00 USD = **₱65.00 PHP**
*   **Workload Sizing:** 3,500 baseline / 5,500 peak concurrent users, 10,000+ merchants, 12,500 document pages/mo, 150,000 APP-CSE items/mo, 10-year WORM compliance retention.

| Cost Dimension | On-Demand (List Price) | 1-Year Committed Use (CUD) | 3-Year Committed Use (CUD) |
| :--- | :--- | :--- | :--- |
| **Monthly Recurring (USD)** | **$21,350.61** | **$16,850.00** | **$13,950.00** |
| **Monthly Recurring (PHP @ ₱65)** | **₱1,387,789.65** | **₱1,095,250.00** | **₱906,750.00** |
| **Annualized Spend (USD)** | **$256,207.32** | **$202,200.00** | **$167,400.00** |
| **Annualized Spend (PHP @ ₱65)** | **₱16,653,475.80** | **₱13,143,000.00** | **₱10,881,000.00** |
| **3-Year Lifecycle Total (USD)** | **$806,807.00** | **$637,500.00** | **$527,600.00** |
| **3-Year Lifecycle Total (PHP @ ₱65)** | **₱52,442,455.00** | **₱41,437,500.00** | **₱34,294,000.00** |
| **Effective Cost Reduction** | *Baseline* | **-21.1%** | **-35.1%** |

### 8 Architectural Cost Pillars:
1. **Core Compute & Containers:** GKE Autopilot (55 vCPU / 150 GiB RAM avg), Cloud Run, Confidential Space VMs — **$3,186.00 / mo**
2. **Databases:** Cloud Spanner + Spanner Graph (1,200 PU), AlloyDB Enterprise HA (8 vCPU / 64 GiB), Memorystore Redis HA — **$3,102.80 / mo**
3. **Data Warehouse & In-Database ML:** BigQuery Active/Long-term storage, on-demand queries, BigQuery ML (`ARIMA_PLUS`), Looker Core — **$5,732.33 / mo**
4. **Sovereign AI & Multi-Agent Hub:** Document AI (CDE/Form/Layout), Gemini 3.1 Pro, Gemini 3.7 Flash, Vertex AI Vector Search, Model Armor — **$702.58 / mo**
5. **Edge Perimeter & Networking:** Apigee API Management (4M calls/mo), Cloud Armor Enterprise, Global ALB, Cloud CDN, Cloud NAT — **$4,872.10 / mo**
6. **Sovereign Root of Trust & SOC:** Cloud KMS HSM (FIPS 140-2 Level 3), Google SecOps (Chronicle) 20 GB/day telemetry — **$931.50 / mo**
7. **Storage & 10-Year WORM:** Cloud Storage Standard (10 TB) + Archive Storage with Bucket Lock in Compliance Mode (25 TB) — **$298.30 / mo**
8. **Observability & 24/7 Support:** Cloud Operations Logging & Monitoring, Gemini Enterprise (35 seats), Enhanced Support with 1-hr P1 SLA — **$2,525.00 / mo**

### 🛡️ High Availability, Spike Handling & Disaster Recovery (BCP)
*   **Intra-Region HA (Singapore Multi-Zone):** Zero single points of failure across 3 independent availability zones (GKE Multi-AZ, Spanner 3-zone Paxos, AlloyDB active-standby, Redis HA).
*   **Traffic Spike Resilience:** Sized for **3,500 baseline** scaling to **5,500+ peak concurrent users** (600–1,000 edge RPS). Spikes absorbed via Cloud CDN (80% cache hit), Cloud Armor DDoS protection, Cloud Run serverless bursts, GKE HPA autoscaling (30 to 80+ pods in 90s), Redis Redlock cart holds, and Spanner autoscaling.
*   **Inter-Region Disaster Recovery (Singapore $\rightarrow$ Jakarta `asia-southeast2`):**
    *   **Option A (Cold Standby DR - Recommended for GAA Budget):** Automated cross-region backups and Terraform rehydration — **+$459.00 / mo (₱29,835 / mo)** with **RPO $< 15\text{ mins}$** and **RTO $< 1\text{ hour}$**.
    *   **Option B (Warm Standby DR):** Continuous live secondary replica in Jakarta — **+$3,129.00 / mo (₱203,385 / mo)** with **RPO $< 1\text{ min}$** and **RTO $< 15\text{ mins}$**.

---

## 🌐 Live Cloud Run Demonstration Prototype

A public demonstration prototype of the mPhilGEPS portal is deployed live on Google Cloud Run:

* 🔗 **Live Web Portal:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/)
* 📑 **Interactive OpenAPI Swagger Docs:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/docs](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/docs)
* 🩺 **Health Check Endpoint:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/health](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/health)
* **Access Mode:** Public unauthenticated demo sandbox (`--allow-unauthenticated`) featuring persistent warning banners indicating prototype demonstration status.

---

## 🚀 Quickstart: Running the APP-CSE Service Locally

The **APP-CSE (Annual Procurement Plan - Common-Use Supplies and Equipment)** service can also be run locally with **zero external cloud dependencies**.

### Prerequisites
*   Python 3.11+
*   *(Optional)* Docker & Docker Compose

---

### Option 1: Run via Python Virtualenv (Fastest)

1. Navigate to the service directory:
   ```bash
   cd services/procurement-planning
   ```

2. Start the development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. Open your web browser and visit:
   👉 **[http://localhost:8001/](http://localhost:8001/)**

4. **Test with Sample Data:**
   * Drag and drop [`sample_app_cse_2026.xlsx`](./sample_app_cse_2026.xlsx) into the upload area and click **"Process & Validate APP-CSE"**.
   * Inspect the extracted line items, 4-tier UNSPSC classifications, and budget ceiling validation badge.

5. **Test the Multi-Agent Hub POC:**
   * Click the glowing `✨` button in the bottom right corner.
   * Toggle between the specialised agents (BAC Advisor, COA Auditor, Merchant Help) and test interactive chat sessions anchored in RA 12009 policy rules.

---

### Option 2: Run via Docker Compose

```bash
docker compose -f docker-compose.local.yml up --build
```
Access the portal at **[http://localhost:8001/](http://localhost:8001/)**.

---

## 🧪 Running Automated Tests

To execute the unit and integration test suite (`pytest`):

```bash
cd services/procurement-planning
pytest -v
```

---

## 📁 Repository Structure

```
psdbm-philgeps-2026/
├── PS-DBM - Gemini Reqs - v1.0.pdf       # Core architecture specifications
├── mPhilGEPS_GoogleCloud_BRD.md          # Business Requirements Document
├── mPhilGEPS_GoogleCloud_TDD.md          # Technical Design Document
├── mPhilGEPS_Production_BOM.md          # Itemized Bill of Materials & Sizing (Markdown)
├── mPhilGEPS_Production_BOM.pdf          # 14-Page Executive BOM & 3-Year TCO Report (PDF)
├── generate_pdf.py                       # Automated PDF report generation pipeline
├── mPhilGEPS_Implementation_Plan.md      # Master Implementation & Delivery Plan
├── README.md                             # Project overview and run instructions
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

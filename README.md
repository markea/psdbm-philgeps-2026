# Modernized Philippine Government Electronic Procurement System (mPhilGEPS) Phase 2

[![Architecture](https://img.shields.io/badge/Architecture-Google_Cloud_%26_Spanner_Graph-4285F4?logo=googlecloud&logoColor=white)](./mPhilGEPS_GoogleCloud_TDD.md)
[![AI Stack](https://img.shields.io/badge/AI-Gemini_3.1_Pro_%26_3.7_Flash-8E75B2?logo=google&logoColor=white)](./mPhilGEPS_GoogleCloud_BRD.md)
[![BOM & Cost](https://img.shields.io/badge/BOM-3--Year_TCO_₱35.9M-34A853?logo=googlecloud&logoColor=white)](./mPhilGEPS_Production_BOM.md)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Cloud_Run-0F9D58?logo=googlecloud&logoColor=white)](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/)

Modernized electronic procurement platform for the Republic of the Philippines (Procurement Service - Department of Budget and Management / PS-DBM), engineered to comply with the **New Government Procurement Act (RA 12009 / NGPA)** and the **Data Privacy Act (RA 10173)**.

---

## 📚 Architectural, Delivery & Financial Documentation

*   📄 **[Business Requirements Document (BRD)](./mPhilGEPS_GoogleCloud_BRD.md):** Detailed mapping of procurement workflows, legal mandates, next-generation AI requirements, and 4-tier commercial anti-scraping / OCDS Open Data de-monetization strategy to the Google Cloud stack.
*   📄 **[Technical Design Document (TDD)](./mPhilGEPS_GoogleCloud_TDD.md):** Engineering blueprint detailing in-database AI processing (Spanner Graph & BigQuery ML), dual-pass UNSPSC classification, Document AI verification matrix, Confidential Space Bid Vault, reCAPTCHA Enterprise + Cloud Armor JA3 anti-scraping perimeter, and progressive deployment paths (Localhost $\rightarrow$ GCP Demo $\rightarrow$ Production GKE).
*   📊 **[Production Bill of Materials (BOM) & 3-Year TCO (Markdown)](./mPhilGEPS_Production_BOM.md):** Itemized production-grade cost model across 8 architectural categories, multi-environment distribution, CUD optimizations (-35.4%), and 3-year lifecycle projection ($1.00 USD = ₱65.00 PHP).
*   📑 **[Production Bill of Materials (BOM) & 3-Year TCO (Executive PDF)](./mPhilGEPS_Production_BOM.pdf):** 14-page styled executive report with line-item SKU rates, subtotals, and budgetary recommendations for PS-DBM leadership.
*   📄 **[Master Implementation & Delivery Plan](./mPhilGEPS_Implementation_Plan.md):** Phased execution roadmap, Work Breakdown Structure (WBS), risk registry (including commercial anti-scraping mitigation `RSK-07`), and environment promotion matrix.
*   📄 **[PS-DBM Gemini Requirements Architecture v1.0](./PS-DBM%20-%20Gemini%20Reqs%20-%20v1.0.pdf):** Foundational architectural specifications and Terms of Reference (TOR) analysis.

---

## 💰 Production Bill of Materials (BOM) & Sizing Summary

*   **Primary Region:** Singapore (`asia-southeast1`) | **Disaster Recovery Region:** Jakarta (`asia-southeast2`)
*   **Currency Benchmark:** $1.00 USD = **₱65.00 PHP**
*   **Workload Sizing:** 3,500 baseline / 5,500 peak concurrent users, 10,000+ merchants, 12,500 document pages/mo, 150,000 APP-CSE items/mo, 10-year WORM compliance retention.
*   **Data Warehouse Engine:** BigQuery Enterprise Edition Autoscaling Slots (25 Baseline, 100 Hard Cap) with zero-cost bundled BigQuery ML.
*   **Anti-Scraping & Open Data Offload:** Cloud Armor Enterprise (JA3 TLS Fingerprinting) + reCAPTCHA Enterprise (500k frictionless risk assessments/mo protecting shared agency NAT IPs) + Dedicated OCDS Open Data bulk feeds on Cloud Storage/CDN.

| Cost Dimension | On-Demand (List Price) | 1-Year Committed Use (CUD) | 3-Year Committed Use (CUD) |
| :--- | :--- | :--- | :--- |
| **Monthly Recurring (USD)** | **$22,588.66** | **$17,709.05** | **$14,586.55** |
| **Monthly Recurring (PHP @ ₱65)** | **₱1,468,262.90** | **₱1,151,088.25** | **₱948,125.75** |
| **Annualized Spend (USD)** | **$271,063.92** | **$212,508.60** | **$175,038.60** |
| **Annualized Spend (PHP @ ₱65)** | **₱17,619,154.80** | **₱13,813,059.00** | **₱11,377,509.00** |
| **3-Year Lifecycle Total (USD)** | **$853,500.00** | **$669,500.00** | **$551,808.60** |
| **3-Year Lifecycle Total (PHP @ ₱65)** | **₱55,477,500.00** | **₱43,517,500.00** | **₱35,867,559.00** |
| **Effective Cost Reduction** | *Baseline* | **-21.6%** | **-35.4%** |

### 8 Architectural Cost Pillars:
1. **Core Compute & Containers:** GKE Autopilot (55 vCPU / 150 GiB RAM avg), Cloud Run, Confidential Space VMs — **$3,186.00 / mo**
2. **Databases:** Cloud Spanner + Spanner Graph (1,200 PU), AlloyDB Enterprise HA (8 vCPU / 64 GiB), Memorystore Redis HA — **$3,102.80 / mo**
3. **Data Warehouse & Governed Slots:** BigQuery Enterprise Edition Slots (25 Baseline, 100 Max Cap), BigQuery ML (`ARIMA_PLUS` bundled at $0 additional cost), Active/Long-term storage, Looker Core — **$6,480.38 / mo**
4. **Sovereign AI & Multi-Agent Hub:** Document AI (CDE/Form/Layout), Gemini 3.1 Pro, Gemini 3.7 Flash, Vertex AI Vector Search, Model Armor — **$702.58 / mo**
5. **Edge Perimeter, Networking & Anti-Scraping:** Apigee API Management (4M calls/mo), Cloud Armor Enterprise (JA3), reCAPTCHA Enterprise (500k assessments/mo), Global ALB, Cloud CDN (OCDS Open Data), Cloud NAT — **$5,362.10 / mo**
6. **Sovereign Root of Trust & SOC:** Cloud KMS HSM (FIPS 140-2 Level 3), Google SecOps (Chronicle) 20 GB/day telemetry — **$931.50 / mo**
7. **Storage, OCDS Open Data & 10-Year WORM:** Cloud Storage Standard (10 TB incl. OCDS Bulk Exports) + Archive Storage with Bucket Lock in Compliance Mode (25 TB) — **$298.30 / mo**
8. **Observability & 24/7 Support:** Cloud Operations Logging & Monitoring, Gemini Enterprise (35 seats), Enhanced Support with 1-hr P1 SLA — **$2,525.00 / mo**

### 🛡️ High Availability, Anti-Scraping & Disaster Recovery (BCP)
*   **Intra-Region HA (Singapore Multi-Zone):** Zero single points of failure across 3 independent availability zones (GKE Multi-AZ, Spanner 3-zone Paxos, AlloyDB active-standby, Redis HA).
*   **Traffic Spike & Anti-Scraping Resilience:** Sized for **3,500 baseline** scaling to **5,500+ peak concurrent users** (600–1,000 edge RPS). Commercial scrapers and volumetric surges are absorbed at the edge via **Cloud Armor JA3 TLS fingerprinting**, **reCAPTCHA Enterprise frictionless edge scoring** (preventing false positives on shared government agency NAT IPs), **Cloud CDN** (80% cache hit + public OCDS bulk feeds), Cloud Run serverless bursts, GKE HPA autoscaling, Redis Redlock cart holds, and Spanner autoscaling.
*   **Inter-Region Disaster Recovery (Singapore $\rightarrow$ Jakarta `asia-southeast2`):**
    *   **Option A (Cold Standby DR - Recommended for GAA Budget):** Automated cross-region backups and Terraform rehydration — **+$459.00 / mo (₱29,835 / mo)** with **RPO $< 15\text{ mins}$** and **RTO $< 1\text{ hour}$**.
    *   **Option B (Warm Standby DR):** Continuous live secondary replica in Jakarta — **+$3,129.00 / mo (₱203,385 / mo)** with **RPO $< 1\text{ min}$** and **RTO $< 15\text{ mins}$**.

---

## 🌐 Live Cloud Run Demonstration Prototype (`v2.0.0-DEMO`)

A public demonstration prototype of the mPhilGEPS portal and Multi-Agent Intelligence Command Center is deployed live on Google Cloud Run:

* 🔗 **Live Web Portal:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/)
* 📊 **Golden Dataset Agent Evaluation API:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/api/v1/agents/eval-report](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/api/v1/agents/eval-report) ([Markdown Scorecard](./evals/EVAL_REPORT.md))
* 🕸️ **Spanner Graph Cartel API:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/api/v1/collusion/graph](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/api/v1/collusion/graph)
* 🌐 **OCDS v1.1 Open Data Bulk Feed:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/api/v1/open-data/ocds-export?format=json](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/api/v1/open-data/ocds-export?format=json)
* 📑 **Interactive OpenAPI Swagger Docs:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/docs](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/docs)
* 🩺 **Health Check Endpoint:** [https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/health](https://mphilgeps-demo-portal-684075603690.asia-southeast1.run.app/health)
* **Interactive Demo Capabilities:**
  1. **Tab 1 — APP-CSE Dual-Pass AI Ingestion:** One-click synthetic workbook generator, Pass 1 (`Gemini 3.7 Flash`) & Pass 2 (`Gemini 3.1 Pro`) 4-tier UNSPSC classification, RA 12009 Sec. 7.2 ceiling validation, and BigQuery ML `ARIMA_PLUS` stream.
  2. **Tab 2 — Cloud Spanner Graph Anti-Collusion Visualizer:** Interactive SVG property graph (`MPhilGepsProcurementGraph`), GQL query viewer, `CPI = 0.942` alert, and Benford's Law first-digit anomaly chart.
  3. **Tab 3 — 4-Tier Anti-Scraping & OCDS Open Data Offload:** Live edge simulator comparing Shared LGU NAT IPs (`Score 0.94 -> 200 OK`) vs. Commercial Scraper Bots (`Score 0.08 -> 429 Blocked & Redirected to OCDS CDN`), plus 1-click OCDS v1.1 JSON/CSV downloads.
  4. **Tab 4 — Golden Dataset Evaluation Suite (15 Cases):** Live evaluation dashboard benchmarking `BAC Advisor`, `COA Auditor`, `Merchant Help`, `Supervisor Auto-Router`, and `Model Armor RA 10173 DLP` (`15/15 PASS — 100.0% Composite Score`).
* **Access Mode:** Public unauthenticated demo sandbox (`--allow-unauthenticated`) featuring persistent **⚠️ DEMO ENVIRONMENT ONLY** warning banners.

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

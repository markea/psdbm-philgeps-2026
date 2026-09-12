## Goal Description
The objective is to establish the Technical Design Document (TDD) for the Modernized Philippine Government Electronic Procurement System (mPhilGEPS). This document provides the architectural blueprint to transition the business requirements (BRD) into a technical reality. Crucially, the architecture is designed to support three distinct environments: a developer-friendly **Localhost** setup, a cost-effective **GCP Demo** environment for stakeholder validation, and a highly scalable, secure **Production** path on Google Cloud.

## User Review Required
> [!IMPORTANT]
> **Database Selection:** The TDD proposes PostgreSQL as the primary relational database. Please confirm if there are any legacy database compatibility requirements (e.g., Oracle or SQL Server) that would necessitate a different engine or a migration tool like Database Migration Service (DMS).

> [!WARNING]
> **AI API Usage Locally:** The localhost version assumes developers will use their own Google Cloud credentials (`gcloud auth application-default login`) to call Vertex AI and Document AI endpoints, as there are no local emulators for these advanced enterprise models. Please confirm if developer access to a sandbox GCP project is permitted.

## Open Questions
1. **Frontend Tech Stack:** Do you have a preferred frontend framework (e.g., React, Next.js, Angular) for the UI? The TDD currently remains framework-agnostic.
2. **Backend Tech Stack:** For the microservices, what is the preferred programming language (e.g., Go, Python, Node.js)? Python is highly recommended for seamless Vertex AI and Agent Development Kit (ADK) integration.
3. **CI/CD Pipeline:** Do you intend to use Google Cloud Build, GitLab CI/CD, or GitHub Actions for deployment from the `psdbm-philgeps-2026` repository?

---

## Proposed Changes

The system architecture is divided into three evolutionary stages to facilitate rapid development, stakeholder demonstration, and enterprise-grade production deployment.

### 1. Localhost Version (Developer Environment)
This setup ensures developers can build and test rapidly without incurring cloud costs for standard compute and database resources.

#### Infrastructure & Tools
*   **Orchestration:** `Docker Compose` to spin up the entire stack locally.
*   **Frontend & Microservices:** Run natively or inside lightweight Docker containers with hot-reloading.
*   **Database:** Local `PostgreSQL 15+` Docker container.
*   **Cache:** Local `Redis` Docker container for session and catalog caching.

#### AI & Integrations
*   **Gemini & Document AI:** Calls route to a shared "Sandbox" GCP project via Application Default Credentials (ADC).
*   **Multi-Agent ADK:** Runs locally alongside the microservices.

```mermaid
graph TD
    Dev[Developer Browser] --> Frontend[Local Web Server :3000]
    Frontend --> API[Local API Gateway/BFF :8080]
    API --> Services[Docker: Microservices]
    Services --> DB[(Docker: PostgreSQL)]
    Services --> Cache[(Docker: Redis)]
    Services --> GCP_Sandbox[GCP Sandbox: Vertex AI & DocAI]
```

---

### 2. GCP Demo Version (Stakeholder Validation)
A cost-optimized, serverless environment deployed in Google Cloud to demonstrate functionalities (like the Virtual Store and Multi-Agent Chatbot) to PS-DBM executives and COA auditors.

#### Infrastructure & Tools
*   **Compute:** **Cloud Run** (Serverless). Scales to zero when not in use to save costs.
*   **Database:** **Cloud SQL for PostgreSQL** (Basic `db-f1-micro` tier) or AlloyDB Omni.
*   **Cache:** **Memorystore for Redis** (Basic tier).
*   **Storage:** **Cloud Storage** for uploading test eligibility documents.

#### Security & AI
*   **Access Control:** **Identity-Aware Proxy (IAP)** to restrict access only to authorized PS-DBM demo accounts. No public internet access.
*   **Agent Security:** **Google Cloud Model Armor** intercepts all ADK agent inputs/outputs to prevent prompt injection and redact sensitive data (DLP).
*   **AI Integrations:** Live Vertex AI, Document AI, and ADK Agents enabled.

```mermaid
graph TD
    DemoUser[Stakeholder] --> IAP[Identity-Aware Proxy]
    IAP --> CloudRun[Cloud Run: mPhilGEPS Demo Services]
    CloudRun --> CloudSQL[(Cloud SQL PostgreSQL)]
    CloudRun --> Memorystore[(Memorystore)]
    CloudRun --> ModelArmor[Google Cloud Model Armor]
    ModelArmor --> AI[Vertex AI & ADK Agents]
```

---

### 3. Path to Production (Enterprise Scale)
The enterprise architecture built to handle 3,500 - 5,500 daily concurrent users, 5-second max page loads, and strict compliance with RA 12009.

#### Infrastructure & Tools
*   **Compute:** **Google Kubernetes Engine (GKE)** for high availability, auto-scaling, and microservice orchestration.
*   **Database:** **Cloud SQL HA** (High Availability across zones) or **AlloyDB Enterprise** for massive transactional throughput.
*   **API Management:** **Apigee** for secure, throttled integration with external agencies (SEC, BIR, DTI).
*   **Data Analytics & Fraud:** **BigQuery** serving as the data warehouse for Looker dashboards and BigQuery ML forecasting.

#### Security, AI & Observability
*   **WAF & DDoS Protection:** **Cloud Load Balancing + Cloud Armor** protects the perimeter.
*   **Agent Security (Model Armor):** All interactions with the ADK Multi-Agent System are routed through **Google Cloud Model Armor**, providing robust protection against prompt injection, jailbreaks, and ensuring sensitive PII is redacted before reaching the LLMs.
*   **Agent Evaluation (Evals):** Implementing a continuous **Vertex AI Eval Quality Flywheel**. This framework uses LLM-as-a-judge to score ADK agent responses for groundedness, safety, and helpfulness before and after code changes.
*   **Encryption:** **Cloud KMS** (Customer Managed Encryption Keys) for cryptographic sealing of e-Bids.
*   **Anti-Gravity Maintenance:** PS-DBM Developers use the Anti-Gravity IDE assistant integrated directly with Gemini Enterprise to monitor, debug, and patch the GKE clusters.
*   **Observability & Audit Trails (COA Compliance):** **Cloud Audit Logs** and **Cloud Logging** integrated via OpenTelemetry. A highly secure, append-only sink to **BigQuery** guarantees data immutability for the Commission on Audit (COA).
*   **CI/CD Pipeline:** **Cloud Build** combined with Artifact Registry handles automated testing and zero-downtime rolling deployments to GKE.

```mermaid
graph TD
    Public[Public Users / Merchants] --> Armor[Cloud Armor WAF + Load Balancer]
    Armor --> GKE[GKE Cluster: mPhilGEPS Prod Services]
    GKE --> AlloyDB[(AlloyDB HA)]
    GKE --> BQ[(BigQuery: Immutable Audit & Analytics)]
    GKE --> Apigee[Apigee API Gateway]
    Apigee <--> Ext[External Gov Agencies]
    GKE --> ModelArmor[Google Cloud Model Armor]
    ModelArmor --> AI[Vertex AI, DocAI, ADK Agents]
    AI -.-> Evals[Vertex AI Evals Framework]
    GKE -.-> Obs[Cloud Logging & Monitoring]
    CI[Cloud Build CI/CD] -.-> GKE
```

---


---

## Detailed Subsystem Design

To provide a deeper understanding of the implementation, this section breaks down the specific microservices, database schemas, and the Multi-Agent System topology required to fulfill the BRD.

### 4.1 Microservices Architecture
To fully support the Core Functional Requirements outlined in the BRD, the system will be decoupled into the following domain-driven microservices. We recommend **Python (FastAPI)** for AI-heavy services and **Go** for high-throughput transactional services.

*   **`IdentityAndAccessService`:** Manages user authentication (Cloud Identity), Role-Based Access Control (RBAC), and session JWTs.
*   **`MerchantRegistryService` (GOP-OMR):** Handles supplier registration, Platinum Eligibility upgrades, and integrates with Document AI to automatically extract and verify business permits.
*   **`ProcurementPlanningService`:** Manages the submission, validation, and consolidation of the Annual Procurement Plan for Common-Use Supplies and Equipment (APP-CSE) for all government agencies.
*   **`VirtualStoreService`:** Powers the eMarketplace frontend. Handles catalog browsing, cart management, and order placement. Heavily utilizes Redis for sub-second caching.
*   **`LogisticsAndInventoryService`:** Tracks physical stock levels across the Main, Regional, and LGU Depots. Integrates with BigQuery ML for predictive demand forecasting to prevent stockouts.
*   **`BiddingAndAuctionService`:** Manages the entire lifecycle of procurement projects, including e-bidding, smart contracts, e-Reverse Auctions, and electronic bid sealing (via Cloud KMS).
*   **`PaymentAndBillingService`:** Manages digital wallets, electronic payments, and integrations with external gateways (e.g., LBP e-Payment, GovPay, LDDAP-ADA).
*   **`AIOrchestratorService`:** The dedicated Python backend hosting the Agent Development Kit (ADK) runtime, Vertex AI search grounding, and routing for all Multi-Agent interactions.
*   **`AnalyticsAndAuditService`:** An asynchronous service responsible for funneling transactional logs into BigQuery for COA audit trails, Looker dashboards, and fraud anomaly detection.

### 4.2 Database Schema (High-Level)
The primary relational database (PostgreSQL/AlloyDB) will be structured to enforce strict referential integrity.

*   `users`: Stores PS-DBM admins, agency buyers, and COA auditors.
*   `merchants`: Stores registered suppliers (GOP-OMR) and their eligibility status (linked to SEC/BIR integrations).
*   `app_cse_submissions`: Stores the Annual Procurement Plans submitted by agencies, containing line items for demand forecasting.
*   `bids`: Stores encrypted bid payloads, timestamped, with foreign keys linking back to `merchants` and specific procurement projects.
*   `audit_ledger`: An append-only table (mirrored to BigQuery) capturing every state change to a bid or merchant status.

### 4.3 Multi-Agent ADK Topology (The AI Engine)
Instead of a monolithic chatbot or Dialogflow CX, the AI engine is a distributed, multi-agent system built on Google's ADK.

```mermaid
graph TD
    Client[Frontend Chat UI] --> ModelArmor[Google Cloud Model Armor]
    ModelArmor --> Triage[Triage Agent / Router]
    
    Triage -->|Intent: Find Products| VSAgent[Virtual Store Agent]
    Triage -->|Intent: Procurement Rules| LegalAgent[Legal / RA 12009 Agent]
    Triage -->|Intent: Audit & Anomalies| AuditorAgent[COA Auditor Agent]
    
    VSAgent --> DB[(Virtual Store Catalog / Redis)]
    LegalAgent --> Drive[Google Drive / Vertex AI Search]
    AuditorAgent --> BQML[BigQuery Fraud Detection]
```

*   **Triage Agent (Router):** Uses a fast model (e.g., Gemini 2.0 Flash) to instantly classify user intent and route the query to the correct specialized sub-agent.
*   **Virtual Store Agent:** Capable of executing SQL/API calls to query the catalog (e.g., "Find me the top 3 cheapest laptops that meet these specs").
*   **Legal / RA 12009 Agent:** Grounded in a Vertex AI Search corpus containing the full text of Republic Act 12009 and historical GPPB resolutions.
*   **COA Auditor Agent:** Synthesizes complex anomaly detection reports from BigQuery ML into readable narratives for investigators.


---

## 5. Subsystem Deep Dive: APP-CSE Submission Portal

To illustrate the concrete implementation path, this section provides the code-ready technical design for the **APP-CSE (Annual Procurement Plan - Common-Use Supplies and Equipment) Submission Portal**.

### 5.1 Architecture & End-to-End Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Officer as Agency Procurement Officer
    participant UI as Next.js Web Portal
    participant API as ProcurementPlanningService (FastAPI)
    participant GCS as Cloud Storage Bucket (app-cse-uploads)
    participant Tasks as Cloud Tasks / Pub/Sub
    participant Worker as Asynchronous Parser Worker
    participant DocAI as Document AI / Gemini Flash
    participant DB as PostgreSQL / AlloyDB
    participant BQ as BigQuery (Demand Forecasting)

    Officer->>UI: Uploads signed APP-CSE (.xlsx / .pdf) or fills web form
    UI->>API: POST /api/v1/app-cse/upload
    API->>GCS: Stage file in GCS
    API->>DB: Create submission record (Status: PROCESSING)
    API->>Tasks: Enqueue parse & validation task
    API-->>UI: Return submission_id & 202 Accepted
    
    Tasks->>Worker: Consume task
    Worker->>GCS: Download workbook
    Worker->>DocAI: Extract line items & validate against budget
    Worker->>DocAI: Auto-map descriptions to UNSPSC codes
    Worker->>DB: Persist normalized line items (Status: VALIDATED)
    Worker->>BQ: Stream validated records for Demand Forecast
    UI->>API: Poll GET /api/v1/app-cse/{id}/status
    API-->>UI: Return validation summary & budget variance
```

### 5.2 Frontend Component Architecture
*   **`AppCseUploaderComponent`:** Drag-and-drop zone with client-side file signature validation (`.xlsx`, `.pdf`), file size limit enforcement (max 25MB), and upload progress reporting.
*   **`AppCseLineItemGrid`:** Virtualized dynamic table (e.g., AG Grid / TanStack Table) allowing agencies to adjust quarterly quantities (Q1–Q4), unit prices, and target delivery depots.
*   **`BudgetValidationBadge`:** Real-time visual indicator comparing the total estimated cost of Common-Use Supplies against the agency's approved budget allocation.

### 5.3 REST API Contracts (OpenAPI)

#### `POST /api/v1/app-cse/upload`
*   **Purpose:** Initial staging of uploaded APP-CSE Excel workbook or PDF.
*   **Request:** `multipart/form-data` with `agency_id`, `fiscal_year`, and `file`.
*   **Response (202 Accepted):**
```json
{
  "submission_id": "cse-2026-0912-abcd",
  "agency_id": "NGA-DEPED-001",
  "fiscal_year": 2026,
  "status": "PROCESSING",
  "file_uri": "gs://mphilgeps-app-cse-uploads/2026/NGA-DEPED-001/app_cse.xlsx",
  "estimated_completion_seconds": 15
}
```

#### `GET /api/v1/app-cse/{submission_id}`
*   **Purpose:** Fetch submission status, extracted line items, and budget validation results.
*   **Response (200 OK):**
```json
{
  "submission_id": "cse-2026-0912-abcd",
  "status": "COMPLETED",
  "total_items": 42,
  "total_estimated_budget": 1250000.00,
  "allocated_budget": 1500000.00,
  "budget_status": "WITHIN_LIMIT",
  "items": [
    {
      "item_code": "44122011-FO-F01",
      "unspsc_code": "44122011",
      "description": "FOLDER, FANCY, A4",
      "q1_qty": 500,
      "q2_qty": 500,
      "q3_qty": 200,
      "q4_qty": 200,
      "total_qty": 1400,
      "unit_price": 42.50,
      "total_amount": 59500.00,
      "preferred_depot": "DEPOT-NCR-MANILA"
    }
  ],
  "validation_errors": []
}
```

#### `POST /api/v1/app-cse/{submission_id}/submit`
*   **Purpose:** Final cryptographic submission and locking of the APP-CSE.
*   **Response:** 200 OK with digital signature hash and submission timestamp.

### 5.4 Database Schema (DDL)

```sql
-- Main APP-CSE Submission Metadata
CREATE TABLE app_cse_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id VARCHAR(64) NOT NULL REFERENCES agencies(id),
    fiscal_year INT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT', -- DRAFT, PROCESSING, VALIDATED, SUBMITTED, REJECTED
    gcs_raw_uri TEXT NOT NULL,
    total_estimated_budget NUMERIC(15, 2) DEFAULT 0.00,
    allocated_budget NUMERIC(15, 2) DEFAULT 0.00,
    submission_hash VARCHAR(64),
    submitted_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual Normalized Line Items
CREATE TABLE app_cse_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES app_cse_submissions(id) ON DELETE CASCADE,
    item_code VARCHAR(64),
    unspsc_code VARCHAR(16) NOT NULL,
    raw_description TEXT NOT NULL,
    standardized_description TEXT,
    unit_of_measure VARCHAR(32) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    q1_qty INT DEFAULT 0,
    q2_qty INT DEFAULT 0,
    q3_qty INT DEFAULT 0,
    q4_qty INT DEFAULT 0,
    total_qty INT GENERATED ALWAYS AS (q1_qty + q2_qty + q3_qty + q4_qty) STORED,
    total_amount NUMERIC(15, 2) GENERATED ALWAYS AS ((q1_qty + q2_qty + q3_qty + q4_qty) * unit_price) STORED,
    preferred_depot_id VARCHAR(32) NOT NULL,
    confidence_score NUMERIC(4, 3) -- Gemini classification confidence
);

CREATE INDEX idx_app_cse_agency_year ON app_cse_submissions(agency_id, fiscal_year);
CREATE INDEX idx_app_cse_items_submission ON app_cse_items(submission_id);
CREATE INDEX idx_app_cse_items_unspsc ON app_cse_items(unspsc_code);
```

### 5.5 BigQuery Analytics & Demand Forecasting Integration
Once an APP-CSE submission reaches `SUBMITTED` status:
*   An Eventarc event triggers a Cloud Function to stream line items into BigQuery: `mphilgeps_analytics.app_cse_consolidated_demand`.
*   The `ARIMA_PLUS` BigQuery ML model automatically aggregates quarterly regional demand to update minimum stock levels and automated replenishment triggers for each Regional Depot.


---

## 6. Subsystem Deep Dive: Virtual Store & eMarketplace

The **Virtual Store** enables government agencies to purchase Common-Use Supplies and Equipment (CSE) directly from PS-DBM Main and Regional Depots with sub-second catalog responsiveness and guaranteed stock consistency.

### 6.1 Architecture & Inventory Reservation Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Buyer as Agency Buyer
    participant UI as Virtual Store UI (Next.js)
    participant API as VirtualStoreService (Go)
    participant Cache as Redis (Stock & Catalog)
    participant DB as AlloyDB / Cloud SQL
    participant Lock as Redis Distributed Lock (Redlock)

    Buyer->>UI: Adds 100 boxes of A4 Paper to Cart
    UI->>API: POST /api/v1/virtual-store/cart/items
    API->>Lock: Acquire lock: depot-ncr:prod-44122011
    API->>Cache: Check available depot inventory
    alt Stock Available
        API->>Cache: Decrement temporary reservation (TTL: 15 mins)
        API->>DB: Upsert cart_items with expiration
        API->>Lock: Release lock
        API-->>UI: 200 OK (Item Added, Reserved)
    else Insufficient Stock
        API->>Lock: Release lock
        API-->>UI: 409 Conflict (Stock Exhausted)
    end

    Buyer->>UI: Clicks "Checkout & Generate APR"
    UI->>API: POST /api/v1/virtual-store/checkout
    API->>DB: Convert Cart to Purchase Order (PO/APR)
    API->>DB: Permanently commit inventory deduction
    API->>Cache: Evict cached stock counts
    API-->>UI: 201 Created (PO #PO-2026-8831 generated)
```

### 6.2 REST API Contracts (OpenAPI)

#### `GET /api/v1/virtual-store/catalog`
*   **Query Params:** `depot_id`, `category_id`, `search`, `page`, `page_size`
*   **Response (200 OK):**
```json
{
  "total": 128,
  "page": 1,
  "items": [
    {
      "product_id": "prod-44122011-01",
      "unspsc_code": "44122011",
      "name": "PAPER, MULTICOPY, 80gsm, size: A4",
      "unit_of_measure": "ream",
      "unit_price": 185.50,
      "available_stock": 2450,
      "depot_id": "DEPOT-NCR-MANILA",
      "image_url": "https://storage.googleapis.com/mphilgeps-catalog/paper_a4.jpg"
    }
  ]
}
```

#### `POST /api/v1/virtual-store/checkout`
*   **Request:**
```json
{
  "agency_id": "NGA-DEPED-001",
  "depot_id": "DEPOT-NCR-MANILA",
  "cart_id": "cart-9921-uuid",
  "delivery_address": "DepEd Complex, Meralco Ave, Pasig City",
  "charging_account": "WALLET-DEPED-2026"
}
```
*   **Response (201 Created):**
```json
{
  "purchase_order_id": "PO-2026-0912-8841",
  "order_status": "APPROVED_PENDING_DELIVERY",
  "total_amount": 18550.00,
  "allocated_depot": "DEPOT-NCR-MANILA",
  "estimated_dispatch_date": "2026-09-16T08:00:00Z"
}
```

### 6.3 Database Schema (DDL)

```sql
CREATE TABLE products (
    id VARCHAR(64) PRIMARY KEY,
    unspsc_code VARCHAR(16) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit_of_measure VARCHAR(32) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE product_depot_inventory (
    product_id VARCHAR(64) REFERENCES products(id),
    depot_id VARCHAR(32) NOT NULL,
    stock_on_hand INT NOT NULL DEFAULT 0,
    reserved_stock INT NOT NULL DEFAULT 0,
    safety_stock_level INT NOT NULL DEFAULT 100,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (product_id, depot_id)
);

CREATE TABLE purchase_orders (
    id VARCHAR(64) PRIMARY KEY,
    agency_id VARCHAR(64) NOT NULL REFERENCES agencies(id),
    depot_id VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING', -- PENDING, DISPATCHED, DELIVERED, CANCELLED
    total_amount NUMERIC(15, 2) NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(64) NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id VARCHAR(64) NOT NULL REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(15, 2) NOT NULL
);
```

---

## 7. Subsystem Deep Dive: GOP-OMR (Official Merchants Registry)

The **GOP-OMR** enforces strict compliance with RA 12009 by automating merchant onboarding, document verification via Document AI, and live integration with regulatory agencies (SEC, BIR, DTI).

### 7.1 Automated Verification Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Merchant as Prospective Supplier
    participant UI as Merchant Portal (Next.js)
    participant API as MerchantRegistryService (FastAPI)
    participant GCS as Cloud Storage
    participant DocAI as Document AI Specialized Form Parser
    participant Apigee as Apigee Gateway
    participant Gov as External Agency APIs (BIR/SEC)
    participant DB as PostgreSQL / AlloyDB

    Merchant->>UI: Uploads Mayor's Permit, DTI/SEC Reg, & Tax Clearance
    UI->>API: POST /api/v1/merchants/{id}/documents
    API->>GCS: Store encrypted documents
    API->>DocAI: Trigger specialized form extraction
    DocAI-->>API: Extracted fields (SEC #, Tax Validity Date, Business Name)
    API->>Apigee: Query SEC & BIR verification endpoints
    Apigee->>Gov: Validate business standing & TIN active status
    Gov-->>Apigee: Valid & Active
    Apigee-->>API: Verification Success
    API->>DB: Record eligibility status (Status: PLATINUM_ELIGIBLE)
    API-->>UI: Real-time verification badge: Platinum Tier Approved
```

### 7.2 Database Schema (DDL)

```sql
CREATE TABLE merchants (
    id VARCHAR(64) PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    tin VARCHAR(32) UNIQUE NOT NULL,
    registration_type VARCHAR(32) NOT NULL, -- DTI, SEC, CDA
    registration_number VARCHAR(64) NOT NULL,
    membership_tier VARCHAR(16) NOT NULL DEFAULT 'RED', -- RED, PLATINUM
    is_blacklisted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE merchant_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id VARCHAR(64) NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    document_type VARCHAR(32) NOT NULL, -- MAYORS_PERMIT, TAX_CLEARANCE, SEC_CERT, AUDITED_FS
    gcs_uri TEXT NOT NULL,
    extracted_metadata JSONB,
    verification_status VARCHAR(32) DEFAULT 'PENDING', -- PENDING, VERIFIED, EXPIRED, REJECTED
    valid_until DATE,
    verified_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_merchants_tin ON merchants(tin);
CREATE INDEX idx_merchants_tier ON merchants(membership_tier);
```

---

## 8. Subsystem Deep Dive: e-Bidding & e-Reverse Auction Engine

The **e-Bidding & e-Reverse Auction Engine** provides cryptographically secure, two-envelope electronic bidding and ultra-low-latency reverse auctions with anti-sniping protection.

### 8.1 Cryptographic Two-Envelope Bid Sealing Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Bidder as Qualified Merchant
    participant UI as Bidding Portal
    participant API as BiddingAndAuctionService (Go)
    participant KMS as Google Cloud KMS
    participant Storage as Cloud Storage (Sealed Bid Vault)
    participant DB as AlloyDB / Cloud SQL

    Bidder->>UI: Submits Technical & Financial Bid Packages
    UI->>UI: Generate local AES-256 session key
    UI->>UI: Encrypt bid payloads locally
    UI->>API: POST /api/v1/bidding/{project_id}/submit-bid
    API->>KMS: Wrap AES session key with Project Master Asymmetric Key
    KMS-->>API: Wrapped key ciphertext
    API->>Storage: Store encrypted bid package
    API->>DB: Record bid submission metadata & timestamp
    API-->>Bidder: Bid Submission Acknowledgment with SHA-256 Hash

    Note over API,KMS: Bid Opening Phase (Requires BAC Quorum)
    API->>KMS: BAC Quorum unlocks Project Private Key
    API->>KMS: Unwrap AES session keys
    API->>DB: Mark Technical Envelope as UNSEALED
```

### 8.2 Real-Time e-Reverse Auction Protocol
*   **Transport:** WebSockets over WSS secured via Cloud Armor DDoS mitigation.
*   **Anti-Sniping Rule:** If a lower bid is submitted within the final 2 minutes of the auction clock, the auction countdown automatically extends by an additional 2 minutes.
*   **State Management:** High-frequency price floor cached inside **Redis Sorted Sets (`ZSET`)** for $O(\log N)$ real-time rank determination.

### 8.3 Database Schema (DDL)

```sql
CREATE TABLE procurement_projects (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    approved_budget_for_contract NUMERIC(15, 2) NOT NULL,
    procurement_mode VARCHAR(32) NOT NULL, -- PUBLIC_BIDDING, REVERSE_AUCTION, DIRECT_CONTRACTING
    bid_submission_deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    bid_opening_date TIMESTAMP WITH TIME ZONE NOT NULL,
    kms_key_id TEXT NOT NULL,
    status VARCHAR(32) DEFAULT 'PUBLISHED'
);

CREATE TABLE bid_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(64) NOT NULL REFERENCES procurement_projects(id),
    merchant_id VARCHAR(64) NOT NULL REFERENCES merchants(id),
    gcs_encrypted_payload_uri TEXT NOT NULL,
    wrapped_encryption_key TEXT NOT NULL,
    bid_hash VARCHAR(64) NOT NULL,
    technical_envelope_status VARCHAR(32) DEFAULT 'SEALED',
    financial_envelope_status VARCHAR(32) DEFAULT 'SEALED',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE auction_sessions (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) UNIQUE NOT NULL REFERENCES procurement_projects(id),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    current_lowest_bid NUMERIC(15, 2) NOT NULL,
    lowest_bidder_merchant_id VARCHAR(64) REFERENCES merchants(id),
    status VARCHAR(32) DEFAULT 'SCHEDULED' -- SCHEDULED, ACTIVE, EXTENDED, CONCLUDED
);
```

---

## 9. Subsystem Deep Dive: e-Payment & Digital Wallet Integration

The **PaymentAndBillingService** manages agency budget allocations, electronic payment processing (via Landbank and GovPay), and pre-funded digital wallets.

### 9.1 Payment Orchestration Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Agency as Agency Disbursement Officer
    participant UI as Payment Checkout
    participant API as PaymentAndBillingService
    participant DB as AlloyDB (Financial Ledger)
    participant LBP as Landbank / GovPay Gateway

    Agency->>UI: Selects Payment Mode: Agency E-Wallet
    UI->>API: POST /api/v1/payments/checkout (with Idempotency-Key)
    API->>DB: Check wallet balance & lock row (SELECT ... FOR UPDATE)
    alt Balance Sufficient
        API->>DB: Deduct wallet balance & create ledger entry
        API->>DB: Mark order as PAID
        API-->>UI: 200 OK (Payment Receipt Generated)
    else Balance Insufficient
        API->>LBP: Initiate online bank redirection (LDDAP-ADA / e-Payment)
        LBP-->>UI: Render secure bank payment gateway
        UI->>LBP: Authorize government disbursement
        LBP->>API: Webhook: Payment Settled (HMAC-SHA256 signature)
        API->>DB: Commit payment transaction
        API-->>UI: 200 OK (Payment Confirmed via Gateway)
    end
```

### 9.2 Database Schema (Double-Entry Financial Ledger DDL)

```sql
CREATE TABLE agency_wallets (
    id VARCHAR(64) PRIMARY KEY,
    agency_id VARCHAR(64) UNIQUE NOT NULL REFERENCES agencies(id),
    current_balance NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (current_balance >= 0.00),
    currency VARCHAR(3) DEFAULT 'PHP',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE wallet_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id VARCHAR(64) NOT NULL REFERENCES agency_wallets(id),
    transaction_type VARCHAR(16) NOT NULL, -- CREDIT, DEBIT
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0.00),
    reference_order_id VARCHAR(64),
    idempotency_key VARCHAR(128) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_wallet_ledger_wallet ON wallet_ledger(wallet_id);
```


---

## 10. Enterprise Security, Governance & Disaster Recovery

Following the deep-reasoning multi-persona audit, this section hardens the infrastructure, data protection, and operational continuity across all microservices and AI modules.

### 10.1 Cryptographic Quorum & Cloud KMS Key Management
*   **Dual-Control Envelope Encryption:** The master asymmetric encryption keys for procurement projects are hosted in **Cloud KMS (FIPS 140-2 Level 3 validated Cloud HSM)**.
*   **BAC Quorum Release:** Decrypting sealed financial envelopes requires an $M$-of-$N$ threshold cryptographic release (minimum 3 of 5 Bids and Awards Committee member electronic tokens) submitted through Secret Manager, preventing single-admin compromise.
*   **Key Rotation:** Automatic 90-day rotation schedule for data encryption keys (DEK) and key-encrypting keys (KEK).

### 10.2 Model Armor & Sensitive Data Protection (DLP)
*   **Model Armor Filter Pipelines:** Positioned upstream of all ADK agent invocations to evaluate prompt risk scores against jailbreaks, system prompt extractions, and malicious instructions.
*   **Cloud Data Loss Prevention (DLP):** Integrated inspection templates actively scan and mask Philippine-specific PII, including:
    *   Tax Identification Number (`PH_TIN`)
    *   Philippine National ID / PhilSys Card Number (`PH_PCN`)
    *   Social Security System (`PH_SSS`) Number
    *   Supplier bank account numbers and internal bid ceilings.

### 10.3 Zero-Trust GKE Hardening & Secrets Management
*   **Dataplane V2 Network Policies:** Strict default-deny egress and ingress between Kubernetes namespaces. The `bidding` and `payments` namespaces are isolated from direct public traffic and can only communicate with the API gateway and their dedicated database endpoints.
*   **Secret Management:** No credentials, tokens, or private keys are baked into container images or environment variables. All secrets are stored in **Google Secret Manager** and mounted as ephemeral in-memory volumes via the **CSI Secret Store Driver**.

### 10.4 10-Year Tamper-Proof Audit & Record Retention (RA 12009 / COA)
*   **WORM Storage Policies:** All submitted procurement documents, APP-CSE plans, and awarded contracts are archived in **Cloud Storage Buckets with Bucket Lock (Object Retention in Compliance Mode)** set to a non-reversible 10-year retention duration, satisfying Commission on Audit (COA) Circulars.
*   **Immutable BigQuery Audit Sinks:** Transactional state changes and security logs are streamed via log sinks to an append-only BigQuery dataset with column-level access controls and row hashing.

### 10.5 High-Concurrency Resilience & Locking Fallbacks
*   **Two-Tier Inventory Locking:** When high volume hits the Virtual Store, services attempt distributed locking via **Redis Redlock**. If Redis experiences network partition or node failure, the system gracefully falls back to database-level row-level pessimistic locking (`SELECT ... FOR UPDATE NOWAIT`) with exponential backoff, guaranteeing zero duplicate inventory allocation.
*   **Financial Idempotency:** The `PaymentAndBillingService` enforces a strict unique constraint on `idempotency_key` backed by Redis and AlloyDB to eliminate double-debits during bank callback retries.

### 10.6 Multi-Region Disaster Recovery & Business Continuity
*   **Topology:** Multi-Region Active-Passive deployment:
    *   **Primary Region:** `asia-southeast1` (Singapore)
    *   **Disaster Recovery Region:** `asia-southeast2` (Jakarta)
*   **Recovery Point Objective (RPO):** **< 15 minutes** achieved via continuous asynchronous replication in AlloyDB and dual-region Cloud Storage buckets.
*   **Recovery Time Objective (RTO):** **< 1 hour** facilitated by automated Cloud DNS failover and pre-warmed standby GKE cluster manifests.

### 10.7 Automated Database Migrations
*   Database schema evolution across PostgreSQL/AlloyDB instances is strictly managed using **Liquibase / Flyway**. Migration jobs run as pre-sync Kubernetes init containers or Cloud Build pipeline steps prior to rolling application deployments, ensuring backward and forward schema compatibility.

## Verification Plan

### Automated Tests
*   **Unit & Integration Tests:** Run local test suites to verify business logic (e.g., e-Reverse Auction bid validation) using `pytest` or `jest` prior to containerization.
*   **Infrastructure as Code (IaC) Validation:** If using Terraform for GCP deployments, run `terraform plan` and `terraform validate` to ensure cloud architectures conform to the TDD.

### Manual Verification
1.  **Local Environment:** Developer runs `docker-compose up` and confirms the frontend can connect to the local PostgreSQL and Redis containers.
2.  **AI Sandbox Connectivity:** Developer authenticates with `gcloud auth application-default login` and successfully executes a test prompt to the Gemini API.
3.  **Demo Environment Access:** Deploy to Cloud Run, enable IAP, and verify that unauthorized users receive a 403 Forbidden error, while authorized demo users can access the system.

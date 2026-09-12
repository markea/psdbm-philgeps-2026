# Business Requirements Document (BRD)
## Modernized Philippine Government Electronic Procurement System (mPhilGEPS)
**Target Cloud Platform:** Google Cloud Platform & Google AI Stack

---

## 1. Introduction and Purpose
This document translates the Terms of Reference (TOR) for the mPhilGEPS modernization (compliance with RA 12009 / NGPA) into actionable business and technical requirements. It specifically maps the core functionalities, data analytics, and Artificial Intelligence (AI) asks to the **Google Cloud Stack**, emphasizing **Gemini, Gemini Enterprise, Vertex AI, and Agent Platform**.

## 2. Business Objectives
*   **Compliance:** Align with the New Government Procurement Act (RA 12009).
*   **Centralization:** Transition entirely from PhilGEPS 1.5 to mPhilGEPS to eliminate redundancy and create a unified platform.
*   **Modernization:** Introduce cutting-edge e-procurement features (eMarketplace, e-Reverse Auction, Smart Framework Agreements).
*   **Intelligence:** Embed AI at the core of the procurement lifecycle for document verification, fraud detection, predictive forecasting, and real-time user assistance.
*   **Transparency & Open Data:** Adhere to Open Contracting Data Standard (OCDS) and Open Government Partnership (OGP) commitments.

---

## 3. Artificial Intelligence (AI) Requirements & Google AI Stack Mapping

The TOR explicitly mandates six (6) minimum AI functionalities. Below is the mapping of these requirements to Google's Enterprise AI Stack.

### 3.1 AI-Powered Procurement Insights
*   **Requirement:** Analyze historical data, recommend procurement planning, supplier selection, cost optimization, and auto-suggest UNSPSC classifications.
*   **Google AI Mapping:** 
    *   **Vertex AI Search & Conversation:** To search through historical bid documents and extract insights.
    *   **Gemini 1.5 Pro (via Vertex AI):** Utilized for semantic matching of procurement descriptions to the correct United Nations Standard Products and Services Code (UNSPSC). Gemini can read unstructured bid descriptions and recommend the most accurate classification.
    *   **Gemini Enterprise Agent Platform:** Deployed as a "Procurement Strategist Agent" to assist procuring entities in drafting plans and optimizing budgets based on historical context.

### 3.2 Predictive Analytics for Demand Forecasting
*   **Requirement:** Leverage predictive modeling to forecast procurement needs based on historical trends, budget allocations, and external factors.
*   **Google AI Mapping:**
    *   **BigQuery ML:** Run ARIMA_PLUS time-series forecasting models directly where the procurement data lives (BigQuery).
    *   **Vertex AI AutoML Tabular & Forecast:** Train high-accuracy models on historical purchasing behavior to predict seasonal demand for Common-Use Supplies and Equipment (CSE), optimizing inventory for the e-Marketplace.

### 3.3 Automated Document Verification
*   **Requirement:** AI-driven tools for validating submitted documents (e.g., eligibility requirements, DTI/SEC registrations, technical proposals) to reduce manual workload.
*   **Google AI Mapping:**
    *   **Google Cloud Document AI:** Use pre-trained or custom extractors to ingest identity, business, and financial documents (e.g., Audited Financial Statements, Tax Clearances, PCAB Licenses).
    *   **Gemini 1.5 Pro (Multimodal):** For complex Technical Proposals, Gemini's large context window (up to 2M tokens) and multimodal capabilities can cross-reference hundreds of pages of a vendor's proposal against the exact specifications of the Procuring Entity's TOR, flagging discrepancies automatically.

### 3.4 Chatbot and Virtual Assistant Support
*   **Requirement:** AI-powered chatbot to assist users with navigation, FAQs, and real-time support.
*   **Google AI Mapping:**
    *   **Gemini Enterprise Agent Platform:** Build stateful, multi-turn AI agents grounded in PhilGEPS manuals and RA 12009 (RAG - Retrieval-Augmented Generation).
    *   **Dialogflow CX:** For deterministic routing and conversational flows, seamlessly handing over to generative Gemini agents for complex, open-ended queries about procurement laws and system navigation.

### 3.5 Enhanced Data Analytics
*   **Requirement:** Advanced AI analytics for insights into procurement patterns, custom reporting, and visualization of KPIs.
*   **Google AI Mapping:**
    *   **Looker & Looker Studio:** For building interactive, embeddable dashboards and exposing Open Contracting Data Standard (OCDS) datasets to the public.
    *   **Gemini in Looker / Gemini in BigQuery:** Allow users (e.g., auditors, agency heads) to ask natural language questions (e.g., *"Show me the average bid variance for IT equipment in 2025"*) and have the AI generate the SQL query and visualization instantly.

### 3.6 Fraud Detection and Prevention
*   **Requirement:** AI algorithms to monitor procurement activities, flag suspicious patterns, collusion, and support red tagging/blacklisting.
*   **Google AI Mapping:**
    *   **Vertex AI (Custom Models):** Train anomaly detection models (e.g., Isolation Forests, Autoencoders) to spot unusual bidding behaviors, sudden price drops/spikes, or abnormal vendor activity.
    *   **Google Cloud Graph (Spanner/BigQuery):** Map beneficial ownership (SEC/DTI data) to detect hidden links between competing bidders (collusion rings).
    *   **Agent Platform (Auditor Agent):** An AI agent that synthesizes anomaly alerts and drafts investigative summaries for the COA (Commission on Audit) or the PS-DBM evaluation team.

---

## 4. Core System Modules & Google Cloud Infrastructure Mapping

| mPhilGEPS Module | Description | Recommended Google Cloud Service |
| :--- | :--- | :--- |
| **Subscriber Registry & GOP-OMR** | Centralized merchant and government agency registry. | **Cloud SQL / AlloyDB** (Relational Data), **Cloud Storage** (Uploaded docs). |
| **e-Bidding Facility (APP, PR, EBB)** | End-to-end electronic bidding, notices, and evaluations. | **Google Kubernetes Engine (GKE) / Cloud Run** (Microservices architecture). |
| **e-Marketplace & e-Catalogue** | Online shopping platform for Common-Use Supplies. | **GKE** (scalable e-commerce backend), **Memorystore (Redis)** for caching. |
| **Contract Management** | Monitoring contracts, milestones, POs, and amendments. | **Cloud Spanner** (if global consistency/scale is needed), **Cloud Storage** (Contracts). |
| **e-Reverse Auction** | Real-time competitive downward bidding. | **Firebase / Firestore** (Real-time database and websocket synchronization). |
| **Integration System (API)** | Integration with BTMS, SEC, BIR, DTI, PCAB, etc. | **Apigee API Management** (Secure, throttled, monitored API Gateway). |

---

## 5. Non-Functional & Service Level Requirements

*   **Security & Encryption:**
    *   **Cloud Key Management Service (KMS):** For managing encryption keys (data at rest and in transit).
    *   **Google Cloud Armor:** Web Application Firewall (WAF) to protect against OWASP Top 10, DDoS attacks, and unauthorized intrusions (as mandated in Annex F & G).
    *   **Identity-Aware Proxy (IAP) & Cloud Identity:** Zero-trust security for administrative access.
*   **High Availability & Disaster Recovery (SLA 99.9% / 24x7):**
    *   **Multi-Region Deployment:** Active-passive or Active-Active deployment across Google Cloud Asian regions.
    *   **Cloud Load Balancing:** Global load balancing to ensure response times stay well below the required 5-second maximum (Annex C).
*   **Data Standards (OCDS / Open Data):**
    *   **BigQuery:** Expose public datasets for Civil Society Organizations (CSOs) and researchers using BigQuery's public data sharing capabilities, natively outputting JSON, CSV, and XML.

---

## 6. Implementation Strategy & Next Steps

1.  **Phase 1: Inception & Prototyping:** Finalize system architecture on GCP. Develop rapid prototypes of the Gemini-powered Chatbot and Document AI extraction pipelines.
2.  **Phase 2: Core Development:** Build the microservices (GKE/Cloud Run) for the GOP-OMR and e-Bidding facilities. Establish secure API tunnels (Apigee) to external agencies (BIR, SEC).
3.  **Phase 3: AI & Analytics Integration:** Overlay Vertex AI, BigQuery ML, and Gemini Enterprise Agents onto the transactional data to activate fraud detection, insights, and predictive forecasting.
4.  **Phase 4: UAT & Security Hardening:** Vulnerability Assessment and Penetration Testing (VAPT) via Cloud Armor and Security Command Center.
5.  **Phase 5: Go-Live & Managed Operations:** 24/7 Monitoring using Google Cloud Operations Suite (Cloud Monitoring, Cloud Logging).

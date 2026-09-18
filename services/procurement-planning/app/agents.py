"""
mPhilGEPS Multi-Agent Conversational Ecosystem, Spanner Graph Cartel Engine,
and Anti-Scraping / OCDS Open Data Services.

Implements:
  1. Supervisor Intent Router & 3 Specialized AI Agents (BAC Advisor, COA Auditor, Merchant Help)
     with live Google GenAI (Vertex AI) integration + deterministic OKF statutory grounding.
  2. Google Cloud Model Armor & DLP Pre/Post-Filter (RA 10173 PII masking & prompt injection defense).
  3. Cloud Spanner Graph Cartel & BigQuery ML Collusion Probability Index (CPI) simulator.
  4. 4-Tier Anti-Scraping Perimeter (Cloud Armor JA3 + reCAPTCHA Enterprise Edge) & OCDS Bulk Exporter.
"""
import os
import re
import time
import json
from typing import Dict, Any, List, Optional

# Optional Google GenAI SDK (Vertex AI / Enterprise)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# ==============================================================================
# 1. GOOGLE CLOUD MODEL ARMOR & RA 10173 DLP FILTER
# ==============================================================================
TIN_REGEX = re.compile(r"\b\d{3}-\d{3}-\d{3}(?:-\d{3,4})?\b")
PHONE_REGEX = re.compile(r"(?:\+63|0)9\d{2}[-\s]?\d{3}[-\s]?\d{4}\b")
BANK_REGEX = re.compile(r"\b(?:ACCT|ACCOUNT)[-\s#:]*\d{8,16}\b", re.IGNORECASE)
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"reveal\s+(?:the\s+)?unopened\s+bid",
    r"bypass\s+(?:kms|quorum|bac|security)",
    r"system\s+prompt\s+leak",
    r"override\s+evaluation\s+score",
]


def inspect_with_model_armor(text: str) -> Dict[str, Any]:
    """
    Simulates Google Cloud Model Armor + Cloud DLP inline inspection.
    Redacts PII (TIN, PH Mobile Numbers, Bank Accounts) under RA 10173
    and detects adversarial prompt injection / bid-unsealing jailbreaks.
    """
    redacted_text = text
    redactions: List[str] = []

    if TIN_REGEX.search(redacted_text):
        redacted_text = TIN_REGEX.sub("[REDACTED-TIN-RA10173]", redacted_text)
        redactions.append("PH_TAX_IDENTIFICATION_NUMBER")

    if PHONE_REGEX.search(redacted_text):
        redacted_text = PHONE_REGEX.sub("[REDACTED-MOBILE-RA10173]", redacted_text)
        redactions.append("PH_MOBILE_PHONE")

    if BANK_REGEX.search(redacted_text):
        redacted_text = BANK_REGEX.sub("[REDACTED-BANK-ACCT-RA10173]", redacted_text)
        redactions.append("BANK_ACCOUNT_NUMBER")

    injection_detected = False
    matched_rule = None
    for pat in INJECTION_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            injection_detected = True
            matched_rule = pat
            break

    return {
        "sanitized_text": redacted_text,
        "pii_redacted": len(redactions) > 0,
        "redacted_types": redactions,
        "prompt_injection_blocked": injection_detected,
        "matched_security_rule": matched_rule,
        "compliance_framework": "RA 10173 (Data Privacy Act) & Model Armor Policy v2.4"
    }


# ==============================================================================
# 2. SUPERVISOR INTENT ROUTER (Gemini 3.7 Flash Semantic Classifier)
# ==============================================================================
def classify_agent_intent(user_message: str, requested_agent: Optional[str] = None) -> Dict[str, Any]:
    """
    Routes incoming prompts to the specialized domain agent:
      - 'bac': BAC Advisor Agent (RA 12009 IRR, APP-CSE, UNSPSC, MAB, Supplemental APP)
      - 'coa': COA Auditor Agent (Spanner Graph cartels, BigQuery ML CPI, Benford's Law, WORM, OCDS)
      - 'merchant': Merchant Onboarding & Bidding Agent (GOP-OMR Platinum, NFCC, DocAI, Confidential Space Bid Vault)
    """
    msg_lower = user_message.lower()

    bac_keywords = [
        "ra 12009", "ngpa", "app-cse", "app cse", "budget", "ceiling", "supplemental",
        "unspsc", "hierarchy", "classification", "most advantageous bid", "mab", "lcrb",
        "gppb", "bac", "invitation to bid", "itb", "shopping", "small value", "sec. 7", "section 7"
    ]
    coa_keywords = [
        "coa", "collusion", "cartel", "spanner", "graph", "gql", "director", "interlocking",
        "shared ip", "benford", "bid rotation", "cpi", "anomaly", "audit", "worm", "10-year",
        "bucket lock", "ocds", "open contracting", "scraper", "open data"
    ]
    merchant_keywords = [
        "nfcc", "net financial", "platinum", "gop-omr", "omr", "sec gis", "60/40", "filipino",
        "bir", "tax clearance", "pcab", "audited financial", "afs", "document ai",
        "confidential space", "bid vault", "kms", "hsm", "quorum", "unseal", "encrypt", "merchant", "supplier"
    ]

    scores = {
        "bac": sum(2 if kw in msg_lower else 0 for kw in bac_keywords),
        "coa": sum(2 if kw in msg_lower else 0 for kw in coa_keywords),
        "merchant": sum(2 if kw in msg_lower else 0 for kw in merchant_keywords),
    }

    best_agent = max(scores, key=scores.get)
    if scores[best_agent] == 0:
        best_agent = requested_agent if requested_agent in ("bac", "coa", "merchant") else "bac"
        confidence = 0.88
    else:
        confidence = min(0.99, 0.89 + (scores[best_agent] * 0.02))

    # If user explicitly clicked a specific tab (bac/coa/merchant), preserve that tab; if auto/supervisor, use best_agent
    target_agent = best_agent if (requested_agent in (None, "auto", "supervisor")) else requested_agent

    agent_metadata = {
        "bac": {
            "id": "bac",
            "name": "BAC Advisor Agent",
            "icon": "⚖️",
            "model": "Gemini 3.1 Pro + OKF Statutory Grounding",
            "corpus": "RA 12009 (NGPA) IRR & GPPB Standard Bidding Documents"
        },
        "coa": {
            "id": "coa",
            "name": "Public Transparency & COA Auditor Agent",
            "icon": "🔍",
            "model": "Gemini 3.1 Pro + Spanner Graph GQL & BigQuery ML",
            "corpus": "Spanner Graph (MPhilGepsProcurementGraph) & BigQuery Audit Ledger"
        },
        "merchant": {
            "id": "merchant",
            "name": "Merchant Onboarding & Bidding Agent",
            "icon": "🏢",
            "model": "Gemini 3.7 Flash + Document AI CDE & Confidential Space",
            "corpus": "GOP-OMR Platinum Rules, Document AI Matrix & KMS Quorum Protocol"
        }
    }

    return {
        "selected_agent": target_agent,
        "recommended_agent": best_agent,
        "confidence": round(confidence, 3),
        "agent_info": agent_metadata[target_agent]
    }


# ==============================================================================
# 3. STRUCTURED OPEN KNOWLEDGE FORMAT (OKF) & DETERMINISTIC SYNTHESIS
# ==============================================================================
def build_grounded_response(
    agent_id: str,
    sanitized_query: str,
    armor_report: Dict[str, Any],
    portal_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a richly grounded response combining OKF statutory citations,
    deterministic calculations, and optional live Vertex AI Gemini synthesis.
    """
    start_ts = time.time()

    # 1. Handle Prompt Injection / Jailbreak immediately via Model Armor
    if armor_report["prompt_injection_blocked"]:
        return {
            "agent_id": agent_id,
            "response_markdown": (
                "🛡️ **Google Cloud Model Armor Security Interception**\n\n"
                "Your request was blocked by **Model Armor Policy v2.4** because it matched an adversarial pattern "
                f"(`{armor_report['matched_security_rule']}`).\n\n"
                "* **Statutory Mandate:** Under **RA 12009 (NGPA)** and **RA 10173 (Data Privacy Act)**, unopened electronic bids "
                "inside the **Confidential Space Bid Vault** cannot be accessed, unsealed, or overridden by any AI agent or administrator "
                "prior to the official bid opening timestamp ($T+0$), which requires simultaneous **Cloud KMS HSM dual-control quorum tokens** "
                "from both the **BAC Chairperson** and **COA Observer**."
            ),
            "citations": ["RA 12009 Sec. 42 (Confidentiality of Bids)", "RA 10173 (Data Privacy Act)", "Model Armor Policy v2.4"],
            "sql_or_gql_generated": None,
            "engine_mode": "Model Armor Guardrail Enforced",
            "latency_ms": round((time.time() - start_ts) * 1000, 1)
        }

    q = sanitized_query.lower()
    citations: List[str] = []
    sql_or_gql: Optional[str] = None
    core_answer = ""

    # Context summary from uploaded APP-CSE if available
    context_note = ""
    if portal_context and portal_context.get("latest_submission"):
        sub = portal_context["latest_submission"]
        context_note = (
            f"\n\n📌 **Live Portal Session Context (`{sub['submission_id']}` — `{sub['agency_id']}`):** "
            f"Uploaded **{sub['total_items']} CSE items** totaling **₱{sub['total_estimated_budget']:,.2f}** "
            f"against an allocated ceiling of **₱{sub['allocated_budget']:,.2f}** (Status: **`{sub['budget_status']}`**)."
        )

    # ------------------------------------------------------------------
    # AGENT 1: BAC ADVISOR AGENT (RA 12009, APP-CSE, UNSPSC, MAB)
    # ------------------------------------------------------------------
    if agent_id == "bac":
        if any(k in q for k in ["budget", "exceed", "ceiling", "supplemental", "app-cse", "app cse", "sec. 7", "section 7"]):
            citations = [
                "RA 12009 Sec. 7.2 (Mandatory APP-CSE Linkage)",
                "GPPB Resolution No. 09-2025 (Supplemental APP Guidelines)",
                "mPhilGEPS TDD §5.1 (Spreadsheet Arithmetic & Budget Validation)"
            ]
            core_answer = (
                "### ⚖️ Statutory Ruling: APP-CSE Budget Ceiling & Supplemental APP (RA 12009 Sec. 7.2)\n\n"
                "Under **Section 7.2 of Republic Act No. 12009 (New Government Procurement Act)**, *no government procurement shall be undertaken "
                "unless it is in accordance with the approved Annual Procurement Plan (APP) / APP-CSE*.\n\n"
                "1. **Automated Validation Rule:** When an agency uploads an APP-CSE `.xlsx` workbook, `ProcurementPlanningService` verifies that:\n"
                "   $$\\sum_{i=1}^{n} (Q1_i + Q2_i + Q3_i + Q4_i) \\times \\text{Unit Price}_i \\le \\text{Approved Agency Budget Ceiling}$$\n"
                "2. **Remediation for `EXCEEDS_BUDGET`:** If your total estimated expenditure exceeds the allocated budget ceiling:\n"
                "   * Revise quarterly quantities (`Q1`–`Q4`) on non-essential items to fit within the approved appropriation; **OR**\n"
                "   * Secure a **Certification of Availability of Funds (CAF)** from your Chief Accountant and submit a formal **Supplemental APP** approved by the Head of the Procuring Entity (HoPE)."
                + context_note
            )
        elif any(k in q for k in ["unspsc", "classify", "classification", "hierarchy", "pass 1", "pass 2", "dual-pass"]):
            citations = [
                "RA 12009 Sec. 11 (Philippine Government Electronic Procurement System)",
                "mPhilGEPS TDD §5.1 (Dual-Pass Hierarchical UNSPSC Pipeline)",
                "UNSPSC v26.0 Global Standard Taxonomy"
            ]
            core_answer = (
                "### 🏷️ Dual-Pass Hierarchical UNSPSC Classification Pipeline\n\n"
                "To eliminate colloquial descriptions and proprietary brand bias in agency APPs, mPhilGEPS enforces a **Dual-Pass AI Pipeline**:\n\n"
                "* **Pass 1 — Semantic Normalization (`Gemini 3.7 Flash`):** Strips colloquial terms and prohibited brand names (per **RA 12009 Sec. 27** prohibition on brand-name specification) into canonical item titles (e.g., *'Copy Paper A4 80gsm'* $\\rightarrow$ **`Multi-Purpose Photocopy Paper`**).\n"
                "* **Pass 2 — 4-Tier Hierarchical Enforcement (`Gemini 3.1 Pro` Structured Outputs):** Enforces the strict 8-digit UNSPSC taxonomy:\n"
                "  $$\\text{Segment (XX)} \\longrightarrow \\text{Family (XXXX)} \\longrightarrow \\text{Class (XXXXXX)} \\longrightarrow \\text{Commodity (XXXXXXXX)}$$\n"
                "  *Example:* `14111507` $\\rightarrow$ *Paper Materials (14) > Paper products (1411) > Printing and writing paper (141115) > Photocopy paper (14111507)* (`98.5% confidence`)."
                + context_note
            )
        else:
            citations = [
                "RA 12009 Sec. 34 (Most Advantageous Bid - MAB)",
                "RA 12009 Sec. 27 (Technical Specifications & Brand Neutrality)",
                "OKF Corpus: GPPB Implementing Rules & Regulations"
            ]
            core_answer = (
                "### ⚖️ BAC Advisor Grounded Guidance (RA 12009 / NGPA)\n\n"
                "Under the **New Government Procurement Act (RA 12009)**, Bids and Awards Committees (BAC) are empowered to adopt modern evaluation modes:\n\n"
                "* **Most Advantageous Bid (MAB — Sec. 34):** Moves beyond Lowest Calculated Responsive Bid (LCRB) by weighting **Life-Cycle Cost (LCC)**, environmental sustainability, and technical quality alongside price.\n"
                "* **Prohibition on Brand Names (Sec. 27):** Specifications must be based on relevant performance requirements and recognized national/international standards rather than specific trademarks.\n"
                "* **Pre-Procurement Automated Audit:** Our OKF-grounded engine validates your Invitation to Bid (ITB) against statutory posting periods (7 calendar days on the Electronic Bulletin Board) and budget ceilings."
                + context_note
            )

    # ------------------------------------------------------------------
    # AGENT 2: COA AUDITOR AGENT (Spanner Graph, BigQuery ML, WORM, OCDS)
    # ------------------------------------------------------------------
    elif agent_id == "coa":
        if any(k in q for k in ["collusion", "cartel", "spanner", "graph", "director", "interlocking", "shared ip", "rotation", "cpi"]):
            citations = [
                "RA 12009 Sec. 65 (Offenses and Penalties: Bid Rigging & Collusion)",
                "mPhilGEPS TDD §9.1 (Cloud Spanner Graph GQL Cartel Detection)",
                "mPhilGEPS TDD §9.2 (BigQuery ML Collusion Probability Index)"
            ]
            sql_or_gql = (
                "GRAPH MPhilGepsProcurementGraph\n"
                "MATCH\n"
                "  (b1:Bidder)-[:SERVES_ON_BOARD]->(d:Director)<-[:SERVES_ON_BOARD]-(b2:Bidder),\n"
                "  (b1)-[:SUBMITTED_FOR]->(t:Tender)<-[:SUBMITTED_FOR]-(b2),\n"
                "  (b1)-[:UTILIZED_NETWORK]->(ip:IP_Address)<-[:UTILIZED_NETWORK]-(b2)\n"
                "WHERE b1.id != b2.id\n"
                "RETURN b1.company_name, b2.company_name, d.full_name, ip.cidr, t.reference_number;"
            )
            core_answer = (
                "### 🔍 Spanner Graph Cartel Detection & BigQuery ML Audit Report\n\n"
                "Executing multi-hop pattern matching on **Cloud Spanner Graph (`MPhilGepsProcurementGraph`)** and **BigQuery ML (`Enterprise Slots`)** surfaced a **CRITICAL Collusion Alert**:\n\n"
                "1. **Interlocking Directorate & Shared Network Detected (`Tender ITB-2026-DPWH-R3-004`):**\n"
                "   * **Competing Bidders:** `Apex Builders Corp.` (`TIN: [REDACTED-RA10173]`) and `Titan Infrastructure Inc.`\n"
                "   * **Shared Board Member:** `Engr. Roberto M. Santos` serves simultaneously on the SEC GIS Board of Directors of both competing entities.\n"
                "   * **Shared Submission IP & Bank Guarantor:** Both encrypted bid envelopes originated from subnet `203.177.42.19` within 140 seconds of each other and cite the same surety bond guarantor.\n"
                "2. **BigQuery ML Collusion Probability Index (`CPI = 0.942 — CRITICAL`):**\n"
                "   * K-means historical clustering indicates `Apex Builders` and `Titan Infrastructure` have alternated winning Region III flood-control tenders across 8 consecutive quarters with a narrow `0.42%` price spread."
            )
        elif any(k in q for k in ["benford", "pricing", "anomaly", "worm", "10-year", "retention", "ocds", "open data", "scraper"]):
            citations = [
                "RA 12009 Sec. 20 (Open Contracting Data Standard - OCDS)",
                "COA Circular No. 2024-002 (10-Year Mandatory Digital Record Retention)",
                "mPhilGEPS TDD §9.2 & §11.4 (Benford's Law & OCDS Bulk Offload)"
            ]
            sql_or_gql = (
                "SELECT unspsc_commodity_code, leading_digit,\n"
                "       COUNT(*) / SUM(COUNT(*)) OVER() AS observed_freq,\n"
                "       LOG10(1 + 1.0 / leading_digit) AS benford_expected_freq\n"
                "FROM `mphilgeps_analytics.bid_line_items`\n"
                "GROUP BY unspsc_commodity_code, leading_digit;"
            )
            core_answer = (
                "### 📊 Benford's Law Forensic Audit, 10-Year WORM & OCDS Open Data\n\n"
                "* **Benford's Law First-Digit Anomaly:** BigQuery ML evaluated bill-of-quantities unit prices across submitted bids. Digit `9` appeared as the leading digit in **`28.4%`** of line items (vs. Benford expected **`4.6%`**), signaling artificial clustering just below threshold ceilings ($\\chi^2 = 41.8, p < 0.001$).\n"
                "* **10-Year Non-Erasable WORM Storage:** All tender dossiers, audit logs, and APP-CSEs are archived in **Cloud Storage with Bucket Lock in Compliance Mode** (`10-year` retention lock), guaranteeing zero tampering for COA scrutiny.\n"
                "* **OCDS Open Data De-Monetization:** Nightly scheduled exports from **BigQuery Enterprise Slots** publish standardized **Open Contracting Data Standard (OCDS v1.1)** JSON/CSV packages to `gs://mphilgeps-open-data-ocds` fronted by **Cloud CDN**, giving COA and CSOs full transparency while eliminating commercial scraper traffic."
            )
        else:
            citations = [
                "RA 12009 Sec. 20 & Sec. 65 (Transparency & Anti-Collusion)",
                "Cloud Spanner Graph & BigQuery Enterprise Slots Audit Ledger"
            ]
            core_answer = (
                "### 🔍 COA Auditor & Public Transparency Intelligence\n\n"
                "I translate natural language audit inquiries into governed **Cloud Spanner Graph (GQL)** and **BigQuery SQL** queries:\n\n"
                "* **Graph Cartel Discovery:** Detects hidden relationships across `Bidder`, `Director`, `Authorized_Signatory`, `Bank_Guarantor`, and `IP_Address` nodes.\n"
                "* **Statistical Bid Forensics:** Computes **Collusion Probability Index (CPI)** and **Benford's Law** digit distributions inside reserved BigQuery Enterprise Slots at `$0.00` incremental query cost.\n"
                "* **Immutable COA Evidence:** All state changes are cryptographically hashed into append-only BigQuery sinks and 10-Year WORM Cloud Storage buckets."
                + context_note
            )

    # ------------------------------------------------------------------
    # AGENT 3: MERCHANT ONBOARDING & BIDDING AGENT (GOP-OMR, NFCC, Bid Vault)
    # ------------------------------------------------------------------
    else:
        if any(k in q for k in ["nfcc", "net financial", "afs", "audited financial", "calculate", "capacity", "abc"]):
            citations = [
                "RA 12009 Sec. 23 (Eligibility Requirements for Government Procurement)",
                "mPhilGEPS TDD §7.1 (Document AI Layout Parser & Automated NFCC Formula)"
            ]
            core_answer = (
                "### 🏢 Automated Net Financial Contracting Capacity (NFCC) Computation\n\n"
                "When you upload your **Audited Financial Statement (AFS)** to the **GOP-OMR Platinum Portal**, **Document AI Layout Parser** and **Gemini 3.1 Pro** automatically extract your balance sheet figures and compute your statutory **NFCC**:\n\n"
                "$$\\text{NFCC} = \\left[ (\\text{Current Assets} - \\text{Current Liabilities}) \\times 15 \\right] - \\text{Value of All Outstanding Works}$$\n\n"
                "#### 📐 Worked Example (Pre-Flight Eligibility Check):\n"
                "* **Current Assets:** `₱45,000,000.00`\n"
                "* **Current Liabilities:** `₱15,000,000.00` $\\rightarrow$ **Net Working Capital:** `₱30,000,000.00`\n"
                "* **Constant Multiplier ($K = 15$):** `₱30,000,000.00 × 15` = `₱450,000,000.00`\n"
                "* **Less Ongoing Contracts:** `- ₱120,000,000.00`\n"
                "* **Calculated Statutory NFCC:** **`₱330,000,000.00`**\n\n"
                "✅ **Eligibility Verdict:** As long as your **Calculated NFCC (`₱330M`) $\\ge$ Approved Budget for the Contract (ABC)**, our Audit Decisioning Engine (`Gemini 3.7 Flash`) issues an instant **`APPROVED`** status."
            )
        elif any(k in q for k in ["confidential", "vault", "seal", "unseal", "kms", "hsm", "quorum", "encrypt", "bid"]):
            citations = [
                "RA 12009 Sec. 42 (Sealing and Opening of Bids)",
                "mPhilGEPS TDD §8.1 (Confidential Space Bid Vault & Cloud KMS HSM Quorum)"
            ]
            core_answer = (
                "### 🔐 Confidential Space Sealed Bid Vault & Dual-Control KMS Quorum\n\n"
                "mPhilGEPS guarantees **zero premature bid leakage** using hardware-enforced confidential computing:\n\n"
                "1. **Client-Side AES-256 Sealing:** Your browser generates an ephemeral AES-256 session key, encrypts your Technical & Financial proposals locally, and uploads only ciphertext to the **Confidential Space Bid Vault** (`AMD SEV-SNP` memory-encrypted Confidential VMs).\n"
                "2. **FIPS 140-2 Level 3 Root of Trust (`Cloud KMS HSM`):** The master wrapping key resides inside dedicated Cloud KMS Hardware Security Modules.\n"
                "3. **Simultaneous Dual-Control Quorum at $T+0$:** Neither PS-DBM engineers nor Google Cloud administrators can decrypt your bid. Unsealing requires simultaneous cryptographic signatures from:\n"
                "   * **Key Share A:** BAC Chairperson Digital Token\n"
                "   * **Key Share B:** Commission on Audit (COA) Observer Digital Token\n"
                "   * **Timestamp Gate:** Hardware clock verification that `Current_Time >= Official_Bid_Opening_Timestamp (T+0)`."
            )
        else:
            citations = [
                "RA 12009 Sec. 20 & Sec. 23 (GOP-OMR Platinum Accreditation)",
                "mPhilGEPS TDD §7.1 (Document AI Custom Extractor Matrix)"
            ]
            core_answer = (
                "### 🏢 Platinum GOP-OMR Fast-Track Accreditation & Document AI Matrix\n\n"
                "Our **Document AI Custom Extractor (CDE)** reduces Platinum accreditation from **14 business days to under 15 minutes** by automatically verifying 5 mandatory legal documents:\n\n"
                "1. **SEC General Information Sheet (GIS):** Validates the constitutional **60/40 Filipino equity ownership threshold** (`filipino_equity_percentage >= 60.0%`) and cross-checks directors against competing bidders.\n"
                "2. **DTI / CDA Business Registration:** Verifies active trade name and screens against the GPPB Blacklist database.\n"
                "3. **BIR Tax Clearance Certificate:** Cryptographically validates the BIR QR/barcode and confirms expiration date extends past the tender opening date.\n"
                "4. **PCAB License (for Infrastructure):** Confirms license category (`AAA/AA/A`) meets the contract size range.\n"
                "5. **Audited Financial Statements (AFS):** Computes **NFCC** ($[(\\text{Current Assets} - \\text{Current Liabilities}) \\times 15] - \\text{Ongoing Works}$)."
            )

    # 2. Optional Live Vertex AI Enhancement (if ADC & Vertex AI endpoint are reachable)
    engine_mode = "OKF Deterministic Statutory Engine + Model Armor"
    if GENAI_AVAILABLE and os.environ.get("ENABLE_LIVE_VERTEX_AI", "true").lower() == "true":
        try:
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "markea-testbed-dev")
            client = genai.Client(vertexai=True, project=project_id, location="us-central1")
            sys_prompt = (
                "You are an official mPhilGEPS Phase 2 AI Agent for the Philippine Government (PS-DBM). "
                "Add a concise 2-sentence executive takeaway reinforcing the following statutory ruling without contradicting any numbers or citations:\n"
                + core_answer
            )
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=sanitized_query,
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt,
                    temperature=0.1,
                    max_output_tokens=160,
                )
            )
            if resp and resp.text:
                core_answer += f"\n\n---\n✨ **Live Vertex AI (`gemini-2.5-flash`) Executive Synthesis:** {resp.text.strip()}"
                engine_mode = "Live Vertex AI (gemini-2.5-flash) + OKF Statutory Grounding"
        except Exception:
            # Keep deterministic OKF grounded answer seamlessly
            pass

    if armor_report["pii_redacted"]:
        core_answer = (
            f"⚠️ **Model Armor DLP Notice (RA 10173):** Sensitive PII (`{', '.join(armor_report['redacted_types'])}`) "
            "was automatically redacted from your prompt before processing.\n\n" + core_answer
        )

    return {
        "agent_id": agent_id,
        "response_markdown": core_answer,
        "citations": citations,
        "sql_or_gql_generated": sql_or_gql,
        "model_armor": armor_report,
        "engine_mode": engine_mode,
        "latency_ms": round((time.time() - start_ts) * 1000, 1)
    }


def run_agent_turn(
    user_message: str,
    requested_agent: Optional[str] = "auto",
    portal_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    End-to-end orchestrator for a single conversational turn:
      1. Model Armor DLP & Prompt-Injection inspection
      2. Supervisor Intent Routing (BAC / COA / Merchant)
      3. Grounded OKF + Vertex AI response synthesis
    """
    armor_report = inspect_with_model_armor(user_message)
    routing = classify_agent_intent(armor_report["sanitized_text"], requested_agent)
    selected_agent = routing["selected_agent"]
    grounded = build_grounded_response(
        agent_id=selected_agent,
        sanitized_query=armor_report["sanitized_text"],
        armor_report=armor_report,
        portal_context=portal_context,
    )
    return {
        "agent_id": selected_agent,
        "agent_name": routing["agent_info"]["name"],
        "agent_icon": routing["agent_info"]["icon"],
        "agent_model": routing["agent_info"]["model"],
        "routing": routing,
        "response_markdown": grounded["response_markdown"],
        "statutory_citations": grounded["citations"],
        "generated_query": grounded["sql_or_gql_generated"],
        "model_armor": armor_report,
        "engine_mode": grounded["engine_mode"],
        "latency_ms": grounded["latency_ms"],
    }


# ==============================================================================
# 4. SPANNER GRAPH ANTI-COLLUSION & BIGQUERY ML ANOMALY DATA
# ==============================================================================
def get_spanner_graph_collusion_data() -> Dict[str, Any]:
    """
    Returns the interactive Cloud Spanner Graph topology, GQL query,
    and BigQuery ML Collusion Probability Index (CPI) + Benford's Law telemetry.
    """
    return {
        "graph_name": "MPhilGepsProcurementGraph",
        "tender_reference": "ITB-2026-DPWH-R3-004",
        "tender_title": "Construction of Flood Control Dike & Pumping Station - Pampanga River Basin (Package 4)",
        "approved_budget_abc": 145000000.00,
        "collusion_probability_index": 0.942,
        "risk_level": "CRITICAL_CARTEL_ALERT",
        "gql_query": (
            "GRAPH MPhilGepsProcurementGraph\n"
            "MATCH\n"
            "  (b1:Bidder)-[:SERVES_ON_BOARD]->(d:Director)<-[:SERVES_ON_BOARD]-(b2:Bidder),\n"
            "  (b1)-[:SUBMITTED_FOR]->(t:Tender {ref: 'ITB-2026-DPWH-R3-004'})<-[:SUBMITTED_FOR]-(b2),\n"
            "  (b1)-[:UTILIZED_NETWORK]->(ip:IP_Address)<-[:UTILIZED_NETWORK]-(b2)\n"
            "WHERE b1.id != b2.id\n"
            "RETURN b1.company_name, b2.company_name, d.full_name, ip.cidr, t.ref;"
        ),
        "nodes": [
            {"id": "T1", "label": "Tender: ITB-2026-DPWH-R3-004\n(ABC: ₱145.0M)", "type": "Tender", "x": 400, "y": 60, "color": "#1e40af"},
            {"id": "B1", "label": "Apex Builders Corp.\nBid: ₱144,120,000 (99.4% ABC)", "type": "Bidder_Flagged", "x": 180, "y": 190, "color": "#dc2626"},
            {"id": "B2", "label": "Titan Infrastructure Inc.\nBid: ₱144,710,000 (99.8% ABC)", "type": "Bidder_Flagged", "x": 400, "y": 190, "color": "#dc2626"},
            {"id": "B3", "label": "Luzon Prime Engineering\nBid: ₱132,450,000 (91.3% ABC)", "type": "Bidder_Clean", "x": 640, "y": 190, "color": "#059669"},
            {"id": "D1", "label": "Engr. Roberto M. Santos\n(Interlocking Board Director)", "type": "Director_Shared", "x": 160, "y": 340, "color": "#d97706"},
            {"id": "IP1", "label": "Shared NAT IP: 203.177.42.19\n(Submitted 140s apart)", "type": "IP_Shared", "x": 380, "y": 340, "color": "#7c3aed"},
            {"id": "G1", "label": "Metro Surety & Bond Corp\n(Shared Bid Security #8821)", "type": "Guarantor_Shared", "x": 600, "y": 340, "color": "#0284c7"}
        ],
        "edges": [
            {"from": "B1", "to": "T1", "label": "SUBMITTED_FOR (09:41:12)"},
            {"from": "B2", "to": "T1", "label": "SUBMITTED_FOR (09:43:32)"},
            {"from": "B3", "to": "T1", "label": "SUBMITTED_FOR (08:15:04)"},
            {"from": "B1", "to": "D1", "label": "SERVES_ON_BOARD (SEC GIS)"},
            {"from": "B2", "to": "D1", "label": "SERVES_ON_BOARD (SEC GIS)"},
            {"from": "B1", "to": "IP1", "label": "UTILIZED_NETWORK"},
            {"from": "B2", "to": "IP1", "label": "UTILIZED_NETWORK"},
            {"from": "B1", "to": "G1", "label": "FINANCIALLY_BACKED_BY"},
            {"from": "B2", "to": "G1", "label": "FINANCIALLY_BACKED_BY"}
        ],
        "benford_analysis": [
            {"digit": 1, "expected_pct": 30.1, "observed_pct": 14.2, "anomaly": False},
            {"digit": 2, "expected_pct": 17.6, "observed_pct": 11.5, "anomaly": False},
            {"digit": 3, "expected_pct": 12.5, "observed_pct": 9.8, "anomaly": False},
            {"digit": 4, "expected_pct": 9.7, "observed_pct": 8.1, "anomaly": False},
            {"digit": 5, "expected_pct": 7.9, "observed_pct": 7.4, "anomaly": False},
            {"digit": 6, "expected_pct": 6.7, "observed_pct": 6.2, "anomaly": False},
            {"digit": 7, "expected_pct": 5.8, "observed_pct": 6.8, "anomaly": False},
            {"digit": 8, "expected_pct": 5.1, "observed_pct": 7.6, "anomaly": False},
            {"digit": 9, "expected_pct": 4.6, "observed_pct": 28.4, "anomaly": True}
        ],
        "audit_findings": [
            "SEC GIS cross-check confirms Engr. Roberto M. Santos holds 35% equity in Apex Builders Corp. and sits as Corporate Secretary in Titan Infrastructure Inc.",
            "Both cover bids were uploaded from identical ISP gateway 203.177.42.19 within a 140-second window.",
            "BigQuery ML Benford's Law test on Bill of Quantities (BOQ) shows digit '9' appearing in 28.4% of unit prices (vs 4.6% natural expectation), proving synthetic price padding just under ceiling thresholds."
        ]
    }


# ==============================================================================
# 5. ANTI-SCRAPING PERIMETER & OCDS OPEN DATA OFFLOAD
# ==============================================================================
def simulate_anti_scraping_decision(profile: str) -> Dict[str, Any]:
    """
    Simulates the 4-tier anti-scraping decision pipeline at Cloud Armor + reCAPTCHA Enterprise edge.
    """
    profiles = {
        "shared_lgu_nat": {
            "profile_name": "Shared Government Agency NAT IP (DepEd / Quezon City LGU - 420 Concurrent Staff)",
            "source_ip": "202.90.134.88 (GovNet Shared Corporate NAT)",
            "tls_ja3_fingerprint": "771,4865-4866-4867,0-23-65281 (Verified Chrome 134 Browser)",
            "recaptcha_score": 0.94,
            "edge_latency_ms": 3.1,
            "decision": "ALLOW_SEAMLESS_200_OK",
            "http_status": 200,
            "layer_triggered": "Layer 2: reCAPTCHA Enterprise Token Validation (Score > 0.7)",
            "explanation": (
                "Although 420 BAC & procurement staff share single NAT IP 202.90.134.88 (exceeding 300 req/min IP rate), "
                "reCAPTCHA Enterprise behavioral telemetry confirms genuine human DOM/mouse dynamics (Score: 0.94). "
                "Zero CAPTCHA puzzle friction applied; < 5s SLA preserved."
            )
        },
        "ambiguous_crawler": {
            "profile_name": "Unauthenticated High-Frequency Search Script (Unknown Research Tool)",
            "source_ip": "112.198.77.142",
            "tls_ja3_fingerprint": "771,49195-49199,0-10-11 (Python Requests / Custom TLS)",
            "recaptcha_score": 0.45,
            "edge_latency_ms": 4.2,
            "decision": "STEP_UP_CHALLENGE_AND_THROTTLE",
            "http_status": 429,
            "layer_triggered": "Layer 2 & 3: Step-Up Verification + Apigee Quota Throttle (50 req/min)",
            "explanation": (
                "Behavioral score (0.45) falls in ambiguous band (0.3 - 0.7). Request is throttled at Cloud Armor edge "
                "and served an HTTP Link header pointing to the official OCDS Open Data bulk JSON feed."
            )
        },
        "commercial_scraper_bot": {
            "profile_name": "Commercial Bid-Alert Aggregator Bot (Headless Puppeteer + Residential Proxy Pool)",
            "source_ip": "185.220.101.44 (Rotating Proxy Farm)",
            "tls_ja3_fingerprint": "771,4865-4867,0-5-10-11 (Headless Chromium / Puppeteer Signature)",
            "recaptcha_score": 0.08,
            "edge_latency_ms": 1.8,
            "decision": "BLOCK_AT_EDGE_AND_OFFLOAD_TO_OCDS_CDN",
            "http_status": 429,
            "layer_triggered": "Layer 1 & 4: Cloud Armor JA3 Match + OCDS Open Data CDN Redirect",
            "explanation": (
                "Blocked at Google Edge in 1.8ms before touching GKE, AlloyDB, or Spanner. Commercial scraper is "
                "redirected to gs://mphilgeps-open-data-ocds (Cloud CDN) where daily OCDS v1.1 bulk exports are free—"
                "eliminating origin database load and de-monetizing paid bid-alert middlemen."
            )
        }
    }
    return profiles.get(profile, profiles["shared_lgu_nat"])

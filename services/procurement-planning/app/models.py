from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any

class UnspscHierarchy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    segment: str = Field(description="Segment (e.g., Information Technology Broadcasting and Telecommunications)")
    family: str = Field(description="Family (e.g., Computer Equipment and Accessories)")
    class_name: str = Field(alias="class", description="Class (e.g., Computers)")
    commodity: str = Field(description="Commodity (e.g., Desktop computers)")

class AppCseItem(BaseModel):
    item_code: Optional[str] = None
    unspsc_code: str
    hierarchy: Optional[UnspscHierarchy] = None
    confidence_score: float = Field(default=0.95, description="Gemini classification confidence score")
    description: str
    standardized_description: Optional[str] = None
    extracted_specifications: Optional[Dict[str, Any]] = None
    unit_of_measure: str
    unit_price: float
    q1_qty: int = 0
    q2_qty: int = 0
    q3_qty: int = 0
    q4_qty: int = 0
    total_qty: int
    total_amount: float
    preferred_depot: str = "DEPOT-NCR-MANILA"

class BigQueryDemandRecord(BaseModel):
    procurement_date: str = Field(description="ISO Date for time-series aggregation")
    unspsc_commodity_code: str = Field(description="UNSPSC 8-digit commodity code")
    total_expenditure: float = Field(description="Quarterly/Total planned expenditure")
    holiday_region: str = Field(default="PH", description="Philippine national calendar adjustment")

class AppCseSubmissionResponse(BaseModel):
    submission_id: str
    agency_id: str
    fiscal_year: int
    status: str
    total_items: int
    total_estimated_budget: float
    allocated_budget: float
    budget_status: str
    items: List[AppCseItem]
    bigquery_demand_stream: List[BigQueryDemandRecord] = []
    validation_errors: List[str] = []

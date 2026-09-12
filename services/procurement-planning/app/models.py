from pydantic import BaseModel, Field
from typing import List, Optional

class AppCseItem(BaseModel):
    item_code: Optional[str] = None
    unspsc_code: str
    description: str
    unit_of_measure: str
    unit_price: float
    q1_qty: int = 0
    q2_qty: int = 0
    q3_qty: int = 0
    q4_qty: int = 0
    total_qty: int
    total_amount: float
    preferred_depot: str = "DEPOT-NCR-MANILA"

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
    validation_errors: List[str] = []

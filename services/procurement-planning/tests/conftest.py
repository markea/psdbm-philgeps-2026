import pytest
import openpyxl
from io import BytesIO

@pytest.fixture
def sample_app_cse_bytes() -> bytes:
    """Creates an in-memory sample PS-DBM APP-CSE spreadsheet."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "APP-CSE 2026"

    # Header Row
    headers = [
        "Item Code", "Item Description", "Unit of Measure", 
        "Unit Price", "Q1", "Q2", "Q3", "Q4", "Total Qty", "Total Amount"
    ]
    ws.append(headers)

    # Sample Line Items
    rows = [
        ["14111507-PP-M01", "Paper, Multi-Copy, 80gsm, A4", "ream", 185.50, 100, 100, 50, 50, 300, 55650.00],
        ["44122011-FO-F01", "Folder, Fancy, A4, 50s/pack", "pack", 320.00, 10, 10, 5, 5, 30, 9600.00],
        ["44121704-BP-B01", "Ballpoint Pen, Black, Fine 0.7mm", "piece", 12.00, 200, 200, 100, 100, 600, 7200.00],
        ["53131626-AL-E01", "Ethyl Alcohol, 70% Solution, 500ml", "bottle", 55.00, 50, 50, 25, 25, 150, 8250.00]
    ]

    for r in rows:
        ws.append(r)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()

@pytest.fixture
def mismatch_app_cse_bytes() -> bytes:
    """Creates a sample spreadsheet with intentional arithmetic discrepancies."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "APP-CSE Errors"

    headers = [
        "Item Code", "Item Description", "Unit of Measure", 
        "Unit Price", "Q1", "Q2", "Q3", "Q4", "Total Qty", "Total Amount"
    ]
    ws.append(headers)

    # Q1..Q4 sum to 40, but reported Total Qty is 100
    rows = [
        ["44122011-FO-F01", "Folder, Fancy, A4", "pack", 320.00, 10, 10, 10, 10, 100, 32000.00]
    ]
    for r in rows:
        ws.append(r)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()

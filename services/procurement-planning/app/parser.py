"""
APP-CSE Excel Workbook Parser.
Reads and validates PS-DBM formatted spreadsheets (.xlsx) using openpyxl.
"""
import openpyxl
from io import BytesIO
from typing import List, Tuple
from app.models import AppCseItem
from app.classifier import classify_item_unspsc

def parse_app_cse_excel(file_bytes: bytes) -> Tuple[List[AppCseItem], List[str]]:
    """
    Parses workbook rows into normalized AppCseItem instances.
    Validates arithmetic for quarterly quantities and total pricing.
    """
    workbook = openpyxl.load_workbook(filename=BytesIO(file_bytes), data_only=True)
    sheet = workbook.active
    
    items: List[AppCseItem] = []
    errors: List[str] = []

    # Find the header row by looking for key procurement keywords
    header_row_idx = None
    col_map = {}

    for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        if not row:
            continue
        row_str = [str(cell).strip().lower() if cell is not None else "" for cell in row]
        if any("description" in c for c in row_str) and any("price" in c or "unit" in c for c in row_str):
            header_row_idx = row_idx
            for c_idx, val in enumerate(row_str):
                if "item" in val and "code" in val:
                    col_map["item_code"] = c_idx
                elif "description" in val or "item" in val:
                    col_map.setdefault("description", c_idx)
                elif "uom" in val or "unit" in val and "measure" in val:
                    col_map["uom"] = c_idx
                elif "price" in val:
                    col_map["price"] = c_idx
                elif "q1" in val:
                    col_map["q1"] = c_idx
                elif "q2" in val:
                    col_map["q2"] = c_idx
                elif "q3" in val:
                    col_map["q3"] = c_idx
                elif "q4" in val:
                    col_map["q4"] = c_idx
                elif "total" in val and "qty" in val:
                    col_map["total_qty"] = c_idx
                elif "total" in val and ("amount" in val or "price" in val):
                    col_map["total_amount"] = c_idx
            break

    # Fallback to positional columns if explicit headers aren't detected
    if header_row_idx is None:
        header_row_idx = 1
        col_map = {
            "item_code": 0,
            "description": 1,
            "uom": 2,
            "price": 3,
            "q1": 4,
            "q2": 5,
            "q3": 6,
            "q4": 7,
            "total_qty": 8,
            "total_amount": 9
        }

    for row_idx, row in enumerate(sheet.iter_rows(min_row=header_row_idx + 1, values_only=True), start=header_row_idx + 1):
        if not row or not any(row):
            continue
            
        desc_idx = col_map.get("description", 1)
        if desc_idx >= len(row) or not row[desc_idx]:
            continue
            
        raw_desc = str(row[desc_idx]).strip()
        if not raw_desc or raw_desc.lower().startswith("total") or raw_desc.lower().startswith("note"):
            continue

        try:
            item_code = str(row[col_map["item_code"]]).strip() if col_map.get("item_code") is not None and col_map["item_code"] < len(row) and row[col_map["item_code"]] else None
            uom = str(row[col_map.get("uom", 2)]).strip() if col_map.get("uom") is not None and col_map["uom"] < len(row) and row[col_map["uom"]] else "piece"
            
            def safe_int(val):
                try:
                    return int(float(val)) if val is not None else 0
                except (ValueError, TypeError):
                    return 0

            def safe_float(val):
                try:
                    return float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    return 0.0

            q1 = safe_int(row[col_map["q1"]]) if col_map.get("q1") is not None and col_map["q1"] < len(row) else 0
            q2 = safe_int(row[col_map["q2"]]) if col_map.get("q2") is not None and col_map["q2"] < len(row) else 0
            q3 = safe_int(row[col_map["q3"]]) if col_map.get("q3") is not None and col_map["q3"] < len(row) else 0
            q4 = safe_int(row[col_map["q4"]]) if col_map.get("q4") is not None and col_map["q4"] < len(row) else 0
            unit_price = safe_float(row[col_map["price"]]) if col_map.get("price") is not None and col_map["price"] < len(row) else 0.0

            calculated_qty = q1 + q2 + q3 + q4
            calculated_amount = round(calculated_qty * unit_price, 2)

            # Check for spreadsheet arithmetic mismatches
            if col_map.get("total_qty") is not None and col_map["total_qty"] < len(row):
                reported_qty = safe_int(row[col_map["total_qty"]])
                if reported_qty > 0 and reported_qty != calculated_qty:
                    errors.append(f"Row {row_idx} ({raw_desc}): Reported Total Qty ({reported_qty}) does not match sum of quarters ({calculated_qty})")

            unspsc = classify_item_unspsc(raw_desc, item_code)

            item = AppCseItem(
                item_code=item_code,
                unspsc_code=unspsc,
                description=raw_desc,
                unit_of_measure=uom,
                unit_price=unit_price,
                q1_qty=q1,
                q2_qty=q2,
                q3_qty=q3,
                q4_qty=q4,
                total_qty=calculated_qty,
                total_amount=calculated_amount,
                preferred_depot="DEPOT-NCR-MANILA"
            )
            items.append(item)
        except Exception as e:
            errors.append(f"Row {row_idx}: Failed to parse ({str(e)})")

    return items, errors

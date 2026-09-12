from app.parser import parse_app_cse_excel

def test_parse_valid_app_cse(sample_app_cse_bytes):
    items, errors = parse_app_cse_excel(sample_app_cse_bytes)
    assert len(items) == 4
    assert len(errors) == 0

    paper = items[0]
    assert paper.description == "Paper, Multi-Copy, 80gsm, A4"
    assert paper.unspsc_code == "14111507"
    assert paper.total_qty == 300
    assert paper.total_amount == 55650.00

    alcohol = items[3]
    assert alcohol.unspsc_code == "53131626"
    assert alcohol.total_qty == 150

def test_parse_arithmetic_mismatch(mismatch_app_cse_bytes):
    items, errors = parse_app_cse_excel(mismatch_app_cse_bytes)
    assert len(items) == 1
    assert len(errors) == 1
    assert "Reported Total Qty (100) does not match sum of quarters (40)" in errors[0]

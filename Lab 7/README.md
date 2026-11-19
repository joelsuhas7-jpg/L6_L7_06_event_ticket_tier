# L6_L7_06 — Event Ticket Tier

## Lab 7: Fuzz Testing with Hypothesis

This lab uses property-based testing to exercise promotional voucher codes,
tiered seat-row specifications, and attendee badge CSV strings.

### Files
- `processor.py` — input-processing functions with explicit validation.
- `test_processor.py` — Hypothesis tests for arbitrary and valid inputs.

### Run
```bash
python -m pip install hypothesis pytest
python -m pytest -v
```

Invalid input is rejected with `TypeError` (wrong input type) or `ValueError`
(malformed or out-of-range input). Valid input keeps the starter program's
output format.

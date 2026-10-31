import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def test_manifest_validation_and_confirmation_branches():
    with pytest.raises(ValueError):
        process_ticket_manifest(None, 0)
    with pytest.raises(ValueError):
        process_ticket_manifest([], -1)
    assert process_ticket_manifest([], 0) == {"total_revenue": 0.0, "status": "ZERO_SALES"}
    assert process_ticket_manifest([
        {"is_confirmed": False, "tier": "not-a-tier"},
        {"is_confirmed": True, "tier": "general", "orders": []},
    ], 0) == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_each_tier_and_invalid_tier():
    data = [
        {"is_confirmed": True, "tier": "vip", "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "premium", "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "general", "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "invalid", "orders": [{"qty": 1}]},
    ]
    assert process_ticket_manifest(data, 0) == {
        "total_revenue": 285.0, "status": "COMPLETED"
    }


def test_quantity_promo_and_discount_branches():
    data = [
        {"is_confirmed": True, "tier": "general", "orders": [
            {"qty": 0}, {"qty": -1},
            {"qty": 1, "promo": "FRAUD_RISK"},
            {"qty": 2, "promo": "EARLYBIRD"},
            {"qty": 4, "promo": "OTHER"},
            {"qty": 5, "promo": "OTHER"},
        ]}
    ]
    assert process_ticket_manifest(data, 0) == {
        "total_revenue": 502.0, "status": "COMPLETED"
    }


def test_vip_fraud_branch_breaks_order_loop():
    data = [{"is_confirmed": True, "tier": "vip", "exclusive_lounge": False,
             "orders": [{"qty": 1}, {"qty": 1, "promo": "FRAUD_RISK"},
                        {"qty": 1}]}]
    assert process_ticket_manifest(data, 0) == {
        "total_revenue": 0.0, "status": "ZERO_SALES"
    }


def test_lounge_and_audit_threshold_branches():
    data = [
        {"is_confirmed": True, "tier": "general", "exclusive_lounge": True,
         "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
    ]
    assert process_ticket_manifest(data, 0.1) == {
        "total_revenue": 132.0, "status": "AUDIT_REJECTED"
    }


def test_gate_flow_all_decision_outcomes_and_loops():
    assert monitor_gate_flow([]) == "NO_DATA"
    assert monitor_gate_flow([[]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51, 52]]) == "OVERFLOW"
    assert monitor_gate_flow([[60, 10, 60, 20], [51, 52]]) == "OVERFLOW"

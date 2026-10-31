import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def test_all_ticket_tiers_and_promotions():
    manifests = [
        {"is_confirmed": True, "tier": "vip", "orders": [{"qty": 1}, {"qty": 2, "promo": "EARLYBIRD"}]},
        {"is_confirmed": True, "tier": "premium", "orders": [{"qty": 5}]},
        {"is_confirmed": True, "tier": "general", "exclusive_lounge": True, "orders": [{"qty": 2}]},
    ]
    result = process_ticket_manifest(manifests, 0.1)
    assert result == {"total_revenue": 1083.5, "status": "COMPLETED"}


def test_unconfirmed_unknown_tier_and_empty_orders():
    manifests = [
        {"is_confirmed": False, "tier": "vip", "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "balcony", "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "general", "orders": []},
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_invalid_quantities_and_non_vip_fraud():
    manifests = [
        {"is_confirmed": True, "tier": "general", "orders": [
            {"qty": 0}, {"qty": -2}, {"qty": 1, "promo": "FRAUD_RISK"}
        ]}
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result == {"total_revenue": 45.0, "status": "COMPLETED"}


def test_vip_fraud_break_and_lounge():
    manifests = [
        {"is_confirmed": True, "tier": "vip", "exclusive_lounge": True,
         "orders": [{"qty": 2}, {"qty": 1, "promo": "FRAUD_RISK"}, {"qty": 3}]}
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result == {"total_revenue": 75.0, "status": "COMPLETED"}


def test_audit_rejection_after_more_than_four_rejections():
    manifests = [
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
        {"is_confirmed": True, "tier": "unknown"},
    ]
    assert process_ticket_manifest(manifests, 0) == {
        "total_revenue": 0.0, "status": "AUDIT_REJECTED"
    }


def test_validation_errors():
    with pytest.raises(ValueError):
        process_ticket_manifest("not-a-list", 0)
    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.01)


def test_gate_flow_paths():
    assert monitor_gate_flow([]) == "NO_DATA"
    assert monitor_gate_flow([[10, 20, 51, 40, 60]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51, 52]]) == "OVERFLOW"

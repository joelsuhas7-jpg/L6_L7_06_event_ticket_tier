"""Property-based fuzz tests for the Lab 7 input processors."""

import pytest
from hypothesis import given, strategies as st

from processor import (
    calculate_seat_tier_price,
    decode_promo_voucher,
    parse_attendee_badge,
)


@given(st.one_of(st.text(), st.none()))
def test_decode_promo_voucher_no_crash(value):
    # Arbitrary fuzz input must either be processed or rejected predictably.
    try:
        result = decode_promo_voucher(value)
    except (TypeError, ValueError):
        pass
    else:
        assert isinstance(result, str)
        assert result.startswith("Valid ")
        assert result.endswith("% OFF")


@given(st.one_of(st.text(), st.none()))
def test_calculate_seat_tier_price_safe(value):
    try:
        result = calculate_seat_tier_price(value)
    except (TypeError, ValueError):
        pass
    else:
        assert isinstance(result, float)
        assert result > 0


@given(st.one_of(st.text(), st.none()))
def test_parse_attendee_badge_safe(value):
    try:
        result = parse_attendee_badge(value)
    except (TypeError, ValueError):
        pass
    else:
        assert isinstance(result, str)
        assert " [" in result
        assert "] - Seat " in result


@given(
    prefix=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1),
    percentage=st.integers(min_value=1, max_value=100),
)
def test_valid_promo_vouchers(prefix, percentage):
    assert decode_promo_voucher(f"{prefix}-{percentage}") == (
        f"Valid {prefix.upper()}: {percentage}% OFF"
    )


@given(
    tier=st.sampled_from(["VIP", "PREMIUM", "GENERAL"]),
    row=st.integers(min_value=1, max_value=100),
)
def test_valid_seat_tier_prices(tier, row):
    rates = {"VIP": 150.0, "PREMIUM": 90.0, "GENERAL": 45.0}
    assert calculate_seat_tier_price(f"{tier}@{row}") == rates[tier] + row * 2.0


@given(
    name=st.text(min_size=1).filter(lambda value: value.strip() != "" and "," not in value),
    age=st.integers(min_value=0, max_value=120),
    seat=st.text(min_size=1).filter(lambda value: value.strip() != "" and "," not in value),
)
def test_valid_attendee_badges(name, age, seat):
    category = "Child" if age < 18 else "Adult"
    assert parse_attendee_badge(f"{name},{age},{seat}") == (
        f"{name.strip()} [{category}] - Seat {seat.strip()}"
    )


@pytest.mark.parametrize("value", [None, 42, 3.14, [], {}])
def test_non_string_inputs_are_rejected(value):
    for processor in (
        decode_promo_voucher,
        calculate_seat_tier_price,
        parse_attendee_badge,
    ):
        with pytest.raises(TypeError):
            processor(value)


@pytest.mark.parametrize(
    "value",
    ["", "EARLY", "EARLY-0", "EARLY-101", "EARLY-TEN", "A-B-20"],
)
def test_invalid_vouchers_are_rejected(value):
    with pytest.raises(ValueError):
        decode_promo_voucher(value)


@pytest.mark.parametrize(
    "value",
    ["", "VIP", "VIP@0", "VIP@101", "UNKNOWN@4", "VIP@abc", "VIP@4@5"],
)
def test_invalid_tier_specs_are_rejected(value):
    with pytest.raises(ValueError):
        calculate_seat_tier_price(value)


@pytest.mark.parametrize(
    "value",
    ["", "Joel,20", "Joel,20,A1,extra", ",20,A1", "Joel,-1,A1", "Joel,121,A1"],
)
def test_invalid_badges_are_rejected(value):
    with pytest.raises(ValueError):
        parse_attendee_badge(value)

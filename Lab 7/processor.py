"""Input processors for the Event Ticket Tier Lab 7 fuzz-testing exercise."""


def _require_string(value, field_name):
    """Reject non-string values consistently before parsing."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")


def decode_promo_voucher(voucher_code):
    """Decode vouchers formatted as PREFIX-PERCENT (for example EARLY-20)."""
    _require_string(voucher_code, "voucher_code")
    code = voucher_code.strip()
    if not code or code.count("-") != 1:
        raise ValueError("voucher must contain one PREFIX-PERCENT separator")

    prefix, pct_str = (part.strip() for part in code.split("-", 1))
    if not prefix or not prefix.isalnum():
        raise ValueError("voucher prefix must be non-empty and alphanumeric")
    if not pct_str.isdigit():
        raise ValueError("voucher percentage must be an integer")
    percentage = int(pct_str)
    if not 1 <= percentage <= 100:
        raise ValueError("voucher percentage must be between 1 and 100")

    return f"Valid {prefix.upper()}: {percentage}% OFF"


def calculate_seat_tier_price(tier_spec):
    """Calculate the price for a tier/row specification such as VIP@4."""
    _require_string(tier_spec, "tier_spec")
    if tier_spec.count("@") != 1:
        raise ValueError("tier specification must contain one @ separator")

    tier_part, row_part = (part.strip() for part in tier_spec.split("@", 1))
    tier = tier_part.upper()
    tier_rates = {
        "VIP": 150.0,
        "PREMIUM": 90.0,
        "GENERAL": 45.0,
    }
    if tier not in tier_rates:
        raise ValueError("unknown seat tier")
    if not row_part.isdigit():
        raise ValueError("row must be a non-negative integer")

    row = int(row_part)
    if row < 1 or row > 100:
        raise ValueError("row must be between 1 and 100")

    return tier_rates[tier] + (row * 2.0)


def parse_attendee_badge(badge_csv):
    """Format attendee data supplied as Name,Age,Seat."""
    _require_string(badge_csv, "badge_csv")
    tokens = badge_csv.split(",")
    if len(tokens) != 3:
        raise ValueError("badge must contain exactly three comma-separated fields")

    name = tokens[0].strip()
    age_text = tokens[1].strip()
    seat = tokens[2].strip()
    if not name:
        raise ValueError("attendee name cannot be empty")
    if not age_text.isdigit():
        raise ValueError("age must be a non-negative integer")
    if not seat:
        raise ValueError("seat cannot be empty")

    age = int(age_text)
    if not 0 <= age <= 120:
        raise ValueError("age must be between 0 and 120")

    category = "Child" if age < 18 else "Adult"
    return f"{name} [{category}] - Seat {seat}"


def main():
    print("==== Running decode_promo_voucher ====")
    v_input = input("Enter voucher (e.g. EARLY-20): ")
    print("Voucher:", decode_promo_voucher(v_input))

    print("\\n==== Running calculate_seat_tier_price ====")
    t_input = input("Enter tier spec (e.g. VIP@4): ")
    print("Seat Price: $", calculate_seat_tier_price(t_input))

    print("\\n==== Running parse_attendee_badge ====")
    b_input = input("Enter badge CSV (Name,Age,Seat): ")
    print("Badge:", parse_attendee_badge(b_input))


if __name__ == "__main__":
    main()

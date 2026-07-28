import re


def validate_details(details):
    """
    Validate extracted driving licence details.
    Returns the details dictionary along with validation results.
    """

    validation = {}

    license_number = details.get("license_number")

    if license_number is None:
        validation["license_number"] = "❌ Not Found"

    elif re.fullmatch(r"[A-Z]{2}\d{2}\s?\d+", license_number):
        validation["license_number"] = "✅ Valid"

    else:
        validation["license_number"] = "⚠️ Invalid"

    return details, validation
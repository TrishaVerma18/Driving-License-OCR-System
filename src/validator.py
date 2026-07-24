import re

def validate_details(details):
    """
    Validate extracted driving licence details.
    """

    license_number = details["license_number"]

    if license_number is None:
        print("License Number: Not Found")
    else:
        if re.fullmatch(r"[A-Z]{2}\d{2}\s?\d+", license_number):
            print("License Number: Valid")
        else:
            print("License Number: Invalid")

    return details
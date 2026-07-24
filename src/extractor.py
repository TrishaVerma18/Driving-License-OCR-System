import re

def extract_details(text_list):
    """
    Extract important details from OCR text.
    """

    details = {
        "name": None,
        "license_number": None,
        "dob": None,
        "issue_date": None,
        "expiry_date": None
    }

    # Convert OCR list into one string
    text = "\n".join(text_list)

    # Extract all dates in DD-MM-YYYY format
    dates = re.findall(r"\d{2}-\d{2}-\d{4}", text)
    print("Dates found:", dates)

    # Extract License Number
    license_match = re.search(r"[A-Z]{2}\d{2}\s?\d+", text)

    if license_match:
        details["license_number"] = license_match.group()

    ignore_words = [
    "INDIA",
    "LICENCE",
    "LICENSE",
    "DRIVING",
    "TRANSPORT",
    "GOVERNMENT",
    "DEPARTMENT"
    ]

    # Extract Name
    for line in text_list:

        if line.isupper():

            if len(line.split()) >= 2:

               if not any(word in line for word in ignore_words):
                   details["name"] = line
                   break

    # Assign dates safely
    if len(dates) >= 1:
        details["issue_date"] = dates[0]

    if len(dates) >= 2:
        details["expiry_date"] = dates[1]

    if len(dates) >= 3:
        details["dob"] = dates[2]

    return details
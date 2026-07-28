from src.preprocess import (
    load_image,
    convert_to_grayscale,
    apply_threshold,
    remove_noise,
)

from src.ocr_engine import extract_text

from src.extractor import extract_details

from src.validator import validate_details

from src.preprocess import preprocess_image

import cv2


def main():

    image = load_image("data/input/license.jpg")

    gray = convert_to_grayscale(image)

    threshold = apply_threshold(gray)

    clean = remove_noise(threshold)

    clean = preprocess_image("data/input/license.jpg")

    text = extract_text(clean)

    cv2.imwrite("data/output/grayscale.jpg", gray)
    cv2.imwrite("data/output/threshold.jpg", threshold)
    cv2.imwrite("data/output/clean.jpg", clean)

    print("\n===== OCR RESULT =====\n")

    text = extract_text(clean)

    details = extract_details(text)

    details = validate_details(details)

    print("\n===== EXTRACTED DETAILS =====")
    print("Name           :", details["name"])
    print("License Number :", details["license_number"])
    print("DOB            :", details["dob"])
    print("Issue Date     :", details["issue_date"])
    print("Expiry Date    :", details["expiry_date"])

    for line in text:
        print(line)

if __name__ == "__main__":
    main()
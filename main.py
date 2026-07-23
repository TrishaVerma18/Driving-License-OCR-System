from src.preprocess import (
    load_image,
    convert_to_grayscale,
    apply_threshold,
    remove_noise,
)

from src.ocr_engine import extract_text

import cv2


def main():

    image = load_image("data/input/license.jpg")

    gray = convert_to_grayscale(image)

    threshold = apply_threshold(gray)

    clean = remove_noise(threshold)

    cv2.imwrite("data/output/grayscale.jpg", gray)
    cv2.imwrite("data/output/threshold.jpg", threshold)
    cv2.imwrite("data/output/clean.jpg", clean)

    print("\n===== OCR RESULT =====\n")

    text = extract_text(clean)

    for line in text:
        print(line)


if __name__ == "__main__":
    main()
import easyocr


# Create the OCR reader only once
reader = easyocr.Reader(['en'])


def extract_text(image):
    """
    Extract text from an image using EasyOCR.

    Parameters:
        image: Preprocessed image (NumPy array)

    Returns:
        list of detected text strings
    """

    results = reader.readtext(image)

    extracted_text = []

    for result in results:
        text = result[1]
        extracted_text.append(text)

    return extracted_text
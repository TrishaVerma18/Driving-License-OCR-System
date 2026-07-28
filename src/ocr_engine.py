import easyocr

reader = easyocr.Reader(["en"])


def extract_text(image):
    results = reader.readtext(image)
    return [result[1] for result in results]


def extract_text_with_boxes(image):
    return reader.readtext(image)
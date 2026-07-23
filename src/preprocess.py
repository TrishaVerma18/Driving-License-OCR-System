import cv2


def load_image(image_path):
    """
    Loads an image from the given path.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    return image


def convert_to_grayscale(image):
    """
    Converts a color image to grayscale.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return gray


def apply_threshold(gray_image):
    """
    Convert grayscale image into black & white using Otsu Thresholding.
    """

    _, threshold = cv2.threshold(
        gray_image,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return threshold

def remove_noise(image):
    """
    Removes small noise using Median Blur.
    """

    denoised = cv2.medianBlur(image, 3)

    return denoised
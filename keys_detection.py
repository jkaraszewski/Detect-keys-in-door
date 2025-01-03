from PIL import Image, ImageOps, ImageChops
import numpy as np

def load_image(image_path):
    """
    Load an image from the specified file path.

    Args:
        image_path (str): The path to the image file.

    Returns:
        Image: The loaded image.

    Raises:
        FileNotFoundError: If the image file is not found.
    """
    try:
        image = Image.open(image_path)
        return image
    except FileNotFoundError:
        raise FileNotFoundError(f"Image at {image_path} not found.")

def preprocess_image(image, target_size=None):
    """
    Preprocess the image by resizing (optional) and converting to grayscale.

    Args:
        image (Image): The image to preprocess.
        target_size (tuple, optional): The target size to resize the image to. Defaults to None.

    Returns:
        Image: The preprocessed grayscale image.
    """
    if target_size:
        image = image.resize(target_size)
    gray_image = ImageOps.grayscale(image)
    return gray_image

def calculate_difference(image1, image2):
    """
    Calculate the difference between two images.

    Args:
        image1 (Image): The first image.
        image2 (Image): The second image.

    Returns:
        Image: The thresholded difference image.
    """
    diff = ImageChops.difference(image1, image2)
    diff = diff.convert("L")
    thresholded_diff = diff.point(lambda p: p > 30 and 255)
    return thresholded_diff

def detect_changes(image1, image2):
    """
    Detect changes between two images by comparing them.

    Args:
        image1 (Image): The first image.
        image2 (Image): The second image.

    Returns:
        int: The number of detected changes.
    """
    diff = calculate_difference(image1, image2)
    diff_array = np.array(diff)
    contours = np.where(diff_array)

    detected_changes = len(contours[0])

    log.info(f"Changes detected: {detected_changes}")
    return detected_changes

def detect_keys_in_image(image, image_without_keys):
    """
    Detect if keys are present in a specific region of the image.

    Args:
        image (Image): The image to check.
        image_without_keys (Image): The reference image without keys.

    Returns:
        bool: True if keys are detected, False otherwise.
    
    """
    # Coordinates defining the area of the picture where you want to detect differences in pixels
    x1, y1, x2, y2 = 1460, 280, 1645, 470
    region_of_interest = image.crop((x1, y1, x2, y2))
    region_without_keys = image_without_keys.crop((x1, y1, x2, y2))
    
    target_size = (region_without_keys.width, region_without_keys.height)
    region_resized = preprocess_image(region_of_interest, target_size)
    region_without_keys_resized = preprocess_image(region_without_keys, target_size)

    # If needed, you can save the region of interest from the image to check to verify the detection area and for example you this picture in notification.
    region_resized.save("</path_to_your_directory>/region_of_interest.png")
    
    detected_changes = detect_changes(region_resized, region_without_keys_resized)
    # You can edit the threshold value to adjust the sensitivity of the detection. This value can be seen in the log.
    if detected_changes > 100:
        return True
    else:
        return False

@service
def process_images():
    """
    Process images to detect the presence of keys and update the state accordingly.

    This function loads the reference image without keys and the image to check,
    detects if keys are present in the image to check, and based on that you can perform actions in Home Assistant for example,
    updates the state of `input_boolean.arekeysindoor` based on the detection result.

    @service is keyword that allows you to call the function from Home Assistant.
    """
    image_without_keys = load_image("</path_to_your_directory>/image_without_keys.png")
    image_to_check = load_image("</path_to_your_directory>/image_to_check.png")
    result_to_check = detect_keys_in_image(image_to_check, image_without_keys)

    if result_to_check:
        input_boolean.turn_on(entity_id="input_boolean.arekeysindoor")
    else:
        input_boolean.turn_off(entity_id="input_boolean.arekeysindoor")

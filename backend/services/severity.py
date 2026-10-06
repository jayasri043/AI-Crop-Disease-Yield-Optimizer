import cv2
import numpy as np


def estimate_severity(image_path, confidence, disease=None):
    """
    Estimate disease severity using image analysis.

    Healthy crops are returned as:
        severity = "None"
        affected_area = 0

    For diseased crops, the affected area is estimated
    from abnormal color regions.

    This is a baseline computer-vision estimate and should not
    be treated as an exact agricultural diagnosis.
    """

    # ------------------------------------------
    # 1. Handle healthy crop
    # ------------------------------------------

    if disease:
        disease_lower = disease.lower()

        if "healthy" in disease_lower:
            return {
                "severity": "None",
                "score": 0,
                "affected_area": 0
            }

    # ------------------------------------------
    # 2. Read image
    # ------------------------------------------

    image = cv2.imread(image_path)

    if image is None:
        return {
            "severity": "Unknown",
            "score": 0,
            "affected_area": 0
        }

    # ------------------------------------------
    # 3. Resize image
    # ------------------------------------------

    image = cv2.resize(
        image,
        (224, 224)
    )

    # ------------------------------------------
    # 4. Convert image to HSV
    # ------------------------------------------

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # ------------------------------------------
    # 5. Detect abnormal/dark regions
    # ------------------------------------------

    lower_bound = np.array(
        [0, 30, 20]
    )

    upper_bound = np.array(
        [179, 255, 180]
    )

    mask = cv2.inRange(
        hsv,
        lower_bound,
        upper_bound
    )

    # ------------------------------------------
    # 6. Remove small noise
    # ------------------------------------------

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # ------------------------------------------
    # 7. Calculate affected area
    # ------------------------------------------

    affected_pixels = np.count_nonzero(mask)

    total_pixels = (
        mask.shape[0] *
        mask.shape[1]
    )

    affected_area = (
        affected_pixels /
        total_pixels
    ) * 100

    affected_area = round(
        affected_area,
        2
    )

    # ------------------------------------------
    # 8. Calculate severity
    # ------------------------------------------

    if confidence < 60:
        severity = "Low"

    elif affected_area < 10:
        severity = "Low"

    elif affected_area < 30:
        severity = "Moderate"

    else:
        severity = "High"

    # ------------------------------------------
    # 9. Return result
    # ------------------------------------------

    return {
        "severity": severity,
        "score": affected_area,
        "affected_area": affected_area
    }
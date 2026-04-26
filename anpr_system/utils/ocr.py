import re

import easyocr
import torch

from config import OCR_LANGUAGES

READER = easyocr.Reader(OCR_LANGUAGES, gpu=torch.cuda.is_available())


def read_plate(plate_image):
    try:
        results = READER.readtext(plate_image, detail=1, paragraph=False)
    except Exception:
        return "UNDETECTED"

    if not results:
        return "UNDETECTED"

    best = max(results, key=lambda item: item[2])
    text = best[1].upper()
    confidence = best[2]
    cleaned = "".join(re.findall(r"[A-Z0-9]", text))

    if confidence < 0.3 or not cleaned:
        return "UNDETECTED"

    return cleaned

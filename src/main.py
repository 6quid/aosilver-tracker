import time
import pyautogui
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
import secrets
import string

# ---- CONFIG ----
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
chat_region = (0, 980, 600, 480)  # adjust to your chat box
update_interval = 1  # seconds

# ---- GLOBALS ----
total_silver = 0
setForAllTime = set()


def generate_random_id(length=8):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


# ---- SILVER PARSER ----
def parse_silver(text: str, seen_in_screenshot: set):
    global total_silver
    global setForAllTime

    print("Parse Silver Method Starts")
    print("----" * 10)
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # ---- Normalize line to generate a robust key ----
        normalized_line = re.sub(r"[^a-zA-Z0-9]+", "", line.lower())
        random_id = generate_random_id()
        normalized_line += random_id
        # ---- Gains ----
        if "you gained" in line.lower():
            match = re.search(r"gained.*?([\d,]+)\s*Silver", line, re.IGNORECASE)
            timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
            if match:
                number = int(match.group(1).replace(",", ""))
                key = (
                    "gain",
                    number,
                    normalized_line,
                )

                if key not in seen_in_screenshot and key not in setForAllTime:
                    seen_in_screenshot.add(key)
                    setForAllTime.add(key)
                    total_silver += number
                    print(f"[GAIN] {number} → Total: {total_silver}")

        # ---- Losses ----
        elif "you paid" in line.lower():
            match = re.search(r"paid.*?([\d,]+)\s*Guild\s*Tax", line, re.IGNORECASE)
            timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
            if match:
                number = int(match.group(1).replace(",", ""))
                key = (
                    "loss",
                    number,
                    normalized_line,
                )

                if key not in seen_in_screenshot and key not in setForAllTime:
                    seen_in_screenshot.add(key)
                    setForAllTime.add(key)
                    total_silver -= number
                    print(f"[LOSS] {number} → Total: {total_silver}")


# ---- MAIN LOOP ----
print("Starting live silver tracker... Ctrl+C to stop")
while True:
    # 1️ Capture chat region
    screenshot = pyautogui.screenshot(region=chat_region)
    # 2️ Preprocess for OCR
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # 3 OCR
    text = pytesseract.image_to_string(Image.fromarray(gray))

    # 4️ Parse silver
    seen_in_screenshot = set()  # temporary set for this screenshot
    # persistent set for all time

    print("Seen in ScreenShotset:", seen_in_screenshot)

    parse_silver(text, seen_in_screenshot)
    print("----" * 10)
    print("Seen in ScreenshotSet after End:", seen_in_screenshot)
    print("Parse Silver Method Ends")

    # 5️ Wait before next update
    time.sleep(update_interval)

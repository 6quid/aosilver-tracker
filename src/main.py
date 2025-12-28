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

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # ---- Gains ----
        if "you gained" in line.lower():
            match = re.search(r"gained.*?([\d,]+)\s*Silver", line, re.IGNORECASE)
            # More flexible timestamp pattern to handle OCR errors
            timestamp_match = re.search(r"\[?(\d{1,2}[:.]\d{1,2}[:.]\d{1,2})\]?", line)
            if match:
                number = int(match.group(1).replace(",", ""))
                key = (
                    "gain",
                    number,
                    timestamp_match.group(1) if timestamp_match else "",
                )

                if key not in seen_in_screenshot and key not in setForAllTime:
                    seen_in_screenshot.add(key)
                    setForAllTime.add(key)
                    total_silver += number
                    print(f"✅ [GAIN] +{number:,} Silver")

        # ---- Losses ----
        elif "you paid" in line.lower():
            match = re.search(r"paid.*?([\d,]+)\s*Guild\s*Tax", line, re.IGNORECASE)
            timestamp_match = re.search(r"\[?(\d{1,2}[:.]\d{1,2}[:.]\d{1,2})\]?", line)
            if match:
                number = int(match.group(1).replace(",", ""))
                key = (
                    "loss",
                    number,
                    timestamp_match.group(1) if timestamp_match else "",
                )

                if key not in seen_in_screenshot and key not in setForAllTime:
                    seen_in_screenshot.add(key)
                    setForAllTime.add(key)
                    total_silver -= number
                    print(f"❌ [LOSS] -{number:,} Silver")


# ---- MAIN LOOP ----
print("=" * 60)
print("🪙  SILVER TRACKER STARTED  🪙".center(60))
print("=" * 60)
print("Press Ctrl+C to stop and see final results\n")

try:
    while True:
        # 1️ Capture chat region
        screenshot = pyautogui.screenshot(region=chat_region)
        screenshot.save("debug_screenshot.png")  # for debugging
        # 2️ Preprocess for OCR - gentler preprocessing to preserve timestamps
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply contrast enhancement instead of harsh thresholding
        gray = cv2.equalizeHist(gray)
        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, h=10)

        # 3 OCR with custom config for better accuracy
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(Image.fromarray(gray), config=custom_config)

        # 4️ Parse silver
        seen_in_screenshot = set()  # temporary set for this screenshot
        parse_silver(text, seen_in_screenshot)

        # Display current total with nice formatting
        print(f"\n💰 Current Total: {total_silver:,} Silver 💰\n")

        # 5️ Wait before next update
        time.sleep(update_interval)

except KeyboardInterrupt:
    # Final summary when user stops the program
    print("\n" + "=" * 60)
    print("📊  FINAL RESULTS  📊".center(60))
    print("=" * 60)
    print(f"\n🏆  Total Silver Earned: {total_silver:,} Silver")
    print(f"📈  Total Transactions: {len(setForAllTime)}")
    print("\n" + "=" * 60)
    print("Thank you for using Silver Tracker!".center(60))
    print("=" * 60 + "\n")

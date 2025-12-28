import cv2
import pytesseract
from PIL import Image
import argparse
import os
from utils.parse_silver import parse_silver
import asyncio

# Image Path
image_path = "./test_chat2.png"
image = cv2.imread(image_path)

# Preprocess the image for better OCR results
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
text: str = pytesseract.image_to_string(Image.open(image_path))
print("Extracted Text:")
print(text)
parse_silver(text)

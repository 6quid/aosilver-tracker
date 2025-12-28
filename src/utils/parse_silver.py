total_silver = 0
import re


def parse_silver(text: str) -> None:
    global total_silver
    for line in text.splitlines():
        if "you gained" in line.lower():
            # Remove commas and + sign, extract digits
            print(f"Processing Line: {line}")
            match = re.search(r"gained.*?([\d,]+)\s*Silver", line, re.IGNORECASE)
            if match:
                number = int(match.group(1).replace(",", ""))
                total_silver += number
                print(f"Number Extracted: {number}")
                print(f"Current Gain: {number}")
            else:
                print("No valid number found in this line")
        elif "you paid" in line.lower():
            print(f"Processing Line: {line}")
            match = re.search(r"paid.*?([\d,]+)\s*Guild\s*Tax", line, re.IGNORECASE)
            if match:
                number = int(match.group(1).replace(",", ""))
                total_silver -= number
                print(f"Number Extracted: {number}")
                print(f"Current Loss: {number}")
            else:
                print("No valid number found in this line")
    print(f"Total Silver Gained: {total_silver}")

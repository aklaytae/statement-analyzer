
import pdfplumber
import re
from datetime import datetime


def clean_number(x):
    return float(x.replace(",", ""))


def classify(desc, amount):
    desc = desc.upper()

    # ✅ เงินเข้า
    if "PPSDTR" in desc or "MOSD" in desc or "ATSDC" in desc:
        return amount, 0

    # ✅ เงินออก
    if "MPPOFF" in desc or "MASWC" in desc or "SWCA" in desc:
        return 0, amount

    return 0, amount


def parse_gsb(pdf_path):
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                if "ยอดยกมา" in line or "C/F" in line:
                    continue

                date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if not date_match:
                    continue

                try:
                    date = datetime.strptime(date_match.group(), "%d/%m/%Y")
                except:
                    continue

                numbers = re.findall(r"[\d,]+\.\d{2}", line)

                if len(numbers) < 3:
                    continue

                # ✅ amount = ตัวหน้า
                amount = clean_number(numbers[-3])

                # ✅ balance = ตัวท้าย
                balance = clean_number(numbers[-1])

                # ✅ ใช้ classify
                income, expense = classify(line, amount)

                if income == 0 and expense == 0:
                    continue

                transactions.append({
                    "date": date,
                    "balance": balance,
                    "income": income,
                    "expense": expense,
                    "description": line
                })

    return transactions

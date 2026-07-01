
import pdfplumber
import re
from datetime import datetime


def clean_number(x):
    return float(x.replace(",", ""))


def parse_gsb(pdf_path):
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                # skip header
                if "ยอดยกมา" in line or "C/F" in line:
                    continue

                date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if not date_match:
                    continue

                date_str = date_match.group()

                try:
                    date = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue

                numbers = re.findall(r"[\d,]+\.\d{2}", line)

                # ✅ ต้องมี 3 ค่า (expense income balance)
                if len(numbers) < 3:
                    continue

                # ✅ ✅ FIX จริงอยู่ตรงนี้
                expense = clean_number(numbers[-3])
                income = clean_number(numbers[-2])
                balance = clean_number(numbers[-1])

                # skip empty
                if expense == 0 and income == 0:
                    continue

                transactions.append({
                    "date": date,
                    "balance": balance,
                    "income": income,
                    "expense": expense,
                    "description": line
                })

    return transactions

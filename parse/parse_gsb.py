import pdfplumber
import re
from datetime import datetime


def clean_number(text):
    """แปลง 1,234.56 → float"""
    return float(text.replace(",", ""))


def parse_gsb(pdf_path):
    transactions = []

    prev_balance = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                # ✅ หา date
                date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if not date_match:
                    continue

                date_str = date_match.group()

                # ✅ หาเลขทั้งหมดในบรรทัด
                numbers = re.findall(r"[\d,]+\.\d{2}", line)

                # ต้องมีขั้นต่ำ balance + amount
                if len(numbers) < 2:
                    continue

                # ✅ balance = ตัวแรก
                balance = clean_number(numbers[0])

                # ✅ parse date
                try:
                    date = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue

                # ✅ ใช้ diff ระหว่าง balance
                if prev_balance is not None:
                    diff = balance - prev_balance

                    # ปัดเศษแก้ floating point
                    diff = round(diff, 2)

                    if diff > 0:
                        income = diff
                        expense = 0
                    else:
                        income = 0
                        expense = abs(diff)

                    transactions.append({
                        "date": date,
                        "balance": balance,
                        "income": income,
                        "expense": expense,
                        "description": line
                    })

                prev_balance = balance

    return transactions

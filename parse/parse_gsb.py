
import pdfplumber
import re
from datetime import datetime


def clean_number(text):
    return float(text.replace(",", ""))


def parse_gsb(pdf_path):
    transactions = []

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

                # ✅ ดึงตัวเลขทั้งหมด
                numbers = re.findall(r"[\d,]+\.\d{2}", line)

                # ✅ GSB pattern: ต้องมีอย่างน้อย 3 ค่า
                # balance + expense + income
                if len(numbers) < 3:
                    continue

                try:
                    date = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue

                # ✅ ตัวสำคัญที่สุด
                expense = clean_number(numbers[-2])
                income = clean_number(numbers[-1])
                balance = clean_number(numbers[0])

                # ✅ skip zero transaction
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

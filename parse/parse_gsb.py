
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

                # ✅ skip header/footer
                if "ยอดยกมา" in line or "C/F" in line:
                    continue

                # ✅ หา date
                date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if not date_match:
                    continue

                date_str = date_match.group()

                try:
                    date = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue

                # ✅ ดึงตัวเลขทั้งหมด
                numbers = re.findall(r"[\d,]+\.\d{2}", line)

                # ✅ ต้องมีอย่างน้อย 2 ตัวท้าย
                if len(numbers) < 2:
                    continue

                # ✅ ✅ KEY FIX ตรงนี้
                expense = clean_number(numbers[-2])
                income = clean_number(numbers[-1])

                # ✅ skip ถ้าไม่มี transaction
                if expense == 0 and income == 0:
                    continue

                transactions.append({
                    "date": date,
                    "expense": expense,
                    "income": income,
                    "description": line
                })

    return transactions

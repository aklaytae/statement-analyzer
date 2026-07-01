
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

                if "ยอดยกมา" in line or "C/F" in line:
                    continue

                date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if not date_match:
                    continue

                date = datetime.strptime(date_match.group(), "%d/%m/%Y")

                numbers = re.findall(r"[\d,]+\.\d{2}", line)

                if len(numbers) < 3:
                    continue

                # ✅ ดึงท้ายสุด
                last = [clean_number(x) for x in numbers[-3:]]

                # structure:
                # [amount, tax, balance]

                amount = last[0]
                tax = last[1]
                balance = last[2]

                desc = line

                # ✅ แยก income / expense จาก DESCRIPTION
                if "PPSDTR" in desc or "ฝาก" in desc or "Transfer SAV" in desc:
                    income = amount
                    expense = 0
                else:
                    income = 0
                    expense = amount

                transactions.append({
                    "date": date,
                    "balance": balance,
                    "income": income,
                    "expense": expense,
                })

    return transactions

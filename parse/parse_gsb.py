
import pdfplumber
import re
from datetime import datetime

def parse_gsb(pdf_path):
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                # หา date
                date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
                if not date_match:
                    continue

                date_str = date_match.group()

                # หา amount
                amounts = re.findall(r"[\d,]+\.\d{2}", line)
                if not amounts:
                    continue

                amount = float(amounts[-1].replace(",", ""))

                desc = line

                # แยกเงินเข้าเงินออก
                if any(x in desc for x in [
                    "PPSDTR", "ฝาก", "Transfer SAV", "ATM", "รับโอน"
                ]):
                    income = amount
                    expense = 0
                else:
                    income = 0
                    expense = amount

                transactions.append({
                    "date": datetime.strptime(date_str, "%d/%m/%Y"),
                    "description": desc,
                    "income": income,
                    "expense": expense
                })

    return transactions
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

                # ✅ หาเลขทั้งหมด
                numbers = re.findall(r"[\d,]+\.\d{2}", line)

                # ต้องมีอย่างน้อย balance + 1 ช่อง amount
                if len(numbers) < 2:
                    continue

                try:
                    date = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue

                # ✅ logic สำคัญ
                # structure GSB:
                # numbers = [balance, expense?, income?]

                balance = clean_number(numbers[0])

                expense = 0
                income = 0

                if len(numbers) == 3:
                    # ✅ มีทั้ง expense และ income (ปกติ)
                    left = clean_number(numbers[1])
                    right = clean_number(numbers[2])

                    # 👉 left = expense, right = income
                    expense = left
                    income = right

                elif len(numbers) == 2:
                    # ✅ มีแค่ช่องเดียว → ต้องดูตำแหน่งจาก text
                    value = clean_number(numbers[1])

                    # heuristic fallback
                    if " " in line:
                        # ถ้าอยู่ด้านขวา (income)
                        if re.search(r"\s{}\s*$".format(numbers[1]), line):
                            income = value
                        else:
                            expense = value
                    else:
                        expense = value

                # ✅ skip zero line
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

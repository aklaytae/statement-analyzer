
import pdfplumber
import re
from datetime import datetime


def clean_number(x):
    return float(x.replace(",", ""))


def merge_lines(lines):
    """รวมบรรทัดที่ belong ด้วยกัน"""
    merged = []
    buffer = ""

    for line in lines:

        # ถ้ามี date = เริ่ม transaction ใหม่
        if re.search(r"\d{2}/\d{2}/\d{4}", line):
            if buffer:
                merged.append(buffer)
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        merged.append(buffer)

    return merged


def parse_gsb(pdf_path):
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            # ✅ ✅ FIX สำคัญตรงนี้
            lines = merge_lines(lines)

            for line in lines:

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

                if len(numbers) < 2:
                    continue

                # ✅ ใช้ 2 ตัวท้ายเหมือนเดิม
                expense = clean_number(numbers[-2])
                income = clean_number(numbers[-1])

                # skip แถวว่าง
                if expense == 0 and income == 0:
                    continue

                transactions.append({
                    "date": date,
                    "expense": expense,
                    "income": income,
                    "description": line
                })

    return transactions

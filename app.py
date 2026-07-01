
import streamlit as st
from tempfile import NamedTemporaryFile
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from collections import defaultdict
from openpyxl import Workbook

# -----------------------------
# ✅ HELPERS
# -----------------------------

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


# -----------------------------
# ✅ PARSE GSB PDF
# -----------------------------

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

                amount = clean_number(numbers[-3])
                balance = clean_number(numbers[-1])

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


# -----------------------------
# ✅ FIX split transaction (สำคัญมาก)
# -----------------------------

def merge_same_day(transactions):
    merged = []
    used = [False] * len(transactions)

    for i in range(len(transactions)):
        if used[i]:
            continue

        t1 = transactions[i]
        found = False

        for j in range(i + 1, len(transactions)):
            if used[j]:
                continue

            t2 = transactions[j]

            if t1["date"] == t2["date"]:
                if abs(t1["expense"] - t2["income"]) < 0.01 or abs(t1["income"] - t2["expense"]) < 0.01:

                    merged.append({
                        "date": t1["date"],
                        "income": max(t1["income"], t2["income"]),
                        "expense": max(t1["expense"], t2["expense"]),
                        "description": t1["description"] + " | " + t2["description"]
                    })

                    used[i] = True
                    used[j] = True
                    found = True
                    break

        if not found:
            merged.append(t1)

    return merged


# -----------------------------
# ✅ SUMMARY
# -----------------------------

def summarize_daily(transactions):
    summary = defaultdict(lambda: {"income": 0, "expense": 0})

    for t in transactions:
        d = t["date"].date()
        summary[d]["income"] += t["income"]
        summary[d]["expense"] += t["expense"]

    result = []

    for date, val in summary.items():
        net = val["income"] - val["expense"]

        result.append({
            "date": str(date),
            "income": round(val["income"], 2),
            "expense": round(val["expense"], 2),
            "net": round(net, 2)
        })

    return sorted(result, key=lambda x: x["date"])


# -----------------------------
# ✅ EXPORT EXCEL
# -----------------------------

def generate_excel(summary):
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"

    ws.append(["Date", "Income", "Expense", "Net"])

    for row in summary:
        ws.append([
            row["date"],
            row["income"],
            row["expense"],
            row["net"]
        ])

    file_path = "statement_summary.xlsx"
    wb.save(file_path)

    return file_path


# =============================
# ✅ STREAMLIT UI
# =============================

st.set_page_config(page_title="Statement Analyzer")

st.title("📊 Statement Analyzer (GSB)")

file = st.file_uploader("Upload PDF Statement", type=["pdf"])

if file:
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.read())
        pdf_path = tmp.name

    st.info("🔍 กำลังอ่านไฟล์...")

    transactions = parse_gsb(pdf_path)
    transactions = merge_same_day(transactions)

    if not transactions:
        st.error("❌ ไม่พบข้อมูล")
    else:
        st.success("✅ อ่านข้อมูลสำเร็จ")

        df = pd.DataFrame(transactions)

        st.subheader("📄 Transaction Preview")
        st.dataframe(df.head(20))

        summary = summarize_daily(transactions)
        df_summary = pd.DataFrame(summary)

        st.subheader("📊 Daily Summary")
        st.dataframe(df_summary)

        st.bar_chart(df_summary.set_index("date")[["income", "expense"]])

        excel_file = generate_excel(summary)

        with open(excel_file, "rb") as f:
            st.download_button(
                "⬇️ Download Excel",
                f,
                file_name="statement_summary.xlsx"
            )

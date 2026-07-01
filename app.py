
import streamlit as st
from tempfile import NamedTemporaryFile
import pandas as pd

from parse_gsb import parse_gsb
from utils.summary import summarize_daily
from generate.generate_excel import generate_excel

st.set_page_config(page_title="Statement Analyzer")

st.title("📊 Statement Analyzer (GSB)")

file = st.file_uploader("Upload PDF Statement", type=["pdf"])

if file:
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.read())
        pdf_path = tmp.name

    st.info("🔍 กำลังอ่านไฟล์...")

    # ✅ ต้องอยู่ใน block นี้
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

        # generate excel
        excel_file = generate_excel(summary)

        with open(excel_file, "rb") as f:
            st.download_button(
                "⬇️ Download Excel",
                f,
                file_name="statement_summary.xlsx"
            )


def merge_same_day(transactions):
    merged = []
    used = [False] * len(transactions)

    for i in range(len(transactions)):
        if used[i]:
            continue

        t1 = transactions[i]
        found_pair = False

        for j in range(i + 1, len(transactions)):
            if used[j]:
                continue

            t2 = transactions[j]

            # ✅ เงื่อนไขจับคู่ (วันเดียว + amount เท่ากัน)
            if t1["date"] == t2["date"]:
                if abs(t1["expense"] - t2["income"]) < 0.01 or abs(t1["income"] - t2["expense"]) < 0.01:

                    merged.append({
                        "date": t1["date"],
                        "income": max(t1["income"], t2["income"]),
                        "expense": max(t1["expense"], t2["expense"]),
                        "description": t1.get("description", "") + " | " + t2.get("description", "")
                    })

                    used[i] = True
                    used[j] = True
                    found_pair = True
                    break

        if not found_pair:
            merged.append(t1)

    return merged


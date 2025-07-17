import streamlit as st
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Sensitive Word Checker", layout="wide")
st.title("🔍 Grammar (Sensitive words) check")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, keep_default_na=False)

    # List of sensitive words
    sensitive_words = [
        "sex", "drugs", "alcohol", "behaviour", "behavioral", "aggression", "aggressive"
    ]

    # Function to detect sensitive words
    def detect_sensitive_words(note):
        found = [word for word in sensitive_words if re.search(rf"\b{re.escape(word)}\b", note, re.IGNORECASE)]
        return f"Yes: {', '.join(found)}" if found else "No"

    if st.button("🚨 Check for Sensitive Words"):
        with st.spinner("Scanning notes..."):
            df["Sensitive Word Flag"] = df["Student notes"].apply(detect_sensitive_words)

            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.success("✅ Scan Complete!")

            st.download_button(
                label="📥 Download Results",
                data=output,
                file_name="Grammar_Check.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

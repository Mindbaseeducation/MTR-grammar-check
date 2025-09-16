import streamlit as st
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Sensitive Word Checker", layout="wide")
st.title("🔍 Grammar (Sensitive words & Name check)")

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

    # Function to check student's name presence
    def check_student_name(row):
        note = str(row["Student notes"]).lower()
        first_name = str(row["Student Name"]).split()[0].lower() if row["Student Name"] else ""
        
        # Check if first name is present OR "student"/"mentee" mentioned
        if (first_name in note) or ("student" in note) or ("mentee" in note):
            return "No"
        else:
            return "Yes"

    if st.button("🚨 Run Checks"):
        with st.spinner("Scanning notes..."):
            # Sensitive words check
            df["Sensitive Word Flag"] = df["Student notes"].apply(detect_sensitive_words)

            # Student name check
            df["Correct Student Name Not Mentioned"] = df.apply(check_student_name, axis=1)

            # Save results
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.success("✅ Scan Complete!")

            st.download_button(
                label="📥 Download Results",
                data=output,
                file_name="Sensitive words and Student Name Check.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            

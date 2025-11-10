import streamlit as st
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Sensitive Word Checker", layout="wide")
st.title("🔍 Grammar (Sensitive words, Name & Contact Details Check)")

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
        
        if (first_name in note) or ("student" in note) or ("mentee" in note):
            return "No"
        else:
            return "Yes"

    # Function to validate contact numbers
    def contact_details_check(row):
        country = str(row.get("Country", "")).strip().lower()
        primary = str(row.get("Primary Mobile Number", "")).strip()
        whatsapp = str(row.get("Whatsapp Mobile Number", "")).strip()
        abroad = str(row.get("Abroad Mobile Number", "")).strip()

        issues = []

        # Check Primary & Whatsapp numbers for UAE (+971 or 971)
        for label, number in [("Primary", primary), ("Whatsapp", whatsapp)]:
            if number and not (number.startswith("+971") or number.startswith("971")):
                issues.append(f"{label} not UAE")

        # Check Abroad number based on Country
        if country in ["usa", "canada"]:
            if abroad and not (abroad.startswith("+1") or abroad.startswith("1")):
                issues.append("Abroad num not US/Canada format")
        elif country == "australia":
            if abroad and not (abroad.startswith("+61") or abroad.startswith("61")):
                issues.append("Abroad num not Australia format")
        elif country == "new zealand":
            if abroad and not (abroad.startswith("+64") or abroad.startswith("64")):
                issues.append("Abroad num not NZ format")

        return "✅ Correct" if not issues else f"❌ {', '.join(issues)}"

    if st.button("🚨 Run Checks"):
        with st.spinner("Scanning notes..."):
            # Sensitive words check
            df["Sensitive Word Flag"] = df["Student notes"].apply(detect_sensitive_words)

            # Student name check
            df["Incorrect Student Name Flag"] = df.apply(check_student_name, axis=1)

            # Contact details check
            df["Contact Details Check"] = df.apply(contact_details_check, axis=1)

            # Save results
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.success("✅ Scan Complete!")

            st.download_button(
                label="📥 Download Results",
                data=output,
                file_name="Sensitive_Words_Name_Contact_Check.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

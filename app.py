import streamlit as st
import pandas as pd
import openai
from io import BytesIO
import re

# Set OpenAI API Key securely
openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="Grammar Reviewer", layout="wide")
st.title("📝 Notes Grammar & Content Review")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, keep_default_na=False)

    def generate_prompt(row):
        return f"""
You are a grammar and content checker reviewing the “Notes on student” field from a monthly academic report.

--- Notes on student ---
{row['Student notes']}

Your task:

🔍 Carefully check the grammar, spelling, and content of the notes.

Return the following flags:

1. ❌ If the word **"student"** is NOT used (e.g., if a name is used instead), flag it.
2. ❌ If there are grammar or spelling issues, mention them briefly.
3. ❌ If the notes contain any sensitive keywords: **sex**, **drugs**, **alcohol**, **behaviour**, **behavioural**, **aggression**, **aggressive**, flag them.
4. ✅ If none of the above issues are found, return **No**.

---

Return your response in the format:

Grammar Flag: [Yes: <short explanation> / No]
"""

    # Extract Grammar Flag from response
    def extract_field(lines, label):
        for line in lines:
            match = re.match(rf".*{label}\s*:\s*(.*)", line.strip(), re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Error"

    def review_grammar(row):
        prompt = generate_prompt(row)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a careful grammar reviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            content = response['choices'][0]['message']['content']
            lines = content.strip().split("\n")

            grammar_flag = extract_field(lines, "Grammar Flag")
            return grammar_flag if grammar_flag != "No" else "No", "" if grammar_flag == "No" else grammar_flag

        except Exception as e:
            return "Error", str(e)

    if st.button("🔍 Perform Grammar Review"):
        with st.spinner("Reviewing notes for grammar issues..."):
            grammar_flags, grammar_remarks = [], []
            for _, row in df.iterrows():
                grammar_flag, remark = review_grammar(row)
                grammar_flags.append(grammar_flag)
                grammar_remarks.append(remark)

            df["Grammar Flag"] = grammar_flags
            df["Grammar Remark"] = grammar_remarks

            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.success("✅ Grammar Review Complete!")

            st.download_button(
                label="📥 Download Grammar-Checked File",
                data=output,
                file_name="Grammar_Reviewed_Students.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

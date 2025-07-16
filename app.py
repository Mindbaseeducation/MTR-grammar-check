import streamlit as st
import pandas as pd
import openai
from io import BytesIO
import re

# Set OpenAI API Key securely
openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="Grammar Reviewer", layout="wide")
st.title("📝 Student Notes - Grammar & Privacy Review")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, keep_default_na=False)

    def check_name_in_notes(student_name, notes):
        first_name = student_name.strip().split()[0]
        pattern = re.compile(rf"\b{re.escape(first_name)}\b", re.IGNORECASE)
        return bool(pattern.search(notes)), first_name

    def generate_prompt(notes):
        return f"""
You are a grammar and safety reviewer.

--- Notes to review ---
{notes}

Please check the following:

1. If there are grammar or spelling issues, flag them briefly.
2. If the notes contain any inappropriate or sensitive terms (e.g., sex, drugs, alcohol, behaviour, behavioral, aggression, aggressive), flag that.
3. If everything looks clean, say **No**.

Return the result in this format only:
Grammar Flag: [Yes: <short reason> / No]
"""

    def extract_field(lines, label):
        for line in lines:
            match = re.match(rf".*{label}\s*:\s*(.*)", line.strip(), re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Error"

    def review_grammar(row):
        notes = row["Student notes"]
        student_name = row["Student Name"]
        name_used, first_name = check_name_in_notes(student_name, notes)

        # If name is found in notes, we already flag it
        if name_used:
            return f"Yes: Student's first name '{first_name}' used instead of 'student'"

        # Else, ask the AI for grammar/sensitivity check
        prompt = generate_prompt(notes)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a strict grammar and content reviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            content = response['choices'][0]['message']['content']
            lines = content.strip().split("\n")
            grammar_flag = extract_field(lines, "Grammar Flag")
            return grammar_flag
        except Exception as e:
            return f"Error: {str(e)}"

    if st.button("🔍 Perform Grammar Review"):
        with st.spinner("Reviewing notes for grammar and name usage..."):
            grammar_flags = []
            for _, row in df.iterrows():
                flag = review_grammar(row)
                grammar_flags.append(flag)

            df["Grammar Flag"] = grammar_flags

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

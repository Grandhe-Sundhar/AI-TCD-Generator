

import streamlit as st
import pandas as pd
import docx
import io
import openai
from PyPDF2 import PdfReader
from openpyxl import Workbook

# 🔑 Set your OpenAI API key directly here
client = openai.OpenAI(api_key="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")

# --------- Utility Functions ---------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_file(uploaded_file):
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    elif filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    elif filename.endswith(".doc"):
        return None
    else:
        return None

def generate_test_cases_with_openai(requirements_text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a senior QA engineer who writes complete, high-quality test cases for business applications."
            },
            {
                "role": "user",
                "content": f"""
From the following BRD and FSD content, generate a **comprehensive set of test cases** that include:

- Functional test cases (core business logic)
- Non-functional test cases (performance, usability, security, etc.)
- Boundary value test cases (upper/lower limits, edge inputs)

Format the test cases in a **markdown table** with the following columns:

- Test Case ID
- Module / Feature Name
- Requirement Reference
- Test Type (Functional / Non-Functional / Boundary)
- Test Scenario
- Test Case Description
- Preconditions
- Test Data
- Expected Result
- Actual Result
- Pass/Fail
- Severity / Priority
- Comments / Notes

Here is the input text:
{requirements_text}
"""
            }
        ],
        temperature=0.2
    )
    return response.choices[0].message.content



# --------- Streamlit UI ---------
st.set_page_config(page_title="AI Powered TCD Generator", layout="wide")
st.markdown("""
    <style>
        .main {
            background-color: #f4f9ff;
        }
        .stButton>button {
            background-color: #4B8BBE;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.6em 2em;
        }
        .stDownloadButton>button {
            background-color: #10b981;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }
        .stTextArea textarea {
            font-size: 0.95em;
            line-height: 1.5;
        }
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>AI-Powered Test Case Document Generator</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Upload BRD or FSD ➝ Generate Test Cases ➝ Download Excel 📥</h4>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# File Upload
with st.container():
    uploaded_file = st.file_uploader("📎 Upload BRD or FSD Document", type=["pdf", "docx", "doc", "txt"])

    if uploaded_file:
        if uploaded_file.name.lower().endswith(".doc"):
            st.warning("⚠️ `.doc` files are not supported directly. Please convert to `.docx` and re-upload.")
        else:
            file_text = extract_text_from_file(uploaded_file)
            if not file_text:
                st.error("❌ Failed to extract text from the uploaded file.")
            else:
                with st.expander("📜 Extracted Requirement Text (Preview)", expanded=False):
                    st.text_area("Preview Text", file_text[:3000], height=300)

                if st.button("✨ Generate Test Cases"):
                    with st.spinner("🧠 Thinking deeply... generating test magic with AI ⚙️🪄"):
                        output_text = generate_test_cases_with_openai(file_text)

                    st.success("✅ Test Cases Generated Successfully!")
                    with st.expander("🔍 View AI Output Table (Markdown Format)", expanded=False):
                        st.text_area("GPT-4 Output", output_text, height=400)

                    try:
                        lines = output_text.strip().split("\n")
                        table_lines = [line for line in lines if "|" in line and "---" not in line]
                        headers = [col.strip() for col in table_lines[0].split("|")[1:-1]]
                        data = [row.split("|")[1:-1] for row in table_lines[1:] if len(row.split("|")[1:-1]) == len(headers)]
                        df = pd.DataFrame(data, columns=headers)

                        st.markdown("### 📊 Generated Test Case Table")
                        st.dataframe(df)

                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='TestCases')
                        st.download_button("📥 Download Excel", data=output.getvalue(), file_name="TCD_Generated.xlsx")
                    except Exception as e:
                        st.error(f"⚠️ Failed to parse test case table. Error: {e}")
    else:
        st.info("⬆️ Please upload a BRD or FSD document to begin.")

# Footer
st.markdown("""
    <hr style="margin-top: 3rem;"/>
    <div style="text-align: center; font-size: 16px; color: gray;">
        Made with ❤️ by <strong>Sundhar</strong> | Developed in USA 🇺🇸
    </div>
""", unsafe_allow_html=True)

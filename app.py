import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="MRI Research Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("MRI Research Assistant")
st.write(
    "AI-powered tool for analyzing MRI-related research papers and clinical-style reports."
)

st.warning(
    "This is a research and portfolio prototype only. It does not provide medical diagnosis."
)

uploaded_file = st.file_uploader(
    "Upload an MRI research paper or report PDF",
    type=["pdf"]
)

analysis_type = st.selectbox(
    "Choose analysis type",
    [
        "Research Paper Analysis",
        "MRI Report Summary",
        "CNN/HQNN Comparison Extraction"
    ]
)


def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def analyze_with_ai(text, analysis_type):
    if analysis_type == "Research Paper Analysis":
        prompt = f"""
        You are an AI research assistant specializing in medical imaging and MRI analysis.

        Analyze the research paper text below and extract:

        1. Research Aim
        2. Methodology
        3. Dataset Used
        4. AI/ML Model or Architecture
        5. Key Results
        6. Limitations
        7. Clinical Implications
        8. Relevance to CNN, HQNN, or medical image classification research

        Use clear academic language.
        Do not invent information. If something is not mentioned, write "Not clearly stated".

        Paper text:
        {text[:12000]}
        """

    elif analysis_type == "MRI Report Summary":
        prompt = f"""
        You are an AI assistant for summarizing MRI-related text.

        Summarize the MRI report text below into:

        1. Main Findings
        2. Mentioned Brain/Body Region
        3. Abnormal Observations
        4. Terms That May Need Clinical Review
        5. Plain-English Summary
        6. Safety Note

        Do not diagnose. Do not recommend treatment.

        MRI text:
        {text[:12000]}
        """

    else:
        prompt = f"""
        You are an AI research assistant helping with CNN vs HQNN literature review.

        From the text below, extract:

        1. Classical AI/CNN model used
        2. Quantum or hybrid quantum model used
        3. Dataset
        4. Performance metrics
        5. Accuracy or reported results
        6. Number of parameters, if mentioned
        7. Whether real quantum hardware or simulation was used
        8. Limitations related to quantum noise, qubits, cost, or hardware
        9. How this paper supports CNN vs HQNN comparison

        If information is missing, write "Not clearly stated".

        Text:
        {text[:12000]}
        """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


if uploaded_file is not None:
    st.success("PDF uploaded successfully.")

    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_pdf_text(uploaded_file)

    with st.expander("Preview extracted text"):
        st.write(extracted_text[:3000])

    if st.button("Analyze Document"):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OpenAI API key not found. Please add it to your .env file.")
        else:
            with st.spinner("Analyzing document with AI..."):
                result = analyze_with_ai(extracted_text, analysis_type)

            st.header("AI Analysis Result")
            st.markdown(result)
else:
    st.info("Upload a PDF to begin.")
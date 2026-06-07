import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

from ai_analyzer import analyze_with_ai
from pdf_utils import extract_pdf_text

load_dotenv()

APP_VERSION = "0.2.0"

st.set_page_config(
    page_title="MRI Research Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("MRI Research Assistant")
st.caption(f"Version {APP_VERSION}")
st.write("AI-powered dashboard for analyzing MRI-related research papers and medical imaging reports.")

st.warning("This is a research and portfolio prototype only. It does not provide medical diagnosis.")

with st.sidebar:
    st.header("Analysis Settings")

    analysis_type = st.selectbox(
        "Choose analysis type",
        [
            "Research Paper Analysis",
            "MRI Report Summary",
            "CNN/HQNN Comparison Extraction"
        ]
    )

    st.markdown("---")
    st.write("Upload a PDF paper or report to generate a structured AI research dashboard.")

uploaded_file = st.file_uploader(
    "Upload an MRI research paper or report PDF",
    type=["pdf"]
)

if uploaded_file is None:
    st.info("Upload a PDF to begin.")
    st.stop()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key not found. Please add it to your .env file.")
    st.stop()

st.success("PDF uploaded successfully.")

with st.spinner("Extracting text from PDF..."):
    extracted_text = extract_pdf_text(uploaded_file)

if not extracted_text.strip():
    st.error("No readable text was found in this PDF.")
    st.stop()

with st.expander("Preview extracted text"):
    st.write(extracted_text[:3000])

if st.button("Analyze Document"):
    with st.spinner("Analyzing document with AI..."):
        result = analyze_with_ai(extracted_text, analysis_type)

    st.header("Research Analysis Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Analysis Type", analysis_type)

    with col2:
        st.metric("Keywords Found", len(result.get("keywords", [])))

    with col3:
        hardware = result.get("metrics", {}).get("hardware_or_simulation", "Not clearly stated")
        st.metric("Hardware / Simulation", hardware if hardware else "Not clearly stated")

    st.subheader("Overview")

    card1, card2 = st.columns(2)

    with card1:
        st.markdown("### Research Aim")
        st.write(result.get("research_aim", "Not clearly stated"))

        st.markdown("### Dataset")
        st.write(result.get("dataset", "Not clearly stated"))

        st.markdown("### AI Model / Architecture")
        st.write(result.get("ai_model_architecture", "Not clearly stated"))

    with card2:
        st.markdown("### Methodology")
        st.write(result.get("methodology", "Not clearly stated"))

        st.markdown("### Key Results")
        st.write(result.get("key_results", "Not clearly stated"))

        st.markdown("### Limitations")
        st.write(result.get("limitations", "Not clearly stated"))

    st.subheader("Metrics Extracted")

    metrics = result.get("metrics", {})

    metrics_df = pd.DataFrame(
        [
            {"Metric": "Accuracy", "Value": metrics.get("accuracy", "Not clearly stated")},
            {"Metric": "F1 Score", "Value": metrics.get("f1_score", "Not clearly stated")},
            {"Metric": "Precision", "Value": metrics.get("precision", "Not clearly stated")},
            {"Metric": "Recall", "Value": metrics.get("recall", "Not clearly stated")},
            {"Metric": "Parameters", "Value": metrics.get("parameters", "Not clearly stated")},
            {"Metric": "Hardware / Simulation", "Value": metrics.get("hardware_or_simulation", "Not clearly stated")},
        ]
    )

    st.dataframe(metrics_df, use_container_width=True)

    st.subheader("Clinical and Research Interpretation")

    tab1, tab2, tab3 = st.tabs(
        ["Clinical Implications", "CNN/HQNN Relevance", "Overall Summary"]
    )

    with tab1:
        st.write(result.get("clinical_implications", "Not clearly stated"))

    with tab2:
        st.write(result.get("cnn_hqnn_relevance", "Not clearly stated"))

    with tab3:
        st.write(result.get("overall_summary", "Not clearly stated"))

    st.subheader("Keywords")

    keywords = result.get("keywords", [])

    if keywords:
        st.write(", ".join(keywords))
    else:
        st.write("No keywords extracted.")
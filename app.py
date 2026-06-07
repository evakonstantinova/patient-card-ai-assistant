import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

from ai_analyzer import analyze_with_ai
from pdf_utils import extract_pdf_text
from literature_search import search_semantic_scholar

load_dotenv()

APP_VERSION = "0.3.0"

st.set_page_config(
    page_title="ResearchIQ",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2.2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        opacity: 0.9;
        margin-bottom: 0.8rem;
    }

    .hero-note {
        font-size: 0.85rem;
        opacity: 0.7;
    }

    .upload-card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 1.4rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem;
        min-height: 100px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    }

    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 1.15rem;
        font-weight: 750;
        color: #0f172a;
    }

    .section-title {
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #0f172a;
    }

    .section-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.25rem;
        min-height: 210px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.7rem;
    }

    .card-text {
        font-size: 0.98rem;
        line-height: 1.6;
        color: #334155;
    }

    .footer-note {
        margin-top: 2rem;
        font-size: 0.85rem;
        color: #64748b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">ResearchIQ</div>
        <div class="hero-subtitle">
            AI-powered literature analysis for medical imaging and healthcare AI research.
        </div>
        <div class="hero-note">
            Version {APP_VERSION} · Research prototype only · Not intended for medical diagnosis
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="upload-card">
        <h3 style="margin-top:0;">Upload Research Document</h3>
        <p style="color:#64748b; margin-bottom:0;">
            Upload an MRI research paper, medical imaging report, or CNN/HQNN study in PDF format.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

upload_col, type_col = st.columns([2, 1])

with upload_col:
    uploaded_file = st.file_uploader(
        "PDF document",
        type=["pdf"],
        label_visibility="collapsed"
    )

with type_col:
    analysis_type = st.selectbox(
        "Analysis type",
        [
            "Research Paper Analysis",
            "MRI Report Summary",
            "CNN/HQNN Comparison Extraction"
        ]
    )

if uploaded_file is None:
    st.info("Upload a PDF to begin.")
    st.stop()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key not found. Please add it to your .env file.")
    st.stop()

with st.spinner("Extracting text from PDF..."):
    extracted_text = extract_pdf_text(uploaded_file)

if not extracted_text.strip():
    st.error("No readable text was found in this PDF.")
    st.stop()

with st.expander("Preview extracted text"):
    st.write(extracted_text[:3000])

if st.button("Analyze Document", use_container_width=True):
    with st.spinner("Analyzing document with AI..."):
        result = analyze_with_ai(extracted_text, analysis_type)

    st.session_state["analysis_result"] = result
    st.session_state["analysis_type"] = analysis_type

if "analysis_result" not in st.session_state:
    st.stop()

result = st.session_state["analysis_result"]
analysis_type = st.session_state["analysis_type"]
metrics = result.get("metrics", {})

st.markdown('<div class="section-title">Research Analysis Dashboard</div>', unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Analysis Type</div>
            <div class="metric-value">{analysis_type}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric_col2:
    research_gap = result.get("research_gap", "")
    gap_status = "Detected" if research_gap and research_gap != "Not clearly stated" else "Not clearly stated"

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Research Gap</div>
            <div class="metric-value">{gap_status}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric_col3:
    hardware = metrics.get("hardware_or_simulation", "Not clearly stated")
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Hardware / Simulation</div>
            <div class="metric-value">{hardware if hardware else "Not clearly stated"}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div class="section-title">Paper Overview</div>', unsafe_allow_html=True)

overview_col1, overview_col2 = st.columns(2)

with overview_col1:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Research Aim</div>
            <div class="card-text">{result.get("research_aim", "Not clearly stated")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Dataset</div>
            <div class="card-text">{result.get("dataset", "Not clearly stated")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with overview_col2:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Methodology</div>
            <div class="card-text">{result.get("methodology", "Not clearly stated")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">AI Model / Architecture</div>
            <div class="card-text">{result.get("ai_model_architecture", "Not clearly stated")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div class="section-title">Results and Metrics</div>', unsafe_allow_html=True)

result_col1, result_col2 = st.columns([1.2, 1])

with result_col1:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Key Results</div>
            <div class="card-text">{result.get("key_results", "Not clearly stated")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with result_col2:
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

    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Research Interpretation</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Limitations", "Clinical Implications", "CNN/HQNN Relevance", "Overall Summary"]
)

with tab1:
    st.write(result.get("limitations", "Not clearly stated"))

with tab2:
    st.write(result.get("clinical_implications", "Not clearly stated"))

with tab3:
    st.write(result.get("cnn_hqnn_relevance", "Not clearly stated"))

with tab4:
    st.write(result.get("overall_summary", "Not clearly stated"))

st.markdown('<div class="section-title">Literature Review Support</div>', unsafe_allow_html=True)

tab_gap, tab_note, tab_search = st.tabs(
    ["Research Gap", "Literature Review Note", "Find Related Papers"]
)

with tab_gap:
    st.write(result.get("research_gap", "Not clearly stated"))

with tab_note:
    st.write(result.get("literature_review_note", "Not clearly stated"))

with tab_search:
    search_queries = result.get("recommended_search_queries", [])

    if search_queries:
        selected_query = st.selectbox(
            "AI-generated search query",
            search_queries
        )

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            from_year = st.number_input(
                "From year",
                min_value=2015,
                max_value=2026,
                value=2021
            )

        with filter_col2:
            min_citations = st.number_input(
                "Minimum citations",
                min_value=0,
                max_value=1000,
                value=10
            )

        with filter_col3:
            result_limit = st.selectbox(
                "Number of papers",
                [5, 10, 15, 20],
                index=1
            )

        if st.button("Find Related Papers", use_container_width=True):
            with st.spinner("Searching related literature..."):
                papers = search_semantic_scholar(
                    selected_query,
                    limit=result_limit,
                    from_year=from_year,
                    min_citations=min_citations
                )

            if papers:
                related_papers = []

                for paper in papers:
                    authors = paper.get("authors", [])
                    author_names = ", ".join(
                        [author.get("name", "") for author in authors[:3]]
                    )

                    related_papers.append(
                        {
                            "Title": paper.get("title", "Not available"),
                            "Year": paper.get("year", "Not available"),
                            "Authors": author_names,
                            "Venue": paper.get("venue", "Not available"),
                            "Citations": paper.get("citationCount", 0),
                            "URL": paper.get("url", "")
                        }
                    )

                papers_df = pd.DataFrame(related_papers)
                st.dataframe(papers_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No related papers found with the selected filters.")
    else:
        st.info("No literature search queries were generated.")

st.markdown(
    """
    <div class="footer-note">
        This dashboard is generated using AI and should be reviewed critically.
        It is designed for research support, not clinical decision-making.
    </div>
    """,
    unsafe_allow_html=True
)
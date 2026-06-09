import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

from ai_analyzer import analyze_with_ai
from pdf_utils import extract_pdf_text
from literature_search import search_semantic_scholar

load_dotenv()

APP_VERSION = "0.5.0"

DEFAULT_SEARCH_QUERIES = [
    "medical imaging MRI deep learning classification",
    "CNN MRI classification medical imaging",
    "hybrid quantum neural network MRI classification",
    "quantum machine learning medical imaging",
    "CNN vs HQNN healthcare AI"
]

st.set_page_config(
    page_title="ResearchIQ",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }

    .hero {
        background: linear-gradient(135deg, #111827 0%, #1e293b 55%, #334155 100%);
        padding: 2.4rem;
        border-radius: 26px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16);
    }

    .hero-title {
        font-size: 3.1rem;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1.08rem;
        opacity: 0.92;
        max-width: 760px;
        line-height: 1.6;
        margin-bottom: 0.9rem;
    }

    .hero-note {
        display: inline-block;
        font-size: 0.82rem;
        opacity: 0.85;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 999px;
        padding: 0.45rem 0.75rem;
    }

    .upload-card, .metric-card, .section-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
    }

    .upload-card {
        background: #f8fafc;
        padding: 1.35rem;
        margin-bottom: 1.1rem;
    }

    .metric-card {
        min-height: 118px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .metric-label {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.55rem;
    }

    .metric-value {
        font-size: 1.08rem;
        font-weight: 800;
        line-height: 1.35;
        color: #0f172a;
    }

    .section-title {
        font-size: 1.75rem;
        font-weight: 850;
        letter-spacing: -0.035em;
        margin-top: 2.1rem;
        margin-bottom: 1rem;
        color: #0f172a;
    }

    .section-card {
        padding: 1.35rem;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 1.02rem;
        font-weight: 850;
        color: #0f172a;
        margin-bottom: 0.65rem;
    }

    .card-text {
        font-size: 0.97rem;
        line-height: 1.65;
        color: #334155;
    }

    .footer-note {
        margin-top: 2rem;
        font-size: 0.85rem;
        color: #64748b;
        text-align: center;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def clean_value(value, fallback="Not clearly stated"):
    if value is None:
        return fallback
    value = str(value).strip()
    return value if value else fallback


def short_value(value, limit=95):
    value = clean_value(value)
    if len(value) > limit:
        return value[:limit].rstrip() + "..."
    return value


st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">ResearchIQ</div>
        <div class="hero-subtitle">
            Upload a research paper and generate a structured summary, extracted methods and results,
            literature review notes, and related-paper search queries.
        </div>
        <div class="hero-note">
            Version {APP_VERSION} · Research support tool · Not for medical diagnosis
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="upload-card">
        <h3 style="margin-top:0; margin-bottom:0.35rem;">Upload research document</h3>
        <p style="color:#64748b; margin-bottom:0; line-height:1.55;">
            Best results come from full-text PDF papers with methodology, results, and conclusion sections.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "PDF document",
    type=["pdf"],
    label_visibility="collapsed"
)

generate_summary = st.button(
    "Generate Research Summary",
    use_container_width=True
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
    st.write(extracted_text[:5000])

if generate_summary:
    with st.spinner("Analyzing the full paper structure with AI..."):
        result = analyze_with_ai(extracted_text, "Research Paper Analysis")
    st.session_state["analysis_result"] = result

if "analysis_result" not in st.session_state:
    st.stop()

result = st.session_state["analysis_result"]
st.write("Research type:", result.get("research_type", "Not found"))
metrics = result.get("metrics", {}) or {}

st.markdown('<div class="section-title">Research Analysis Dashboard</div>', unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Paper Focus</div>
            <div class="metric-value">{short_value(result.get("research_aim"), 105)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Model / Architecture</div>
            <div class="metric-value">{short_value(result.get("ai_model_architecture"), 105)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric_col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Dataset</div>
            <div class="metric-value">{short_value(result.get("dataset"), 105)}</div>
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
            <div class="card-text">{clean_value(result.get("research_aim"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Dataset</div>
            <div class="card-text">{clean_value(result.get("dataset"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with overview_col2:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Methodology</div>
            <div class="card-text">{clean_value(result.get("methodology"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">AI Model / Architecture</div>
            <div class="card-text">{clean_value(result.get("ai_model_architecture"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div class="section-title">Results and Metrics</div>', unsafe_allow_html=True)

result_col1, result_col2 = st.columns([1.25, 1])

with result_col1:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Key Results</div>
            <div class="card-text">{clean_value(result.get("key_results"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with result_col2:
    metrics_df = pd.DataFrame(
        [
            {"Metric": "Accuracy", "Value": clean_value(metrics.get("accuracy"))},
            {"Metric": "F1 Score", "Value": clean_value(metrics.get("f1_score"))},
            {"Metric": "Precision", "Value": clean_value(metrics.get("precision"))},
            {"Metric": "Recall", "Value": clean_value(metrics.get("recall"))},
            {"Metric": "Parameters", "Value": clean_value(metrics.get("parameters"))},
            {"Metric": "Hardware / Simulation", "Value": clean_value(metrics.get("hardware_or_simulation"))},
        ]
    )
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Literature Review Support</div>', unsafe_allow_html=True)

tab_note, tab_search = st.tabs([
    "Research Gap & Literature Note",
    "Find Similar Papers"
])

with tab_note:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Research Gap</div>
            <div class="card-text">{clean_value(result.get("research_gap"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Literature Review Note</div>
            <div class="card-text">{clean_value(result.get("literature_review_note"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab_search:
    search_queries = result.get("recommended_search_queries", []) or DEFAULT_SEARCH_QUERIES

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
            value=2018
        )

    with filter_col2:
        min_citations = st.number_input(
            "Minimum citations",
            min_value=0,
            max_value=1000,
            value=0
        )

    with filter_col3:
        result_limit = st.selectbox(
            "Number of papers",
            [5, 10, 15, 20],
            index=1
        )

    if st.button("Search Related Literature", use_container_width=True):
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
                authors = paper.get("authors", []) or []
                author_names = ", ".join(
                    [author.get("name", "") for author in authors[:3] if author.get("name")]
                )

                related_papers.append(
                    {
                        "Title": paper.get("title", "Not available"),
                        "Year": paper.get("year", "Not available"),
                        "Authors": author_names if author_names else "Not available",
                        "Venue": paper.get("venue", "Not available"),
                        "Citations": paper.get("citationCount", 0),
                        "URL": paper.get("url", "")
                    }
                )

            papers_df = pd.DataFrame(related_papers)
            st.dataframe(papers_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No related papers found with the selected filters. Try an earlier year or broader query.")

st.markdown(
    """
    <div class="footer-note">
        AI-generated research support output. Review all summaries and related-paper results critically before using them academically.
    </div>
    """,
    unsafe_allow_html=True
)

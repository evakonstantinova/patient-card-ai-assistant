import os
import html
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

from ai_analyzer import analyze_with_ai
from pdf_utils import extract_pdf_text
from literature_search import search_semantic_scholar

load_dotenv()

DEFAULT_SEARCH_QUERIES = [
    "academic research methodology",
    "literature review related studies",
    "empirical research findings",
    "research limitations future work",
    "systematic review related topic"
]

st.set_page_config(
    page_title="ResearchIQ",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    :root {
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
        --soft: #f1f5f9;
        --border: #e5e7eb;
        --shadow: 0 10px 28px rgba(15, 23, 42, 0.055);
        --radius: 22px;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.25rem;
        padding-bottom: 2.5rem;
    }

    .hero {
        background: linear-gradient(135deg, #111827 0%, #1e293b 55%, #334155 100%);
        padding: 3rem 2.5rem;
        border-radius: 30px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16);
        text-align: center;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -0.055em;
        margin-bottom: 0.75rem;
        line-height: 1;
    }

    .hero-subtitle {
        font-size: 1.08rem;
        opacity: 0.92;
        max-width: 820px;
        margin: 0 auto;
        line-height: 1.75;
    }

    .upload-card,
    .metric-card,
    .section-card,
    .detail-panel,
    .papers-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
    }

    .upload-card {
        background: #f8fafc;
        padding: 1.35rem 1.45rem;
        margin-bottom: 1.1rem;
    }

    .upload-card h3 {
        margin-top: 0;
        margin-bottom: 0.35rem;
        font-size: 1.08rem;
        font-weight: 850;
        color: var(--text);
        letter-spacing: -0.02em;
    }

    .upload-card p {
        color: var(--muted);
        margin-bottom: 0;
        line-height: 1.6;
        font-size: 0.96rem;
    }

    .metric-card {
        min-height: 170px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
    }

    .metric-label,
    .detail-label {
        font-size: 0.76rem;
        color: var(--muted);
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.055em;
    }

    .metric-value {
        font-size: 1.02rem;
        font-weight: 740;
        line-height: 1.5;
        color: var(--text);
        white-space: normal;
        overflow-wrap: break-word;
    }

    .section-title {
        font-size: 1.72rem;
        font-weight: 900;
        letter-spacing: -0.045em;
        margin-top: 2.15rem;
        margin-bottom: 1rem;
        color: var(--text);
    }

    .section-card {
        padding: 1.35rem;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 1.02rem;
        font-weight: 875;
        color: var(--text);
        margin-bottom: 0.7rem;
        letter-spacing: -0.015em;
    }

    .card-text {
        font-size: 0.97rem;
        line-height: 1.7;
        color: #334155;
        white-space: normal;
        overflow-wrap: break-word;
    }

    .detail-panel {
        overflow: hidden;
        margin-bottom: 1rem;
    }

    .detail-row {
        display: grid;
        grid-template-columns: 35% 65%;
        border-bottom: 1px solid var(--border);
        min-height: 64px;
    }

    .detail-row:last-child {
        border-bottom: none;
    }

    .detail-label {
        background: #f8fafc;
        padding: 1rem;
        display: flex;
        align-items: flex-start;
        line-height: 1.45;
    }

    .detail-value {
        padding: 1rem;
        font-size: 0.96rem;
        line-height: 1.65;
        color: var(--text);
        overflow-wrap: break-word;
        white-space: normal;
    }

    .papers-card {
        padding: 1rem;
        margin-top: 1rem;
        overflow-x: auto;
    }

    .papers-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 0.92rem;
    }

    .papers-table th {
        background: #f8fafc;
        color: #475569;
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.055em;
        text-align: left;
        padding: 0.85rem;
        border-bottom: 1px solid var(--border);
    }

    .papers-table td {
        padding: 0.9rem 0.85rem;
        border-bottom: 1px solid var(--border);
        color: #334155;
        line-height: 1.5;
        vertical-align: top;
        overflow-wrap: anywhere;
    }

    .papers-table tr:last-child td {
        border-bottom: none;
    }

    .papers-table tr:hover td {
        background: #f8fafc;
    }

    .papers-table a {
        color: #2563eb;
        font-weight: 750;
        text-decoration: none;
    }

    .papers-table a:hover {
        text-decoration: underline;
    }

    .footer-note {
        margin-top: 2rem;
        font-size: 0.85rem;
        color: var(--muted);
        text-align: center;
        line-height: 1.6;
    }

    div[data-testid="stButton"] button {
        border-radius: 14px;
        font-weight: 800;
    }

    div[data-baseweb="select"] {
        border-radius: 14px;
    }

    @media (max-width: 900px) {
        .hero {
            padding: 2.25rem 1.5rem;
        }

        .hero-title {
            font-size: 2.6rem;
        }

        .detail-row {
            grid-template-columns: 1fr;
        }

        .detail-label {
            border-bottom: 1px solid var(--border);
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


def clean_value(value, fallback="Not clearly stated"):
    if value is None:
        return fallback

    value = str(value).strip()

    if not value or value.lower() in ["none", "nan", "n/a", "not available", ""]:
        return fallback

    return value


def html_value(value, fallback="Not clearly stated"):
    return html.escape(clean_value(value, fallback))


def is_ai_paper(result):
    research_type = clean_value(result.get("research_type"), "").lower()
    architecture = clean_value(result.get("ai_model_architecture"), "").lower()

    if "ai" in research_type or "machine learning" in research_type:
        return True

    if architecture and architecture not in ["not applicable", "not clearly stated", "n/a", "none"]:
        return True

    return False


def get_results_title(research_type):
    research_type = clean_value(research_type).lower()

    if "ai" in research_type or "machine learning" in research_type:
        return "Model Results"
    if "qualitative" in research_type:
        return "Main Themes / Findings"
    if "systematic literature review" in research_type:
        return "Main Findings"
    if "mixed methods" in research_type:
        return "Main Findings"

    return "Key Results"


def build_study_details(result, metrics):
    research_type = clean_value(result.get("research_type"))

    if "AI / Machine Learning" in research_type:
        return [
            ("Evaluation Metrics", f"Accuracy: {clean_value(metrics.get('accuracy'))}; F1: {clean_value(metrics.get('f1_score'))}; Precision: {clean_value(metrics.get('precision'))}; Recall: {clean_value(metrics.get('recall'))}"),
            ("Model Complexity", clean_value(metrics.get("parameters"))),
            ("Execution Setting", clean_value(metrics.get("hardware_or_simulation"))),
            ("Limitations", clean_value(result.get("limitations"))),
        ]

    if "Qualitative" in research_type:
        return [
            ("Analysis Approach", clean_value(result.get("methodology"))),
            ("Limitations", clean_value(result.get("limitations"))),
            ("Research Gap", clean_value(result.get("research_gap"))),
        ]

    if "Survey" in research_type:
        return [
            ("Measured Outcomes", clean_value(result.get("key_results"))),
            ("Analysis Method", clean_value(result.get("methodology"))),
            ("Limitations", clean_value(result.get("limitations"))),
            ("Research Gap", clean_value(result.get("research_gap"))),
        ]

    if "Systematic Literature Review" in research_type:
        return [
            ("Evidence Base", clean_value(result.get("dataset"))),
            ("Synthesis Method", clean_value(result.get("methodology"))),
            ("Limitations", clean_value(result.get("limitations"))),
            ("Research Gap", clean_value(result.get("research_gap"))),
        ]

    if "Mixed Methods" in research_type:
        return [
            ("Methods Integration", clean_value(result.get("methodology"))),
            ("Limitations", clean_value(result.get("limitations"))),
            ("Research Gap", clean_value(result.get("research_gap"))),
        ]

    return [
        ("Limitations", clean_value(result.get("limitations"))),
        ("Research Gap", clean_value(result.get("research_gap"))),
    ]


def render_card(title, body):
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">{html.escape(str(title))}</div>
            <div class="card-text">{html_value(body)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html_value(value)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_detail_panel(rows):
    rows_html = ""

    for label, value in rows:
        rows_html += f"""
        <div class="detail-row">
            <div class="detail-label">{html.escape(str(label))}</div>
            <div class="detail-value">{html_value(value)}</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="detail-panel">
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_papers_table(papers_df):
    st.markdown(
        f"""
        <div class="papers-card">
            {papers_df.to_html(
                escape=False,
                index=False,
                classes="papers-table"
            )}
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">ResearchIQ</div>
        <div class="hero-subtitle">
            Your personal AI research assistant for analyzing papers, exploring literature,
            generating research insights, and discovering relevant academic publications.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="upload-card">
        <h3>Upload research document</h3>
        <p>Best results come from full-text PDF papers with methodology, results, and conclusion sections.</p>
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
    st.error("No readable text was found in this PDF. It may be scanned or image-based.")
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
metrics = result.get("metrics", {}) or {}
research_type = clean_value(result.get("research_type"))

st.markdown('<div class="section-title">Research Analysis Dashboard</div>', unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    render_metric_card("Paper Topic", result.get("paper_topic"))

with metric_col2:
    render_metric_card("Research Type", research_type)

with metric_col3:
    render_metric_card("Dataset / Sample", result.get("dataset"))

st.markdown('<div class="section-title">Paper Overview</div>', unsafe_allow_html=True)

overview_col1, overview_col2 = st.columns(2)

with overview_col1:
    render_card("Research Aim", result.get("research_aim"))
    render_card("Methodology", result.get("methodology"))

with overview_col2:
    render_card("Dataset / Sample", result.get("dataset"))

    if is_ai_paper(result):
        render_card("AI Model / Architecture", clean_value(result.get("ai_model_architecture"), "Not applicable"))
    else:
        render_card("Overall Summary", result.get("overall_summary"))

st.markdown('<div class="section-title">Results and Study Details</div>', unsafe_allow_html=True)

result_col1, result_col2 = st.columns([1.25, 1])

with result_col1:
    render_card(get_results_title(research_type), result.get("key_results"))

with result_col2:
    render_detail_panel(build_study_details(result, metrics))

st.markdown(
    '<div class="section-title">Find Similar Papers</div>',
    unsafe_allow_html=True
)

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
                    "Title": html.escape(str(paper.get("title", "Not available"))),
                    "Year": paper.get("year", "Not available"),
                    "Authors": html.escape(author_names if author_names else "Not available"),
                    "Venue": html.escape(str(paper.get("venue", "Not available"))),
                    "Citations": paper.get("citationCount", 0),
                    "Source": html.escape(str(paper.get("source", "Not available"))),
                    "Link": paper.get("link", html.escape(str(paper.get("url", ""))))
                }
            )

        papers_df = pd.DataFrame(related_papers)
        render_papers_table(papers_df)

    else:
        st.warning(
            "No related papers found with the selected filters. Try an earlier year or broader query."
        )

st.markdown(
    """
    <div class="footer-note">
        AI-generated research support output. Review all summaries and related-paper results critically before using them academically.
    </div>
    """,
    unsafe_allow_html=True
)

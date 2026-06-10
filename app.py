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

    .hero {
    background: linear-gradient(135deg, #111827 0%, #1e293b 55%, #334155 100%);
    padding: 3rem;
    border-radius: 28px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16);
    text-align: center;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    margin-bottom: 0.7rem;
}

.hero-subtitle {
    font-size: 1.1rem;
    opacity: 0.92;
    max-width: 850px;
    margin: 0 auto;
    line-height: 1.7;
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
        min-height: 175px;
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
        font-size: 1.02rem;
        font-weight: 760;
        line-height: 1.45;
        color: #0f172a;
        white-space: normal;
        overflow-wrap: break-word;
        word-break: normal;
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
        white-space: normal;
        overflow-wrap: break-word;
    }
     
     .detail-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
}

.detail-label {
    font-size: 0.78rem;
    font-weight: 800;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.45rem;
}

.detail-value {
    font-size: 0.98rem;
    line-height: 1.6;
    color: #0f172a;
    overflow-wrap: break-word;
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

    if not value:
        return fallback

    return value


def html_value(value, fallback="Not clearly stated"):
    return html.escape(clean_value(value, fallback))


def is_not_applicable(value):
    value = clean_value(value, "").lower()
    return value in ["", "not applicable", "not clearly stated", "n/a", "none"]


def is_ai_paper(result):
    research_type = clean_value(result.get("research_type"), "").lower()
    architecture = clean_value(result.get("ai_model_architecture"), "").lower()

    if "ai" in research_type or "machine learning" in research_type:
        return True

    if architecture and architecture not in ["not applicable", "not clearly stated", "n/a", "none"]:
        return True

    return False


def build_study_details(result, metrics):
    research_type = clean_value(result.get("research_type"))

    if "AI / Machine Learning" in research_type:
        return [
            ("Evaluation Metrics", f"Accuracy: {clean_value(metrics.get('accuracy'))}; F1: {clean_value(metrics.get('f1_score'))}; Precision: {clean_value(metrics.get('precision'))}; Recall: {clean_value(metrics.get('recall'))}"),
            ("Model Complexity", clean_value(metrics.get("parameters"), "Not clearly stated")),
            ("Execution Setting", clean_value(metrics.get("hardware_or_simulation"), "Not clearly stated")),
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
metrics = result.get("metrics", {}) or {}
research_type = clean_value(result.get("research_type"))

st.markdown('<div class="section-title">Research Analysis Dashboard</div>', unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Paper Topic</div>
            <div class="metric-value">{html_value(result.get("paper_topic"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Research Type</div>
            <div class="metric-value">{html.escape(research_type)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric_col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Dataset / Sample</div>
            <div class="metric-value">{html_value(result.get("dataset"))}</div>
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
            <div class="card-text">{html_value(result.get("research_aim"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Methodology</div>
            <div class="card-text">{html_value(result.get("methodology"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with overview_col2:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Dataset / Sample</div>
            <div class="card-text">{html_value(result.get("dataset"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if is_ai_paper(result):
        st.markdown(
            f"""
            <div class="section-card">
                <div class="card-title">AI Model / Architecture</div>
                <div class="card-text">{html_value(result.get("ai_model_architecture"), "Not applicable")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="card-title">Overall Summary</div>
                <div class="card-text">{html_value(result.get("overall_summary"))}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown('<div class="section-title">Results and Study Details</div>', unsafe_allow_html=True)

result_col1, result_col2 = st.columns([1.25, 1])

with result_col1:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">Key Results</div>
            <div class="card-text">{html_value(result.get("key_results"))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with result_col2:
    study_details = build_study_details(result, metrics)

    for detail, value in study_details:
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">{html.escape(str(detail))}</div>
                <div class="detail-value">{html.escape(str(value))}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

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
                    "Title": paper.get("title", "Not available"),
                    "Year": paper.get("year", "Not available"),
                    "Authors": author_names if author_names else "Not available",
                    "Venue": paper.get("venue", "Not available"),
                    "Citations": paper.get("citationCount", 0),
                    "Source": paper.get("source", "Not available"),
                    "URL": paper.get("url", "")
                }
            )

        papers_df = pd.DataFrame(related_papers)

        st.dataframe(
            papers_df,
            use_container_width=True,
            hide_index=True,
            height=450
        )

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

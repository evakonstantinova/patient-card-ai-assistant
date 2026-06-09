import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_SEARCH_QUERIES = [
    "academic research methodology",
    "literature review related studies",
    "empirical research findings",
    "research limitations future work",
    "systematic review related topic"
]

DEFAULT_METRICS = {
    "accuracy": "",
    "f1_score": "",
    "precision": "",
    "recall": "",
    "parameters": "",
    "hardware_or_simulation": ""
}


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please create a .env file and add your OpenAI API key."
        )

    return OpenAI(api_key=api_key)


def build_document_sample(text, max_chars=45000):
    text = text.strip()

    if len(text) <= max_chars:
        return text

    first_part = text[:18000]
    middle_start = max((len(text) // 2) - 7000, 0)
    middle_part = text[middle_start:middle_start + 14000]
    last_part = text[-13000:]

    return f"""
[BEGINNING OF PAPER]
{first_part}

[MIDDLE OF PAPER]
{middle_part}

[END OF PAPER]
{last_part}
"""


def fallback_response(content="Could not parse AI response."):
    return {
        "paper_topic": "Could not parse AI response.",
        "research_type": "Could not parse AI response.",
        "research_aim": content,
        "dataset": "Could not parse AI response.",
        "methodology": "Could not parse AI response.",
        "ai_model_architecture": "Could not parse AI response.",
        "key_results": content,
        "limitations": "Could not parse AI response.",
        "research_gap": "Could not parse AI response.",
        "literature_review_note": "Could not parse AI response.",
        "recommended_search_queries": DEFAULT_SEARCH_QUERIES,
        "metrics": DEFAULT_METRICS,
        "overall_summary": content
    }


def analyze_with_ai(text, analysis_type):
    client = get_openai_client()
    document_sample = build_document_sample(text)

    prompt = f"""
You are an AI research assistant.

Analyze the uploaded academic paper and return ONLY valid JSON.

Important:
- First identify the actual topic of the uploaded paper.
- Identify the research type.
- Choose exactly one research type from this list:
  "AI / Machine Learning",
  "Experimental / Quantitative",
  "Qualitative / Interview-based",
  "Survey-based",
  "Systematic Literature Review",
  "Mixed Methods",
  "Theoretical / Conceptual",
  "Other".
- Do not assume the paper is about MRI, CNNs, HQNNs, healthcare, or medical imaging unless the document clearly says so.
- Do not analyze only the abstract or introduction.
- Use the beginning, middle, and end of the document.
- Look for research aim, topic, dataset/sample, methodology, results, limitations, conclusion, and future work.
- Only fill AI model architecture and AI metrics if the paper actually uses an AI or machine learning model.
- If the paper is not about AI or machine learning, write "Not applicable" for AI model architecture and AI metrics.
- Do not include markdown.
- Do not include explanations outside the JSON.
- Do not invent information.
- If something is missing, write "Not clearly stated".
- The field "recommended_search_queries" MUST contain 5 search queries.
- The 5 search queries MUST be based on the actual topic of the uploaded paper.
- Do not use generic MRI, CNN, HQNN, healthcare, or medical imaging queries unless the uploaded paper is actually about those topics.

Return this exact JSON structure:

{{
  "paper_topic": "",
  "research_type": "",
  "research_aim": "",
  "dataset": "",
  "methodology": "",
  "ai_model_architecture": "",
  "key_results": "",
  "limitations": "",
  "research_gap": "",
  "literature_review_note": "",
  "recommended_search_queries": [
    "",
    "",
    "",
    "",
    ""
  ],
  "metrics": {{
    "accuracy": "",
    "f1_score": "",
    "precision": "",
    "recall": "",
    "parameters": "",
    "hardware_or_simulation": ""
  }},
  "overall_summary": ""
}}

Analysis type: {analysis_type}

Document text:
{document_sample}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        data.setdefault("research_type", "Not clearly stated")

        if not data.get("recommended_search_queries"):
            data["recommended_search_queries"] = DEFAULT_SEARCH_QUERIES

        if not isinstance(data.get("metrics"), dict):
            data["metrics"] = DEFAULT_METRICS
        else:
            for key, value in DEFAULT_METRICS.items():
                data["metrics"].setdefault(key, value)

        return data

    except Exception as e:
        return fallback_response(f"AI analysis failed: {e}")
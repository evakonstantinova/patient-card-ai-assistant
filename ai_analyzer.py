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


def build_document_sample(text, max_chars=50000):
    text = text.strip()

    if len(text) <= max_chars:
        return text

    first_part = text[:18000]
    middle_start = max((len(text) // 2) - 8000, 0)
    middle_part = text[middle_start:middle_start + 16000]
    last_part = text[-16000:]

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
You are an advanced academic research assistant.

Analyze the uploaded academic paper and return ONLY valid JSON.

Your task:
- Identify the actual topic of the paper.
- Identify the correct research type.
- Extract the research aim, dataset/sample, methodology, key findings, limitations, and research gap.
- Generate useful literature search queries based on the actual paper topic.
- Do not assume the paper is about AI, healthcare, MRI, CNNs, HQNNs, or medicine unless the document clearly says so.

Research type classification:
Choose exactly ONE from this list:
- "AI / Machine Learning"
- "Experimental / Quantitative"
- "Qualitative / Interview-based"
- "Survey-based"
- "Systematic Literature Review"
- "Mixed Methods"
- "Theoretical / Conceptual"
- "Other"

Rules by research type:
- For AI / Machine Learning papers: focus on dataset, model architecture, training setup, evaluation metrics, baseline comparison, and hardware/software setup.
- For Experimental / Quantitative papers: focus on sample, variables, statistical methods, measured outcomes, significance, and numerical results.
- For Survey-based papers: focus on respondents/sample size, survey instrument, variables measured, statistical tests, and main quantitative findings.
- For Qualitative / Interview-based papers: focus on participants, interview/focus group method, coding approach, thematic analysis, and main themes.
- For Systematic Literature Review papers: focus on number of studies, databases searched, inclusion/exclusion criteria, PRISMA/screening method, synthesis approach, and major themes.
- For Mixed Methods papers: separate quantitative and qualitative components clearly.
- For Theoretical / Conceptual papers: focus on concepts, framework, argument, contribution, and limitations.

Important:
- Do not analyze only the abstract or introduction.
- Use the beginning, middle, and end of the document.
- Do not invent information.
- If something is missing, write "Not clearly stated".
- If a field does not apply to the paper, write "Not applicable".
- Do not include markdown.
- Do not include explanations outside the JSON.
- Keep answers concise but specific.
- Do not write long paragraphs unless needed.
- The field "recommended_search_queries" MUST contain exactly 5 search queries.

Search query rules:
Generate exactly 5 useful search queries:
1. One exact-topic query.
2. One broader-topic query.
3. One methodology-based query.
4. One population/sample-based query.
5. One research-gap or future-research query.

Do not use generic MRI, CNN, HQNN, healthcare, or medical imaging queries unless the uploaded paper is actually about those topics.

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
            temperature=0.15,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        data.setdefault("paper_topic", "Not clearly stated")
        data.setdefault("research_type", "Not clearly stated")
        data.setdefault("research_aim", "Not clearly stated")
        data.setdefault("dataset", "Not clearly stated")
        data.setdefault("methodology", "Not clearly stated")
        data.setdefault("ai_model_architecture", "Not applicable")
        data.setdefault("key_results", "Not clearly stated")
        data.setdefault("limitations", "Not clearly stated")
        data.setdefault("research_gap", "Not clearly stated")
        data.setdefault("literature_review_note", "Not clearly stated")
        data.setdefault("overall_summary", "Not clearly stated")

        if not isinstance(data.get("recommended_search_queries"), list):
            data["recommended_search_queries"] = DEFAULT_SEARCH_QUERIES

        data["recommended_search_queries"] = [
            q for q in data["recommended_search_queries"]
            if isinstance(q, str) and q.strip()
        ][:5]

        while len(data["recommended_search_queries"]) < 5:
            data["recommended_search_queries"].append(DEFAULT_SEARCH_QUERIES[len(data["recommended_search_queries"])])

        if not isinstance(data.get("metrics"), dict):
            data["metrics"] = DEFAULT_METRICS.copy()
        else:
            for key, value in DEFAULT_METRICS.items():
                data["metrics"].setdefault(key, value)

        if data.get("research_type") != "AI / Machine Learning":
            data["ai_model_architecture"] = data.get("ai_model_architecture") or "Not applicable"

            for key in ["accuracy", "f1_score", "precision", "recall", "parameters", "hardware_or_simulation"]:
                if not data["metrics"].get(key):
                    data["metrics"][key] = "Not applicable"

        return data

    except Exception as e:
        return fallback_response(f"AI analysis failed: {e}")
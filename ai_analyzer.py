import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_with_ai(text, analysis_type):
    prompt = f"""
You are an AI research assistant specializing in medical imaging, MRI analysis, CNNs, HQNNs, and healthcare AI.

Analyze the uploaded document and return ONLY valid JSON.

Do not include markdown.
Do not include explanations outside the JSON.
Do not invent information.
If something is missing, write "Not clearly stated".

The field "recommended_search_queries" MUST contain 5 search queries.
Do not leave it empty.

Return this exact JSON structure:

{{
  "research_aim": "",
  "dataset": "",
  "methodology": "",
  "ai_model_architecture": "",
  "key_results": "",
  "limitations": "",
  "clinical_implications": "",
  "cnn_hqnn_relevance": "",
  "research_gap": "",
  "literature_review_note": "",
  "recommended_search_queries": [
    "medical imaging MRI deep learning classification",
    "CNN MRI classification medical imaging",
    "hybrid quantum neural network MRI classification",
    "quantum machine learning medical imaging",
    "CNN vs HQNN healthcare AI"
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
{text[:12000]}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)

        if not data.get("recommended_search_queries"):
            data["recommended_search_queries"] = [
                "medical imaging MRI deep learning classification",
                "CNN MRI classification medical imaging",
                "hybrid quantum neural network MRI classification",
                "quantum machine learning medical imaging",
                "CNN vs HQNN healthcare AI"
            ]

        return data

    except json.JSONDecodeError:
        return {
            "research_aim": "Could not parse AI response.",
            "dataset": "Could not parse AI response.",
            "methodology": "Could not parse AI response.",
            "ai_model_architecture": "Could not parse AI response.",
            "key_results": content,
            "limitations": "Could not parse AI response.",
            "clinical_implications": "Could not parse AI response.",
            "cnn_hqnn_relevance": "Could not parse AI response.",
            "research_gap": "Could not parse AI response.",
            "literature_review_note": "Could not parse AI response.",
            "recommended_search_queries": [
                "medical imaging MRI deep learning classification",
                "CNN MRI classification medical imaging",
                "hybrid quantum neural network MRI classification",
                "quantum machine learning medical imaging",
                "CNN vs HQNN healthcare AI"
            ],
            "metrics": {
                "accuracy": "",
                "f1_score": "",
                "precision": "",
                "recall": "",
                "parameters": "",
                "hardware_or_simulation": ""
            },
            "overall_summary": content
        }
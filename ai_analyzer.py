import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_with_ai(text, analysis_type):
    prompt = f"""
You are an AI research assistant specializing in MRI, medical imaging, CNNs, HQNNs, quantum machine learning, and healthcare AI.

Analyze the uploaded document and return ONLY valid JSON.

Do not include markdown.
Do not include explanations outside the JSON.
Do not invent information.
If something is missing, write "Not clearly stated".

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
  "recommended_search_queries": [],
  "metrics": {{
    "accuracy": "",
    "f1_score": "",
    "precision": "",
    "recall": "",
    "parameters": "",
    "hardware_or_simulation": ""
  }},
  "keywords": [],
  "overall_summary": ""
}}

Instructions:
- Generate 3 to 5 academic search queries for finding related recent literature.
- Search queries should focus on MRI, medical imaging, CNN, HQNN, quantum machine learning, classification, and healthcare AI when relevant.
- Generate a clear research gap statement.
- Generate a literature review note explaining how this paper could be used in a literature review.
- Keep all answers concise and academic.

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
        return json.loads(content)
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
            "recommended_search_queries": [],
            "metrics": {
                "accuracy": "",
                "f1_score": "",
                "precision": "",
                "recall": "",
                "parameters": "",
                "hardware_or_simulation": ""
            },
            "keywords": [],
            "overall_summary": content
        }
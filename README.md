# ResearchIQ

ResearchIQ is a web application that helps users analyze academic papers and find related research articles.

The application allows users to upload a PDF paper and automatically generate a structured summary covering the study topic, research aim, methodology, dataset or participants, key findings, limitations, and overall conclusions. It also suggests relevant search queries and retrieves related publications from academic databases.

The goal of the project is to make it easier to review research papers, understand unfamiliar topics, and identify literature that may be useful for assignments, projects, or further study.

---

## Features

### Paper Analysis

Upload a PDF paper and generate a summary that includes:

* Research topic
* Research type
* Research aim
* Dataset or participants
* Methodology
* Key findings
* Limitations
* Overall summary

For studies involving artificial intelligence or machine learning, the application can also identify information about the model architecture and evaluation metrics.

### Related Literature Search

Based on the uploaded paper, ResearchIQ generates topic-specific search queries and retrieves related publications.

Users can:

* Filter results by publication year
* Filter results by citation count
* Open source articles directly
* Explore related studies on similar topics

### Support for Different Research Types

The application adapts its summaries based on the type of paper being analyzed, including:

* Quantitative studies
* Qualitative studies
* Survey-based research
* Mixed methods studies
* Systematic literature reviews
* AI and machine learning research

---

## Technologies Used

* Python
* Streamlit
* OpenAI API
* Semantic Scholar API
* Crossref API
* Pandas
* PyPDF

---

## Installation

Clone the repository:

```bash
git clone https://github.com/evakonstantinova/ai-research-assistant.git
cd ai-research-assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

---

## Project Structure

```text
ai-research-assistant/
│
├── app.py
├── ai_analyzer.py
├── literature_search.py
├── pdf_utils.py
├── styles.css
├── requirements.txt
├── .env.example
└── README.md
```

---

## Notes

ResearchIQ is intended as a research support tool. Generated summaries and literature recommendations should be reviewed and verified by the user before being used in academic or professional work.


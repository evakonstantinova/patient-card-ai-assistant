import requests


def search_semantic_scholar(query, limit=10, from_year=2021, min_citations=0):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": query,
        "limit": limit,
        "fields": "title,year,authors,venue,url,citationCount,publicationTypes"
    }

    response = requests.get(url, params=params, timeout=20)

    if response.status_code != 200:
        return []

    papers = response.json().get("data", [])
    filtered = []

    for paper in papers:
        year = paper.get("year")
        citations = paper.get("citationCount", 0)

        if year is None:
            continue

        if year >= from_year and citations >= min_citations:
            filtered.append(paper)

    return filtered
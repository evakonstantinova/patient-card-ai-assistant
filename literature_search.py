import requests


def search_semantic_scholar(query, limit=10, from_year=2018, min_citations=0):
    papers = []

    # 1) Semantic Scholar
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            "query": query,
            "limit": limit,
            "fields": "title,year,authors,venue,url,citationCount,abstract"
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json().get("data", [])

        for paper in data:
            year = paper.get("year")
            citations = paper.get("citationCount", 0)

            if year and year >= from_year and citations >= min_citations:
                papers.append({
                    "title": paper.get("title", "Not available"),
                    "year": year,
                    "authors": paper.get("authors", []),
                    "venue": paper.get("venue", "Not available"),
                    "citationCount": citations,
                    "url": paper.get("url", ""),
                    "source": "Semantic Scholar"
                })

    except Exception as e:
        print("Semantic Scholar failed:", e)

    # If Semantic Scholar found enough, return results
    if len(papers) >= 3:
        return papers[:limit]

    # 2) Crossref fallback
    try:
        url = "https://api.crossref.org/works"

        params = {
            "query": query,
            "rows": limit,
            "filter": f"from-pub-date:{from_year}"
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        items = response.json().get("message", {}).get("items", [])

        for item in items:
            title_list = item.get("title", [])
            title = title_list[0] if title_list else "Not available"

            year = None
            date_parts = item.get("published-print", item.get("published-online", {})).get("date-parts", [])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]

            if not year or year < from_year:
                continue

            authors = []
            for author in item.get("author", [])[:3]:
                name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                authors.append({"name": name})

            papers.append({
                "title": title,
                "year": year,
                "authors": authors,
                "venue": item.get("container-title", ["Not available"])[0] if item.get("container-title") else "Not available",
                "citationCount": item.get("is-referenced-by-count", 0),
                "url": item.get("URL", ""),
                "source": "Crossref"
            })

    except Exception as e:
        print("Crossref failed:", e)

    return papers[:limit]
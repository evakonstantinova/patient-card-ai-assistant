import requests
import re
import html


def clean_words(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()

    stopwords = {
        "the", "and", "or", "of", "in", "on", "to", "for", "with", "a", "an",
        "impact", "effect", "effects", "study", "research", "analysis",
        "using", "based", "review", "systematic", "relationship", "role",
        "influence", "evidence", "paper", "article"
    }

    return [word for word in words if word not in stopwords and len(word) > 2]


def relevance_score(query, title, venue="", abstract=""):
    query_words = set(clean_words(query))
    title_words = set(clean_words(title))
    venue_words = set(clean_words(venue))
    abstract_words = set(clean_words(abstract))

    if not query_words:
        return 0

    title_matches = len(query_words.intersection(title_words))
    venue_matches = len(query_words.intersection(venue_words))
    abstract_matches = len(query_words.intersection(abstract_words))

    return (title_matches * 4) + (abstract_matches * 2) + venue_matches


def search_semantic_scholar(query, limit=10, from_year=2018, min_citations=0):
    papers = []

    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            "query": query,
            "limit": 100,
            "fields": "title,year,authors,venue,url,citationCount,abstract"
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        results = response.json().get("data", [])

        for paper in results:
            title = html.unescape(paper.get("title") or "")
            venue = html.unescape(paper.get("venue") or "")
            abstract = html.unescape(paper.get("abstract") or "")
            year = paper.get("year")
            citations = paper.get("citationCount") or 0

            if not year or year < from_year:
                continue

            if citations < min_citations:
                continue

            score = relevance_score(query, title, venue, abstract)

            if score < 1:
                continue

            papers.append({
                "title": title,
                "year": year,
                "authors": paper.get("authors", []),
                "venue": venue or "Not available",
                "citationCount": citations,
                "url": paper.get("url", ""),
                "source": "Semantic Scholar",
                "relevanceScore": score
            })

    except Exception as e:
        print("Semantic Scholar error:", e)

    if len(papers) < limit:
        try:
            url = "https://api.crossref.org/works"

            params = {
                "query.title": query,
                "rows": 100,
                "filter": f"from-pub-date:{from_year}",
                "sort": "score",
                "order": "desc"
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            results = response.json().get("message", {}).get("items", [])

            for item in results:
                citations = item.get("is-referenced-by-count") or 0

                if citations < min_citations:
                    continue

                title_list = item.get("title", [])
                title = html.unescape(title_list[0]) if title_list else ""

                venue_list = item.get("container-title", [])
                venue = html.unescape(venue_list[0]) if venue_list else "Not available"

                abstract = html.unescape(item.get("abstract", ""))

                date_parts = (
                    item.get("published-print", {}).get("date-parts")
                    or item.get("published-online", {}).get("date-parts")
                    or item.get("created", {}).get("date-parts")
                )

                if not date_parts:
                    continue

                year = date_parts[0][0]

                if year < from_year:
                    continue

                score = relevance_score(query, title, venue, abstract)

                if score < 2:
                    continue

                authors = []
                for author in item.get("author", [])[:3]:
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                    if name:
                        authors.append({"name": name})

                papers.append({
                    "title": title,
                    "year": year,
                    "authors": authors,
                    "venue": venue,
                    "citationCount": citations,
                    "url": item.get("URL", ""),
                    "source": "Crossref",
                    "relevanceScore": score
                })

        except Exception as e:
            print("Crossref error:", e)

    unique = {}

    for paper in papers:
        title = paper.get("title", "").lower().strip()

        if title and title not in unique:
            unique[title] = paper

    final_papers = list(unique.values())

    final_papers.sort(
        key=lambda paper: (
            paper.get("relevanceScore", 0),
            paper.get("citationCount", 0)
        ),
        reverse=True
    )

    return final_papers[:limit]
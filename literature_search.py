import requests
import re
import html


GOOD_PUBLISHERS_OR_VENUES = [
    "nature", "science", "springer", "elsevier", "wiley", "sage",
    "taylor", "francis", "oxford", "cambridge", "ieee", "acm",
    "jama", "lancet", "bmj", "bmc", "frontiers", "plos",
    "journal", "research", "review", "international journal"
]

LOW_QUALITY_VENUES = [
    "researchgate",
    "preprint",
    "ssrn",
    "osf",
    "arxiv",
    "bioRxiv",
    "medRxiv",
    "multidisciplinary research",
    "unknown"
]


def clean_words(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()

    stopwords = {
        "the", "and", "or", "of", "in", "on", "to", "for", "with", "a", "an",
        "impact", "effect", "effects", "study", "research", "analysis",
        "using", "based", "review", "systematic", "relationship", "role",
        "influence", "evidence", "paper", "article", "among", "between",
        "during", "through", "towards", "toward", "case"
    }

    return [word for word in words if word not in stopwords and len(word) > 2]


def is_likely_english(text):
    text = str(text).strip()

    if not text:
        return False

    # Allows normal English punctuation, DOI symbols, and academic title formatting.
    ascii_chars = sum(1 for char in text if ord(char) < 128)
    return ascii_chars / max(len(text), 1) > 0.92


def venue_quality_score(venue):
    venue = str(venue).lower()

    if not venue or venue == "not available":
        return 0

    if any(bad in venue for bad in LOW_QUALITY_VENUES):
        return -4

    if any(good in venue for good in GOOD_PUBLISHERS_OR_VENUES):
        return 3

    return 1


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

    score = (title_matches * 5) + (abstract_matches * 2) + venue_matches

    # Extra boost if most important title words match.
    if title_matches >= 2:
        score += 3

    score += venue_quality_score(venue)

    return score


def clean_title(title):
    title = html.unescape(str(title or "")).strip()
    title = re.sub(r"\s+", " ", title)
    return title


def clean_abstract(abstract):
    abstract = html.unescape(str(abstract or "")).strip()
    abstract = re.sub(r"<[^>]+>", "", abstract)
    abstract = re.sub(r"\s+", " ", abstract)
    return abstract


def make_clickable_link(url):
    url = str(url or "").strip()

    if not url:
        return ""

    return f'<a href="{html.escape(url)}" target="_blank">Open paper</a>'


def is_good_result(query, title, venue, abstract, year, citations, min_citations):
    if not title or not year:
        return False

    if not is_likely_english(title):
        return False

    if citations < min_citations:
        return False

    score = relevance_score(query, title, venue, abstract)

    if score < 3:
        return False

    return True


def search_semantic_scholar(query, limit=10, from_year=2018, min_citations=0):
    papers = []

    # Semantic Scholar usually gives better topic relevance than Crossref.
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            "query": query,
            "limit": 100,
            "fields": "title,year,authors,venue,url,citationCount,abstract,publicationTypes"
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        results = response.json().get("data", [])

        for paper in results:
            title = clean_title(paper.get("title"))
            venue = clean_title(paper.get("venue")) or "Not available"
            abstract = clean_abstract(paper.get("abstract"))
            year = paper.get("year")
            citations = paper.get("citationCount") or 0
            publication_types = paper.get("publicationTypes") or []

            if not year or year < from_year:
                continue

            if not is_good_result(query, title, venue, abstract, year, citations, min_citations):
                continue

            # Prefer journal/review/conference papers. Avoid very weak unknown types where possible.
            type_text = " ".join(publication_types).lower()
            if type_text and not any(t in type_text for t in ["journal", "review", "conference"]):
                continue

            papers.append({
                "title": title,
                "year": year,
                "authors": paper.get("authors", []),
                "venue": venue,
                "citationCount": citations,
                "url": paper.get("url", ""),
                "link": make_clickable_link(paper.get("url", "")),
                "source": "Semantic Scholar",
                "relevanceScore": relevance_score(query, title, venue, abstract),
                "qualityScore": venue_quality_score(venue)
            })

    except Exception as e:
        print("Semantic Scholar error:", e)

    # Crossref fallback only fills missing results.
    if len(papers) < limit:
        try:
            url = "https://api.crossref.org/works"

            params = {
                "query.title": query,
                "rows": 100,
                "filter": f"from-pub-date:{from_year},type:journal-article",
                "sort": "score",
                "order": "desc"
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            results = response.json().get("message", {}).get("items", [])

            for item in results:
                citations = item.get("is-referenced-by-count") or 0

                title_list = item.get("title", [])
                title = clean_title(title_list[0]) if title_list else ""

                venue_list = item.get("container-title", [])
                venue = clean_title(venue_list[0]) if venue_list else "Not available"

                abstract = clean_abstract(item.get("abstract", ""))

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

                if not is_good_result(query, title, venue, abstract, year, citations, min_citations):
                    continue

                authors = []

                for author in item.get("author", [])[:3]:
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                    if name:
                        authors.append({"name": name})

                url_value = item.get("URL", "")

                papers.append({
                    "title": title,
                    "year": year,
                    "authors": authors,
                    "venue": venue,
                    "citationCount": citations,
                    "url": url_value,
                    "link": make_clickable_link(url_value),
                    "source": "Crossref",
                    "relevanceScore": relevance_score(query, title, venue, abstract),
                    "qualityScore": venue_quality_score(venue)
                })

        except Exception as e:
            print("Crossref error:", e)

    unique = {}

    for paper in papers:
        title_key = paper.get("title", "").lower().strip()

        if title_key and title_key not in unique:
            unique[title_key] = paper

    final_papers = list(unique.values())

    final_papers.sort(
        key=lambda paper: (
            paper.get("qualityScore", 0),
            paper.get("relevanceScore", 0),
            paper.get("citationCount", 0)
        ),
        reverse=True
    )

    return final_papers[:limit]
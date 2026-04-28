from core.retriever import search

def search_notes(query):
    results = search(query)

    if not results or "No content" in results[0]:
        return ""

    return " ".join(results[:3])  # limit size
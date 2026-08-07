import re

STOPWORDS = {
    "what", "is", "the", "a", "an", "of",
    "to", "and", "in", "on", "for", "by"
}

def extract_keywords(text):
    words = re.findall(r"\w+", text.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return set(keywords)

def keyword_coverage(question, response):
    q_keywords = extract_keywords(question)
    r_keywords = extract_keywords(response)

    if not q_keywords:
        return 0

    matched = q_keywords.intersection(r_keywords)
    coverage = len(matched) / len(q_keywords)

    return round(coverage * 100, 2)
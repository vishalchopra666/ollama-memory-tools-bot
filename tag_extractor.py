import ollama
from config import MODEL_NAME

ALLOWED_TAGS = {
    "tax", "gst", "income", "itr", "reminder", "domain", "blog", "tally", "python", "code"
}

def extract_tags_from_query(query, model=MODEL_NAME):
    prompt = f"""
    From the following user note, extract up to 3 relevant tags that best categorize it.

    Only choose from the following allowed tags: {ALLOWED_TAGS}
    If the note doesn’t clearly match any of these, return: general

    Note: Return the tags as plain, lowercase, comma-separated words with no extra explanation.

    User Note: {query}

    Tags:
    """

    response = ollama.chat(model=model, messages=[{
        "role": "user", "content": prompt
    }])

    tags_raw = response['message']['content']
    tags = [tag.strip().lower() for tag in tags_raw.split(',') if tag.strip()]
    final_tags = [tag for tag in tags if tag in ALLOWED_TAGS]

    # ✅ Add fallback if none match
    if not final_tags:
        final_tags = ["general"]

    return final_tags


if __name__ == "__main__":
    extract_tags_from_query("gst return filling last date is 20th june 2025", MODEL_NAME)


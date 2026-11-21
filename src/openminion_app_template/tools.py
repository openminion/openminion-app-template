from openminion import tool


@tool(min_scope="READ_ONLY", idempotent=True)
def count_words(text: str) -> int:
    """Count whitespace-separated words in application text."""

    return len(text.split())

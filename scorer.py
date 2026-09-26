def judge(question: str, expects: str, answer: str, results) -> bool:
    """
    Judge whether the answer is correct.

    Args:
        question: The question string.
        expects: The expected answer string.
        answer: The actual answer string.
        results: The list of result strings from the retrieval system.

    Returns:
        True if the answer is correct, False otherwise.

    """
    if not expects:
        return False
    return expects.strip().lower() in (answer or "").lower()

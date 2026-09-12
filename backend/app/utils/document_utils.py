import re


def tokenize(text: str) -> set[str]:
    return {
        word.lower()
        for word in re.findall(
            r"\b[a-zA-Z0-9_]+\b",
            text,
        )
        if len(word) > 2
    }


def select_relevant_chunks(
    chunks: list[str],
    question: str,
    max_chunks: int = 4,
) -> list[str]:
    question_words = tokenize(question)

    if not question_words:
        return chunks[:max_chunks]

    scored_chunks: list[tuple[int, str]] = []

    for chunk in chunks:
        chunk_words = tokenize(chunk)

        score = len(
            question_words.intersection(
                chunk_words
            )
        )

        scored_chunks.append(
            (score, chunk)
        )

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    selected = [
        chunk
        for score, chunk in scored_chunks[:max_chunks]
        if score > 0
    ]

    if not selected:
        return chunks[:max_chunks]

    return selected
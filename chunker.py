"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


# A body shorter than this is a fragment, not a chunk. When packing leaves a
# runt at the end of a document — the "2-character chunk" problem the brief
# warns about — it gets folded back into the piece before it instead.
MIN_BODY_CHARS = 100

# A first paragraph this short, on a single line, is a title rather than
# content. Every campus_life post has one: "The Atrium", "On-campus work",
# "Old Brewhouse — what it's actually like".
MAX_TITLE_CHARS = 100

# Sentence boundary: ., ! or ? followed by whitespace. Only used for the rare
# paragraph that is too long to fit a chunk on its own.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _split_title(text: str) -> tuple[str, list[str]]:
    """Separate a document's title line from its body paragraphs.

    Returns ("", paragraphs) when the first paragraph doesn't look like a
    title, so the packing below works either way.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return "", []

    first = paragraphs[0]
    is_title = "\n" not in first and len(first) <= MAX_TITLE_CHARS
    if is_title and len(paragraphs) > 1:
        return first, paragraphs[1:]
    return "", paragraphs


def _split_long_paragraph(paragraph: str, budget: int) -> list[str]:
    """Break one over-long paragraph on sentence boundaries.

    campus_life never needs this — its longest paragraph fits. It's here so a
    single runaway paragraph degrades into whole sentences rather than being
    cut mid-word, which is what the starter did everywhere.
    """
    sentences = [s.strip() for s in _SENTENCE_END.split(paragraph) if s.strip()]
    pieces: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > budget:
            pieces.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces or [paragraph]


def _pack(paragraphs: list[str], budget: int) -> list[str]:
    """Group whole paragraphs into bodies of at most `budget` characters."""
    bodies: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        for piece in (
            _split_long_paragraph(paragraph, budget)
            if len(paragraph) > budget
            else [paragraph]
        ):
            addition = len(piece) + (2 if current else 0)
            if current and current_len + addition > budget:
                bodies.append("\n\n".join(current))
                current, current_len = [piece], len(piece)
            else:
                current.append(piece)
                current_len += addition

    if current:
        bodies.append("\n\n".join(current))

    # Fold a trailing runt back into its neighbour rather than shipping a
    # fragment. Going a little over budget beats a chunk nobody can answer from.
    if len(bodies) > 1 and len(bodies[-1]) < MIN_BODY_CHARS:
        tail = bodies.pop()
        bodies[-1] = f"{bodies[-1]}\n\n{tail}"

    return bodies


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents on paragraph boundaries, keeping the title line on every
    chunk.

    Why this and not fixed-size windows, for campus_life:

    The starter cut at 800 characters and the longest post here is 549, so it
    never cut anything — 88 documents, 88 chunks. That was mostly the right
    call. These posts are already topic-scoped by whoever wrote the corpus:
    housing_aldridge_hall_laundry.txt and housing_aldridge_hall_noise.txt are
    separate files. Most of the chunking was done for me in the filenames.

    Two things were still wrong with it.

    First, the "what it's actually like" housing overviews genuinely hold
    several topics at once — the building, the good, the bad, and a last
    paragraph that packs laundry prices and noise together. Those are the posts
    a laundry question has to dig the answer out of, competing with 300
    characters about elevators and heating. Those should come apart.

    Second — and this is why splitting on paragraphs alone would have been
    worse than doing nothing — every post's first paragraph is its title, a
    median of 26 characters. A plain `\\n\\n` split yields 88 chunks that say
    only "The Atrium" or "On-campus work": the fragment failure mode, 88 times
    over. Worse, it orphans the bodies. "Laundry costs $1.75 wash, $1.75 dry,
    app-based" never names a building; only the title line does. Cut loose, it
    matches every laundry question equally and answers none of them.

    So: cut on paragraph boundaries, pack up to CHUNK_SIZE, and prepend the
    title to every piece. At 400 characters that leaves 78 posts whole and
    splits the 10 that are actually carrying more than one topic: 98 chunks,
    shortest 123 characters, longest 419.
    """
    chunk_size = config.CHUNK_SIZE
    chunks: list[Chunk] = []

    for doc in documents:
        title, paragraphs = _split_title(doc.text)
        prefix = f"{title}\n\n" if title else ""
        budget = max(chunk_size - len(prefix), MIN_BODY_CHARS)

        for index, body in enumerate(_pack(paragraphs, budget)):
            chunks.append(
                Chunk(
                    text=f"{prefix}{body}",
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))

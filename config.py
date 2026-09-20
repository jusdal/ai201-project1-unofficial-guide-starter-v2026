"""
Settings for The Unofficial Guide.

Everything you're likely to change lives here, at the top, on purpose.
You'll edit THRESHOLD in Milestone 4 and the chunking numbers in Milestone 3.

Anything you set in your .env file wins over the defaults here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


# ─── The corpus you're working with ──────────────────────────────────────────
# Change this to switch corpora, or pass --corpus on the command line.
# Options are the folder names inside corpora/. See corpora/README.md.

CORPUS = os.getenv("AI201_CORPUS", "campus_life")


# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# Tuned for campus_life: 88 short posts, 178–549 characters, median 309.
# Every post opens with a one-line title and runs 2–5 short paragraphs.
#
# 400 is set just under the length of the multi-topic overview posts, so those
# 10 come apart at a paragraph boundary while the other 78 stay whole. See
# chunker.py::split_documents for why, and the README for the measurements.

CHUNK_SIZE = 400  # characters per chunk, title line included

# Zero on purpose. Cutting on paragraph boundaries means no chunk ever starts
# mid-thought, so there is nothing for a character overlap to repair. The job
# overlap used to do — carrying context across the cut — is done instead by
# repeating the document's title line at the top of every chunk, which costs
# ~26 characters rather than 120 and carries the part that actually matters:
# which hall, dining hall or course this is about.
CHUNK_OVERLAP = 0  # characters shared between neighbouring chunks


# ─── Retrieval (Milestone 4) ─────────────────────────────────────────────────

# Left at 5. The document holding the answer came back at rank 1 for all five
# questions in questions.py, so this is insurance rather than necessity — but
# it costs ~600 tokens and the grounding instruction ignores the extra chunks
# cleanly, including the four CS 210 docs at 0.63+ that the study-room question
# drags in.
TOP_K = 5  # how many chunks to pull back per question

# The relevance gate. If the best chunk is further away than this, the system
# refuses to answer instead of handing the model thin material.
#
# LOWER IS BETTER: 0.3 is a close match, 0.9 is unrelated.
#
# 0.75, not the starter's 0.6. The five questions in questions.py sit at
# 0.21–0.41 and the five in OUT_OF_SCOPE at 0.82–0.93, which looks like a wide
# gap — but rephrasing the real questions pushes the worst one to 0.6663
# ("Do buses run on Sunday?", which retrieves transit_shuttle.txt at rank 1
# and would be refused at 0.6). The only band with nothing real in it is
# 0.6663–0.8246, and 0.75 is its midpoint. See the README.
THRESHOLD = 0.75


# ─── Models ──────────────────────────────────────────────────────────────────
# Embeddings run on your own machine and cost no API quota.
# Only generation calls out to a service.

# This is the model Chroma bundles, and leaving it alone is the fast path: it
# downloads about 80 MB from Chroma's own CDN and needs nothing else installed.
#
# Setting it to any other name — unit 2's "try a second embedding model"
# stretch option — switches to loading that model from Hugging Face instead,
# which needs `pip install 'sentence-transformers>=3.4,<3.5'` first. store.py
# says so with a real error message rather than a stack trace if you forget.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL = os.getenv("AI201_MODEL", "gemini-3.5-flash-lite")


# ─── Rate limiting and quota guards ──────────────────────────────────────────
# You should not need to touch these. They exist so that a runaway loop costs
# you a warning instead of your whole day's allowance.

REQUESTS_PER_MINUTE = 30  # outgoing calls the limiter will allow per minute
SESSION_REQUEST_BUDGET = 300  # stop and warn rather than draining the daily quota
MAX_RETRIES = 4  # on 429 / resource-exhausted, with backoff

CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"
CACHE_DIR = ROOT / ".cache"


# ─── Paths ───────────────────────────────────────────────────────────────────

CORPORA_DIR = ROOT / "corpora"
CHROMA_DIR = ROOT / "chroma_db"
RESULTS_DIR = ROOT / "results"


def corpus_path(name: str | None = None) -> Path:
    """Folder holding the documents for a corpus."""
    return CORPORA_DIR / (name or CORPUS) / "documents"


def collection_name(name: str | None = None, variant: str = "default") -> str:
    """
    Name of the vector-store collection for a corpus.

    `variant` lets you index the same corpus two different ways and query both
    without deleting anything — you'll want that in unit 2 when you compare
    chunking strategies.

    Chroma is fussy about collection names: 3 to 63 characters, starting and
    ending with a letter or digit, and nothing but letters, digits, underscores
    and hyphens in between. If you bring your own corpus and name the folder
    something Chroma won't accept, this cleans it up rather than failing.
    """
    import re

    raw = f"{name or CORPUS}__{variant}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", raw)
    cleaned = cleaned.strip("_-")  # must start and end alphanumeric
    if not cleaned or not cleaned[0].isalnum():
        cleaned = f"c{cleaned}"
    if not cleaned[-1].isalnum():
        cleaned = f"{cleaned}0"
    return cleaned[:63].rstrip("_-") or "collection"

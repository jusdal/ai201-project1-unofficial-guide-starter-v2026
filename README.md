# The Unofficial Guide

Justin Daly — corpus: `campus_life`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a retrieval-augmented question answering system over `campus_life`: 88
short posts from a student forum at a fictional university, covering housing,
courses, dining, registrar admin, transit, and money. You ask it the kind of
factual question a student actually asks another student — what laundry costs
in a specific hall, how often the weekend shuttle runs, how many hours a week
you're allowed to work on campus, which study rooms have whiteboards that
erase — and it retrieves the posts most likely to hold the answer, answers from
those posts alone, and names the files it drew on. Questions the corpus doesn't
cover never reach the model: a relevance gate compares the best retrieved
distance against a cutoff of 0.75 and returns "I don't have enough information
about that" instead of guessing. Those 88 files are the only thing it knows.

## Chunking Strategy

**Chunk size:** 400 characters, title line included
**Overlap:** 0 characters — replaced by repeating the title line on every chunk

Produced by `chunker.py::split_documents`. Paragraph-aware packing: cut only on
paragraph boundaries, pack whole paragraphs up to 400 characters, and prepend
the document's title line to every chunk.

**What the starter did.** `python app.py index` reported:

```
loaded   88 documents, 27,908 characters, ~317 characters per document
chunked  88 chunks, 317 characters on average (shortest 178, longest 549),
         produced by chunker.py::fallback_split
```

88 documents, 88 chunks. The starter cuts at 800 characters and the longest
post in campus_life is 549, so it never split anything. That was mostly the
right call, and it's the first thing I had to decide about rather than
"improve". These posts are already topic-scoped by whoever built the corpus —
`housing_aldridge_hall.txt`, `housing_aldridge_hall_laundry.txt` and
`housing_aldridge_hall_noise.txt` are three separate files. Most of the
chunking was done for me in the filenames.

**Why I still changed it.** Two things about the documents, both from reading
them rather than from the summary line:

1. The seven `housing_*` "what it's actually like" posts really do hold several
   topics at once. Old Brewhouse (549 characters) runs: the building, then "the
   good", then "the bad", then a last paragraph that packs laundry prices *and*
   noise together. As one 549-character chunk, a laundry question has to find
   "$1.50 wash, $1.50 dry" underneath 300 characters about 1902 brickwork and
   uneven heating. Those are the posts that should come apart.

2. **Every single post opens with a one-line title**, median 26 characters —
   "The Atrium", "On-campus work", "Old Brewhouse — what it's actually like".
   All 88 of them. This is why I did *not* just split on `\n\n`, which was my
   first instinct and would have been worse than leaving the starter alone. It
   produces 271 chunks, 88 of which are nothing but a title — the fragment
   failure mode, 88 times over. Worse, it orphans the bodies: "Laundry costs
   $1.75 wash, $1.75 dry, app-based" never names a building. Only the title
   line does. Cut loose, that chunk matches every laundry question in the
   corpus equally well and answers none of them.

So the title line gets repeated onto every chunk instead of being a chunk. That
is also what killed the overlap: once you cut on paragraph boundaries no chunk
ever starts mid-thought, so there's nothing for a character overlap to repair.
The job overlap was doing — carrying context across the cut — is done better by
the title at ~26 characters than by 120 characters of the previous paragraph's
tail.

**Why 400.** I measured the document lengths first: median 309, 90th percentile
~430, max 549. Then I simulated the packer at several targets:

| Target | Chunks | Documents split | Avg | Shortest | Longest |
|---|---|---|---|---|---|
| 300 | 125 | 35 | 231 | 117 | 366 |
| 350 | 111 | 23 | 257 | 118 | 419 |
| **400** | **98** | **10** | **287** | **123** | **419** |
| 450 | 91 | 3 | 307 | 159 | 430 |
| 600 | 88 | 0 | 317 | 178 | 549 |

400 sits just under the multi-topic posts, so the 10 documents carrying more
than one topic come apart and the other 78 stay whole. Those 10 are exactly the
ones I'd have picked by hand: five `housing_*` overviews and four `course_*`
overviews, plus `dining_the_atrium.txt`. 450 caught only 3 — barely a change
from the starter. 300 split 35 documents, which starts breaking up posts whose
paragraphs genuinely belong together.

**The runt guard.** Packing can leave a short tail at the end of a document.
`_pack` folds any trailing body under 100 characters back into the piece before
it, going slightly over budget rather than shipping a fragment. This is the
same failure the brief points at in `advice_threads`, where the starter's
800/120 window produces a 2-character chunk. My chunker's shortest chunk on
`advice_threads` is 157 characters; on campus_life it's 123.

**After the change:**

```
chunked  98 chunks, 287 characters on average (shortest 123, longest 419),
         produced by chunker.py::split_documents
```

All five questions in `questions.py` still retrieve their correct source
document at rank 1, at distances from 0.21 to 0.41.

## Sample Chunks

From `python app.py chunks -n 5` — 98 chunks total, 5 spread across the corpus.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

Stands on its own. One document, one topic, under the limit — left whole.

**Chunk 2** — source: `course_biol_160_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for BIOL 160 Cell Biology

People keep asking so: 9 to 11 hours a week, the heaviest first-year course by reputation. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

Both paragraphs are about workload, so packing them together is right: the
hours figure and the "front-loaded" caveat answer one question between them.

**Chunk 3** — source: `course_math_220.txt#0` — produced by: `chunker.py::split_documents`

```
MATH 220 Linear Algebra

I lived here my sophomore year. Format is chalk-and-talk lecture, weekly problem sets marked for correctness. Assessment: two midterms and a cumulative final. Curved to a b- median.

Expect 6 to 8 hours a week, almost all of it on problem sets.

The one piece of advice: the problem sets are the course; the lectures make sense afterwards rather than during.
```

This is the one I'd split first if I tightened the size — format, workload and
advice are three separately answerable things in one chunk. It stays whole only
because the document is 383 characters, just under the 400 budget. A student
asking "how many hours a week is MATH 220?" gets the answer wrapped in two
topics they didn't ask about. That's the cost of the threshold I picked, and
`course_math_220_workload.txt` exists separately and covers it more tightly.

(Also: "I lived here my sophomore year" is in a *course* document. That's a
copy-paste artifact in the corpus itself, not something my chunker did — a
loading-stage observation to come back to.)

**Chunk 4** — source: `dining_the_atrium.txt#1` — produced by: `chunker.py::split_documents`

```
The Atrium

Hours are 8:00am to 6:00pm weekdays. Costs one meal swipe for a sandwich-plus-drink combination, or à la carte.
```

This is the case the title prefix exists for. The body alone is "Hours are
8:00am to 6:00pm weekdays" — hours for *what*? Unanswerable, and it would match
every opening-hours question in the corpus. With the title attached it answers
one question exactly.

**Chunk 5** — source: `housing_innisfree_hall.txt#1` — produced by: `chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

The multi-topic split working. Under the starter this was buried in a
516-character chunk with the building's construction date, its good point and
its bad point. On its own, with the hall named, it answers a laundry question
and a noise question. It's the one chunk of the five I'd still call slightly
too big — laundry and noise are two topics — but the corpus has dedicated
`housing_innisfree_hall_laundry.txt` and `_noise.txt` files that cover both in
more depth, so splitting this further would mostly duplicate them.

## Sample Answer

**Question:** How much does it cost to do laundry at Aldridge Hall?

**Answer:**

```
  (best distance 0.213, cutoff 0.75)

Laundry at Aldridge Hall costs $1.75 to wash and $1.50 to dry.

This information comes from `housing_aldridge_hall.txt` and
`housing_aldridge_hall_laundry.txt`.

Sources retrieved: housing_aldridge_hall.txt, housing_aldridge_hall_laundry.txt,
housing_innisfree_hall.txt, housing_innisfree_hall_laundry.txt,
housing_old_brewhouse.txt
```

Worth noting what the prompt contained: four *different* halls' laundry prices,
three of them wrong for this question. Innisfree charges $1.75/$1.75 and Old
Brewhouse $1.50/$1.50. The answer takes Aldridge's numbers and names both files
that carry them — I checked, and the prices really are in both.

**My relevance cutoff:** 0.75

The two groups came out cleanly separated. The five questions my corpus covers
landed at 0.2133–0.4114; the five in `OUT_OF_SCOPE` landed at 0.8246–0.9335. On
those ten numbers alone the gap is 0.41 wide and almost any cutoff works, so I
rephrased each of my five questions three more ways to find where the real
questions actually top out. They top out at **0.6663** — "Do buses run on
Sunday?", which retrieves `transit_shuttle.txt` at rank 1 with the answer in it.
The starter's 0.6 refuses that question. The document says "shuttle" and never
says "bus."

So the band with nothing real in it is 0.6663–0.8246, and I put the cutoff at
its midpoint. That still refuses all five `OUT_OF_SCOPE` questions with 0.075 to
spare, which is what criterion 3 measures.

| Question | In corpus? | Best distance |
|---|---|---|
| How much does it cost to do laundry at Aldridge Hall? | yes | 0.2133 |
| Approximately how many pages of reading per week should a student expect in HIST 118 Modern World History? | yes | 0.2374 |
| Which specific group study room numbers have whiteboards that actually erase? | yes | 0.3883 |
| What is the maximum number of hours a student can work on campus per week during the term? | yes | 0.3901 |
| How often does the campus shuttle run on weekends? | yes | 0.4114 |
| What is the capital of Mongolia? | no | 0.8246 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.8442 |
| Who won the 1994 World Cup? | no | 0.8859 |
| How do I write a for loop in Rust? | no | 0.8907 |
| How do I change the oil in a diesel engine? | no | 0.9335 |

## How I Used AI

**1. I asked for a second pair of eyes on my criteria and got a draft about the
wrong corpus.**

In Milestone 2 I had criteria 1–3 written and wanted help sharpening 4 and 5, so
I asked Claude what it would propose. What came back was specific, grounded in
real documents, and about a corpus I wasn't using: criterion 4 was "numbers stay
attached to their place," justified by walking routes and transport timetables.
It had read `CORPUS = "city_guides"` out of `config.py` — a default I'd flipped
days earlier while looking through the other corpora and forgotten about — and
never asked which corpus I was working in. It also told me, confidently, that my
`questions.py` was full of questions about buildings that don't exist. They do
exist. I was the only thing in the repo that knew it.

I threw both drafts out, told it the corpus was `campus_life`, and had it go
read the files before suggesting anything else. The one thing worth keeping from
the second pass was an observation, not a criterion: the seven `housing_*`
laundry posts are near-identical templates differing only by a hall name and a
price. But its rewrite was still built around embedding-discrimination failures,
which is a sophisticated thing to measure and not something I could score by
looking. I told it I wanted simpler criteria I could check by eye, asked for
plain options instead of finished text, and wrote 4 and 5 myself from there —
the 150–600 character bound, and the no-invented-entities check against the 88
filenames.

The fix that mattered wasn't a better prompt, though. It was setting `config.py`
back to `campus_life`, because the same thing happened again at the start of
Milestone 3: it read the config, and by the time I interrupted it, it was
designing a chunker that split on markdown `##` headers, which `campus_life`
doesn't have. What it believes about my project comes from my files. A stale
file is a lie I'm telling it, and it has no way to catch me.

**2. I made it interrogate my criteria instead of writing them.**

My first try at the "why this target" reasons was to ask Claude to draft them.
Each one came back at four or five sentences citing distances and character
counts — reasons that could only have been written after running the pipeline.
That's backwards for this assignment. The point of writing criteria in unit 1 is
that they're a bet placed before the results are in, so I told it the reasons
were too detailed and rewrote each one to a sentence or two I could have
defended on day one. Criterion 1's reason is now just that the work-hours answer
isn't duplicated anywhere else in the corpus and shares the phrase "hours a
week" with nine course-workload docs that could outrank it — something I knew
from reading files in Milestone 1, not from a run.

So I stopped asking it for text. I gave it the five criteria I had and three
questions to answer about each — how would you test this using only the sentence
itself, would two different people score it the same way, what would have to
happen for it to fail — and added "don't rewrite them for me," because otherwise
it quietly fixes things instead of telling me they're broken. Four held up. By
its own answer, criterion 5 didn't: two people wouldn't have scored my original
wording the same way. I asked it to lay out ways the sentence could be rewritten
and picked the one I could check without an opinion — the system never names a
hall, course, or dining hall outside the 88 filenames in
`corpora/campus_life/documents/`. Reading three options I didn't write was what
made it obvious which one was actually checkable.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

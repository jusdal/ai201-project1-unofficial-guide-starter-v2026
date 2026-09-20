# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
I picked 4 of 5 because the work-hours question is the one answer that isn't
duplicated anywhere else in my corpus, and it shares phrasing ("hours a
week") with nine other course-workload docs that could plausibly outrank it.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
I picked 5 of 5 because the source list is attached by the pipeline code
itself from whatever chunks were retrieved, not left up to the model to
remember — so there's no obvious way for a passed question to come back
without one.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
I picked 4 of 5 because my out-of-scope questions are on topics with nothing
in common with my corpus (car engines, sports trivia, medication dosages), so
I expect them to sit far from any real question — but I'm leaving one slot
for a surprise, since an embedding model can occasionally place unrelated
text closer than it should be.

---

## 4. No chunk is under 150 characters or over 600

Across every chunk `split_documents` produces, none falls outside the
150–600 character range.

**Why this target:**
Every real document in `campus_life` falls between 183 characters
(`course_hist_118_exams.txt`) and 554 (`housing_old_brewhouse.txt`). A chunk
outside 150–600 would mean something broke — a document got truncated,
merged with its neighbor, or split mid-file — not that a document just
happened to run long or short.

---

## 5. No hallucinated entities

The system never names a hall, course, or dining hall that isn't one of my 88
real documents, in 5 of 5 trials.

**Why this target:**
This is 5 of 5, not 4 of 5, because there's no reasonable rate of making up a
building that doesn't exist — a student would actually go looking for
"Wexford Hall" laundry hours that were never real. It's also the easiest
thing on this list to check: the full list of valid entities is just the 88
filenames in `corpora/campus_life/documents/`.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->

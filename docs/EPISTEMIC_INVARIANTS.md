# Epistemic Invariants: Broadcast Mind

> Rules that implementation must never violate.
> Each invariant has a test.

## Invariant 1: Persona opinion ≠ world fact

**Rule:** A persona's opinion cannot become a world
fact merely because the persona expressed it.

**Enforcement:** PersonaOpinion writes to persona
store, never world store. WorldStore rejects any
write without proven evidence.

**Test:** Create persona, have it express opinion on
unverified claim. Verify world state contains no
new facts. Verify opinion is tagged as persona-held.

## Invariant 2: Generated statement ≠ evidence

**Rule:** A generated statement (script, summary,
analysis) cannot automatically become evidence.

**Enforcement:** Only externally sourced material
with a source URL and fetch timestamp enters as
evidence. Generated content is tagged as SYNTHETIC.

**Test:** Generate a script via LLM. Verify the
script text is NOT in the evidence table. Verify
it IS tagged as SYNTHETIC.

## Invariant 3: External claims require provenance

**Rule:** Every externally sourced factual claim must
retain its source URL, fetch timestamp, and extractor
identity.

**Enforcement:** Claim creation requires source_url,
extractor, and fetched_at. Missing any → rejected.

**Test:** Attempt to create claim without source_url.
Verify rejection. Attempt with all fields → verify
acceptance.

## Invariant 4: Speculation ≠ reporting

**Rule:** Speculation must remain distinguishable from
reporting in all outputs.

**Enforcement:** Every broadcast segment includes
epistemic labels. Speculative content is prefixed
with "Speculation:" or labeled in the segment type.

**Test:** Generate broadcast with speculative content.
Verify segment type includes SPECULATION label.
Verify transcript labels speculation explicitly.

## Invariant 5: Synthetic ≠ factual reporting

**Rule:** Synthetic content must be distinguishable from
retrieved reporting in all outputs.

**Enforcement:** SYNTHETIC segments are labeled as
synthetic in the broadcast queue and transcript.
User can always see segment type.

**Test:** Create synthetic segment. Verify it is
labeled SYNTHETIC in queue metadata and transcript.

## Invariant 6: Corrections preserve history

**Rule:** Corrections must preserve the historical record
rather than silently rewriting it.

**Enforcement:** Corrections create new records with
correction_of reference. Old records are never
deleted or modified.

**Test:** Create claim, correct it, verify both
records exist with correction_of linkage. Verify
old claim status shows "corrected by" reference.

## Invariant 7: Source timestamp ≠ event timestamp

**Rule:** A source's publication timestamp must not be
confused with when the system fetched or processed it.

**Enforcement:** Event records carry both
published_at (source) and fetched_at (system).
These are never the same field.

**Test:** Create event with published_at ≠ fetched_at.
Verify both timestamps are distinct and correctly
labeled.

## Invariant 8: Multiple sources ≠ independent confirmation

**Rule:** Multiple sources discussing the same claim do
not automatically constitute independent confirmation.

**Enforcement:** Source reliability and independence
are tracked separately. Same-origin sources are not
counted as independent corroboration.

**Test:** Create 3 claims from same source. Verify
confidence does not increase as if from independent
sources. Create 3 claims from 3 independent sources
→ confidence increases.

## Invariant 9: World state ≠ presentation

**Rule:** World state must be separable from presentation.
The broadcast script is not the world state.

**Enforcement:** WorldStore contains only factual
records. Script generation reads from WorldStore but
produces SYNTHETIC output. No script text enters
world state.

**Test:** Generate broadcast script. Verify script
text is NOT in any world state table. Verify WorldStore
contains only evidence, claims, events.

## Invariant 10: Persona state ≠ world state

**Rule:** Persona state must be separable from world state.

**Enforcement:** PersonaStore and WorldStore are
separate interfaces. PersonaOpinion references world
claims but never modifies them. WorldStore never
accepts persona-owned records.

**Test:** Create persona opinion about world claim.
Verify WorldStore unchanged. Verify PersonaStore
contains the opinion with reference to claim.

## Invariant 11: Confidence ≠ certainty

**Rule:** High confidence is not certainty. The system
must never treat a confidence threshold as a gate.

**Enforcement:** Confidence scores are advisory.
Thresholds (≥0.85 for fact) are configurable and
documented as provisional. Broadcast labels uncertainty
regardless of confidence.

**Test:** Set confidence to 0.99. Verify system still
allows "uncertain" label in broadcast. Verify
threshold is configurable.

## Invariant 12: Unknown ≠ false

**Rule:** Unknown is not the same as false. The system
must communicate unknown states honestly.

**Enforcement:** When evidence is insufficient, the
system says "unknown" — never "false" or "no evidence."

**Test:** Query claim with no evidence. Verify status
is UNKNOWN, not FALSE. Verify broadcast communicates
uncertainty.

## Invariant 13: Evidence is never deleted

**Rule:** Evidence records are immutable and never
deleted, even if source becomes unavailable.

**Enforcement:** No DELETE on evidence table. Source
URL may become 404 — evidence record persists with
confidence adjusted.

**Test:** Create evidence. Attempt to delete. Verify
rejection. Mark source unavailable → verify evidence
persists with adjusted confidence.

## Invariant 14: World state is append-only

**Rule:** World state tables never accept UPDATE or
DELETE on core records. Only INSERT (new records) and
READ.

**Enforcement:** WorldStore interface has no update or
delete methods for core entities. Corrections create
new records.

**Test:** Attempt to update a story. Verify rejection.
Attempt to delete evidence. Verify rejection.
Create correction → verify new record created.
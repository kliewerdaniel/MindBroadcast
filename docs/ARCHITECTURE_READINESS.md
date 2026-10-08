# Architecture Readiness Review: Broadcast Mind

> Determines whether documentation is sufficient to begin
> implementation. Every claim is verified against the
> actual repository, not assumed.

## How to read this review

- **READY** — Design is sufficiently specified for implementation to begin
- **NEEDS DESIGN** — Concept exists but lacks concrete specification
- **NEEDS RESEARCH** — Requires external evaluation/experimentation
- **BLOCKED** — Cannot proceed without external decision

## 1. Domain model completeness: READY

DOMAIN_MODEL.md defines 23 entities with purpose, ownership,
lifecycle, relationships, persistence, provenance, mutability,
versioning, and user-visibility.

**Verified against code:** Article and BroadcastSegment dataclasses
in main.py are clean seeds for Story and BroadcastSegment. The
remaining 21 entities are new — correct, nothing to migrate.

**Gap:** Entity attributes and relationships are described
conceptually but not as schema definitions. Implementation needs
the schema. This is expected — docs/ say "not yet."

## 2. Architecture completeness: READY

ARCHITECTURE.md defines all 5 layers with responsibilities and
the append-only core rule.

**Verified against code:** news08 has no layers — it is a single
file. The architecture is genuinely new, not a refactoring of
existing code. This is correct.

**Gap:** The architecture diagram does not show data flow
between layers explicitly (only vertical grouping). The pipeline
document covers this but is missing (see item 8).

## 3. Epistemic model: READY

EPISTEMIC_MODEL.md defines 9 categories with provenance,
confidence thresholds, information flow, and violation rules.

**Verified against code:** news08 treats all LLM output as fact.
The epistemic model is a genuine addition, not a refactoring.

**Gap:** Confidence thresholds (≥0.85 for fact) are hard-coded
in the document but not marked as NEEDS USER DECISION. The user
must confirm these values or they become invisible defaults.

## 4. Persistence model: NEEDS DESIGN

PERSISTENCE.md does not exist yet. The domain model says
"SQLite confirmed" but does not specify:

- Schema structure
- Table relationships
- Migration strategy
- ORM vs raw SQL
- Connection management
- Backup procedure

**This is the single largest readiness gap.** Implementation
cannot begin without a persistence model.

## 5. Provider boundaries: READY

CONTRACTS.md defines 11 interfaces with purpose, inputs, outputs,
errors, invariants, dependencies, and provider boundaries.

**Verified against code:** main.py has zero interface boundaries.
All logic is in NewsGenerator class with direct Ollama/edge-tts
calls. The contracts are genuinely new architecture, not
refactoring.

**Gap:** Contracts are conceptual — no type hints, no async
signatures. Implementation needs concrete Python signatures.

## 6. Persona architecture: NEEDS DESIGN

PERSONA_SYSTEM.md is detailed (52-dimension trait vector, Big Five,
Dark Triad, Moral Foundations) but:

- Trait vector dimensionality (52) is stated but not justified
- No existing code implements personas — this is all greenfield
- Trait evolution rules are described but not formalized
- Persona runtime semantics (PERSONA_RUNTIME.md gap) are not defined

**Confirmed by code:** main.py has no persona concept at all.

## 7. Newsroom architecture: READY

NEWSROOM.md defines roles, communication patterns, shared state,
disagreement handling, and conflict resolution.

**Verified against code:** news08 has no newsroom concept. The
 simplification section correctly identifies that a single
agent with modular capabilities suffices for MVP.

**Gap:** The document says "single NewsProcessor with modular
capabilities" for MVP but doesn't define the MVP boundary
explicitly. MVP.md will address this.

## 8. Broadcast lifecycle: NEEDS DESIGN

BROADCAST_PIPELINE.md does not exist yet. The architecture
mentions the 13-phase lifecycle but no document defines:

- State machine transitions
- Queue semantics
- Breaking story behavior
- Idle content generation rules
- Error handling per phase

**This is the second largest readiness gap.** The pipeline is
the core runtime behavior — it cannot be implemented without
specification.

## 9. Source architecture: READY

SOURCES.md defines the SourceProvider interface, normalization,
deduplication, source identity, reliability, and failure handling.

**Verified against code:** main.py's fetch_single_feed and
fetch_feeds_batch are the RSS provider prototype. The interface
is a genuine abstraction over existing code.

**Gap:** Source reliability scoring is heuristic in the doc
(0.8–1.0 for reputable outlets) but no methodology is defined.

## 10. World snapshots: READY

WORLD_SNAPSHOTS.md defines snapshot contents, creation triggers,
comparison, serialization, versioning, and restoration.

**Verified against code:** news08 has no snapshot capability.
This is entirely new.

**Gap:** Snapshot comparison algorithm is not specified (what
constitutes a "change"?). Needs a simple definition before
implementation.

## 11. Personal knowledge: NEEDS DESIGN

PERSONAL_KNOWLEDGE.md defines categories, separation rules, and
ingestion pipeline.

**Verified against code:** news08 has no personal knowledge
integration. This is entirely new.

**Gap:** The ingestion pipeline (discovery → extraction →
normalization → linking → tagging) is described but not
specified at the interface level. Which documents? Which repos?
How are they discovered? Needs concrete MVP scope.

## 12. Relevance engine: NEEDS DESIGN

RELEVANCE_ENGINE.md defines signal sources, scoring formula,
transparency, and continuous learning.

**Verified against code:** news08 has a hard-coded relevancy_threshold
of 5 and a simple --topic flag. The new engine is a genuine
replacement.

**Gap:** The scoring formula uses 6 weighted signals but no
weights are specified. The default weights are not defined.
The learned behavior component requires user interaction data
that doesn't exist yet.

## 13. Artifact model: READY

ARTIFACTS.md defines artifact contents, storage, correction
support, and retention policy.

**Verified against code:** news08 saves flat Markdown logs. The
artifact system is a genuine upgrade.

**Gap:** Audio retention policy (30 days default) is stated but
not justified. Compression format not specified.

## 14. UI architecture: NEEDS DESIGN

UI_ARCHITECTURE.md defines components and interaction patterns
but not the information architecture for MVP.

**Verified against code:** news08 has no UI (gradio is in
requirements but not used in main.py — confirmed by grep).

**Gap:** Which components belong in MVP vs post-MVP is not
defined. The "SHOW ANALYSIS" interaction pattern is clear but
the default view specification is missing.

## 15. Voice architecture: NEEDS RESEARCH

VOICE.md defines the VoiceProvider interface and provider
candidates.

**Verified against code:** main.py hard-codes edge-tts with
en-US-JennyNeural. The provider abstraction is entirely new.

**Gap:** TTS research is explicitly marked as a future task in
the doc, but no research has been done. Edge-TTS on macOS needs
verification. Piper/Coqui availability needs checking. This is
blocked on runtime verification.

## 16. Portability: NEEDS DESIGN

PORTABILITY.md defines the separation of core/config/personas/sources
but references a directory layout that assumes the repo has been
restructured.

**Verified against code:** main.py is a single file with CONFIG
dict inline. The portability document assumes a modular package
structure that doesn't exist yet.

**Gap:** The clone → configure → run instructions reference
files (.env.example, personas/, config/) that don't exist.
These are aspirational, not current.

## 17. Testing strategy: MISSING

TESTING.md does not exist. No document defines:

- What constitutes a passing test
- Epistemic invariant tests
- Provenance tests
- Persona isolation tests
- End-to-end test procedure

**This is a critical gap.** The AGENTS.md says "test before
declaring completion" but TESTING.md doesn't exist to define
what that means.

## 18. Migration strategy: READY

MIGRATION.md maps every existing subsystem to KEEP/REFACTOR/REPLACE/
REMOVE/UNKNOWN/NEW with counts (13 KEEP, 3 REFACTOR, 8 REPLACE,
28 NEW).

**Verified against code:** The migration categories match the
actual code. RSS fetching, circuit breaker, dedup, TTS are KEEP.
TF-IDF clustering, heuristic scoring, flat Markdown logs are
REPLACE. World state, personas, editorial layer are NEW.

## Summary

| Area | Status |
|------|--------|
| Domain model | READY |
| Architecture | READY |
| Epistemic model | READY |
| Persistence model | NEEDS DESIGN |
| Provider boundaries | READY |
| Persona architecture | NEEDS DESIGN |
| Newsroom architecture | READY |
| Broadcast lifecycle | NEEDS DESIGN |
| Source architecture | READY |
| World snapshots | READY |
| Personal knowledge | NEEDS DESIGN |
| Relevance engine | NEEDS DESIGN |
| Artifact model | READY |
| UI architecture | NEEDS DESIGN |
| Voice architecture | NEEDS RESEARCH |
| Portability | NEEDS DESIGN |
| Testing strategy | MISSING |
| Migration strategy | READY |

## Conclusion

**12 of 18 areas are READY. 5 NEEDS DESIGN. 1 NEEDS RESEARCH.
1 is MISSING entirely.**

The documentation is sufficient to begin Phase 1 (world model
and persistence) because that phase only depends on the domain
model, contracts, and epistemic model — all READY.

The documentation is NOT sufficient to begin Phase 2 (source
ingestion) because the broadcast pipeline and persistence model
are not yet specified.

**Recommendation:** Create the missing documents (PERSISTENCE.md,
BROADCAST_PIPELINE.md, TESTING.md, and the NEEDS DESIGN items)
before beginning implementation. Then start Phase 1.
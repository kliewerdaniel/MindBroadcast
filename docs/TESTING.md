# Testing Architecture: Broadcast Mind

## Test categories

### Unit tests
Domain logic — isolated, fast, deterministic.
- Story creation and status transitions
- Claim status transitions
- Evidence append-only semantics
- Correction chain integrity
- Entity deduplication
- Snapshot creation and comparison
- Relevance score computation
- Editorial score computation
- Queue ordering
- Epistemic category validation

### Integration tests
Persistence and provider boundaries.
- SQLite schema creation and migration
- WorldStore CRUD operations
- Source provider fetch and normalize
- TTS synthesis (mocked)
- LLM script generation (mocked)
- End-to-end: source → world → editorial → queue

### Epistemic tests
Ensure fact/claim/evidence/speculation
distinctions survive processing.
- Claim cannot become FACT without evidence
- Evidence without source URL is rejected
- Persona opinion cannot enter world state
- Generated text is tagged SYNTHETIC
- Speculation is labeled as speculation
- Unknown is not confused with false
- Confidence thresholds are configurable

### Provenance tests
Ensure source lineage survives transformations.
- Source URL preserved through ingestion
- Fetch timestamp preserved
- Extractor identity preserved
- Correction chain is auditable
- Evidence references are valid
- Story provenance traces to source

### Persona isolation tests
Ensure persona opinions cannot mutate world facts.
- Persona opinion write rejected by WorldStore
- Persona memory never enters world state
- World state unchanged after persona processing
- Persona opinions reference world claims but don't modify them
- Multiple personas can process same world state independently

### Queue tests
Ensure ordering and breaking-news behavior.
- Queue ordering by priority
- BREAKING gets next slot after current
- Starvation prevention (idle content)
- Queue persists across restarts
- Currently-speaking segment immutable
- Empty queue generates idle content

### Story continuity tests
Ensure multiple articles map to same story.
- Title similarity matching
- Entity overlap matching
- Duplicate detection (content hash)
- Story update detection
- Story status transitions
- Dead story revival
- Contradictory reporting handling

### Snapshot tests
Ensure world states can be saved and compared.
- Snapshot creation
- Snapshot comparison (diff)
- Snapshot restoration
- Snapshot immutability
- Snapshot with empty world state

### End-to-end tests
Source → world → editorial → script → TTS → archive.
- Full broadcast cycle
- Breaking story enters queue
- Idle content generation
- Correction workflow
- Multi-persona simulation
- Personal knowledge query

## Test infrastructure

- pytest as test runner
- pytest-asyncio for async tests
- SQLite in-memory for tests
- Mock Ollama for LLM tests
- Mock edge-tts for TTS tests
- Fixtures for common test data
- Factory pattern for entity creation

## Test data

- Seed stories with known properties
- Seed claims with known epistemic categories
- Seed evidence with known provenance
- Seed personas with known traits
- Seed sources with known reliability

## Test environment

- Isolated test database
- No network calls (mocked)
- Deterministic random seeds
- Fast execution (< 30s for full suite)
- CI-ready (GitHub Actions)

## Pass criteria

- All unit tests pass
- All integration tests pass
- All epistemic tests pass
- 80%+ code coverage on core modules
- No regressions in existing functionality

## What testing proves

1. Epistemic categories survive processing
2. World/persona separation is enforced
3. Provenance is preserved through transformations
4. Queue ordering is correct
5. Story continuity works across cycles
6. Snapshots are comparable and restorable
7. System operates end-to-end
8. Corrections are auditable and immutable
9. System admits uncertainty honestly
10. Synthetic content is always labeled
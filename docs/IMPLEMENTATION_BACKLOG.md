# Implementation Backlog: Broadcast Mind

## Backlog items

### B-001: SQLite world schema
- **Purpose:** Persistent world state tables
- **Dependencies:** None
- **Scope:** Schema creation, migration system
- **Acceptance:** All tables created, schema version tracked
- **Tests:** Schema integrity tests
- **Documentation:** PHASE_1.md
- **Status:** TODO

### B-002: WorldStore implementation
- **Purpose:** CRUD for world state with append-only semantics
- **Dependencies:** B-001
- **Scope:** WorldStore class, SQLite operations
- **Acceptance:** All CRUD ops work, append-only enforced
- **Tests:** Unit + integration tests
- **Documentation:** CONTRACTS.md
- **Status:** TODO

### B-003: Story and Event models
- **Purpose:** Story entity with events
- **Dependencies:** B-001, B-002
- **Scope:** Story/Event dataclasses, storage ops
- **Acceptance:** Stories created, events linked, status transitions
- **Tests:** Story lifecycle tests
- **Documentation:** STORY_LIFECYCLE.md
- **Status:** TODO

### B-004: Claim and Evidence models
- **Purpose:** Claim tracking with evidence
- **Dependencies:** B-001, B-002
- **Scope:** Claim/Evidence dataclasses, storage ops
- **Acceptance:** Claims with evidence, epistemic categories
- **Tests:** Epistemic invariant tests
- **Documentation:** EPISTEMIC_MODEL.md
- **Status:** TODO

### B-005: Entity extraction
- **Purpose:** Extract entities from articles
- **Dependencies:** B-001, B-002
- **Scope:** Entity extraction (LLM or regex-based)
- **Acceptance:** Entities extracted and stored
- **Tests:** Entity dedup tests
- **Documentation:** DOMAIN_MODEL.md
- **Status:** TODO

### B-006: RSS source provider
- **Purpose:** Fetch and normalize RSS feeds
- **Dependencies:** B-001
- **Scope:** SourceProvider implementation for RSS
- **Acceptance:** Feeds fetched, articles normalized
- **Tests:** Provider interface tests
- **Documentation:** SOURCES.md
- **Status:** TODO

### B-007: Content extraction
- **Purpose:** Clean article content with newspaper3k
- **Dependencies:** B-006
- **Scope:** Replace regex with newspaper3k
- **Acceptance:** Content extracted, HTML stripped
- **Tests:** Content extraction tests
- **Documentation:** LEGACY_SYSTEM.md
- **Status:** TODO

### B-008: Deduplication
- **Purpose:** Content-hash dedup against SQLite
- **Dependencies:** B-006
- **Scope:** Hash computation, cache check
- **Acceptance:** Duplicates detected and skipped
- **Tests:** Dedup tests
- **Documentation:** SOURCES.md
- **Status:** TODO

### B-009: Story tracking
- **Purpose:** Match articles to stories
- **Dependencies:** B-003, B-006
- **Scope:** Title similarity, entity overlap matching
- **Acceptance:** Articles matched to existing stories
- **Tests:** Story continuity tests
- **Documentation:** STORY_LIFECYCLE.md
- **Status:** TODO

### B-010: World snapshot
- **Purpose:** Save and compare world states
- **Dependencies:** B-001, B-002
- **Scope:** Snapshot creation, comparison, diff
- **Acceptance:** Snapshots created, diffs computed
- **Tests:** Snapshot tests
- **Documentation:** WORLD_SNAPSHOTS.md
- **Status:** TODO

### B-011: Default persona
- **Purpose:** Single persona with trait vector
- **Dependencies:** B-001
- **Scope:** Persona config, trait vector, persona store
- **Acceptance:** Persona created, traits stored
- **Tests:** Persona isolation tests
- **Documentation:** PERSONA_SYSTEM.md
- **Status:** TODO

### B-012: PersonaStore
- **Purpose:** Persona CRUD with opinion separation
- **Dependencies:** B-011
- **Scope:** PersonaStore implementation
- **Acceptance:** Personas CRUD, opinions separate from world
- **Tests:** Persona isolation tests
- **Documentation:** PERSONA_SYSTEM.md
- **Status:** TODO

### B-013: Editorial scoring
- **Purpose:** Score stories for broadcast
- **Dependencies:** B-003, B-004
- **Scope:** Importance, novelty, freshness, relevance scoring
- **Acceptance:** Stories scored, decisions explained
- **Tests:** Editorial score tests
- **Documentation:** EDITORIAL_MODEL.md
- **Status:** TODO

### B-014: Broadcast queue
- **Purpose:** Priority-ordered segment queue
- **Dependencies:** B-013
- **Scope:** Queue implementation, status lifecycle
- **Acceptance:** Queue ordering, breaking news handling
- **Tests:** Queue tests
- **Documentation:** QUEUE_MODEL.md
- **Status:** TODO

### B-015: Script generation
- **Purpose:** Generate broadcast scripts via Ollama
- **Dependencies:** B-014, B-011
- **Scope:** Script generation with persona context
- **Acceptance:** Scripts generated, persona voice present
- **Tests:** Script generation tests
- **Documentation:** BROADCAST_PIPELINE.md
- **Status:** TODO

### B-016: TTS synthesis
- **Purpose:** Convert scripts to audio
- **Dependencies:** B-015
- **Scope:** edge-tts integration, VoiceProvider interface
- **Acceptance:** Audio synthesized, artifacts stored
- **Tests:** TTS tests
- **Documentation:** VOICE.md
- **Status:** TODO

### B-017: Broadcast archival
- **Purpose:** Archive segments with full provenance
- **Dependencies:** B-016
- **Scope:** Artifact storage, metadata, correction support
- **Acceptance:** Segments archived, searchable
- **Tests:** Archive tests
- **Documentation:** ARTIFACTS.md
- **Status:** TODO

### B-018: Minimal UI
- **Purpose:** Live broadcast display
- **Dependencies:** B-014, B-016
- **Scope:** Live broadcast, transcript, queue, persona
- **Acceptance:** UI shows live state, SHOW ANALYSIS works
- **Tests:** UI integration tests
- **Documentation:** UI_INFORMATION_ARCHITECTURE.md
- **Status:** TODO

### B-019: Correction workflow
- **Purpose:** Correct previous claims
- **Dependencies:** B-004
- **Scope:** Correction records, chain integrity
- **Acceptance:** Corrections create new records, history preserved
- **Tests:** Correction tests
- **Documentation:** SELF_CORRECTION.md
- **Status:** TODO

### B-020: Idle content generation
- **Purpose:** Generate content when no breaking news
- **Dependencies:** B-014
- **Scope:** Retrospective, analysis, explainer, discovery
- **Acceptance:** Idle content generated when queue empty
- **Tests:** Idle content tests
- **Documentation:** SYNTHETIC_CONTENT.md
- **Status:** TODO

## Dependency ordering

```
B-001 → B-002 → B-003 → B-004 → B-005 → B-006 → B-007 → B-008 → B-009
                                                                          ↓
B-010 ← B-002                                    B-013 ← B-003, B-004
                                                        ↓
B-011 → B-012                                  B-014 ← B-013
                       ↓                              ↓
                   (parallel)                  B-015 ← B-014, B-011
                                              ↓
                                         B-016 ← B-015
                                          ↓
                                         B-017 ← B-016
                                          ↓
                                         B-018 ← B-014, B-016
                                          ↓
                                     B-019 ← B-004
                                          ↓
                                     B-020 ← B-014
```

## MVP slice (first 6 items)

B-001, B-002, B-003, B-004, B-006, B-008

This establishes:
- SQLite schema
- WorldStore with append-only semantics
- Story and Event persistence
- Claim and Evidence with epistemic categories
- RSS source provider
- Deduplication

Everything else builds on this foundation.
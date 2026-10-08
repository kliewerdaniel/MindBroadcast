# Phase 1 Implementation Plan: World Model and Persistence

> Concrete plan for building the persistent world foundation.
> Derived from the approved architecture in docs/plans/PHASE_1.md.

## Implementation strategy

The existing `main.py` is a working prototype. We will NOT
modify it directly. Instead we:

1. Create a new `core/` package with modular architecture
2. Archive `main.py` as reference (do not delete — LEGACY_SYSTEM.md
   says preserve it)
3. Build the world model on top of raw sqlite3 (no ORM —
   PERSISTENCE.md explicitly selected raw sqlite3 for MVP)
4. Append-only semantics enforced at the WorldStore interface level
5. Tests verify invariants, not just functionality

## Files to create

```
core/__init__.py              # Package init
core/models.py                # Domain model dataclasses + enums
core/persistence.py           # SQLite connection, schema creation, migrations
core/world_store.py           # WorldStore implementation
core/snapshot.py              # World snapshot creation + comparison
core/contracts.py             # Interface stubs (WorldStore)
tests/__init__.py             # Test package
tests/test_models.py          # Domain model tests
tests/test_persistence.py     # Schema + persistence tests
tests/test_world_store.py     # WorldStore CRUD tests
tests/test_epistemic.py       # Epistemic invariant tests
tests/test_snapshot.py        # Snapshot tests
tests/conftest.py             # Shared fixtures (in-memory DB)
requirements.txt              # Add: pytest, pytest-asyncio
```

## Files to modify

- `requirements.txt` — Add pytest, pytest-asyncio
- `docs/ROADMAP.md` — Update Phase 1 status to IN PROGRESS
- `docs/NEXT_STEP.md` — Update to reference Phase 1 completion

## Files to preserve (not modify)

- `main.py` — Archived as reference, not deleted
- `feeds.yaml` — Referenced by Phase 2
- `docs/` — All documentation, kept in sync

## Domain objects

### Enums (core/models.py)

```python
class StoryStatus(Enum):
    ACTIVE = "active"
    UPDATING = "updating"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"

class ClaimStatus(Enum):
    UNVERIFIED = "unverified"
    PARTIALLY_VERIFIED = "partially_verified"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"

class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"

class EpistemicCategory(Enum):
    FACT = "fact"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    ANALYSIS = "analysis"
    INTERPRETATION = "interpretation"
    SPECULATION = "speculation"
    FICTION = "fiction"
    SATIRE = "satire"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"
```

### Dataclasses (core/models.py)

Story, Event, Claim, Evidence, Entity, WorldSnapshot, Correction —
as defined in PHASE_1.md and DOMAIN_MODEL.md.

## Persistence layer (core/persistence.py)

- SQLite connection factory (WAL mode, foreign keys ON)
- Schema creation (all tables, indexes)
- Schema version table
- Raw sqlite3 (no ORM)
- Context manager for connections

### Tables

```sql
CREATE TABLE stories (
    story_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    first_seen TIMESTAMP NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    entity_ids TEXT DEFAULT '[]',     -- JSON list
    claim_ids TEXT DEFAULT '[]',      -- JSON list
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    corrected_by TEXT DEFAULT NULL,
    UNIQUE(story_id)
);

CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    fetched_at TIMESTAMP NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    published_at TIMESTAMP,
    extractor TEXT NOT NULL DEFAULT 'rss',
    entity_ids TEXT DEFAULT '[]',
    claim_ids TEXT DEFAULT '[]',
    epistemic_category TEXT NOT NULL DEFAULT 'unknown',
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    corrected_by TEXT DEFAULT NULL,
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
);

CREATE TABLE claims (
    claim_id TEXT PRIMARY KEY,
    claim_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unverified',
    confidence REAL DEFAULT 0.0,
    evidence_ids TEXT DEFAULT '[]',
    contradiction_ids TEXT DEFAULT '[]',
    source_url TEXT NOT NULL,
    extractor TEXT NOT NULL DEFAULT 'rss',
    created_at TIMESTAMP NOT NULL,
    corrected_by TEXT DEFAULT NULL,
    UNIQUE(claim_id)
);

CREATE TABLE evidence (
    evidence_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    extraction_method TEXT NOT NULL DEFAULT 'rss',
    extractor TEXT NOT NULL DEFAULT 'rss',
    reliability REAL DEFAULT 0.0,
    epistemic_category TEXT NOT NULL DEFAULT 'evidence',
    created_at TIMESTAMP NOT NULL,
    correction_of TEXT DEFAULT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL DEFAULT 'concept',
    aliases TEXT DEFAULT '[]',
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    mention_count INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(name, entity_type)
);

CREATE TABLE world_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    story_count INTEGER DEFAULT 0,
    claim_count INTEGER DEFAULT 0,
    evidence_count INTEGER DEFAULT 0,
    entity_count INTEGER DEFAULT 0,
    story_summaries TEXT DEFAULT '{}',     -- JSON
    claim_summaries TEXT DEFAULT '{}',     -- JSON
    diff_from_previous TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_events_story_id ON events(story_id);
CREATE INDEX idx_evidence_claim_id ON evidence(claim_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_stories_status ON stories(status);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_events_fetched_at ON events(fetched_at);
```

## WorldStore implementation (core/world_store.py)

Append-only enforcement:
- No UPDATE or DELETE methods on core tables
- Corrections create new records with `corrected_by` reference
- `correct_record()` inserts correction, marks original with `corrected_by`
- All "updates" are new INSERTs with correction chain

Methods:
```python
class WorldStore:
    def __init__(self, db_path: str = "data/world.db")
    
    # Story operations
    async def add_story(self, story: Story) -> str
    async def get_story(self, story_id: str) -> Optional[Story]
    async def list_stories(self, filter: StoryFilter) -> List[Story]
    async def update_story_status(self, story_id: str, status: StoryStatus) -> None
    
    # Event operations
    async def add_event(self, event: Event) -> str
    async def get_events_for_story(self, story_id: str) -> List[Event]
    
    # Claim operations
    async def add_claim(self, claim: Claim) -> str
    async def get_claim(self, claim_id: str) -> Optional[Claim]
    async def list_claims(self, filter: ClaimFilter) -> List[Claim]
    
    # Evidence operations
    async def add_evidence(self, evidence: Evidence) -> str
    async def get_evidence_for_claim(self, claim_id: str) -> List[Evidence]
    
    # Entity operations
    async def add_entity(self, entity: Entity) -> str
    async def get_entity(self, entity_id: str) -> Optional[Entity]
    async def list_entities(self) -> List[Entity]
    
    # Correction
    async def correct_record(self, record_id: str, correction: Correction) -> str
    
    # Snapshots
    async def create_snapshot(self) -> WorldSnapshot
    async def compare_snapshots(self, a: str, b: str) -> SnapshotDiff
    async def get_snapshot(self, snapshot_id: str) -> Optional[WorldSnapshot]
    async def list_snapshots(self) -> List[WorldSnapshot]
```

## World snapshot (core/snapshot.py)

```python
class SnapshotService:
    def __init__(self, world_store: WorldStore)
    
    async def create_snapshot(self) -> WorldSnapshot
    async def compare_snapshots(self, a_id: str, b_id: str) -> SnapshotDiff
    async def get_latest_snapshot(self) -> Optional[WorldSnapshot]
```

Snapshot diff compares:
- Story count delta
- Claim count delta
- Evidence count delta
- Entity count delta
- New stories, resolved stories
- Claim status changes
- New entities

## Contracts (core/contracts.py)

Interface stubs matching CONTRACTS.md:

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class WorldStore(ABC):
    @abstractmethod
    async def add_story(self, story) -> str: ...
    @abstractmethod
    async def get_story(self, story_id: str) -> Optional: ...
    @abstractmethod
    async def list_stories(self, filter) -> List: ...
    @abstractmethod
    async def add_event(self, event) -> str: ...
    @abstractmethod
    async def add_claim(self, claim) -> str: ...
    @abstractmethod
    async def add_evidence(self, evidence) -> str: ...
    @abstractmethod
    async def add_entity(self, entity) -> str: ...
    @abstractmethod
    async def correct_record(self, record_id: str, correction) -> str: ...
    @abstractmethod
    async def create_snapshot(self) -> WorldSnapshot: ...
    @abstractmethod
    async def compare_snapshots(self, a: str, b: str) -> SnapshotDiff: ...
```

## Tests

### tests/conftest.py
- In-memory SQLite for all tests
- Fresh WorldStore per test
- Shared fixtures: sample stories, claims, evidence, entities

### tests/test_models.py
- Dataclass creation
- Enum values
- Epistemic category values
- StoryStatus transitions
- ClaimStatus transitions
- EntityType values

### tests/test_persistence.py
- Schema creation (all tables present)
- Schema version tracking
- WAL mode enabled
- Foreign key enforcement
- Index creation

### tests/test_world_store.py
- add_story / get_story
- add_event / get_events_for_story
- add_claim / get_claim
- add_evidence / get_evidence_for_claim
- add_entity / get_entity
- correct_record (old record preserved, new record created)
- append-only enforcement (UPDATE rejected)
- list_stories with filter
- list_claims with filter

### tests/test_epistemic.py
- Claim cannot become FACT without evidence
- Evidence without source_url rejected
- Epistemic categories enforced
- Confidence range validation (0.0–1.0)

### tests/test_snapshot.py
- Snapshot creation
- Snapshot comparison (diff)
- Snapshot with empty world state
- Snapshot immutability

## Migration strategy

### news08 → Broadcast Mind Phase 1

1. `main.py` archived as `legacy/main.py` (preserved, not modified)
2. `news_cache.db` (news08 SQLite) preserved — NOT imported
3. New `data/world.db` created fresh by Phase 1 code
4. Article cache data stays in `news_cache.db` — can be referenced
   by Phase 2 but NOT imported into world schema
5. feeds.yaml referenced by Phase 2 — not modified

### No data migration needed

Phase 1 creates a new empty world. The old article cache is
preserved but not imported. Story identity will be established
in Phase 2 when source ingestion begins.

## Non-goals (reinforced)

- No source ingestion (Phase 2)
- No persona system (Phase 4)
- No editorial engine (Phase 5)
- No broadcast queue (Phase 6)
- No script generation (Phase 7)
- No TTS (Phase 8)
- No UI (Phase 9)
- No semantic embeddings (Phase 2+)
- No multi-persona support (Phase 4+)
- No self-correction automation (Phase 10+)

## Acceptance criteria

1. `core/` package with all modules present
2. SQLite schema created with all 7 tables + indexes
3. WorldStore CRUD operations functional
4. Append-only semantics enforced (UPDATE rejected)
5. Corrections create new records, old preserved
6. Snapshots created and compared
7. All 5 test files pass
8. Epistemic invariants enforced in data model
9. Legacy main.py preserved as reference
10. docs/ROADMAP.md updated with Phase 1 status
11. docs/NEXT_STEP.md updated
12. docs/plans/PHASE_1_IMPLEMENTATION.md exists (this file)

## Deviations from original plan (to document as they occur)

None expected at start. Any deviation will be recorded here
and an ADR added to docs/DECISIONS.md.

## Rollback

- Delete `data/world.db`
- Remove `core/` package
- Restore main.py from archive if needed
- No migration needed (fresh schema)
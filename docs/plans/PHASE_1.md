# Phase 1: World Model and Persistence

> Establish the persistent world foundation. Everything
> else depends on this.

## Objective

Create the persistent world model with SQLite storage,
append-only semantics, and correction support. This is
the data foundation for all subsequent phases.

## Scope

- World state schema (stories, events, claims, evidence, entities)
- SQLite persistence with append-only writes
- Correction mechanism (new record supersedes old)
- World snapshot creation and comparison
- Basic CRUD for world state operations
- World store interface (WorldStore contract)

## Non-goals

- Source ingestion (that's Phase 2)
- Persona system (Phase 4)
- Editorial engine (Phase 5)
- Broadcast queue (Phase 6)
- Script generation (Phase 7)
- TTS (Phase 8)
- UI (Phase 9)
- Semantic embeddings (Phase 2+)
- Multi-persona support (Phase 4+)
- Self-correction automation (Phase 10+)

## Files likely to change

### New modules
```
core/world_store.py        # WorldStore implementation
core/persistence.py        # SQLite connection, schema, migrations
core/models.py             # Domain model dataclasses
core/snapshot.py           # World snapshot creation/comparison
core/contracts.py          # Interface definitions (stubs)
```

### Existing files
```
main.py                    # Will be archived / replaced (not modified)
feeds.yaml                 # Referenced by Phase 2, not modified
requirements.txt           # Add: SQLAlchemy, networkx (for later)
```

### Preserved from news08
```
main.py                    → Archived as reference, not modified
feeds.yaml                 → Referenced by Phase 2
requirements.txt           → Extended, not replaced
```

## Data structures

### Story
```python
@dataclass
class Story:
    story_id: str            # UUID
    title: str               # Narrative thread title
    summary: str             # Current best summary
    status: StoryStatus      # ACTIVE / UPDATING / RESOLVED / ABANDONED
    first_seen: datetime     # First article timestamp
    last_updated: datetime   # Most recent evidence timestamp
    entity_ids: List[str]    # Entities mentioned in this story
    claim_ids: List[str]     # Claims associated with this story
    confidence: float        # 0.0–1.0, derived from evidence
    created_at: datetime
    corrected_by: Optional[str]  # Reference to correcting record
```

### Event
```python
@dataclass
class Event:
    event_id: str
    story_id: str            # Parent story
    source_url: str          # Origin article URL
    fetched_at: datetime     # When fetched
    title: str               # Article title
    content: str             # Cleaned article content
    published_at: Optional[datetime]  # Article publish time (not fetch time)
    extractor: str           # Which provider extracted this
    entity_ids: List[str]    # Entities mentioned
    claim_ids: List[str]     # Claims extracted
    epistemic_category: EpistemicCategory  # FACT/CLAIM/UNKNOWN
    confidence: float
    created_at: datetime
    corrected_by: Optional[str]
```

### Claim
```python
@dataclass
class Claim:
    claim_id: str
    claim_text: str          # Immutable — the asserted statement
    status: ClaimStatus      # UNVERIFIED / PARTIALLY_VERIFIED / VERIFIED / CONTRADICTED
    confidence: float        # 0.0–1.0
    evidence_ids: List[str]  # Supporting evidence
    contradiction_ids: List[str]  # Contradicting evidence
    source_url: str
    extractor: str
    created_at: datetime
    corrected_by: Optional[str]
```

### Evidence
```python
@dataclass
class Evidence:
    evidence_id: str
    claim_id: str            # What this supports/contradicts
    source_url: str
    content: str             # Extracted content or summary
    extraction_method: str   # "rss_summary", "web_search", "user_document"
    extractor: str           # Which analyst/provider
    reliability: float       # Source reliability × extraction confidence
    epistemic_category: EpistemicCategory
    created_at: datetime
    correction_of: Optional[str]  # If this corrects previous evidence
```

### Entity
```python
@dataclass
class Entity:
    entity_id: str
    name: str                # Canonical name
    entity_type: EntityType  # PERSON / ORGANIZATION / LOCATION / CONCEPT
    aliases: List[str]       # Alternative names
    first_seen: datetime
    last_seen: datetime
    mention_count: int
    created_at: datetime
```

### WorldSnapshot
```python
@dataclass
class WorldSnapshot:
    snapshot_id: str
    timestamp: datetime
    story_count: int
    claim_count: int
    evidence_count: int
    entity_count: int
    story_summaries: Dict[str, str]  # story_id → summary
    claim_summaries: Dict[str, str]  # claim_id → status+confidence
    diff_from_previous: Optional[str]  # Human-readable diff
    created_at: datetime
```

## Persistence requirements

- SQLite database file: `data/world.db`
- Append-only tables: no UPDATE on core records, only INSERT
- Corrections reference previous records via `corrected_by` field
- Schema version table for migrations
- WAL mode for concurrent read/write
- Backup: copy database file

## Interfaces

### WorldStore (contract)
```python
class WorldStore:
    async def add_story(self, story: Story) -> str
    async def get_story(self, story_id: str) -> Optional[Story]
    async def list_stories(self, filter: StoryFilter) -> List[Story]
    async def add_event(self, event: Event) -> str
    async def add_claim(self, claim: Claim) -> str
    async def add_evidence(self, evidence: Evidence) -> str
    async def add_entity(self, entity: Entity) -> str
    async def correct_record(self, record_id: str, correction: Correction) -> str
    async def create_snapshot(self) -> WorldSnapshot
    async def compare_snapshots(self, a: str, b: str) -> SnapshotDiff
    async def get_claim(self, claim_id: str) -> Optional[Claim]
    async def get_evidence_for_claim(self, claim_id: str) -> List[Evidence]
```

## Migration considerations

- news08 SQLite cache (`data/news_cache.db`) has article dedup data
- Article cache can be referenced but NOT imported into world schema
- Article content hashes can inform dedup but not story identity
- Migration: read article cache for reference only, write new world tables

## Tests

### Unit tests
- Story creation and status transitions
- Event linking to story
- Claim status transitions (UNVERIFIED → PARTIALLY_VERIFIED → VERIFIED/CONTRADICTED)
- Evidence append-only semantics (no UPDATE allowed)
- Correction creates new record, old record preserved
- Entity deduplication by name + type
- Snapshot creation and comparison

### Integration tests
- SQLite schema creation and migration
- WorldStore CRUD operations
- Append-only enforcement (attempting UPDATE raises error)
- Correction chain integrity (corrected_by references valid record)
- Snapshot diff produces meaningful output

### Epistemic tests
- Claim cannot become FACT without sufficient evidence
- Evidence without source URL is rejected
- Persona opinion cannot enter world state

## Acceptance criteria

1. SQLite database created with correct schema
2. Stories, events, claims, evidence, entities all persist
3. Append-only semantics enforced at interface level
4. Corrections create new records, old ones preserved
5. Snapshots can be created and compared
6. All unit and integration tests pass
7. Epistemic invariants hold (see EPISTEMIC_INVARIANTS.md)
8. WorldStore interface matches CONTRACTS.md specification

## Verification procedure

1. Run `pytest tests/test_world_store.py` — all pass
2. Run `pytest tests/test_persistence.py` — all pass
3. Run `pytest tests/test_epistemic.py` — all pass
4. Inspect database: `sqlite3 data/world.db ".tables"` — all 5+ tables present
5. Verify append-only: attempt UPDATE on evidence table — must fail or be rejected
6. Verify correction: create claim, correct it, confirm both records exist
7. Verify snapshot: create snapshot, compare with empty, confirm diff

## Rollback strategy

- Delete `data/world.db` and restart (fresh schema)
- No migration path needed (Phase 1 is first schema)
- If schema changes in Phase 2, migration script in `core/migrations/`
- Backup: `cp data/world.db data/world.db.bak`

## Dependencies

- SQLite (stdlib)
- SQLAlchemy 2.0+ (async) — TBD, could be raw sqlite3 for MVP
- UUID generation (stdlib)
- Pydantic or dataclasses for model validation — TBD
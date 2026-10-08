# Persistence Model: Broadcast Mind

## What must persist and why

### World state (relational)

| Entity | Storage | Why |
|--------|---------|-----|
| Story | SQLite | Queryable, relational, needs joins |
| Event | SQLite | Immutable, append-only, linked to stories |
| Claim | SQLite | Status transitions, evidence links |
| Evidence | SQLite | Append-only, immutable, source links |
| Entity | SQLite | Dedup by name+type, graph relationships |
| Timeline | Computed | Derived from events, not stored |
| Correction | SQLite | Append-only, references corrected record |
| WorldSnapshot | SQLite + JSON | Metadata relational, content as JSON blob |

### Persona data (relational)

| Entity | Storage | Why |
|--------|---------|-----|
| Persona definition | SQLite | Configuration, trait vector |
| PersonaMemory | SQLite | Append-only, persona-scoped |
| PersonaOpinion | SQLite | Mutable, versioned, persona-scoped |
| PersonaExperience | SQLite | Immutable, persona-scoped |
| PersonaSession | SQLite | Continuity across broadcast cycles |

### Broadcast artifacts (files + relational metadata)

| Entity | Storage | Why |
|--------|---------|-----|
| Script | File (Markdown) | Human-readable, versionable |
| Transcript | File (text) | Searchable, diffable |
| Audio | File (MP3/OGG) | Binary, large |
| BroadcastSegment metadata | SQLite | Queryable, linked to files |
| BroadcastHistory | SQLite | Immutable, append-only |
| EditorialDecision | SQLite | Audit trail |

### Configuration (files)

| Entity | Storage | Why |
|--------|---------|-----|
| Source configuration | YAML | Human-editable, versionable |
| Persona definitions | YAML/JSON | Human-editable, versionable |
| Environment variables | .env | Sensitive values |
| Feeds/sources | YAML | Retained from news08 |

## Why SQLite for system-of-record

### Confirmed by news08
- news08 already uses SQLite for article caching
- SQLite works on both primary and secondary machines
- Zero infrastructure, no server process
- WAL mode supports concurrent reads

### Why not other options
- **PostgreSQL**: Overkill for single-user, requires server
- **MongoDB**: Document model doesn't fit relational world state
- **File-based JSON**: Not queryable, no transactions
- **Vector DB**: Only for embedding similarity — separate concern

### ORM vs raw SQL

For MVP, raw sqlite3 is sufficient. SQLAlchemy adds
complexity without benefit at this scale. Upgrade to
SQLAlchemy if:
- Migration support needed
- Complex queries require ORM
- Multi-table transactions become error-prone

Decision: raw sqlite3 for MVP, evaluate SQLAlchemy in
Phase 2 if needed.

## What should eventually be vectorized

| Data | Vectorize? | When |
|------|-----------|------|
| Article content | Yes | Phase 2 — story matching |
| Claims | Yes | Phase 3 — similarity search |
| Entity names | Yes | Phase 2 — dedup |
| Persona memories | Maybe | Phase 4 — relevance |
| Broadcast transcripts | Maybe | Phase 10 — search |

Vectorization uses nomic-embed-text via Ollama. Not
required for MVP.

## What needs graph relationships

| Relationship | Implementation | When |
|-------------|---------------|------|
| Story → Events | Foreign key | MVP (Phase 1) |
| Claim → Evidence | Foreign key | MVP (Phase 1) |
| Entity → Stories | Join table | Phase 2 |
| Claim → Entity | Join table | Phase 2 |
| Story → Story (similar) | Computed | Phase 10 |
| Persona → Opinions | Foreign key | Phase 4 |
| Evidence → Evidence (contradicts) | Join table | Phase 3 |

Graph queries use SQL JOINs for MVP. NetworkX or graph
DB only if relationship traversal becomes complex.

## What needs versioning

| Entity | Versioned? | How |
|--------|-----------|-----|
| Story | Yes | Status + corrected_by chain |
| Claim | Yes | Status history + corrected_by |
| Evidence | No (immutable) | Append-only |
| Entity | Yes | Attribute change history |
| PersonaOpinion | Yes | Versioned records |
| WorldSnapshot | N/A (immutable) | Each snapshot is a version |
| EditorialDecision | Yes | Decision history |
| BroadcastSegment | Yes | Archive versioning |

## What needs provenance

Every record in world state must carry:

- source_url (where information came from)
- extracted_at (when extracted)
- extractor (which provider/analyst)
- confidence (system confidence)
- epistemic_category (FACT/CLAIM/EVIDENCE/etc.)
- correction_of (if correcting previous record)

## What can be reconstructed

- Timeline: derived from Events
- Story summary: generated from Events + Claims
- HistoricalSummary: generated from WorldSnapshots
- Entity graph: derived from Story + Claim relationships
- BroadcastHistory: assembled from BroadcastSegments

Reconstruction is preferred over storage where possible.
Derived data is computed on demand and cached.

## Persistence layout

```
data/
├── world.db              # SQLite — world state
├── persona.db            # SQLite — persona data (separate for isolation)
├── archive/              # Broadcast artifacts
│   ├── scripts/          # Markdown scripts
│   ├── transcripts/      # Text transcripts
│   ├── audio/            # Audio files (with retention policy)
│   └── metadata/         # JSON metadata for each segment
├── snapshots/            # World snapshot JSON exports
└── backups/              # Database backups
```

## Schema design principles

1. Append-only core tables — no UPDATE on facts
2. Corrections reference, don't delete
3. Foreign keys with CASCADE for derived data
4. Indexes on frequently-queried fields (story_id, claim_id, entity_id)
5. Timestamps on every table for audit
6. UUID primary keys for stable references
7. JSON blob for flexible snapshot content
8. Schema version table for migrations
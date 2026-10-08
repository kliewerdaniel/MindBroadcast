# Next Step: Broadcast Mind

## What is the smallest correct implementation?

**Phase 1: World model and persistence.**

## Objective

Create the persistent world foundation:
SQLite schema, WorldStore with append-only
semantics, Story/Event/Claim/Evidence/Entity
models, correction mechanism, and world
snapshot capability.

## Files/modules involved

### New modules
```
core/world_store.py        # WorldStore implementation
core/persistence.py        # SQLite connection, schema, migrations
core/models.py             # Domain model dataclasses
core/snapshot.py           # World snapshot creation/comparison
core/contracts.py          # Interface definitions (stubs)
```

### Preserved
```
main.py                    → Archived as reference, not modified
feeds.yaml                 → Referenced by Phase 2
requirements.txt           → Extended, not replaced
```

## Contracts involved

- WorldStore (CRUD + append-only + corrections + snapshots)
- SourceProvider (stub — full impl in Phase 2)

## Tests required

- Schema creation and migration
- WorldStore CRUD operations
- Append-only enforcement (UPDATE rejected)
- Correction chain integrity
- Snapshot creation and comparison
- Epistemic invariant tests
- Entity deduplication

## Acceptance criteria

1. SQLite database created with correct schema
2. Stories, events, claims, evidence, entities all persist
3. Append-only semantics enforced at interface level
4. Corrections create new records, old ones preserved
5. Snapshots can be created and compared
6. All unit and integration tests pass
7. Epistemic invariants hold
8. WorldStore interface matches CONTRACTS.md

## What must NOT be built yet

- Source ingestion (Phase 2)
- Persona system (Phase 4)
- Editorial engine (Phase 5)
- Broadcast queue (Phase 6)
- Script generation (Phase 7)
- TTS (Phase 8)
- UI (Phase 9)
- Semantic embeddings (Phase 2+)
- Multi-persona support (Phase 4+)
- Self-correction automation (Phase 10+)

## Why this is the correct first slice

1. Everything else depends on world state
2. No external dependencies beyond SQLite
3. Append-only semantics is the core architectural invariant
4. Testing is straightforward (no mocks needed)
5. Foundation for all subsequent phases
6. Domain model is specified and verified
7. Contracts are defined and stable
8. Persistence model is specified in PERSISTENCE.md
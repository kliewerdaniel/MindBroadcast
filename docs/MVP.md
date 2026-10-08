# Minimum Viable Architecture: Broadcast Mind

> The smallest system that demonstrates the central idea:
> a local-first artificial newsroom with a persistent world
> model, synthetic personas, and an audible broadcast.

## Central idea

The user wakes up, turns on the system, and hears what
matters — with evidence, uncertainty, and continuity.

## MVP must demonstrate

1. Real news retrieval
2. Persistent story storage
3. Story tracking over time
4. Evidence and provenance
5. World state
6. At least one persona
7. World/persona separation
8. Relevance selection
9. Broadcast segment generation
10. Speech synthesis
11. Queue management
12. Broadcast archival
13. Minimal UI

## MUST HAVE FOR MVP

### World model
- Story entity with title, summary, first_seen, last_updated
- Event entity (one per source article) linked to a Story
- Claim entity with epistemic category (FACT/CLAIM/UNKNOWN)
- Evidence entity referencing source URL and fetch time
- Entity (person/org/location) extracted from articles
- Append-only correction mechanism (new record supersedes old)

### Source ingestion
- RSS provider (retained from news08, feeds.yaml)
- Content extraction using newspaper3k (not regex)
- Content-hash deduplication against SQLite
- Source identity and reliability score

### Story tracking
- Article-to-story matching by title similarity + entity overlap
- Story status: active / updating / resolved / abandoned
- Story update detection (new article same story = update, not duplicate)

### Persona system
- Single default persona with trait vector (identity, cognitive style, values)
- Persona opinions stored separately from world facts
- Persona-aware script generation (personality influences tone, not content)

### Editorial queue
- Story scoring: importance + novelty + continuity
- Segment types: breaking, update, analysis, retrospective
- Non-preemptive: new breaking story queues for next slot
- Idle content when no breaking news (retrospective from recent stories)

### Broadcast
- Script generation via Ollama (story + persona + evidence context)
- Edge-TTS for audio
- Segment archival: script + transcript + audio reference + metadata

### Persistence
- SQLite for all world state (stories, events, claims, evidence, entities, personas)
- Append-only writes; corrections create new records
- World snapshot on demand

### UI
- Live broadcast display (current segment, transcript, persona)
- Next queue display
- "SHOW ANALYSIS" toggle for evidence and reasoning

## SHOULD HAVE AFTER MVP

- Multiple personas with disagreement display
- Semantic embeddings (nomic-embed-text) for clustering
- Web search source provider
- Personal knowledge ingestion
- Relevance engine with learned behavior
- Continuous learning from user interaction
- Broadcast history search
- Correction broadcasts ("we said X, now Y")
- Persona evolution (evidence-driven trait shifts)

## FUTURE

- Multi-persona simulation / God Mode
- User document/repo ingestion
- Full editorial decision explanation ("why this story?")
- Scenario / "what if" analysis
- Graph visualization (world graph, story graph)
- Voice per persona
- Provider pluggability for TTS and LLM
- Docker deployment

## EXPERIMENTAL

- Self-correction automation (system discovers its own errors)
- Synthetic content generation (thought experiments, fiction)
- Multi-agent newsroom with separate researcher/fact-checker/editor agents
- Voice cloning for personas
- Real-time breaking news interruption
- Offline queue with deferred sync

## What MVP does NOT do

- No web search
- No personal knowledge ingestion
- No multiple personas
- No semantic embeddings (TF-IDF fallback)
- No continuous learning
- No correction broadcasts
- No graph visualization
- No Docker deployment
- No multi-user support
- No voice per persona (single voice)
- No research/satire/fiction classification
- No scenario analysis

## MVP success criteria

1. System fetches RSS, stores stories persistently, tracks across cycles
2. World state is append-only; corrections create new records
3. Persona opinions cannot mutate world facts (enforced by interface)
4. Broadcast segments include script + transcript + audio + metadata
5. Queue shows next segment; breaking stories queue non-preemptively
6. UI shows live broadcast, transcript, persona, next queue
7. Archive allows replay of past broadcasts with full provenance
8. Another engineer can clone, configure, and run the system
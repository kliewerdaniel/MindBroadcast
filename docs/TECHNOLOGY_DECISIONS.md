# Technology Decisions: Broadcast Mind

## Current stack inventory

| Technology | Status | Rationale |
|------------|--------|-----------|
| Python | KEEP | Core language, all dependencies available |
| SQLite | KEEP | Proven in news08, local-first, zero-config |
| Ollama | KEEP | Local LLM inference, already integrated |
| RSS | KEEP | Primary source for MVP |
| aiohttp | KEEP | Async HTTP for feed fetching |
| feedparser | KEEP | RSS parsing, proven |
| scikit-learn | REPLACE | TF-IDF → semantic embeddings (Phase 2+) |
| NLTK | REPLACE | Sentiment analysis → editorial signal (Phase 3+) |
| pydub | KEEP | Audio processing (if needed) |
| edge-tts | KEEP | TTS for MVP, provider pluggability later |
| newspaper3k | KEEP | Content extraction (replaces regex) |
| pyyaml | KEEP | Configuration parsing |
| tqdm | KEEP | Progress display |
| lxml | KEEP | HTML parsing for feedparser |
| openai | DEPRECATE | Not used in current code, remove from requirements |
| requests | KEEP | HTTP fallback |
| gradio | REMOVE | In requirements but not used in main.py |
| textblob | REMOVE | In requirements but not used in main.py |
| spacy | REMOVE | In requirements but not used in main.py |

## Dependency changes for MVP

### Add
- SQLAlchemy 2.0+ (async ORM, optional for MVP)
- networkx (graph operations, Phase 2)
- numpy (vector operations, Phase 2+)
- pytest + pytest-asyncio (testing)

### Remove
- openai (not used)
- gradio (not used)
- textblob (not used)
- spacy (not used)

### Keep
- feedparser, aiohttp, pyyaml, edge-tts, lxml, tqdm, ollama, requests
- newspaper3k, scikit-learn (TF-IDF fallback)
- NLTK (VADER for sentiment, Phase 3+)
- pydub (audio processing)

## Technology principles

1. **Local-first** — No cloud dependencies for core
2. **Lightweight** — Must run on secondary machine
3. **Provider-pluggable** — Interfaces allow swapping
4. **Proven over fashionable** — Don't replace working tech
5. **Minimal dependencies** — Avoid unnecessary packages
6. **Async by default** — aiohttp for I/O, asyncio for tasks

## Provider boundaries

| Provider | Interface | Swappable? |
|----------|-----------|------------|
| LLM | Ollama REST API | Yes — any Ollama model |
| TTS | edge-tts → VoiceProvider | Yes — pluggable interface |
| RSS | feedparser → SourceProvider | Yes — any feed |
| Search | None yet | TBD |
| Embeddings | nomic-embed-text | Yes — Ollama-based |
| Database | SQLite | Yes — any SQL backend |

## Hardware considerations

Primary machine:
- Can run mistral-small:24b (16GB+ RAM)
- Can run nomic-embed-text
- Can run edge-tts

Secondary machine:
- Limited RAM — lighter model needed
- Piper or lightweight TTS candidate
- Still runs Ollama (smaller model)

The system must auto-detect hardware
and select appropriate providers.

## Technology decisions to make

1. SQLAlchemy vs raw sqlite3 — NEEDS EXPERIMENT
2. Embedding model — nomic-embed-text candidate, NEEDS VERIFICATION
3. TTS on secondary machine — NEEDS RESEARCH (piper vs edge-tts)
4. Web search provider — NEEDS RESEARCH (DuckDuckGo? SearXNG?)
5. Agent runtime — subprocess vs threading vs async — NEEDS DESIGN
6. Graph implementation — NetworkX vs custom — NEEDS RESEARCH
7. Queue persistence — SQLite-backed vs in-memory — NEEDS DESIGN
8. Deployment strategy — systemd vs Docker vs bare — NEEDS DECISION
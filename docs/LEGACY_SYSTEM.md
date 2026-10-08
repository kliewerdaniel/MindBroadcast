# Legacy System: news08

## What the existing system provides

news08 is a single Python script (~772 lines)
implementing an automated continuous news
broadcast generator.

### RSS ingestion
- `fetch_feeds_batch` — async batch fetching
- `fetch_single_feed` — single feed fetch
- feedparser-based RSS/Atom parsing
- 23 RSS feeds in feeds.yaml

### HTML cleaning
- `extract_content` — regex-based HTML stripping
- Falls back to title when content empty

### Deduplication
- Content hash against SQLite `articles` table
- 3-day TTL on cached articles
- `is_duplicate` / `cache_article` methods

### Summarization
- Ollama `mistral-small:24b-instruct-2501-q8_0`
- REST API via aiohttp
- `generate_summary_safe` with circuit breaker

### Relevancy scoring
- LLM-based 0–10 score against `--topic` filter
- `calculate_relevancy_score`

### Sentiment analysis
- NLTK VADER sentiment intensity
- Used in importance scoring

### Importance scoring
- Freshness (40%) + content quality (30%)
  + sentiment (20%) + readability (10%)
- `calculate_importance_scores`

### TF-IDF clustering
- scikit-learn TfidfVectorizer + KMeans
- `cluster_articles_tfidf`
- Groups similar articles into topics

### Script generation
- Ollama broadcast model
- Anchor-style 5-6 sentence segments
- `generate_segment_script`

### TTS
- edge-tts with `en-US-JennyNeural`
- Async audio queue with playback thread
- `generate_and_queue_audio` / `play_audio_from_queue`

### Queue-based playback
- Audio queue with thread-based playback
- Non-blocking generation

### SQLite caching
- `news_cache.db` for article dedup
- `articles` table with content_hash

### Circuit breaker
- 3-failure threshold, 30s recovery
- `CircuitBreaker` class

### Performance monitoring
- `PerformanceMonitor` tracks:
  - Articles processed
  - Processing times
  - API call success rates

### Logging
- File + console logging
- Broadcast logs saved as Markdown

### CLI arguments
- `--topic` — relevance filter
- `--guidance` — script tone guidance
- `--fetch_interval` — cycle interval
- `--feeds` — custom feeds file

### Configuration
- CONFIG dict with:
  - Ollama API URL
  - Model names
  - Processing parameters
  - Output settings

## What's useful to retain

- RSS fetching architecture (aiohttp + feedparser)
- Ollama integration pattern (REST API calls)
- Circuit breaker pattern
- Content hash deduplication approach
- Edge-tts for TTS
- Performance monitoring skeleton
- Logging infrastructure
- CLI argument parsing
- Article dataclass (clean seed for Story)
- BroadcastSegment dataclass (seed for segment model)

## What's obsolete

- `extract_content` regex HTML stripping → newspaper3k
- `target_segments: 2500` — impossibly high, placeholder
- `max_broadcast_length: 900000000` — effectively unbounded
- `relevancy_threshold: 5` — hard-coded magic number
- TF-IDF clustering → semantic embeddings
- Heuristic importance scoring → editorial engine
- Flat Markdown logs → structured artifact archive
- Single-file architecture → modular package
- No world state → persistent world model
- No persona concept → persona system
- No epistemic categories → fact/claim/evidence model
- No story tracking → story continuity
- No correction mechanism → append-only corrections
- No broadcast history → artifact archive
- No source reliability tracking → source scoring

## What's valuable research

- Circuit breaker in async context (works, needs integration)
- Ollama REST API pattern (proven)
- edge-tts on macOS (proven)
- feedparser reliability (proven)
- Content hash dedup (proven)
- Importance scoring heuristic (foundation, needs replacement)
- Relevancy scoring LLM pattern (foundation, needs replacement)

## Migration targets

| news08 component | Broadcast Mind destination |
|-----------------|---------------------------|
| fetch_feeds_batch | SourceProvider (RSS) |
| fetch_single_feed | SourceProvider (RSS) |
| extract_content | Content extraction (newspaper3k) |
| is_duplicate | Deduplication service |
| cache_article | SQLite article cache → world state |
| generate_summary_safe | Analyst capability |
| calculate_relevancy_score | RelevanceEngine |
| cluster_articles_tfidf | StoryTracker (semantic) |
| calculate_importance_scores | EditorialEngine |
| generate_segment_script | ScriptGenerator |
| generate_and_queue_audio | VoiceProvider + BroadcastQueue |
| play_audio_from_queue | Broadcast output |
| CircuitBreaker | CircuitBreaker (retained) |
| PerformanceMonitor | Monitoring (retained) |
| CONFIG dict | Configuration service |
| main.py | Archived → core/ package |
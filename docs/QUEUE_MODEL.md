# Broadcast Queue Model: Broadcast Mind

## Queue semantics

The queue is an ordered list of broadcast
segments with priority-based ordering and
non-preemptive execution.

## Segment lifecycle

```
PROPOSED
  → SELECTED (editorial decision)
  → SCRIPTING (script generated)
  → READY (script + voice ready)
  → SPEAKING (currently playing)
  → COMPLETED (finished playback)
  → ARCHIVED (stored with provenance)
```

## Segment data model

```python
@dataclass
class BroadcastSegment:
    segment_id: str
    story_id: Optional[str]     # Which story this covers
    persona_id: str             # Which persona speaks
    world_snapshot_id: str      # World state at generation time
    segment_type: SegmentType   # BREAKING/UPDATE/ANALYSIS/etc.
    priority: float             # Editorial score + type bonus
    script: Optional[str]       # Generated script text
    transcript: Optional[str]   # Spoken transcript (post-TTS)
    audio_path: Optional[str]   # Audio file path
    evidence: List[str]         # Evidence IDs used
    analysis: Optional[str]     # Analyst evaluation
    editorial_decision_id: str  # Why this segment was chosen
    status: SegmentStatus       # Lifecycle stage
    created_at: datetime
    scheduled_at: datetime      # When it should play
    spoken_at: Optional[datetime]
    completed_at: Optional[datetime]
    archived_at: Optional[datetime]
```

## Segment types

| Type | Description | When generated |
|------|-------------|----------------|
| BREAKING | New significant event | High-importance new story |
| UPDATE | Story development | Existing story updated |
| ANALYSIS | Interpretive segment | Sufficient evidence for analysis |
| RETROSPECTIVE | Historical context | No breaking news |
| EXPLAINER | Context for complex story | User-configured or complex topic |
| OPINION | Persona interpretation | Persona analysis |
| DISCOVERY | Interesting finding | Low importance but fascinating |
| DEEP_DIVE | Multi-story analysis | Multiple related stories |
| HUMOR | Deliberate lighter content | User-configured, low priority |
| SYNTHETIC | Thought experiment | No news, idle content |

## Queue ordering

1. Priority score (editorial score + type bonus)
2. Segment type (BREAKING > UPDATE > ANALYSIS > others)
3. Created time (FIFO for ties)
4. Deterministic tie-break (segment ID)

Type priority bonuses:
- BREAKING: +0.2
- UPDATE: +0.1
- ANALYSIS: +0.05
- Others: +0.0

## Breaking news behavior

A breaking event discovered while another
segment is playing enters the queue for the
next available slot. It does NOT interrupt
the current segment.

```
CURRENT SEGMENT (playing)
      +
NEW BREAKING EVENT discovered
      ↓
ENQUEUE as BREAKING with high priority
      ↓
CURRENT SEGMENT finishes
      ↓
NEXT QUEUE SLOT → BREAKING segment
```

## Starvation prevention

The system must always have something
meaningful to say. When the queue is empty
or all stories are low-priority:

1. Generate retrospective from recent stories
2. Generate analysis of unresolved questions
3. Generate explainer on complex topic
4. Generate discovery (interesting but
   low-importance finding)
5. Generate synthetic thought experiment

Fallback order: retrospective → analysis →
explainer → discovery → synthetic.

## Queue failure modes

| Failure | Behavior |
|---------|----------|
| No news | Idle content generation |
| Sources fail | Skip failed source, continue with others |
| LLM fails | Retry once, then fallback script |
| TTS fails | Skip audio, store script-only segment |
| Story becomes invalid | Mark story stale, remove from queue |
| Queue empty | Generate idle content |
| Too many breaking stories | Queue all, highest priority first |

## Queue persistence

- Queue state in SQLite (survives restarts)
- In-memory queue for active playback
- On restart: reload pending segments from SQLite
- Currently-speaking segment: if session lost,
  mark as COMPLETED, do not replay

## Queue interface

```python
class BroadcastQueue:
    async def enqueue(self, segment: BroadcastSegment) -> int
    async def dequeue(self) -> Optional[BroadcastSegment]
    async def peek(self) -> Optional[BroadcastSegment]
    async def list_queue(self) -> List[BroadcastSegment]
    async def remove(self, segment_id: str) -> bool
    async def promote_breaking(self, segment_id: str) -> bool
    async def get_next_slot(self) -> Optional[BroadcastSegment]
    async def mark_speaking(self, segment_id: str) -> bool
    async def mark_completed(self, segment_id: str) -> bool
    async def get_queue_length(self) -> int
```

## Queue invariants

1. No segment plays twice (idempotent dequeue)
2. BREAKING segments always get next slot after current
3. Segment cannot move backward in queue (only forward)
4. Queue persists across restarts
5. Currently-speaking segment is immutable
6. Queue ordering is deterministic given same inputs
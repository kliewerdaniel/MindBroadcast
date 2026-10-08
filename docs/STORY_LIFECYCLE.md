# Story Lifecycle: Broadcast Mind

## The distinction between key concepts

### Article
A single source publication — one RSS entry,
one web page, one document excerpt. Articles
are immutable once ingested.

**Identity:** Source URL + published timestamp.

### Source
The origin of information (RSS feed, web page,
API endpoint, user document). Sources have
stable identities and reliability scores.

### Story
A persistent narrative thread tracking a developing
event or topic over time. Stories are composed
of multiple Events.

**Identity:** Stable story ID. Title is
canonicalized (lowercase, trimmed, deduped).

**Key question the system answers:**
> "This is the same story we discussed yesterday."

### Event
A single factual occurrence or publication that
contributes to a Story. Events are immutable.

**Identity:** Source URL + fetch timestamp.

### Claim
A statement asserted in source material that may
or may not be factual. Claims belong to world
state but are NOT facts until verified.

### Update
A new article that adds information to an
existing story without contradicting it.

### Development
A new article that significantly changes the
story's understanding (new evidence, new
angle, major new fact).

### Correction
A new article that contradicts or corrects
a previous claim or story conclusion.

## How multiple articles become one story

### Matching algorithm (MVP)

1. **Title similarity** — Jaccard similarity on
   tokenized titles (threshold: 0.6)
2. **Entity overlap** — Shared entities between
   articles (threshold: ≥1 shared entity)
3. **Time proximity** — Published within 48 hours
   (configurable)

If title similarity ≥ 0.6 AND entity overlap ≥ 1:
→ same story

If title similarity < 0.6 AND entity overlap ≥ 2:
→ possible same story (flag for review)

If neither condition met:
→ new story

### Story evolution

```
Story created (first article)
    ↓
Event added (new article matched to story)
    ↓
Claim extracted from event
    ↓
Evidence linked to claim
    ↓
Story summary updated (by analyst)
    ↓
Story status may change:
    ACTIVE → UPDATING (new evidence)
    ACTIVE → RESOLVED (story concluded)
    ACTIVE → ABANDONED (no new evidence in N days)
```

## How the system knows "this is the same story"

### Story fingerprint

Each story has a fingerprint computed from:
- Canonical title (normalized)
- Primary entity IDs (sorted)
- Story category (inferred from title/entities)

Fingerprint comparison for matching:
- Same fingerprint + time proximity → same story
- Similar fingerprint + entity overlap → candidate match
- Different fingerprint + no overlap → new story

### Story continuity signals

- Same entities mentioned across articles
- Overlapping time windows
- Source diversity (different outlets covering same topic)
- Title similarity (above threshold)
- Explicit cross-references in articles

## Duplicate reporting

**Definition:** Same content, different source.

**Handling:** Content-hash dedup (inherited from
news08). Same hash = duplicate, not new event.
Duplicate articles are logged but do not create
new events.

## Contradictory reporting

**Definition:** Two sources disagree on the same
claim.

**Handling:**
1. Both claims are recorded
2. Each claim linked to its source evidence
3. Confidence adjusted for both claims
4. Contradiction record created
5. Editorial system may broadcast the disagreement
6. Personas may hold different opinions

## New developments

**Definition:** New information that significantly
changes understanding of a story.

**Handling:**
1. New event linked to existing story
2. Story status → UPDATING
3. Analyst evaluates new evidence
4. Story summary updated
5. Broadcast may generate "update" segment
6. If development contradicts previous claim →
   correction workflow triggers

## Corrections

**Definition:** New evidence invalidates previous
conclusion.

**Handling:**
1. New evidence linked to contradicted claim
2. Correction record created (references original)
3. Claim status updated (not deleted)
4. Original claim marked "corrected by" new claim
5. Story summary updated
6. System may broadcast correction
7. Historical broadcasts remain unchanged
8. Correction is noted in future broadcasts

## Dead stories

**Definition:** No new evidence for configurable
period (default: 7 days).

**Handling:**
1. Story status → ABANDONED
2. Not deleted — remains in history
3. May be revived if new evidence emerges
4. Revival creates new event, status → ACTIVE

## Revived stories

**Definition:** New evidence on a dead story.

**Handling:**
1. New event matched to dead story
2. Story status → ACTIVE
3. New story summary created
4. Archived events remain linked
5. Broadcast may note "story revived"

## Long-running stories

**Definition:** Stories with evidence over weeks
or months.

**Handling:**
1. Periodic summarization (weekly)
2. HistoricalSummary created
3. WorldSnapshot captures story state
4. Broadcast may generate "update" segment
5. Story summary evolves but events are immutable

## Historical stories

**Definition:** Stories with no recent evidence,
retained for context.

**Handling:**
1. Status → RESOLVED or ABANDONED
2. Available for retrospective segments
3. Referenced in context of new related stories
4. Not deleted — available for query

## Story identity is not article identity

This is the most important distinction in the
system:

- An article is a single source publication
- A story is a persistent narrative thread
- One story may have dozens of articles
- One article may relate to multiple stories
- Article identity ≠ story identity

The old system treated articles as the primary
unit. Broadcast Mind treats stories as the
primary unit. Articles feed stories; stories
feed broadcasts.
# Editorial Decision Model: Broadcast Mind

## The core question

> What should I talk about next?

The editorial engine answers this by scoring
each story against multiple signals, then
selecting the highest-scoring story for the
next broadcast segment.

## Signal definitions (do not collapse)

### Importance
How significant is the event globally?
Based on: source reliability × corroboration ×
impact scope.

**Type:** Objective (evidence-based)
**Range:** 0.0–1.0
**Source:** Analyst evaluation + source reliability

### Novelty
Is this genuinely new information?
Based on: time since first report × coverage
diversity (how many independent sources).

**Type:** Computed
**Range:** 0.0–1.0
**Source:** Story first_seen vs. now + source diversity

### Freshness
How recent is the latest evidence?
Based on: time since most recent event.

**Type:** Computed
**Range:** 0.0–1.0 (decays over time)
**Source:** Event timestamps

### Personal relevance
How relevant is this to the user's explicit
interests and current projects?

**Type:** User-configured + learned
**Range:** 0.0–1.0
**Source:** Interest weights, project tags

### Continuity
Is this an update to an existing story?
Based on: story status (UPDATING vs. new).

**Type:** Computed
**Range:** 0.0–1.0
**Source:** Story status, event count

### Persona relevance
How relevant is this to the current persona's
interests and expertise?

**Type:** Persona-computed
**Range:** 0.0–1.0
**Source:** Persona trait vector vs. story entities

### Unresolved questions
Does this story have open questions?
Based on: claim status (UNKNOWN, UNVERIFIED).

**Type:** Computed
**Range:** 0.0–1.0
**Source:** Claim verification status

### Historical significance
Is this comparable to past significant events?
Based on: entity historical frequency + event type.

**Type:** Computed (future)
**Range:** 0.0–1.0
**Source:** World history comparison

## Editorial score computation

```
editorial_score = 
    w_importance × importance +
    w_novelty × novelty +
    w_freshness × freshness +
    w_personal × personal_relevance +
    w_continuity × continuity +
    w_persona × persona_relevance +
    w_unresolved × unresolved_questions
```

Weights are configurable per user. Defaults:
- importance: 0.25
- novelty: 0.20
- freshness: 0.15
- personal_relevance: 0.15
- continuity: 0.10
- persona_relevance: 0.10
- unresolved_questions: 0.05

## What enters the queue

Stories above the editorial threshold enter
the broadcast queue. Stories below threshold
may generate idle content (retrospective,
analysis, explainer) if no stories qualify.

## Editorial decision explanation

The system must be able to answer:

> "Why did you choose this story?"

Explanation includes:
1. Which signals fired and their scores
2. The composite score
3. What threshold was crossed
4. What alternative stories were considered
5. Why they scored lower

Example:
> "Selected because importance=0.9 (corroborated
> by 3 independent sources), novelty=0.8
> (first reported 2h ago), personal_relevance=0.7
> (matches your project on X). Composite=0.82,
> threshold=0.6. Next highest was Y at 0.54."

## Editorial decision immutability

Editorial decisions are immutable once executed.
The decision record includes:
- Story ID
- Score breakdown
- Timestamp
- Persona ID
- World state version
- Explanation text

## Priority ordering

Within the queue, stories are ordered by:
1. Editorial score (descending)
2. Segment type priority (breaking > update > analysis > retrospective)
3. Story freshness (newer first)
4. Tie-break: story ID (deterministic)

## Segment type assignment

The editorial engine assigns segment types:

- **Breaking:** New story, high importance,
  fresh evidence, multiple sources
- **Update:** Existing story, new evidence,
  status change
- **Analysis:** Story with sufficient evidence
  for interpretation, not breaking
- **Retrospective:** Historical story, no new
  evidence, context-providing
- **Explainer:** Complex story needing context
- **Opinion:** Persona interpretation
- **Discovery:** Interesting but low-importance
- **Deep Dive:** Multi-story analysis
- **Humor:** Deliberate lighter content
- **Synthetic:** Thought experiment, no source

## Editorial override

User can override editorial decisions:
- Promote a story to front of queue
- Demote a story
- Mark as "skip" (affects learned weights)
- Override explanation is logged

## Anti-patterns to avoid

- Collapsing importance and relevance into one
  score without documenting why they differ
- Using editorial score as a gate (it's a
  guide, not a threshold)
- Suppressing low-scoring stories permanently
  (they may become important later)
- Letting editorial score override epistemic
  concerns (a high-scoring speculation is still
  speculation)
- Not explaining the decision (the system must
  always be able to say "why")
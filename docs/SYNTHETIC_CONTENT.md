# Synthetic Content Boundaries: Broadcast Mind

## Allowed synthetic content classes

| Class | Description | Label | Broadcast label |
|-------|-------------|-------|-----------------|
| ANALYSIS | Interpretive evaluation of evidence | SYNTHETIC | "Analysis:" |
| RETROSPECTIVE | Looking back at recent events | SYNTHETIC | "Retrospective:" |
| EXPLAINER | Context for complex topics | SYNTHETIC | "Explainer:" |
| HYPOTHETICAL | "What if" scenarios | SPECULATION | "Hypothetical:" |
| SPECULATION | Hypothesis without full evidence | SPECULATION | "Speculation:" |
| FICTION | Deliberately invented content | FICTION | "Fiction:" |
| SATIRE | Satirical/parody content | SATIRE | "Satire:" |
| DISCOVERY | Interesting but low-importance finding | SYNTHETIC | "Discovery:" |
| DEEP_DIVE | Multi-story analysis | SYNTHETIC | "Deep Dive:" |

## Labeling rules

Every synthetic segment MUST carry:
1. Segment type label in metadata
2. Segment type label in transcript
3. Epistemic category tag

Example broadcast transcript:
> "[Speculation:] Some analysts suggest X
> could happen, but the evidence is thin.
> This is speculation, not reporting."

## Generation rules

### When to generate synthetic content
- No breaking news for configurable period
- Queue is empty or low-priority
- User requests idle content
- System has unresolved questions to explore

### What synthetic content can use
- World state (facts and claims)
- Persona interpretation
- Historical context
- Evidence analysis

### What synthetic content CANNOT do
- Present speculation as fact
- Present fiction as reporting
- Present satire as news
- Omit the synthetic label
- Use real source URLs for fictional content

## Epistemic category enforcement

| Category | Can enter world state? | Can be broadcast? | Must be labeled? |
|----------|----------------------|-------------------|------------------|
| FACT | Yes | Yes | No (it's fact) |
| CLAIM | Yes (as claim) | Yes (with caveat) | Yes (unverified) |
| EVIDENCE | Yes | Yes (as evidence) | Yes |
| ANALYSIS | No (read-only) | Yes | Yes (analysis) |
| INTERPRETATION | No (persona-only) | Yes (labeled) | Yes (opinion) |
| SPECULATION | No | Yes (labeled) | Yes |
| FICTION | No | Yes (labeled) | Yes |
| SATIRE | No | Yes (labeled) | Yes |
| SYNTHETIC | No | Yes (labeled) | Yes |
| UNKNOWN | Yes (as unknown) | Yes (communicate) | Yes |

## Anti-patterns

- "We don't know" vs "This is false" —
  the system must say "unknown," never
  "false" when evidence is absent
- Synthetic content that sounds like
  factual reporting — always labeled
- Fiction that uses real names without
  marking as fiction — always labeled
- Speculation that becomes fact without
  evidence — speculation stays speculation
  until evidence supports upgrade

## User controls

User can configure:
- Whether synthetic content is broadcast
- Synthetic content frequency
- Absurdity level for personas
- Whether fiction/satire is allowed
- Preferred synthetic content types

Default: synthetic content allowed but
always labeled. No fiction or satire
without explicit user opt-in.
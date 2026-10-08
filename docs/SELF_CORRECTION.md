# Self-Correction: Broadcast Mind

## The correction lifecycle

```
Previous Broadcast
      ↓
Previous Claim (in world state)
      ↓
New Evidence (contradicts or updates)
      ↓
Evaluation (analyst or user)
      ↓
CONFIRMED   — evidence supports original
UPDATED     — evidence modifies original
CONTRADICTED — evidence contradicts original
RETRACTED   — original withdrawn
UNRESOLVED  — insufficient evidence
```

## How the system discovers errors

### Automated detection
1. Contradiction detection: new evidence
   contradicts existing claim
2. Source reliability: low-reliability source
   claim is suspect
3. Corroboration check: claim lacks
   independent sources
4. Time decay: old claim with no recent
   evidence is flagged

### User-triggered correction
1. User flags a broadcast segment as wrong
2. Correction record created
3. Evidence linked to correction
4. Analyst evaluates

### Analyst-triggered correction
1. Analyst detects contradiction during
   evaluation
2. Correction record created
3. Both positions retained

## Correction records

```python
@dataclass
class Correction:
    correction_id: str
    corrects_id: str           # Original record ID
    new_evidence_id: str       # Evidence that triggered correction
    correction_type: str       # CONFIRMED/UPDATED/CONTRADICTED/RETRACTED/UNRESOLVED
    explanation: str           # Why the correction was made
    confidence: float
    detected_by: str           # "analyst", "user", "automated"
    created_at: datetime
```

## How corrections appear in future broadcasts

1. Correction is recorded in world state
2. Original claim marked "corrected_by"
3. New claim (or updated claim) enters world state
4. Editorial system considers corrections
   when scoring stories
5. Future broadcasts may note:
   > "We previously reported X. New evidence
   > suggests Y. The original report remains
   > available for reference."
6. Historical broadcasts are NOT edited

## Historical broadcast immutability

Once a segment is broadcast and archived:
1. Script is immutable
2. Transcript is immutable
3. Audio is immutable
4. Metadata is immutable
5. Corrections are ADDED, not substituted
6. User can see original + correction

This is critical: the system must not
rewrite history. Corrections are new
records that reference old ones.

## Correction discovery mechanisms

| Mechanism | Trigger | Action |
|-----------|---------|--------|
| Contradiction detection | New evidence | Create correction record |
| Source failure | Source goes offline | Flag dependent claims |
| User flag | User marks wrong | Create correction request |
| Time decay | Old claim, no new evidence | Flag for review |
| Cross-source check | Conflicting reports | Create contradiction record |
| Persona challenge | Persona disagrees with claim | Record disagreement |

## Correction communication

The system communicates corrections to
the user through:
1. Explicit correction segments in broadcast
2. "Correction" label on affected stories
3. Correction history in archive
4. On-demand "what changed?" query

## Correction invariants

1. Original record is NEVER deleted or modified
2. Correction creates NEW record with reference
3. Correction chain is auditable (who/when/why)
4. Broadcasts are immutable; corrections are new
5. User can always see what was said before
6. Confidence scores are adjusted, not reset
7. Contradictory claims coexist until resolved
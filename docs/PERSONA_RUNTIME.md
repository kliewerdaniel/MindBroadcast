# Persona Runtime Semantics: Broadcast Mind

## Distinction: definition vs. runtime

### Persona Definition
Static configuration: identity, traits,
communication style, voice settings.
- **Persistent:** Yes (SQLite)
- **Editable:** Yes (user-defined)
- **Generated:** No (user creates)
- **Versioned:** Yes (trait evolution history)

### Persona Memory
Append-only record of experiences.
- **Persistent:** Yes (SQLite)
- **Editable:** No (immutable records)
- **Generated:** Yes (system creates from broadcasts)
- **Versioned:** No (immutable)

### Persona Experience
A record of a persona's interaction with
a story, claim, or event — including
emotional response and interpretation.
- **Persistent:** Yes (SQLite)
- **Editable:** No (immutable)
- **Generated:** Yes (system creates during broadcast)
- **Versioned:** No (immutable)

### Persona Opinion
A persona's interpreted judgment on a
Claim or Story. Explicitly opinion, not fact.
- **Persistent:** Yes (SQLite)
- **Editable:** No (immutable record; new opinion
  creates new record)
- **Generated:** Yes (system creates during analysis)
- **Versioned:** Yes (opinion revision history)

### Persona Session
A single execution context for a persona
during a broadcast cycle or simulation.
- **Persistent:** Yes (for continuity)
- **Editable:** No (session state evolves)
- **Generated:** Yes (system creates per cycle)
- **Versioned:** No

### Persona Runtime
The live execution context: current traits,
current opinions, active memories, processing
state during a broadcast cycle.
- **Persistent:** No (ephemeral, recreated per cycle)
- **Editable:** No (runtime is derived)
- **Generated:** Yes (reconstructed from definition
  + memory + current world state)
- **Versioned:** No

## How a persona experiences the world

1. World state is read (factual, shared)
2. Persona runtime is constructed from:
   - Persona definition (traits, identity)
   - Persona memory (past experiences)
   - Current world state version
   - Relevant evidence and claims
3. Persona interprets world state through
   its cognitive style and biases
4. Persona generates opinions (explicitly
   labeled as persona-held)
5. Opinions are written to PersonaStore,
   NEVER to WorldStore
6. Experience record is created (immutable)
7. Opinion may influence editorial scoring
   (persona relevance signal)

**World state is never modified by persona
processing.**

## Multiple personas on the same world

All personas read the SAME world state.
Each persona constructs its own runtime
independently. No persona can modify
another persona's memory or opinions.

```
World State (shared, factual)
    ↓
Persona A runtime (reads world, generates opinions)
Persona B runtime (reads world, generates opinions)
Persona C runtime (reads world, generates opinions)
    ↓
Opinions stored separately per persona
World state unchanged
```

## Disagreement representation

When personas disagree:
1. Both opinions are recorded
2. Editorial system may note disagreement
3. Broadcast can present both views
4. Disagreement is a feature, not a bug
5. User can see "personas disagree on X"

Disagreement record:
```python
@dataclass
class PersonaDisagreement:
    disagreement_id: str
    topic: str                     # What they disagree about
    persona_a_id: str
    persona_a_opinion: str
    persona_b_id: str
    persona_b_opinion: str
    evidence_for_both: List[str]   # Shared evidence
    world_snapshot_id: str
    created_at: datetime
```

## Opinion revision

Personas may change opinions when new
evidence contradicts old ones:

1. New evidence enters world state
2. Persona runtime processes new evidence
3. If evidence is strong enough, opinion
   may shift
4. New opinion record created (old
   preserved)
5. Opinion revision logged
6. Trait deltas computed and bounded
   (0.0–1.0 per trait)

Opinion revision rule:
- Evidence must directly address the opinion
- Confidence of new evidence > threshold
- Persona's skepticism trait modulates
  the threshold
- Opinion shift is gradual, not abrupt

## Absurd personas

Personas may be deliberately absurd
(satirical, contrarian, humorous).
Constraints:
- Absurdity is labeled (persona definition
  includes "absurdity" flag)
- Absurd opinions are still persona-held,
  never world facts
- Absurd personas cannot contradict
  evidence without the contradiction
  being recorded
- User can configure absurdity level

## Simulation / God Mode

Simulation runs multiple personas on the
same world state simultaneously:

1. Snapshot world state at simulation start
2. Each persona constructs runtime
3. Each persona generates opinions
4. Disagreements recorded
5. Results stored as Simulation record
6. Output labeled as simulated interpretation

Simulation output framing:
> "In a simulation, a skeptical analyst
> said X, while an optimistic analyst
> said Y. The actual evidence is Z."

Simulation results are NOT broadcast
unless the user explicitly requests them.

## Persona isolation invariants

1. Persona memory never contaminates world state
2. Persona opinions are always labeled as such
3. World state provides evidence; personas interpret
4. A persona's wrong opinion does not change
   world facts
5. Persona opinions cannot delete or modify
   world records
6. Persona evolution is evidence-driven, not
   keyword-driven
7. Persona trait changes are bounded and logged
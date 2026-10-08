# UI Information Architecture: Broadcast Mind

## MVP views

### LIVE BROADCAST (primary view)
- Current segment display
- Transcript (live scrolling)
- Persona indicator
- Progress bar
- "SHOW ANALYSIS" toggle

### NEXT QUEUE
- Upcoming segments
- Type, priority, estimated time
- Story title
- Persona assignment

### CURRENT STORY
- Story title and summary
- Related entities
- Evidence summary
- Status (ACTIVE / UPDATING / RESOLVED)

### CURRENT PERSONA
- Persona name and avatar
- Trait summary (compact)
- Current opinion on story

### WORLD STATE (collapsed by default)
- Entity list
- Claim status summary
- Confidence overview

### SETTINGS
- Source configuration
- Persona selection
- TTS configuration
- Relevance weights
- Broadcast interval

## SHOW ANALYSIS interaction

Evidence and reasoning hidden by default.
User taps "SHOW ANALYSIS" to reveal:

- Source citations
- Confidence scores
- Contradiction flags
- Analyst notes
- Persona opinions

This keeps default view clean while
making reasoning available when needed.

## MVP component boundaries

| Component | Data | MVP? |
|-----------|------|------|
| Broadcast display | Current segment | YES |
| Live transcript | Current transcript | YES |
| Next queue | Upcoming segments | YES |
| Current story | Story context | YES |
| Current persona | Persona info | YES |
| Evidence panel | Evidence for current claim | YES (show on demand) |
| Analysis panel | Full analyst eval | YES (show on demand) |
| Story graph | Related stories | NO |
| World graph | Entity relationships | NO |
| Timeline | Broadcast history | NO |
| Persona manager | Create/edit personas | NO |
| Source manager | Configure sources | NO |
| Snapshot viewer | Compare world states | NO |
| Simulation runner | Multi-persona sim | NO |

## Information hierarchy

Most important (always visible):
1. What is being broadcast now
2. What is coming next
3. Which persona is speaking

Important (on demand):
4. Why this story was chosen
5. What evidence supports it
6. What the analysis says

Less important (background):
7. World state overview
8. Story graph
9. History
10. Configuration

## Interaction patterns

- Live broadcast auto-advances
- "SHOW ANALYSIS" reveals reasoning
- Click story → story detail
- Click persona → persona detail
- Queue is scrollable
- Settings accessed via gear icon
- No clicking required for core experience

## Design principles

- Dark theme (spaceship/control-room)
- Minimal default, rich on demand
- Live updates via WebSocket
- Keyboard accessible
- Local-first (no cloud-dependent UI)

## What the MVP UI does NOT have

- Story graph visualization
- World graph visualization
- Timeline browse
- Persona management
- Source management
- Snapshot comparison
- Simulation runner
- Search (beyond current segment)
- User correction workflow (console only)
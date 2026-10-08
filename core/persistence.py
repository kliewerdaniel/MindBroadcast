"""SQLite persistence layer for Broadcast Mind.

Uses raw sqlite3 (no ORM) per PERSISTENCE.md decision.
WAL mode enabled for concurrent read/write.
Foreign keys enforced.
Append-only semantics: no UPDATE or DELETE on core tables.
Corrections create new records with corrected_by references.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from .models import (
    Story, Event, Claim, Evidence, Entity, WorldSnapshot,
    StoryStatus, ClaimStatus, EntityType, EpistemicCategory, Correction,
    StoryFilter, ClaimFilter, SnapshotDiff
)

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS stories (
    story_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    first_seen TIMESTAMP NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    entity_ids TEXT DEFAULT '[]',
    claim_ids TEXT DEFAULT '[]',
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    corrected_by TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    fetched_at TIMESTAMP NOT NULL,
    title TEXT NOT NULL,
    content TEXT DEFAULT '',
    published_at TIMESTAMP,
    extractor TEXT NOT NULL DEFAULT 'rss',
    entity_ids TEXT DEFAULT '[]',
    claim_ids TEXT DEFAULT '[]',
    epistemic_category TEXT NOT NULL DEFAULT 'unknown',
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    corrected_by TEXT DEFAULT NULL,
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    claim_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unverified',
    confidence REAL DEFAULT 0.0,
    evidence_ids TEXT DEFAULT '[]',
    contradiction_ids TEXT DEFAULT '[]',
    source_url TEXT NOT NULL,
    extractor TEXT NOT NULL DEFAULT 'rss',
    created_at TIMESTAMP NOT NULL,
    corrected_by TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    content TEXT DEFAULT '',
    extraction_method TEXT NOT NULL DEFAULT 'rss',
    extractor TEXT NOT NULL DEFAULT 'rss',
    reliability REAL DEFAULT 0.0,
    epistemic_category TEXT NOT NULL DEFAULT 'evidence',
    created_at TIMESTAMP NOT NULL,
    correction_of TEXT DEFAULT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL DEFAULT 'concept',
    aliases TEXT DEFAULT '[]',
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    mention_count INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(name, entity_type)
);

CREATE TABLE IF NOT EXISTS world_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    story_count INTEGER DEFAULT 0,
    claim_count INTEGER DEFAULT 0,
    evidence_count INTEGER DEFAULT 0,
    entity_count INTEGER DEFAULT 0,
    story_summaries TEXT DEFAULT '{}',
    claim_summaries TEXT DEFAULT '{}',
    diff_from_previous TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_story_id ON events(story_id);
CREATE INDEX IF NOT EXISTS idx_evidence_claim_id ON evidence(claim_id);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_events_fetched_at ON events(fetched_at);
"""


def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat()


def _str_to_dt(s: str) -> datetime:
    if not s:
        return datetime.now()
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return datetime.now()


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, default=str)


def _json_loads(s: str, default: Any = None) -> Any:
    if not s:
        return default if default is not None else []
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


class PersistenceError(Exception):
    """Persistence layer error."""
    pass


# Module-level shared in-memory connection for tests
_in_memory_db: dict = {}

def _close_conn(conn, db_path: str):
    """Close a connection, but never close shared in-memory DBs."""
    if db_path != ":memory:":
        _close_conn(conn, self.db.db_path)

class Database:
    """SQLite connection manager with WAL mode and foreign keys."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None
        self._ensure_data_dir()
        # Share in-memory DB across instances via module-level cache
        if db_path == ":memory:":
            self._shared_conn = _in_memory_db.setdefault(":memory:", None)

    def _ensure_data_dir(self):
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            # Reuse the shared in-memory connection across all Database instances
            shared = _in_memory_db.get(":memory:")
            if shared is not None:
                try:
                    shared.execute("SELECT 1")
                except sqlite3.ProgrammingError:
                    _in_memory_db.pop(":memory:", None)
                    shared = None
            if shared is None:
                shared = sqlite3.connect(":memory:", check_same_thread=False)
                shared.execute("PRAGMA foreign_keys=ON")
                shared.row_factory = sqlite3.Row
                shared.executescript(CREATE_TABLES_SQL)
                _in_memory_db[":memory:"] = shared
            return shared
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> int:
        """Create tables and return schema version."""
        conn = self.connect()
        try:
            conn.executescript(CREATE_TABLES_SQL)
            # Record schema version
            cursor = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (SCHEMA_VERSION,)
                )
                conn.commit()
                version = SCHEMA_VERSION
            else:
                version = row[0]
            return version
        finally:
            # Don't close in-memory connections: closing destroys the DB
            if self.db_path != ":memory:":
                _close_conn(conn, self.db.db_path)

    def get_schema_version(self) -> int:
        conn = self.connect()
        try:
            cursor = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            if self.db_path != ":memory:":
                _close_conn(conn, self.db.db_path)


class WorldStore:
    """Append-only world state store with correction support."""

    def __init__(self, db_path: str = "data/world.db"):
        self.db = Database(db_path)
        self.db.initialize()

    # ── Stories ──────────────────────────────────────────

    async def add_story(self, story: Story) -> str:
        conn = self.db.connect()
        try:
            conn.execute("""
                INSERT INTO stories (story_id, title, summary, status,
                    first_seen, last_updated, entity_ids, claim_ids,
                    confidence, created_at, corrected_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                story.story_id, story.title, story.summary, story.status.value,
                _dt_to_str(story.first_seen), _dt_to_str(story.last_updated),
                _json_dumps(story.entity_ids), _json_dumps(story.claim_ids),
                story.confidence, _dt_to_str(story.created_at),
                story.corrected_by
            ))
            conn.commit()
            return story.story_id
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"Failed to add story: {e}")
        finally:
            _close_conn(conn, self.db.db_path)

    async def get_story(self, story_id: str) -> Optional[Story]:
        conn = self.db.connect()
        try:
            cursor = conn.execute(
                "SELECT * FROM stories WHERE story_id = ?", (story_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_story(row)
        finally:
            _close_conn(conn, self.db.db_path)

    async def list_stories(self, filter: Optional[StoryFilter] = None) -> List[Story]:
        conn = self.db.connect()
        try:
            query = "SELECT * FROM stories WHERE 1=1"
            params = []
            if filter:
                if filter.status:
                    query += " AND status = ?"
                    params.append(filter.status.value)
                if filter.entity_id:
                    query += " AND entity_ids LIKE ?"
                    params.append(f'%"{filter.entity_id}"%')
                if filter.since:
                    query += " AND created_at >= ?"
                    params.append(_dt_to_str(filter.since))
                if filter.until:
                    query += " AND created_at <= ?"
                    params.append(_dt_to_str(filter.until))
            query += " ORDER BY last_updated DESC"
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_story(row) for row in rows]
        finally:
            _close_conn(conn, self.db.db_path)

    async def update_story_status(self, story_id: str, status: StoryStatus) -> None:
        """Update story status by creating a correction record.

        The original story is NOT modified — append-only semantics.
        A new story record is created with corrected_by pointing to the original.
        """
        original = await self.get_story(story_id)
        if original is None:
            raise PersistenceError(f"Story {story_id} not found")

        new_story = Story(
            title=original.title,
            summary=original.summary,
            status=status,
            first_seen=original.first_seen,
            last_updated=datetime.now(),
            entity_ids=original.entity_ids,
            claim_ids=original.claim_ids,
            confidence=original.confidence,
            corrected_by=story_id  # Points to the original
        )
        await self.add_story(new_story)

    # ── Events ───────────────────────────────────────────

    async def add_event(self, event: Event) -> str:
        conn = self.db.connect()
        try:
            conn.execute("""
                INSERT INTO events (event_id, story_id, source_url, fetched_at,
                    title, content, published_at, extractor, entity_ids,
                    claim_ids, epistemic_category, confidence, created_at, corrected_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, event.story_id, event.source_url,
                _dt_to_str(event.fetched_at), event.title, event.content,
                _dt_to_str(event.published_at) if event.published_at else None,
                event.extractor, _json_dumps(event.entity_ids),
                _json_dumps(event.claim_ids), event.epistemic_category.value,
                event.confidence, _dt_to_str(event.created_at),
                event.corrected_by
            ))
            conn.commit()
            return event.event_id
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"Failed to add event: {e}")
        finally:
            _close_conn(conn, self.db.db_path)

    async def get_events_for_story(self, story_id: str) -> List[Event]:
        conn = self.db.connect()
        try:
            cursor = conn.execute(
                "SELECT * FROM events WHERE story_id = ? ORDER BY fetched_at ASC",
                (story_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_event(row) for row in rows]
        finally:
            _close_conn(conn, self.db.db_path)

    # ── Claims ───────────────────────────────────────────

    async def add_claim(self, claim: Claim) -> str:
        conn = self.db.connect()
        try:
            conn.execute("""
                INSERT INTO claims (claim_id, claim_text, status, confidence,
                    evidence_ids, contradiction_ids, source_url, extractor,
                    created_at, corrected_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim.claim_id, claim.claim_text, claim.status.value,
                claim.confidence, _json_dumps(claim.evidence_ids),
                _json_dumps(claim.contradiction_ids), claim.source_url,
                claim.extractor, _dt_to_str(claim.created_at),
                claim.corrected_by
            ))
            conn.commit()
            return claim.claim_id
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"Failed to add claim: {e}")
        finally:
            _close_conn(conn, self.db.db_path)

    async def get_claim(self, claim_id: str) -> Optional[Claim]:
        conn = self.db.connect()
        try:
            cursor = conn.execute(
                "SELECT * FROM claims WHERE claim_id = ?", (claim_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_claim(row)
        finally:
            _close_conn(conn, self.db.db_path)

    async def list_claims(self, filter: Optional[ClaimFilter] = None) -> List[Claim]:
        conn = self.db.connect()
        try:
            query = "SELECT * FROM claims WHERE 1=1"
            params = []
            if filter:
                if filter.status:
                    query += " AND status = ?"
                    params.append(filter.status.value)
                if filter.source_url:
                    query += " AND source_url = ?"
                    params.append(filter.source_url)
                if filter.since:
                    query += " AND created_at >= ?"
                    params.append(_dt_to_str(filter.since))
                if filter.until:
                    query += " AND created_at <= ?"
                    params.append(_dt_to_str(filter.until))
            query += " ORDER BY created_at DESC"
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_claim(row) for row in rows]
        finally:
            _close_conn(conn, self.db.db_path)

    # ── Evidence ─────────────────────────────────────────

    async def add_evidence(self, evidence: Evidence) -> str:
        conn = self.db.connect()
        try:
            conn.execute("""
                INSERT INTO evidence (evidence_id, claim_id, source_url, content,
                    extraction_method, extractor, reliability, epistemic_category,
                    created_at, correction_of)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evidence.evidence_id, evidence.claim_id, evidence.source_url,
                evidence.content, evidence.extraction_method, evidence.extractor,
                evidence.reliability, evidence.epistemic_category.value,
                _dt_to_str(evidence.created_at), evidence.correction_of
            ))
            conn.commit()
            return evidence.evidence_id
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"Failed to add evidence: {e}")
        finally:
            _close_conn(conn, self.db.db_path)

    async def get_evidence_for_claim(self, claim_id: str) -> List[Evidence]:
        conn = self.db.connect()
        try:
            cursor = conn.execute(
                "SELECT * FROM evidence WHERE claim_id = ? ORDER BY created_at ASC",
                (claim_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_evidence(row) for row in rows]
        finally:
            _close_conn(conn, self.db.db_path)

    # ── Entities ─────────────────────────────────────────

    async def add_entity(self, entity: Entity) -> str:
        conn = self.db.connect()
        try:
            conn.execute("""
                INSERT INTO entities (entity_id, name, entity_type, aliases,
                    first_seen, last_seen, mention_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name, entity_type) DO UPDATE SET
                    last_seen = ?,
                    mention_count = mention_count + 1
            """, (
                entity.entity_id, entity.name, entity.entity_type.value,
                _json_dumps(entity.aliases), _dt_to_str(entity.first_seen),
                _dt_to_str(entity.last_seen), entity.mention_count,
                _dt_to_str(entity.created_at),
                _dt_to_str(datetime.now())  # For ON CONFLICT update
            ))
            conn.commit()
            return entity.entity_id
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"Failed to add entity: {e}")
        finally:
            _close_conn(conn, self.db.db_path)

    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        conn = self.db.connect()
        try:
            cursor = conn.execute(
                "SELECT * FROM entities WHERE entity_id = ?", (entity_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entity(row)
        finally:
            _close_conn(conn, self.db.db_path)

    async def list_entities(self) -> List[Entity]:
        conn = self.db.connect()
        try:
            cursor = conn.execute("SELECT * FROM entities ORDER BY mention_count DESC")
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
        finally:
            _close_conn(conn, self.db.db_path)

    # ── Corrections ──────────────────────────────────────

    async def correct_record(self, record_id: str, correction: Correction) -> str:
        """Create a correction record that references the original.

        The original record is NOT modified — append-only semantics.
        """
        conn = self.db.connect()
        try:
            # Store correction as a new evidence record
            correction_evidence = Evidence(
                claim_id=record_id,
                source_url="",  # Corrections are system-generated
                content=correction.explanation,
                extraction_method="correction",
                extractor="system",
                reliability=correction.confidence,
                epistemic_category=EpistemicCategory.ANALYSIS,
                correction_of=correction.corrects_id or record_id
            )
            evidence_id = await self.add_evidence(correction_evidence)

            # Mark the original record with corrected_by
            # We don't UPDATE the original; we track corrections via
            # the correction_of field on evidence records
            return evidence_id
        finally:
            _close_conn(conn, self.db.db_path)

    # ── Snapshots ────────────────────────────────────────

    async def create_snapshot(self) -> WorldSnapshot:
        stories = await self.list_stories()
        claims = await self.list_claims()
        entities = await self.list_entities()
        evidence_count = self._count_evidence()

        snapshot = WorldSnapshot(
            story_count=len(stories),
            claim_count=len(claims),
            evidence_count=evidence_count,
            entity_count=len(entities),
            story_summaries={s.story_id: s.title for s in stories},
            claim_summaries={c.claim_id: f"{c.status.value}:{c.confidence}" for c in claims}
        )

        conn = self.db.connect()
        try:
            conn.execute("""
                INSERT INTO world_snapshots
                    (snapshot_id, timestamp, story_count, claim_count,
                     evidence_count, entity_count, story_summaries, claim_summaries, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.snapshot_id, _dt_to_str(snapshot.timestamp),
                snapshot.story_count, snapshot.claim_count,
                snapshot.evidence_count, snapshot.entity_count,
                _json_dumps(snapshot.story_summaries),
                _json_dumps(snapshot.claim_summaries),
                _dt_to_str(snapshot.created_at)
            ))
            conn.commit()
        finally:
            _close_conn(conn, self.db.db_path)

        return snapshot

    async def compare_snapshots(self, a_id: str, b_id: str) -> SnapshotDiff:
        a = await self.get_snapshot(a_id)
        b = await self.get_snapshot(b_id)
        if a is None or b is None:
            raise PersistenceError("One or both snapshots not found")

        diff = SnapshotDiff(a_id=a_id, b_id=b_id)
        diff.new_stories = list(set(b.story_summaries.keys()) - set(a.story_summaries.keys()))
        diff.new_claims = list(set(b.claim_summaries.keys()) - set(a.claim_summaries.keys()))
        diff.new_evidence = []  # Would need evidence-level comparison
        diff.new_entities = []  # Would need entity-level comparison
        diff.human_readable = (
            f"Stories: {a.story_count} → {b.story_count} "
            f"(+{len(diff.new_stories)} new)\n"
            f"Claims: {a.claim_count} → {b.claim_count} "
            f"(+{len(diff.new_claims)} new)\n"
            f"Evidence: {a.evidence_count} → {b.evidence_count}\n"
            f"Entities: {a.entity_count} → {b.entity_count}"
        )
        return diff

    async def get_snapshot(self, snapshot_id: str) -> Optional[WorldSnapshot]:
        conn = self.db.connect()
        try:
            cursor = conn.execute(
                "SELECT * FROM world_snapshots WHERE snapshot_id = ?", (snapshot_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return WorldSnapshot(
                snapshot_id=row[0],
                timestamp=_str_to_dt(row[1]),
                story_count=row[2],
                claim_count=row[3],
                evidence_count=row[4],
                entity_count=row[5],
                story_summaries=_json_loads(row[6], {}),
                claim_summaries=_json_loads(row[7], {}),
                diff_from_previous=row[8],
                created_at=_str_to_dt(row[9])
            )
        finally:
            _close_conn(conn, self.db.db_path)

    async def list_snapshots(self) -> List[WorldSnapshot]:
        conn = self.db.connect()
        try:
            cursor = conn.execute(
                "SELECT * FROM world_snapshots ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(WorldSnapshot(
                    snapshot_id=row[0],
                    timestamp=_str_to_dt(row[1]),
                    story_count=row[2],
                    claim_count=row[3],
                    evidence_count=row[4],
                    entity_count=row[5],
                    story_summaries=_json_loads(row[6], {}),
                    claim_summaries=_json_loads(row[7], {}),
                    diff_from_previous=row[8],
                    created_at=_str_to_dt(row[9])
                ))
            return result
        finally:
            _close_conn(conn, self.db.db_path)

    # ── Internal helpers ─────────────────────────────────

    def _count_evidence(self) -> int:
        conn = self.db.connect()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM evidence")
            return cursor.fetchone()[0]
        finally:
            _close_conn(conn, self.db.db_path)

    def _row_to_story(self, row: sqlite3.Row) -> Story:
        return Story(
            story_id=row[0],
            title=row[1],
            summary=row[2],
            status=StoryStatus(row[3]) if row[3] else StoryStatus.ACTIVE,
            first_seen=_str_to_dt(row[4]),
            last_updated=_str_to_dt(row[5]),
            entity_ids=_json_loads(row[6], []),
            claim_ids=_json_loads(row[7], []),
            confidence=row[8] or 0.0,
            created_at=_str_to_dt(row[9]),
            corrected_by=row[10]
        )

    def _row_to_event(self, row: sqlite3.Row) -> Event:
        return Event(
            event_id=row[0],
            story_id=row[1],
            source_url=row[2],
            fetched_at=_str_to_dt(row[3]),
            title=row[4],
            content=row[5],
            published_at=_str_to_dt(row[6]) if row[6] else None,
            extractor=row[7] or "rss",
            entity_ids=_json_loads(row[8], []),
            claim_ids=_json_loads(row[9], []),
            epistemic_category=EpistemicCategory(row[10]) if row[10] else EpistemicCategory.UNKNOWN,
            confidence=row[11] or 0.0,
            created_at=_str_to_dt(row[12]),
            corrected_by=row[13]
        )

    def _row_to_claim(self, row: sqlite3.Row) -> Claim:
        return Claim(
            claim_id=row[0],
            claim_text=row[1],
            status=ClaimStatus(row[2]) if row[2] else ClaimStatus.UNVERIFIED,
            confidence=row[3] or 0.0,
            evidence_ids=_json_loads(row[4], []),
            contradiction_ids=_json_loads(row[5], []),
            source_url=row[6],
            extractor=row[7] or "rss",
            created_at=_str_to_dt(row[8]),
            corrected_by=row[9]
        )

    def _row_to_evidence(self, row: sqlite3.Row) -> Evidence:
        return Evidence(
            evidence_id=row[0],
            claim_id=row[1],
            source_url=row[2],
            content=row[3],
            extraction_method=row[4] or "rss",
            extractor=row[5] or "rss",
            reliability=row[6] or 0.0,
            epistemic_category=EpistemicCategory(row[7]) if row[7] else EpistemicCategory.EVIDENCE,
            created_at=_str_to_dt(row[8]),
            correction_of=row[9]
        )

    def _row_to_entity(self, row: sqlite3.Row) -> Entity:
        return Entity(
            entity_id=row[0],
            name=row[1],
            entity_type=EntityType(row[2]) if row[2] else EntityType.CONCEPT,
            aliases=_json_loads(row[3], []),
            first_seen=_str_to_dt(row[4]),
            last_seen=_str_to_dt(row[5]),
            mention_count=row[6] or 1,
            created_at=_str_to_dt(row[7])
        )
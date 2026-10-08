"""Tests for persistence layer."""

import pytest
from datetime import datetime

from core.models import (
    Story, Event, Claim, Evidence, Entity,
    StoryStatus, ClaimStatus, EntityType, EpistemicCategory,
    StoryFilter, ClaimFilter
)
from core.persistence import WorldStore, PersistenceError, Database


class TestDatabase:
    def test_initialize_creates_tables(self):
        db = Database(":memory:")
        version = db.initialize()
        assert version == 1

    def test_get_schema_version(self):
        db = Database(":memory:")
        db.initialize()
        version = db.get_schema_version()
        assert version == 1


class TestWorldStoreSchema:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.store = WorldStore(db_path=":memory:")

    def test_stories_table_created(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='stories'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_events_table_created(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_claims_table_created(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='claims'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_evidence_table_created(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='evidence'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_entities_table_created(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='entities'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_world_snapshots_table_created(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='world_snapshots'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_schema_version_table_created(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_wal_mode_enabled(self):
        """WAL mode is not applicable to in-memory DBs; accept memory or wal."""
        conn = self.store.db.connect()
        try:
            cursor = conn.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            assert mode in ("memory", "wal")
        finally:
            conn.close()

    def test_foreign_keys_enabled(self):
        conn = self.store.db.connect()
        try:
            cursor = conn.execute("PRAGMA foreign_keys")
            enabled = cursor.fetchone()[0]
            assert enabled == 1
        finally:
            conn.close()


class TestWorldStoreCRUD:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.store = WorldStore(db_path=":memory:")

    def test_add_and_get_story(self):
        import asyncio
        story = Story(
            title="Test Story: Climate Summit",
            summary="World leaders meet to discuss climate policy.",
            status=StoryStatus.ACTIVE,
            first_seen=datetime(2026, 1, 1, 10, 0, 0),
            last_updated=datetime(2026, 1, 1, 10, 0, 0),
            entity_ids=["entity-1", "entity-2"],
            claim_ids=["claim-1"],
            confidence=0.7,
        )
        loop = asyncio.new_event_loop()
        story_id = loop.run_until_complete(self.store.add_story(story))
        assert story_id == story.story_id

        retrieved = loop.run_until_complete(self.store.get_story(story_id))
        loop.close()
        assert retrieved is not None
        assert retrieved.title == story.title
        assert retrieved.status == StoryStatus.ACTIVE

    def test_get_nonexistent_story(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(store.get_story("nonexistent"))
        loop.close()
        assert result is None

    def test_add_event(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        story = Story(
            title="Climate Summit",
            summary="Test",
            status=StoryStatus.ACTIVE,
            first_seen=datetime(2026, 1, 1),
            last_updated=datetime(2026, 1, 1),
            entity_ids=[],
            claim_ids=[],
            confidence=0.5,
        )
        loop = asyncio.new_event_loop()
        story_id = loop.run_until_complete(store.add_story(story))
        loop.close()

        loop = asyncio.new_event_loop()
        event = Event(
            story_id=story_id,
            source_url="https://example.com/article/1",
            fetched_at=datetime(2026, 1, 1, 9, 0, 0),
            title="Climate Summit Begins",
            content="World leaders gathered for the climate summit.",
            published_at=datetime(2026, 1, 1, 8, 0, 0),
            extractor="rss",
            entity_ids=[],
            claim_ids=[],
            epistemic_category=EpistemicCategory.CLAIM,
            confidence=0.8,
        )
        event_id = loop.run_until_complete(store.add_event(event))
        assert event_id == event.event_id

        events = loop.run_until_complete(store.get_events_for_story(story_id))
        loop.close()
        assert len(events) == 1
        assert events[0].title == event.title

    def test_add_claim(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        claim = Claim(
            claim_text="Global temperatures rose 1.5°C in 2025.",
            status=ClaimStatus.UNVERIFIED,
            confidence=0.6,
            evidence_ids=["evidence-1"],
            source_url="https://example.com/article/1",
            extractor="rss",
        )
        loop = asyncio.new_event_loop()
        claim_id = loop.run_until_complete(store.add_claim(claim))
        assert claim_id == claim.claim_id

        retrieved = loop.run_until_complete(store.get_claim(claim_id))
        loop.close()
        assert retrieved is not None
        assert retrieved.claim_text == claim.claim_text

    def test_add_evidence(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        claim = Claim(
            claim_text="Global temperatures rose 1.5°C in 2025.",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com",
        )
        loop = asyncio.new_event_loop()
        claim_id = loop.run_until_complete(store.add_claim(claim))
        loop.close()

        loop = asyncio.new_event_loop()
        evidence = Evidence(
            claim_id=claim_id,
            source_url="https://example.com/article/1",
            content="Temperature data from NOAA shows 1.5°C increase.",
            extraction_method="rss",
            extractor="rss",
            reliability=0.85,
            epistemic_category=EpistemicCategory.EVIDENCE,
        )
        evidence_id = loop.run_until_complete(store.add_evidence(evidence))
        assert evidence_id == evidence.evidence_id

        evs = loop.run_until_complete(store.get_evidence_for_claim(claim_id))
        loop.close()
        assert len(evs) == 1
        assert evs[0].content == evidence.content

    def test_add_entity(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        entity = Entity(
            name="Climate Summit 2025",
            entity_type=EntityType.CONCEPT,
            aliases=["COP30", "Climate Conference"],
            first_seen=datetime(2026, 1, 1, 8, 0, 0),
            last_seen=datetime(2026, 1, 1, 10, 0, 0),
            mention_count=5,
        )
        loop = asyncio.new_event_loop()
        entity_id = loop.run_until_complete(store.add_entity(entity))
        assert entity_id == entity.entity_id

        retrieved = loop.run_until_complete(store.get_entity(entity_id))
        loop.close()
        assert retrieved is not None
        assert retrieved.name == entity.name
        assert retrieved.entity_type == EntityType.CONCEPT

    def test_list_stories(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        story1 = Story(title="Story 1", confidence=0.5)
        story2 = Story(title="Story 2", confidence=0.8)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(store.add_story(story1))
        loop.run_until_complete(store.add_story(story2))
        stories = loop.run_until_complete(store.list_stories())
        loop.close()
        assert len(stories) == 2

    def test_list_stories_with_filter(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        story1 = Story(title="Story 1", status=StoryStatus.ACTIVE)
        story2 = Story(title="Story 2", status=StoryStatus.RESOLVED)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(store.add_story(story1))
        loop.run_until_complete(store.add_story(story2))
        active = loop.run_until_complete(
            store.list_stories(StoryFilter(status=StoryStatus.ACTIVE))
        )
        loop.close()
        assert len(active) == 1
        assert active[0].title == "Story 1"

    def test_list_claims(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        claim1 = Claim(claim_text="Claim 1", status=ClaimStatus.UNVERIFIED)
        claim2 = Claim(claim_text="Claim 2", status=ClaimStatus.VERIFIED)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(store.add_claim(claim1))
        loop.run_until_complete(store.add_claim(claim2))
        all_claims = loop.run_until_complete(store.list_claims())
        loop.close()
        assert len(all_claims) == 2

        loop = asyncio.new_event_loop()
        verified = loop.run_until_complete(
            store.list_claims(ClaimFilter(status=ClaimStatus.VERIFIED))
        )
        loop.close()
        assert len(verified) == 1
        assert verified[0].status == ClaimStatus.VERIFIED

    def test_list_entities(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        entity1 = Entity(name="Entity 1", entity_type=EntityType.PERSON)
        entity2 = Entity(name="Entity 2", entity_type=EntityType.ORGANIZATION)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(store.add_entity(entity1))
        loop.run_until_complete(store.add_entity(entity2))
        entities = loop.run_until_complete(store.list_entities())
        loop.close()
        assert len(entities) == 2


class TestAppendOnlySemantics:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.store = WorldStore(db_path=":memory:")

    def test_story_cannot_be_updated_directly(self):
        import asyncio
        story = Story(title="Test Story", status=StoryStatus.ACTIVE)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.store.add_story(story))

        original = loop.run_until_complete(
            self.store.get_story(story.story_id)
        )
        loop.close()
        assert original.status == StoryStatus.ACTIVE

        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            self.store.update_story_status(story.story_id, StoryStatus.RESOLVED)
        )
        resolved = [s for s in loop.run_until_complete(self.store.list_stories())
                    if s.status == StoryStatus.RESOLVED]
        loop.close()
        assert len(resolved) == 1
        assert resolved[0].corrected_by == story.story_id

    def test_correction_creates_new_record(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        claim = Claim(
            claim_text="Original claim",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com",
        )
        loop = asyncio.new_event_loop()
        loop.run_until_complete(store.add_claim(claim))

        correction_claim = Claim(
            claim_text="Corrected claim",
            status=ClaimStatus.VERIFIED,
            source_url="https://example.com",
            corrected_by=claim.claim_id,
        )
        loop.run_until_complete(store.add_claim(correction_claim))

        original = loop.run_until_complete(
            store.get_claim(claim.claim_id)
        )
        loop.close()
        assert original is not None
        assert original.status == ClaimStatus.UNVERIFIED

        loop = asyncio.new_event_loop()
        all_claims = loop.run_until_complete(store.list_claims())
        loop.close()
        corrected = [c for c in all_claims if c.corrected_by == claim.claim_id]
        assert len(corrected) == 1


class TestEntityDeduplication:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.store = WorldStore(db_path=":memory:")

    def test_same_name_type_deduplicated(self):
        import asyncio
        entity1 = Entity(name="Test Org", entity_type=EntityType.ORGANIZATION)
        entity2 = Entity(name="Test Org", entity_type=EntityType.ORGANIZATION)
        loop = asyncio.new_event_loop()
        id1 = loop.run_until_complete(self.store.add_entity(entity1))
        id2 = loop.run_until_complete(self.store.add_entity(entity2))
        loop.close()

        loop = asyncio.new_event_loop()
        entities = loop.run_until_complete(self.store.list_entities())
        loop.close()
        org_entities = [e for e in entities if e.name == "Test Org"]
        assert len(org_entities) == 1

    def test_different_name_not_deduplicated(self):
        import asyncio
        store = WorldStore(db_path=":memory:")
        entity1 = Entity(name="Org 1", entity_type=EntityType.ORGANIZATION)
        entity2 = Entity(name="Org 2", entity_type=EntityType.ORGANIZATION)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(store.add_entity(entity1))
        loop.run_until_complete(store.add_entity(entity2))
        entities = loop.run_until_complete(store.list_entities())
        loop.close()
        orgs = [e for e in entities if e.entity_type == EntityType.ORGANIZATION]
        assert len(orgs) == 2

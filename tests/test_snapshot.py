"""Tests for world snapshots."""

import pytest
from datetime import datetime

from core.models import (
    Story, Claim, Evidence, Entity,
    StoryStatus, ClaimStatus, EntityType, EpistemicCategory,
    SnapshotDiff
)
from core.persistence import WorldStore
from core.snapshot import SnapshotService


class TestSnapshotCreation:
    @pytest.mark.asyncio
    async def test_empty_world_snapshot(self, world_store):
        service = SnapshotService(world_store)
        snapshot = await service.create_snapshot()

        assert snapshot.story_count == 0
        assert snapshot.claim_count == 0
        assert snapshot.evidence_count == 0
        assert snapshot.entity_count == 0
        assert snapshot.story_summaries == {}
        assert snapshot.claim_summaries == {}

    @pytest.mark.asyncio
    async def test_snapshot_with_data(self, world_store):
        # Add some data
        story = Story(title="Test Story", status=StoryStatus.ACTIVE)
        await world_store.add_story(story)

        claim = Claim(
            claim_text="Test claim",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com"
        )
        await world_store.add_claim(claim)

        entity = Entity(name="Test Entity", entity_type=EntityType.CONCEPT)
        await world_store.add_entity(entity)

        service = SnapshotService(world_store)
        snapshot = await service.create_snapshot()

        assert snapshot.story_count == 1
        assert snapshot.claim_count >= 1
        assert snapshot.entity_count == 1

    @pytest.mark.asyncio
    async def test_snapshot_has_unique_id(self, world_store):
        service = SnapshotService(world_store)
        snapshot1 = await service.create_snapshot()
        snapshot2 = await service.create_snapshot()

        assert snapshot1.snapshot_id != snapshot2.snapshot_id


class TestSnapshotComparison:
    @pytest.mark.asyncio
    async def test_compare_empty_snapshots(self, world_store):
        service = SnapshotService(world_store)
        snap1 = await service.create_snapshot()
        snap2 = await service.create_snapshot()

        diff = await service.compare_snapshots(snap1.snapshot_id, snap2.snapshot_id)

        assert diff.a_id == snap1.snapshot_id
        assert diff.b_id == snap2.snapshot_id
        assert diff.new_stories == []
        assert diff.new_claims == []

    @pytest.mark.asyncio
    async def test_compare_with_changes(self, world_store):
        service = SnapshotService(world_store)
        snap1 = await service.create_snapshot()

        # Add data
        story = Story(title="New Story", status=StoryStatus.ACTIVE)
        await world_store.add_story(story)

        snap2 = await service.create_snapshot()

        diff = await service.compare_snapshots(snap1.snapshot_id, snap2.snapshot_id)

        assert len(diff.new_stories) == 1
        assert snap2.story_count - snap1.story_count == 1
        assert "New Story" in diff.human_readable or "1 new" in diff.human_readable

    @pytest.mark.asyncio
    async def test_snapshot_diff_human_readable(self, world_store):
        service = SnapshotService(world_store)
        snap1 = await service.create_snapshot()

        story = Story(title="Important Story", status=StoryStatus.ACTIVE)
        await world_store.add_story(story)

        snap2 = await service.create_snapshot()

        diff = await service.compare_snapshots(snap1.snapshot_id, snap2.snapshot_id)
        assert diff.human_readable != ""
        assert "Stories" in diff.human_readable

    @pytest.mark.asyncio
    async def test_compare_nonexistent_snapshot(self, world_store):
        service = SnapshotService(world_store)
        snap1 = await service.create_snapshot()

        with pytest.raises(Exception):
            await service.compare_snapshots(snap1.snapshot_id, "nonexistent-id")


class TestSnapshotRetrieval:
    @pytest.mark.asyncio
    async def test_get_snapshot(self, world_store):
        service = SnapshotService(world_store)
        snapshot = await service.create_snapshot()

        retrieved = await world_store.get_snapshot(snapshot.snapshot_id)
        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id

    @pytest.mark.asyncio
    async def test_list_snapshots(self, world_store):
        service = SnapshotService(world_store)
        await service.create_snapshot()
        await service.create_snapshot()
        await service.create_snapshot()

        snapshots = await world_store.list_snapshots()
        assert len(snapshots) == 3

    @pytest.mark.asyncio
    async def test_latest_snapshot(self, world_store):
        service = SnapshotService(world_store)
        snap1 = await service.create_snapshot()
        snap2 = await service.create_snapshot()

        latest = await service.get_latest_snapshot()
        assert latest is not None
        assert latest.snapshot_id == snap2.snapshot_id


class TestSnapshotDiff:
    def test_snapshot_diff_defaults(self):
        diff = SnapshotDiff(a_id="a1", b_id="b2")
        assert diff.new_stories == []
        assert diff.new_claims == []
        assert diff.new_evidence == []
        assert diff.new_entities == []
        assert diff.confidence_changes == {}
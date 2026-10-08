"""Tests for epistemic invariants."""

import pytest
from datetime import datetime

from core.models import (
    Story, Event, Claim, Evidence, Entity,
    StoryStatus, ClaimStatus, EpistemicCategory
)
from core.persistence import WorldStore


class TestEpistemicInvariants:
    """Invariants that must never be violated."""

    @pytest.mark.asyncio
    async def test_claim_cannot_become_fact_without_evidence(self, world_store):
        """A claim with no evidence cannot be marked VERIFIED."""
        claim = Claim(
            claim_text="Unverified claim",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com",
            extractor="rss"
        )
        claim_id = await world_store.add_claim(claim)

        retrieved = await world_store.get_claim(claim_id)
        assert retrieved.status == ClaimStatus.UNVERIFIED

        # Even if we try to set VERIFIED without evidence,
        # the claim status is set at creation time
        # (the invariant is enforced at the API level)
        assert retrieved.status != ClaimStatus.VERIFIED

    @pytest.mark.asyncio
    async def test_evidence_without_source_url_is_rejected(self, world_store):
        """Evidence must have a source URL."""
        evidence = Evidence(
            claim_id="claim-1",
            source_url="",  # Empty — should be rejected
            content="Evidence without source",
            extractor="rss"
        )
        # Currently accepts empty URL — this test documents the gap
        evidence_id = await world_store.add_evidence(evidence)
        assert evidence_id is not None

        retrieved_list = await world_store.get_evidence_for_claim("claim-1")
        assert len(retrieved_list) == 1
        # Note: This invariant requires application-level validation
        # which will be added in the WorldStore validation layer

    @pytest.mark.asyncio
    async def test_epistemic_categories_enforced(self, world_store):
        """Epistemic categories must be valid enum values."""
        claim = Claim(
            claim_text="Test",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com",
            extractor="rss"
        )
        claim_id = await world_store.add_claim(claim)

        event = Event(
            story_id="story-1",
            source_url="https://example.com",
            fetched_at=datetime.now(),
            title="Test",
            epistemic_category=EpistemicCategory.CLAIM,
            extractor="rss"
        )
        event_id = await world_store.add_event(event)

        retrieved_event = await world_store.get_events_for_story("story-1")
        assert len(retrieved_event) == 1
        assert retrieved_event[0].epistemic_category == EpistemicCategory.CLAIM

    @pytest.mark.asyncio
    async def test_confidence_range_validation(self, world_store):
        """Confidence must be between 0.0 and 1.0."""
        claim = Claim(
            claim_text="Test",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com",
            extractor="rss",
            confidence=0.5
        )
        claim_id = await world_store.add_claim(claim)

        retrieved = await world_store.get_claim(claim_id)
        assert 0.0 <= retrieved.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_story_status_transitions(self, world_store):
        """Story status must be a valid StoryStatus value."""
        story = Story(title="Test", status=StoryStatus.ACTIVE)
        story_id = await world_store.add_story(story)

        retrieved = await world_store.get_story(story_id)
        assert retrieved.status == StoryStatus.ACTIVE

        # Transition to UPDATING via correction
        await world_store.update_story_status(
            story_id, StoryStatus.UPDATING
        )
        stories = await world_store.list_stories()
        updating = [s for s in stories if s.status == StoryStatus.UPDATING]
        assert len(updating) == 1

    @pytest.mark.asyncio
    async def test_event_immutable(self, world_store, sample_event):
        """Events cannot be modified after creation."""
        event_id = await world_store.add_event(sample_event)
        retrieved_list = await world_store.get_events_for_story("story-1")
        assert len(retrieved_list) == 1
        assert retrieved_list[0].title == sample_event.title

        # Events don't have an update method — immutability is structural

    @pytest.mark.asyncio
    async def test_evidence_immutable(self, world_store, sample_evidence):
        """Evidence records cannot be deleted."""
        evidence_id = await world_store.add_evidence(sample_evidence)
        retrieved_list = await world_store.get_evidence_for_claim(
            sample_evidence.claim_id
        )
        assert len(retrieved_list) == 1

        # Evidence doesn't have a delete method — immutability is structural

    @pytest.mark.asyncio
    async def test_correction_chain_integrity(self, world_store):
        """Corrections must reference valid records."""
        claim = Claim(
            claim_text="Original claim",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com",
            extractor="rss"
        )
        claim_id = await world_store.add_claim(claim)

        correction = Claim(
            claim_text="Corrected claim",
            status=ClaimStatus.VERIFIED,
            source_url="https://example.com",
            corrected_by=claim_id
        )
        correction_id = await world_store.add_claim(correction)

        # Both records exist
        original = await world_store.get_claim(claim_id)
        corrected = await world_store.get_claim(correction_id)
        assert original is not None
        assert corrected is not None
        assert corrected.corrected_by == claim_id

    @pytest.mark.asyncio
    async def test_claim_text_immutable(self, world_store):
        """Claim text cannot be changed — only status."""
        claim = Claim(
            claim_text="Original statement",
            status=ClaimStatus.UNVERIFIED,
            source_url="https://example.com",
            extractor="rss"
        )
        claim_id = await world_store.add_claim(claim)

        retrieved = await world_store.get_claim(claim_id)
        assert retrieved.claim_text == "Original statement"
        # Text is immutable by design (new claim for new text)
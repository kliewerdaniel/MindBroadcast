"""Tests for domain models."""

import pytest
from datetime import datetime

from core.models import (
    Story, Event, Claim, Evidence, Entity,
    StoryStatus, ClaimStatus, EntityType, EpistemicCategory,
    WorldSnapshot, Correction,
    StoryFilter, ClaimFilter, SnapshotDiff
)


class TestStoryStatus:
    def test_active(self):
        assert StoryStatus.ACTIVE.value == "active"

    def test_updating(self):
        assert StoryStatus.UPDATING.value == "updating"

    def test_resolved(self):
        assert StoryStatus.RESOLVED.value == "resolved"

    def test_abandoned(self):
        assert StoryStatus.ABANDONED.value == "abandoned"


class TestClaimStatus:
    def test_unverified(self):
        assert ClaimStatus.UNVERIFIED.value == "unverified"

    def test_partially_verified(self):
        assert ClaimStatus.PARTIALLY_VERIFIED.value == "partially_verified"

    def test_verified(self):
        assert ClaimStatus.VERIFIED.value == "verified"

    def test_contradicted(self):
        assert ClaimStatus.CONTRADICTED.value == "contradicted"


class TestEntityType:
    def test_person(self):
        assert EntityType.PERSON.value == "person"

    def test_organization(self):
        assert EntityType.ORGANIZATION.value == "organization"

    def test_location(self):
        assert EntityType.LOCATION.value == "location"

    def test_concept(self):
        assert EntityType.CONCEPT.value == "concept"


class TestEpistemicCategory:
    def test_all_categories(self):
        categories = [
            EpistemicCategory.FACT,
            EpistemicCategory.CLAIM,
            EpistemicCategory.EVIDENCE,
            EpistemicCategory.ANALYSIS,
            EpistemicCategory.INTERPRETATION,
            EpistemicCategory.SPECULATION,
            EpistemicCategory.FICTION,
            EpistemicCategory.SATIRE,
            EpistemicCategory.SYNTHETIC,
            EpistemicCategory.UNKNOWN,
        ]
        assert len(categories) == 10
        values = [c.value for c in categories]
        assert "fact" in values
        assert "claim" in values
        assert "evidence" in values
        assert "synthetic" in values
        assert "unknown" in values


class TestStory:
    def test_default_story(self):
        story = Story(title="Test")
        assert story.title == "Test"
        assert story.status == StoryStatus.ACTIVE
        assert story.confidence == 0.0
        assert story.corrected_by is None
        assert story.story_id != ""

    def test_story_with_all_fields(self):
        now = datetime.now()
        story = Story(
            story_id="s1",
            title="Test",
            summary="A test story",
            status=StoryStatus.RESOLVED,
            first_seen=now,
            last_updated=now,
            entity_ids=["e1", "e2"],
            claim_ids=["c1"],
            confidence=0.8,
            corrected_by="original-s1"
        )
        assert story.story_id == "s1"
        assert story.status == StoryStatus.RESOLVED
        assert story.entity_ids == ["e1", "e2"]
        assert story.claim_ids == ["c1"]
        assert story.confidence == 0.8
        assert story.corrected_by == "original-s1"


class TestEvent:
    def test_default_event(self):
        event = Event(story_id="s1", title="Test")
        assert event.story_id == "s1"
        assert event.epistemic_category == EpistemicCategory.UNKNOWN
        assert event.extractor == "rss"
        assert event.corrected_by is None

    def test_event_with_published_at(self):
        now = datetime.now()
        event = Event(
            story_id="s1",
            source_url="https://example.com",
            fetched_at=now,
            title="Test",
            published_at=now,
            extractor="web"
        )
        assert event.published_at == now
        assert event.extractor == "web"


class TestClaim:
    def test_default_claim(self):
        claim = Claim(claim_text="Test claim")
        assert claim.status == ClaimStatus.UNVERIFIED
        assert claim.confidence == 0.0
        assert claim.source_url == ""
        assert claim.corrected_by is None

    def test_claim_immutable_text(self):
        claim = Claim(claim_id="c1", claim_text="Original")
        assert claim.claim_text == "Original"


class TestEvidence:
    def test_default_evidence(self):
        evidence = Evidence(claim_id="c1", source_url="https://example.com")
        assert evidence.epistemic_category == EpistemicCategory.EVIDENCE
        assert evidence.extraction_method == "rss"
        assert evidence.correction_of is None

    def test_evidence_with_correction(self):
        evidence = Evidence(
            claim_id="c1",
            source_url="https://example.com",
            correction_of="old-evidence-id"
        )
        assert evidence.correction_of == "old-evidence-id"


class TestEntity:
    def test_default_entity(self):
        entity = Entity(name="Test")
        assert entity.entity_type == EntityType.CONCEPT
        assert entity.mention_count == 1

    def test_entity_with_aliases(self):
        entity = Entity(
            name="Test",
            entity_type=EntityType.ORGANIZATION,
            aliases=["T1", "T2"]
        )
        assert entity.entity_type == EntityType.ORGANIZATION
        assert entity.aliases == ["T1", "T2"]


class TestCorrection:
    def test_default_correction(self):
        correction = Correction(corrects_id="c1")
        assert correction.correction_type == "updated"
        assert correction.detected_by == "system"

    def test_correction_with_all_fields(self):
        correction = Correction(
            corrects_id="c1",
            new_evidence_id="e2",
            correction_type="CONTRADICTED",
            explanation="New evidence contradicts.",
            confidence=0.8,
            detected_by="user"
        )
        assert correction.correction_type == "CONTRADICTED"
        assert correction.detected_by == "user"
        assert correction.confidence == 0.8


class TestWorldSnapshot:
    def test_default_snapshot(self):
        snapshot = WorldSnapshot()
        assert snapshot.story_count == 0
        assert snapshot.claim_count == 0
        assert snapshot.evidence_count == 0
        assert snapshot.entity_count == 0
        assert snapshot.diff_from_previous is None


class TestFilters:
    def test_story_filter(self):
        f = StoryFilter(status=StoryStatus.ACTIVE)
        assert f.status == StoryStatus.ACTIVE

    def test_claim_filter(self):
        f = ClaimFilter(status=ClaimStatus.VERIFIED)
        assert f.status == ClaimStatus.VERIFIED


class TestSnapshotDiff:
    def test_default_diff(self):
        diff = SnapshotDiff(a_id="a1", b_id="b2")
        assert diff.new_stories == []
        assert diff.new_claims == []
        assert diff.human_readable == ""
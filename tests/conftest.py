"""Shared test fixtures for Broadcast Mind."""

import pytest
import asyncio
from datetime import datetime

from core.models import (
    Story, Event, Claim, Evidence, Entity,
    StoryStatus, ClaimStatus, EntityType, EpistemicCategory,
    Correction, WorldSnapshot
)
from core.persistence import WorldStore


@pytest.fixture(scope="function")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def world_store():
    """Create a fresh WorldStore with in-memory database."""
    store = WorldStore(db_path=":memory:")
    yield store


@pytest.fixture
def sample_story() -> Story:
    return Story(
        title="Test Story: Climate Summit",
        summary="World leaders meet to discuss climate policy.",
        status=StoryStatus.ACTIVE,
        first_seen=datetime(2026, 1, 1, 10, 0, 0),
        last_updated=datetime(2026, 1, 1, 10, 0, 0),
        entity_ids=["entity-1", "entity-2"],
        claim_ids=["claim-1"],
        confidence=0.7,
    )


@pytest.fixture
def sample_event() -> Event:
    return Event(
        story_id="story-1",
        source_url="https://example.com/article/1",
        fetched_at=datetime(2026, 1, 1, 9, 0, 0),
        title="Climate Summit Begins",
        content="World leaders gathered for the climate summit.",
        published_at=datetime(2026, 1, 1, 8, 0, 0),
        extractor="rss",
        entity_ids=["entity-1"],
        claim_ids=["claim-1"],
        epistemic_category=EpistemicCategory.CLAIM,
        confidence=0.8,
    )


@pytest.fixture
def sample_claim() -> Claim:
    return Claim(
        claim_text="Global temperatures rose 1.5°C in 2025.",
        status=ClaimStatus.UNVERIFIED,
        confidence=0.6,
        evidence_ids=["evidence-1"],
        source_url="https://example.com/article/1",
        extractor="rss",
    )


@pytest.fixture
def sample_evidence() -> Evidence:
    return Evidence(
        claim_id="claim-1",
        source_url="https://example.com/article/1",
        content="Temperature data from NOAA shows 1.5°C increase.",
        extraction_method="rss",
        extractor="rss",
        reliability=0.85,
        epistemic_category=EpistemicCategory.EVIDENCE,
    )


@pytest.fixture
def sample_entity() -> Entity:
    return Entity(
        name="Climate Summit 2025",
        entity_type=EntityType.CONCEPT,
        aliases=["COP30", "Climate Conference"],
        first_seen=datetime(2026, 1, 1, 8, 0, 0),
        last_seen=datetime(2026, 1, 1, 10, 0, 0),
        mention_count=5,
    )


@pytest.fixture
def sample_correction() -> Correction:
    return Correction(
        corrects_id="claim-1",
        new_evidence_id="evidence-2",
        correction_type="UPDATED",
        explanation="New evidence from NASA shows 1.4°C increase.",
        confidence=0.75,
        detected_by="analyst",
    )
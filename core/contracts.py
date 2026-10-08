"""Contracts / interface definitions for Broadcast Mind.

Conceptual interfaces matching the architecture specification.
Implementation in core/world_store.py and core/persistence.py.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .models import (
    Story, Event, Claim, Evidence, Entity,
    WorldSnapshot, SnapshotDiff, StoryFilter, ClaimFilter, Correction
)


class WorldStore(ABC):
    """Abstract world store interface.

    All world state operations go through this interface.
    Append-only semantics: no UPDATE or DELETE on core records.
    Corrections create new records that reference the original.
    """

    @abstractmethod
    async def add_story(self, story: Story) -> str:
        """Add a new story. Returns story_id."""
        ...

    @abstractmethod
    async def get_story(self, story_id: str) -> Optional[Story]:
        """Retrieve a story by ID."""
        ...

    @abstractmethod
    async def list_stories(self, filter: Optional[StoryFilter] = None) -> List[Story]:
        """List stories with optional filtering."""
        ...

    @abstractmethod
    async def add_event(self, event: Event) -> str:
        """Add a new event. Returns event_id."""
        ...

    @abstractmethod
    async def get_events_for_story(self, story_id: str) -> List[Event]:
        """Get all events for a story."""
        ...

    @abstractmethod
    async def add_claim(self, claim: Claim) -> str:
        """Add a new claim. Returns claim_id."""
        ...

    @abstractmethod
    async def get_claim(self, claim_id: str) -> Optional[Claim]:
        """Retrieve a claim by ID."""
        ...

    @abstractmethod
    async def list_claims(self, filter: Optional[ClaimFilter] = None) -> List[Claim]:
        """List claims with optional filtering."""
        ...

    @abstractmethod
    async def add_evidence(self, evidence: Evidence) -> str:
        """Add new evidence. Returns evidence_id."""
        ...

    @abstractmethod
    async def get_evidence_for_claim(self, claim_id: str) -> List[Evidence]:
        """Get all evidence for a claim."""
        ...

    @abstractmethod
    async def add_entity(self, entity: Entity) -> str:
        """Add a new entity. Returns entity_id."""
        ...

    @abstractmethod
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by ID."""
        ...

    @abstractmethod
    async def list_entities(self) -> List[Entity]:
        """List all entities."""
        ...

    @abstractmethod
    async def correct_record(self, record_id: str, correction: Correction) -> str:
        """Create a correction record for an existing record.

        The original is NOT modified — append-only semantics.
        """
        ...

    @abstractmethod
    async def create_snapshot(self) -> WorldSnapshot:
        """Create a point-in-time snapshot of the world state."""
        ...

    @abstractmethod
    async def compare_snapshots(self, a: str, b: str) -> SnapshotDiff:
        """Compare two snapshots and return the diff."""
        ...

    @abstractmethod
    async def get_snapshot(self, snapshot_id: str) -> Optional[WorldSnapshot]:
        """Retrieve a snapshot by ID."""
        ...

    @abstractmethod
    async def list_snapshots(self) -> List[WorldSnapshot]:
        """List all snapshots in reverse chronological order."""
        ...
"""Domain model dataclasses and enums for Broadcast Mind."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


class StoryStatus(Enum):
    ACTIVE = "active"
    UPDATING = "updating"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"


class ClaimStatus(Enum):
    UNVERIFIED = "unverified"
    PARTIALLY_VERIFIED = "partially_verified"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"


class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"


class EpistemicCategory(Enum):
    FACT = "fact"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    ANALYSIS = "analysis"
    INTERPRETATION = "interpretation"
    SPECULATION = "speculation"
    FICTION = "fiction"
    SATIRE = "satire"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


class SegmentType(Enum):
    BREAKING = "breaking"
    UPDATE = "update"
    ANALYSIS = "analysis"
    RETROSPECTIVE = "retrospective"
    EXPLAINER = "explainer"
    OPINION = "opinion"
    DISCOVERY = "discovery"
    DEEP_DIVE = "deep_dive"
    HUMOR = "humor"
    SYNTHETIC = "synthetic"


@dataclass
class Story:
    story_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    summary: str = ""
    status: StoryStatus = StoryStatus.ACTIVE
    first_seen: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    entity_ids: List[str] = field(default_factory=list)
    claim_ids: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    corrected_by: Optional[str] = None


@dataclass
class Event:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    story_id: str = ""
    source_url: str = ""
    fetched_at: datetime = field(default_factory=datetime.now)
    title: str = ""
    content: str = ""
    published_at: Optional[datetime] = None
    extractor: str = "rss"
    entity_ids: List[str] = field(default_factory=list)
    claim_ids: List[str] = field(default_factory=list)
    epistemic_category: EpistemicCategory = EpistemicCategory.UNKNOWN
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    corrected_by: Optional[str] = None


@dataclass
class Claim:
    claim_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim_text: str = ""
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    confidence: float = 0.0
    evidence_ids: List[str] = field(default_factory=list)
    contradiction_ids: List[str] = field(default_factory=list)
    source_url: str = ""
    extractor: str = "rss"
    created_at: datetime = field(default_factory=datetime.now)
    corrected_by: Optional[str] = None


@dataclass
class Evidence:
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim_id: str = ""
    source_url: str = ""
    content: str = ""
    extraction_method: str = "rss"
    extractor: str = "rss"
    reliability: float = 0.0
    epistemic_category: EpistemicCategory = EpistemicCategory.EVIDENCE
    created_at: datetime = field(default_factory=datetime.now)
    correction_of: Optional[str] = None


@dataclass
class Entity:
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    entity_type: EntityType = EntityType.CONCEPT
    aliases: List[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    mention_count: int = 1
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Correction:
    correction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    corrects_id: str = ""
    new_evidence_id: str = ""
    correction_type: str = "updated"  # CONFIRMED/UPDATED/CONTRADICTED/RETRACTED/UNRESOLVED
    explanation: str = ""
    confidence: float = 0.0
    detected_by: str = "system"  # analyst, user, automated
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorldSnapshot:
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    story_count: int = 0
    claim_count: int = 0
    evidence_count: int = 0
    entity_count: int = 0
    story_summaries: Dict[str, str] = field(default_factory=dict)
    claim_summaries: Dict[str, str] = field(default_factory=dict)
    diff_from_previous: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StoryFilter:
    status: Optional[StoryStatus] = None
    entity_id: Optional[str] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None


@dataclass
class ClaimFilter:
    status: Optional[ClaimStatus] = None
    source_url: Optional[str] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None


@dataclass
class SnapshotDiff:
    a_id: str = ""
    b_id: str = ""
    new_stories: List[str] = field(default_factory=list)
    resolved_stories: List[str] = field(default_factory=list)
    new_claims: List[str] = field(default_factory=list)
    changed_claims: List[str] = field(default_factory=list)
    new_evidence: List[str] = field(default_factory=list)
    new_entities: List[str] = field(default_factory=list)
    confidence_changes: Dict[str, float] = field(default_factory=dict)
    human_readable: str = ""
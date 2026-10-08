"""World snapshot service for Broadcast Mind."""

from datetime import datetime
from typing import Optional, List

from .models import WorldSnapshot, SnapshotDiff
from .persistence import WorldStore


class SnapshotService:
    """Creates, compares, and retrieves world snapshots."""

    def __init__(self, world_store: WorldStore):
        self.world_store = world_store

    async def create_snapshot(self) -> WorldSnapshot:
        """Capture current world state as a snapshot."""
        snapshot = await self.world_store.create_snapshot()
        return snapshot

    async def compare_snapshots(self, a_id: str, b_id: str) -> SnapshotDiff:
        """Compare two snapshots and return the diff."""
        diff = await self.world_store.compare_snapshots(a_id, b_id)
        return diff

    async def get_latest_snapshot(self) -> Optional[WorldSnapshot]:
        """Get the most recent snapshot."""
        snapshots = await self.world_store.list_snapshots()
        if not snapshots:
            return None
        return snapshots[0]

    async def get_snapshot_diff_from_previous(
        self, snapshot_id: str
    ) -> Optional[SnapshotDiff]:
        """Get diff between a snapshot and its predecessor."""
        snapshots = await self.world_store.list_snapshots()
        if not snapshots:
            return None

        target_idx = None
        for i, s in enumerate(snapshots):
            if s.snapshot_id == snapshot_id:
                target_idx = i
                break

        if target_idx is None or target_idx == 0:
            return None

        prev = snapshots[target_idx - 1]
        return await self.world_store.compare_snapshots(
            prev.snapshot_id, snapshot_id
        )
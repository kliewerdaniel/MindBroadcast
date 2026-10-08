import asyncio
from core.models import Story, StoryStatus, Entity, EntityType
from core.persistence import WorldStore, Database
from datetime import datetime

print("=== Test 1: single instance ===")
store = WorldStore(db_path=":memory:")
print("Schema version after init:", store.db.get_schema_version())
print("Cached conn:", store.db._conn is not None)

story = Story(
    title="Test",
    summary="Test",
    status=StoryStatus.ACTIVE,
    first_seen=datetime(2026,1,1),
    last_updated=datetime(2026,1,1),
    entity_ids=["e1"],
    claim_ids=["c1"],
    confidence=0.7,
)

async def test1():
    sid = await store.add_story(story)
    print("Added story:", sid)
    retrieved = await store.get_story(sid)
    print("Retrieved:", retrieved is not None)
    return retrieved

result = asyncio.run(test1())
print("Result:", result is not None)
print()

# Test 2: check the entities table dedup issue
print("=== Test 2: entity dedup ===")
store2 = WorldStore(db_path=":memory:")
entity1 = Entity(
    name="Climate Summit 2025",
    entity_type=EntityType.CONCEPT,
    aliases=["COP30"],
    first_seen=datetime(2026,1,1),
    last_seen=datetime(2026,1,1),
    mention_count=5,
)
async def test2():
    eid = await store2.add_entity(entity1)
    print("Added entity:", eid)
    retrieved = await store2.get_entity(eid)
    print("Retrieved:", retrieved is not None)

asyncio.run(test2())
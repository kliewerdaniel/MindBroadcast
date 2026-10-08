import asyncio
from core.models import Story, StoryStatus, Entity, EntityType
from core.persistence import WorldStore, Database, _in_memory_db
from datetime import datetime

print("=== Debug: shared in-memory ===")
store1 = WorldStore(db_path=":memory:")
store2 = WorldStore(db_path=":memory:")
print("Same shared conn?", store1.db.connect() is store2.db.connect())
print("Shared dict:", _in_memory_db)

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

async def test():
    sid = await store1.add_story(story)
    print("Added by store1:", sid)
    
    conn = store1.db.connect()
    cursor = conn.execute("SELECT COUNT(*) FROM stories")
    count = cursor.fetchone()[0]
    print("Story count:", count)
    
    cursor = conn.execute("SELECT * FROM stories")
    rows = cursor.fetchall()
    for row in rows:
        print("Row:", row)
    
    retrieved = await store1.get_story(sid)
    print("Retrieved:", retrieved)

asyncio.run(test())
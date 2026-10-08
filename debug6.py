import asyncio
from core.models import Story, StoryStatus
from core.persistence import WorldStore, Database, _in_memory_db
from datetime import datetime

print("=== Debug add_story ===")
store = WorldStore(db_path=":memory:")

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
    print("Before add_story - tables:")
    conn = store.db.connect()
    cursor = conn.execute("SELECT COUNT(*) FROM stories")
    print("  Count:", cursor.fetchone()[0])
    conn.close()
    
    sid = await store.add_story(story)
    print("Added story id:", sid)
    
    print("After add_story - tables:")
    conn = store.db.connect()
    cursor = conn.execute("SELECT COUNT(*) FROM stories")
    count = cursor.fetchone()[0]
    print("  Count:", count)
    cursor = conn.execute("SELECT * FROM stories")
    rows = cursor.fetchall()
    for row in rows:
        print("  Row:", row)
    conn.close()

asyncio.run(test())
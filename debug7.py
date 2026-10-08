import asyncio
from core.models import Story, StoryStatus
from core.persistence import WorldStore, Database, _in_memory_db
from datetime import datetime

print("=== Debug add_story with same conn ===")
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
    conn = store.db.connect()
    sid = await store.add_story(story)
    print("Added story id:", sid)
    
    cursor = conn.execute("SELECT * FROM stories")
    rows = cursor.fetchall()
    print("Rows (using same conn):", len(rows))
    for row in rows:
        print("  ", row[0], row[1])
    
    conn.close()
    
    # Now try with a new connection
    conn2 = store.db.connect()
    cursor = conn2.execute("SELECT * FROM stories")
    rows = cursor.fetchall()
    print("Rows (using new conn):", len(rows))
    for row in rows:
        print("  ", row[0], row[1])
    conn2.close()

asyncio.run(test())
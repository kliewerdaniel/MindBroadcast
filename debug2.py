import asyncio
from core.models import Story, StoryStatus, Entity, EntityType
from core.persistence import WorldStore, Database
from datetime import datetime

print("=== Debug: row_to_story ===")
store = WorldStore(db_path=":memory:")
conn = store.db.connect()
cursor = conn.execute("SELECT * FROM stories LIMIT 1")
row = cursor.fetchone()
print("Row:", row)
print("Row type:", type(row))
if row:
    print("Row keys:", row.keys() if hasattr(row, 'keys') else "no keys")
    print("Row values:", row)
conn.close()
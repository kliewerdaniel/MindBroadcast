import asyncio
from core.models import Story, StoryStatus, Entity, EntityType
from core.persistence import WorldStore, Database
from datetime import datetime

print("=== Debug: check tables ===")
store = WorldStore(db_path=":memory:")
conn = store.db.connect()
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)
cursor = conn.execute("SELECT COUNT(*) FROM stories")
count = cursor.fetchone()
print("Story count:", count)
conn.close()
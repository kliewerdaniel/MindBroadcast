import asyncio
from core.models import Story, StoryStatus
from core.persistence import WorldStore, Database, _in_memory_db
from datetime import datetime

print("=== Debug step by step ===")
store = WorldStore(db_path=":memory:")
print("DB path:", store.db.db_path)
print("Connection:", store.db.connect())

# Check tables directly
conn = store.db.connect()
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)

# Insert directly
cursor = conn.execute(
    "INSERT INTO stories (story_id, title, summary, status, first_seen, last_updated, entity_ids, claim_ids, confidence, created_at, corrected_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ("test-1", "Test", "Summary", "active", "2026-01-01", "2026-01-01", "[]", "[]", 0.7, "2026-01-01", None)
)
print("Inserted rowid:", cursor.lastrowid)
conn.commit()

cursor = conn.execute("SELECT * FROM stories")
rows = cursor.fetchall()
print("Rows after commit:", len(rows))
for row in rows:
    print("  ", row)
conn.close()
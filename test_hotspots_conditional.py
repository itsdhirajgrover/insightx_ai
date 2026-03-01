#!/usr/bin/env python3
"""Test hotspots only shown when asked"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder

init_db()
db = SessionLocal()

test_queries = [
    ("fraud rate by state", False),  # Should NOT show hotspots
    ("show fraud hotspots by state", True),  # Should show hotspots
    ("top fraud rates by category", True),  # Should show hotspots
    ("fraud by bank", False),  # Should NOT show hotspots
    ("show highest fraud by bank", True),  # Should show hotspots
]

recognizer = IntentRecognizer()
builder = QueryBuilder(db)

print("=" * 80)
print("HOTSPOTS - ONLY SHOW WHEN ASKED TEST")
print("=" * 80)

for query, should_have_hotspots in test_queries:
    print(f"\n🔷 Query: {query}")
    print(f"Should have hotspots: {'✅ YES' if should_have_hotspots else '❌ NO'}")
    print("-" * 80)
    
    intent = recognizer.recognize_intent(query)
    result = builder.execute_query(intent.type, intent.entities, query)
    
    has_hotspots = any('hotspot' in k.lower() for k in result.keys())
    has_groups = 'groups' in result
    
    print(f"Has hotspots in response: {'✅ YES' if has_hotspots else '❌ NO'}")
    print(f"Has groups data: {'✅ YES' if has_groups else '❌ NO'}")
    
    if should_have_hotspots and not has_hotspots:
        print("❌ ERROR: Expected hotspots but they weren't included!")
    elif not should_have_hotspots and has_hotspots:
        print("❌ ERROR: Hotspots included but user didn't ask for them!")
    else:
        print("✅ CORRECT!")
    
    # Show response keys
    hotspot_keys = [k for k in result.keys() if 'hotspot' in k.lower()]
    if hotspot_keys:
        print(f"Hotspot keys: {hotspot_keys}")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)

db.close()

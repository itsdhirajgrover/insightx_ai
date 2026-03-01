#!/usr/bin/env python3
"""Test that hotspots ONLY appear when user says 'hotspot'"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder

init_db()
db = SessionLocal()

test_cases = [
    # Should NOT have hotspots
    ("fraud rate by banks", False),
    ("failure rate highest by banks", False),
    ("top fraud by state", False),
    ("worst failure by category", False),
    ("fraud by banks", False),
    
    # Should ONLY have hotspots
    ("show fraud hotspots by banks", True),
    ("failure hotspots by state", True),
    ("hotspots for fraud by category", True),
    ("fraud hotspots", True),
]

recognizer = IntentRecognizer()
builder = QueryBuilder(db)

print("=" * 80)
print("HOTSPOT KEYWORD-ONLY TEST")
print("=" * 80)

all_pass = True
for query, should_have_hotspots in test_cases:
    intent = recognizer.recognize_intent(query)
    result = builder.execute_query(intent.type, intent.entities, query)
    
    has_hotspots = any('hotspot' in k.lower() for k in result.keys())
    
    if has_hotspots == should_have_hotspots:
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
        all_pass = False
    
    expected = "YES" if should_have_hotspots else "NO"
    actual = "YES" if has_hotspots else "NO"
    
    print(f"{status}: '{query}'")
    print(f"       Expected hotspots: {expected}, Got: {actual}")
    
    if has_hotspots:
        hotspot_keys = [k for k in result.keys() if 'hotspot' in k.lower()]
        print(f"       Hotspots: {hotspot_keys}")

print("\n" + "=" * 80)
if all_pass:
    print("✅ ALL TESTS PASSED - Hotspots only appear when explicitly requested!")
else:
    print("❌ SOME TESTS FAILED")
print("=" * 80)

db.close()

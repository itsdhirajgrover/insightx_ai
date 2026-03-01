#!/usr/bin/env python3
"""Verify hotspots are ONLY shown when explicitly requested"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder
import json

init_db()
db = SessionLocal()

# Queries WITHOUT hotspot keywords
non_hotspot_queries = [
    "fraud rate by state",
    "show fraud by category",
    "failure rate by bank",
    "fraud analysis by state"
]

# Queries WITH hotspot keywords
hotspot_queries = [
    "show top fraud by state",
    "highest fraud hotspots",
    "worst fraud by category",
    "top 5 fraud by bank"
]

recognizer = IntentRecognizer()
builder = QueryBuilder(db)

print("=" * 80)
print("HOTSPOTS EXCLUSIVITY TEST")
print("=" * 80)

print("\n📌 QUERIES WITHOUT HOTSPOT KEYWORDS (Should have NO hotspots):")
print("-" * 80)
for query in non_hotspot_queries:
    intent = recognizer.recognize_intent(query)
    result = builder.execute_query(intent.type, intent.entities, query)
    has_hotspots = any('hotspot' in k.lower() for k in result.keys())
    status = "❌ FAIL" if has_hotspots else "✅ PASS"
    print(f"{status}: '{query}' -> Has hotspots: {has_hotspots}")
    if has_hotspots:
        hotspot_keys = [k for k in result.keys() if 'hotspot' in k.lower()]
        print(f"       Unexpected hotspots: {hotspot_keys}")

print("\n📌 QUERIES WITH HOTSPOT KEYWORDS (Should have hotspots):")
print("-" * 80)
for query in hotspot_queries:
    intent = recognizer.recognize_intent(query)
    result = builder.execute_query(intent.type, intent.entities, query)
    has_hotspots = any('hotspot' in k.lower() for k in result.keys())
    status = "✅ PASS" if has_hotspots else "❌ FAIL"
    print(f"{status}: '{query}' -> Has hotspots: {has_hotspots}")
    if has_hotspots:
        hotspot_keys = [k for k in result.keys() if 'hotspot' in k.lower()]
        print(f"       Hotspot keys: {', '.join(hotspot_keys)}")

print("\n" + "=" * 80)
print("Verification complete!")
print("=" * 80)

db.close()

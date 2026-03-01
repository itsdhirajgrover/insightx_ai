#!/usr/bin/env python3
"""Check what's returned in fraud rate response"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder
import json

init_db()
db = SessionLocal()

query = "fraud rate by state"
recognizer = IntentRecognizer()
builder = QueryBuilder(db)

intent = recognizer.recognize_intent(query)
result = builder.execute_query(intent.type, intent.entities, query)

print("=" * 80)
print(f"Query: {query}")
print(f"Entities: {intent.entities}")
print(f"Comparison Dimension: {intent.entities.get('comparison_dimension', 'NONE')}")
print("=" * 80)

print("\n📊 Response Keys Returned:")
for key in result.keys():
    print(f"  - {key}")

print("\n🔍 Detailed Breakdown:")
print(f"\n1. fraud_hotspots_by_state ({len(result.get('fraud_hotspots_by_state', []))} states):")
for spot in result.get('fraud_hotspots_by_state', [])[:3]:
    print(f"   - {spot['group']}: {spot['fraud_rate']:.2f}%")

print(f"\n2. fraud_hotspots_by_category ({len(result.get('fraud_hotspots_by_category', []))} categories):")
for spot in result.get('fraud_hotspots_by_category', [])[:3]:
    print(f"   - {spot['group']}: {spot['fraud_rate']:.2f}%")

print(f"\n3. fraud_hotspots_by_bank ({len(result.get('fraud_hotspots_by_bank', []))} banks):")
for spot in result.get('fraud_hotspots_by_bank', [])[:3]:
    print(f"   - {spot['group']}: {spot['fraud_rate']:.2f}%")

print(f"\n4. groups (if comparison_dimension present): {len(result.get('groups', []))} groups")
if result.get('groups'):
    for g in result.get('groups', [])[:3]:
        print(f"   - {g['group']}: {g['fraud_rate']:.2f}%")

print("\n" + "=" * 80)
db.close()

#!/usr/bin/env python3
"""Check exactly what response you get for 'failure rate highest by banks'"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder
import json

init_db()
db = SessionLocal()

query = "failure rate highest by banks"

recognizer = IntentRecognizer()
builder = QueryBuilder(db)

print("=" * 80)
print(f"Query: {query}")
print("=" * 80)

intent = recognizer.recognize_intent(query)
print(f"\n🔍 Intent Recognition:")
print(f"  Intent Type: {intent.type}")
print(f"  Confidence: {intent.confidence}")
print(f"  Entities: {intent.entities}")

# Check for hotspot keywords
hotspot_keywords = ["hotspot", "top ", "highest", "worst"]
found_keywords = [kw for kw in hotspot_keywords if kw in query.lower()]
print(f"\n🔑 Hotspot Keywords Found: {found_keywords}")

result = builder.execute_query(intent.type, intent.entities, query)

print(f"\n📊 Response Structure:")
print(f"  Total Keys: {len(result.keys())}")
print(f"  All Keys: {list(result.keys())}")

hotspot_keys = [k for k in result.keys() if 'hotspot' in k.lower()]
print(f"\n🔥 Hotspot Keys in Response: {hotspot_keys if hotspot_keys else 'NONE'}")

if hotspot_keys:
    print(f"\n✅ Hotspots ARE included (because 'highest' keyword was detected)")
    for key in hotspot_keys:
        data = result[key]
        print(f"\n  {key}:")
        for item in data[:3]:  # Show first 3
            print(f"    - {item['group']}: {item['failure_rate']:.2f}%")
else:
    print(f"\n❌ NO Hotspots in response")

# Show summary stats
print(f"\n📈 Summary Stats:")
print(f"  Total Transaction: {result.get('total_transactions')}")
print(f"  Failed Count: {result.get('failed_count')}")
print(f"  Failure Rate: {result.get('failure_rate_percent'):.2f}%")

if 'groups' in result:
    print(f"\n📊 Groups Data (Breakdown by bank):")
    for group in result.get('groups', [])[:5]:
        print(f"  - {group['group']}: {group['failure_rate']:.2f}% failure ({group['failed_count']}/{group['total']})")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)

db.close()

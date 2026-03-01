#!/usr/bin/env python3
"""Check response for 'Top 3 fraud categories in Delhi'"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder
import json

init_db()
db = SessionLocal()

query = "Top 3 fraud categories in Delhi"

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

result = builder.execute_query(intent.type, intent.entities, query)

print(f"\n📊 Response Keys:")
for key in sorted(result.keys()):
    print(f"  - {key}")

print(f"\n📈 Summary Stats:")
print(f"  Total Transactions: {result.get('total_transactions')}")
print(f"  Fraud Count: {result.get('fraud_count')}")
print(f"  Fraud Rate: {result.get('fraud_rate_percent'):.2f}%")

if 'groups' in result:
    print(f"\n📊 Groups Data:")
    for group in result.get('groups', [])[:5]:
        print(f"  - {group['group']}: {group['fraud_rate']:.2f}% fraud ({group['fraud_count']}/{group['total']})")

if 'fraud_by_category' in result:
    print(f"\n🏷️  Fraud by Category:")
    for item in result.get('fraud_by_category', [])[:3]:
        print(f"  - {item['category']}: {item['fraud_count']} frauds")

hotspot_keys = [k for k in result.keys() if 'hotspot' in k.lower()]
if hotspot_keys:
    print(f"\n🔥 Hotspot Keys: {hotspot_keys}")

print("\n" + "=" * 80)
print("Response complete!")
print("=" * 80)

db.close()

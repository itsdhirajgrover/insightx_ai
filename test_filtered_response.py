#!/usr/bin/env python3
"""Test filtered responses for different dimensions"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder

init_db()
db = SessionLocal()

test_queries = [
    "fraud rate by state",
    "fraud rate by category", 
    "fraud rate by bank"
]

recognizer = IntentRecognizer()
builder = QueryBuilder(db)

print("=" * 80)
print("FILTERED RESPONSE TEST - Different Dimensions")
print("=" * 80)

for query in test_queries:
    print(f"\n🔷 Query: {query}")
    print("-" * 80)
    
    intent = recognizer.recognize_intent(query)
    result = builder.execute_query(intent.type, intent.entities, query)
    
    print(f"Comparison Dimension: {intent.entities.get('comparison_dimension', 'NONE')}")
    print(f"\nResponse Keys:")
    hotspot_keys = [k for k in result.keys() if 'hotspot' in k.lower()]
    for key in hotspot_keys:
        data = result.get(key, [])
        print(f"  ✅ {key}: {len(data)} items")
    
    # Check that OTHER dimensions are NOT included
    if 'state' in query.lower():
        assert 'fraud_hotspots_by_category' not in result, "❌ Category should not be in state query!"
        assert 'fraud_hotspots_by_bank' not in result, "❌ Bank should not be in state query!"
        print(f"  ✅ fraud_hotspots_by_category: NOT included (correct)")
        print(f"  ✅ fraud_hotspots_by_bank: NOT included (correct)")
    
    elif 'category' in query.lower():
        assert 'fraud_hotspots_by_state' not in result, "❌ State should not be in category query!"
        assert 'fraud_hotspots_by_bank' not in result, "❌ Bank should not be in category query!"
        print(f"  ✅ fraud_hotspots_by_state: NOT included (correct)")
        print(f"  ✅ fraud_hotspots_by_bank: NOT included (correct)")
    
    elif 'bank' in query.lower():
        assert 'fraud_hotspots_by_state' not in result, "❌ State should not be in bank query!"
        assert 'fraud_hotspots_by_category' not in result, "❌ Category should not be in bank query!"
        print(f"  ✅ fraud_hotspots_by_state: NOT included (correct)")
        print(f"  ✅ fraud_hotspots_by_category: NOT included (correct)")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - Responses are properly filtered!")
print("=" * 80)

db.close()

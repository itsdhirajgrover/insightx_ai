#!/usr/bin/env python3
"""Test script to check fraud rate by state response"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder
import json

# Initialize database
init_db()

# Create session
db = SessionLocal()

# Test queries
test_queries = [
    "Show fraud rate by state",
    "What's the fraud rate for each state?",
    "Fraud analysis broken down by state"
]

recognizer = IntentRecognizer()
builder = QueryBuilder(db)

print("=" * 80)
print("FRAUD RATE BY STATE - RESPONSE TEST")
print("=" * 80)

for query in test_queries:
    print(f"\n🔷 Query: {query}")
    print("-" * 80)
    
    # Recognize intent
    intent = recognizer.recognize_intent(query)
    print(f"Intent Type: {intent.type}")
    print(f"Confidence: {intent.confidence}")
    print(f"Entities: {intent.entities}")
    
    # Execute query
    result = builder.execute_query(intent.type, intent.entities, query)
    
    print(f"\n📊 Response Structure:")
    print(f"  - insight: {result.get('insight')}")
    print(f"  - total_transactions: {result.get('total_transactions')}")
    print(f"  - fraud_count: {result.get('fraud_count')}")
    print(f"  - fraud_rate_percent: {result.get('fraud_rate_percent'):.2f}%")
    print(f"  - failed_count: {result.get('failed_count')}")
    print(f"  - failure_rate_percent: {result.get('failure_rate_percent'):.2f}%")
    print(f"  - risk_level: {result.get('risk_level')}")
    
    # Check if grouped by state
    if 'groups' in result:
        print(f"\n✅ Grouped by state:")
        for group in result['groups'][:5]:  # Show top 5
            print(f"  - {group['group']}: {group['fraud_rate']:.2f}% fraud rate ({group['fraud_count']}/{group['total']})")
    else:
        print(f"\n⚠️  NOT grouped by state!")
        
    # Show fraud hotspots by state
    print(f"\n🔥 Fraud Hotspots by State (Top 5):")
    for spot in result.get('fraud_hotspots_by_state', [])[:5]:
        print(f"  - {spot['group']}: {spot['fraud_rate']:.2f}% ({spot['fraud_count']}/{spot['total']})")
    
    print("\n")

db.close()
print("=" * 80)
print("Test completed!")
print("=" * 80)

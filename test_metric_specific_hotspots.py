#!/usr/bin/env python3
"""Verify hotspots match the metric requested"""

from src.database.database import SessionLocal, init_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder

init_db()
db = SessionLocal()

test_cases = [
    ("fraud rate highest by banks", "fraud_hotspots_by_bank", "fraud"),
    ("failure rate highest by banks", "failure_hotspots_by_bank", "failure"),
    ("top fraud by state", "fraud_hotspots_by_state", "fraud"),
    ("top failure by state", "failure_hotspots_by_state", "failure"),
    ("highest fraud by category", "fraud_hotspots_by_category", "fraud"),
    ("worst failure by category", "failure_hotspots_by_category", "failure"),
]

recognizer = IntentRecognizer()
builder = QueryBuilder(db)

print("=" * 80)
print("METRIC-SPECIFIC HOTSPOTS TEST")
print("=" * 80)

all_pass = True
for query, expected_hotspot, metric_type in test_cases:
    intent = recognizer.recognize_intent(query)
    result = builder.execute_query(intent.type, intent.entities, query)
    
    has_expected = expected_hotspot in result
    has_wrong_metric = False
    
    # Check if wrong metric hotspots are present
    if metric_type == "fraud":
        has_wrong_metric = any(k for k in result.keys() if "failure_hotspot" in k)
    elif metric_type == "failure":
        has_wrong_metric = any(k for k in result.keys() if "fraud_hotspot" in k)
    
    if has_expected and not has_wrong_metric:
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
        all_pass = False
    
    print(f"{status}: '{query}'")
    print(f"       Expected: {expected_hotspot} ✅" if has_expected else f"       Missing: {expected_hotspot} ❌")
    
    if has_wrong_metric:
        wrong_keys = [k for k in result.keys() if "failure_hotspot" in k or "fraud_hotspot" in k]
        wrong_for_metric = [k for k in wrong_keys if (metric_type == "fraud" and "failure" in k) or (metric_type == "failure" and "fraud" in k)]
        if wrong_for_metric:
            print(f"       ❌ Unwanted: {wrong_for_metric}")
    
    print()

print("=" * 80)
if all_pass:
    print("✅ ALL TESTS PASSED - Hotspots correctly match requested metrics!")
else:
    print("❌ SOME TESTS FAILED")
print("=" * 80)

db.close()

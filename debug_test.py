#!/usr/bin/env python
"""Debug script to find the receiver_state error"""
import sys
import traceback
import json
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder
from src.database.database import SessionLocal
from src.api.response_generator import ResponseGenerator

test_queries = [
    "Give me fraud rate state wise"
]

ir = IntentRecognizer()

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Intent recognition
        intent = ir.recognize_intent(query)
        print(f"✓ Intent recognized: {intent.type}")
        print(f"  Entities: {intent.entities}")
        
        # Step 2: Query building
        db = SessionLocal()
        qb = QueryBuilder(db)
        result = qb.execute_query(intent.type, intent.entities, query)
        print(f"✓ Query executed successfully")
        print(f"  Result keys: {list(result.keys())}")
        
        # Step 3: Response generation
        rg = ResponseGenerator()
        response = rg.generate_response(
            query,
            result,
            intent.type,
            resolved_entities=intent.entities
        )
        print(f"✓ Response generated successfully")
        print(f"  Response keys: {list(response.keys())}")
        print(f"  Explanation: {response['explanation'][:100]}...")
        
        # Step 4: Try to serialize like Pydantic would
        print("\nTrying to serialize raw_data...")
        raw_data = response.get('raw_data', {})
        print(f"  Raw data keys: {list(raw_data.keys())}")
        print(f"  Raw data types: {[(k, type(v).__name__) for k, v in raw_data.items()]}")
        
        # Try to JSON-serialize it
        try:
            json_str = json.dumps(raw_data, default=str)
            print(f"  JSON serialization: OK ({len(json_str)} bytes)")
        except Exception as je:
            print(f"  JSON serialization FAILED: {je}")
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()

#!/usr/bin/env python
"""Test the three previously failing queries"""
import requests

queries = [
    'Give me fraud rate state wise',
    'Receiver bank HDFC fraud rate',
    'Give me fraud rate state wise and show groups'
]

passing = 0
failing = 0

for q in queries:
    try:
        r = requests.post('http://127.0.0.1:8000/api/query', json={'query': q}, timeout=5)
        print(f'Q: "{q}"')
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            print(f'✓ Success - Intent: {data.get("intent")}')
            passing += 1
        else:
            print(f'✗ Error: {r.text[:200]}')
            failing += 1
    except Exception as e:
        print(f'Q: "{q}"')
        print(f'✗ Exception: {e}')
        failing += 1
    print()

print(f"\nResults: {passing} passing, {failing} failing")

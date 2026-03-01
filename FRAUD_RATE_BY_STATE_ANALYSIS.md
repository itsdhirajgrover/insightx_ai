# Fraud Rate by State - Response Analysis

## ✅ WORKING QUERIES:
1. **"Show fraud rate by state"** → Correctly extracts `comparison_dimension: 'state'` and groups results
2. **"Fraud analysis broken down by state"** → Correctly extracts `comparison_dimension: 'state'` and groups results

## ❌ BROKEN QUERY:
**"What's the fraud rate for each state?"** 
- ❌ Missing `comparison_dimension: 'state'`
- ❌ Not grouping by state
- ❌ Instead extracts `merchant_category: 'Other'` (incorrect)

---

## ROOT CAUSE:

The Entity Extractor looks for these **segmentation keywords**:
```python
seg_keywords = [
    "by state",      ✓
    "by age",        ✓
    "by category",   ✓
    "by device",     ✓
    "by network",    ✓
    "by bank",       ✓
    "by status",     ✓
    "by type"        ✓
]
```

But it DOES NOT handle:
```
"for each state"     ❌
"for state"          ❌
"per state"          ❌ (handled only for banks)
"each state"         ❌
```

---

## SOLUTION:

Add support for "for each X" pattern in `src/nlp/intent_recognizer.py`:

**File:** `src/nlp/intent_recognizer.py`
**Line:** ~475 (after seg_keywords check)

Add this pattern:
```python
# Handle "for each X" pattern (e.g., "for each state")
for_each_match = re.search(r"\bfor\s+each\s+(state|age|category|device|network|bank|transaction\s+type)\b", query_lower)
if for_each_match and 'comparison_dimension' not in entities:
    dim_word = for_each_match.group(1).lower()
    dim_map = {
        "state": "state",
        "age": "age_group",
        "category": "merchant_category",
        "device": "device_type",
        "network": "network_type",
        "bank": "bank",
        "transaction type": "transaction_type"
    }
    entities['comparison_dimension'] = dim_map.get(dim_word, dim_word)
```

---

## EXPECTED AFTER FIX:

Query: "What's the fraud rate for each state?"
```
Entities: {
    'metric': 'fraud_rate',
    'comparison_dimension': 'state'  ← NOW EXTRACTED!
}

Response:
- Grouped by state ✓
- Shows fraud rate per state ✓
- Correct hotspots analysis ✓
```

---

## TEST RESULTS SUMMARY:

| Query Pattern | Works? | Issue |
|---|---|---|
| `by state` | ✅ | None |
| `broken down by state` | ✅ | None |
| `fraud rate ... by state` | ✅ | None |
| `for each state` | ❌ | Pattern not recognized |
| `state wise fraud` | ✅ | Works via `*-wise` pattern |
| `fraud per state` | ❌ | "per" only works for banks |

---

## ADDITIONAL IMPROVEMENTS:

Also add support for these patterns:
- `"for state"` (e.g., "fraud rate for state")
- `"per state"` (e.g., "fraud per state", not just banks)
- `"each state"` (e.g., "fraud in each state")

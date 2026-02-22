# Quick Start: Context-Aware LLM Setup

## Prerequisites

✅ Python 3.8+  
✅ Running FastAPI server (main.py)  
✅ OpenAI API key (optional but recommended for context-aware features)

## Setup (5 minutes)

### Step 1: Add OpenAI API Key to .env

```bash
# Edit .env file
OPENAI_API_KEY=sk-your-actual-key-here
```

**Don't have an API key?**
- Get one from: https://platform.openai.com/api-keys
- Add billing info to your account

### Step 2: Restart the Server

```bash
# Stop current server (Ctrl+C)
# Restart
python main.py
```

**Expected output:**
```
✓ OpenAI LLM integration enabled
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If you see this, context-aware LLM is active! ✓

### Step 3: Test Conversation Flow

Open Swagger UI: http://localhost:8000/docs

## Test Script

Copy-paste this into your terminal to test the full conversation flow:

```bash
#!/bin/bash

API="http://localhost:8000/api"

# 1. Start conversation
echo "=== Starting Conversation ==="
SESSION=$(curl -s -X POST $API/conversation/start | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)
echo "Session ID: $SESSION"
echo ""

# 2. First question
echo "=== Query 1: What's the average transaction for Food? ==="
curl -s -X POST $API/query \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"What is the average transaction amount for Food?\",\"context\":{\"session_id\":\"$SESSION\"}}" | jq -r '.explanation'
echo ""

# 3. Follow-up (uses context!)
echo "=== Query 2: How about Entertainment? (CONTEXT-AWARE) ==="
curl -s -X POST $API/query \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"How about Entertainment?\",\"context\":{\"session_id\":\"$SESSION\"}}" | jq -r '.explanation'
echo ""

# 4. Another follow-up
echo "=== Query 3: Compare with Shopping ==="
curl -s -X POST $API/query \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Compare with Shopping.\",\"context\":{\"session_id\":\"$SESSION\"}}" | jq -r '.explanation'
echo ""

# 5. Risk analysis follow-up
echo "=== Query 4: What's the fraud rate? ==="
curl -s -X POST $API/query \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"What's the fraud rate?\",\"context\":{\"session_id\":\"$SESSION\"}}" | jq -r '.explanation'
echo ""

# 6. View conversation history
echo "=== Conversation History ==="
curl -s $API/conversation/$SESSION | jq '.conversation_history | length' | xargs echo "Total turns:"
```

## Python Test Script

```python
#!/usr/bin/env python3
"""
Context-Aware Conversation Test
Demonstrates follow-up question handling with LLM
"""

import requests
import json
from time import sleep

API_URL = "http://localhost:8000/api"

def test_context_aware_conversation():
    print("=" * 60)
    print("CONTEXT-AWARE LLM CONVERSATION TEST")
    print("=" * 60)
    
    # 1. Start session
    print("\n[1] Starting conversation session...")
    resp = requests.post(f"{API_URL}/conversation/start")
    session_id = resp.json()["session_id"]
    print(f"✓ Session ID: {session_id}")
    
    # 2-5: Series of questions
    queries = [
        "What is the average transaction amount for Food category?",
        "How about Entertainment?",
        "Compare with Travel category.",
        "What's the fraud rate?"
    ]
    
    for i, query in enumerate(queries, 2):
        print(f"\n[{i}] Query: {query}")
        print("-" * 60)
        
        response = requests.post(
            f"{API_URL}/query",
            json={
                "query": query,
                "context": {"session_id": session_id}
            }
        )
        
        data = response.json()
        print(f"Intent: {data['intent']}")
        print(f"Confidence: {data['confidence_score']:.2f}")
        print(f"\nResponse:\n{data['explanation']}")
        
        sleep(1)  # Polite delay between API calls
    
    # 6. Show conversation history
    print(f"\n[6] Retrieving Conversation History")
    print("-" * 60)
    
    history_resp = requests.get(f"{API_URL}/conversation/{session_id}")
    history = history_resp.json()
    
    print(f"Total conversation turns: {history['total_turns']}")
    print("\nConversation Summary:")
    
    for turn_num, turn in enumerate(history['conversation_history'], 1):
        print(f"\n  Turn {turn_num}:")
        print(f"    User: {turn['user_query']}")
        print(f"    Intent: {turn['intent']}")
        print(f"    Response: {turn['response'][:80]}...")
    
    print("\n" + "=" * 60)
    print("✓ Test Complete - Context-Aware Conversation Works!")
    print("=" * 60)

if __name__ == "__main__":
    test_context_aware_conversation()
```

Save as `test_conversation.py` and run:
```bash
python test_conversation.py
```

## Understanding the Output

### Without Context (Old):
```
User: "How about Entertainment?"
Response: "Unable to determine what to compare"
```

### With Context (New):
```
User (Q1): "Average transaction for Food?"
Response: "Food has an average of ₹450..."

User (Q2): "How about Entertainment?"
Response: "Entertainment shows ₹520 average, which is 15% higher than Food..."
          ↑ LLM understood the comparison because it has Q1's context!
```

## Real-World Conversation Examples

### Example 1: Progressive Segmentation
```
Q: "What's the average transaction?"
A: "₹475 across all transactions"

Q: "Break it down by category"
A: [Shows by category - context helps understand "it"]

Q: "Focus on Food only"
A: [Returns Food-specific analysis - context updated]

Q: "How about state-wise?"
A: [Returns Food by state - still remembers Food context]
```

### Example 2: Comparative Analysis
```
Q: "iOS vs Android comparison?"
A: [Shows device comparison with metrics]

Q: "How's WiFi in comparison?"
A: [Switches to network comparison - understands "comparison"]

Q: "Better fraud rate?"
A: [Compares fraud using latest context - WiFi vs others]
```

### Example 3: Risk Analysis Deep Dive
```
Q: "What's the fraud rate?"
A: "Overall fraud rate is 2.3%"

Q: "By category?"
A: [Shows fraud by category - context maintained]

Q: "Food category highest?"
A: [Analyzes Food fraud - understood from previous analysis]

Q: "How can we reduce it?"
A: [Provides recommendations based on Food fraud context]
```

## Monitoring & Debugging

### Check if LLM is Working

```bash
curl http://localhost:8000/docs
# Look at swagger "Try it out" - LLM responses are much longer and more conversational
```

### View Session Context

```bash
curl http://localhost:8000/api/conversation/YOUR_SESSION_ID | jq .
```

**Output shows:**
- Full conversation history
- Accumulated entities/context
- Each turn's Q&A pair

### Reset a Conversation

```bash
curl -X POST http://localhost:8000/api/conversation/YOUR_SESSION_ID/reset
```

(Keeps session ID, clears history - good for testing)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Responses are generic/template-based | LLM not enabled - add OPENAI_API_KEY to .env |
| Follow-ups don't use context | Pass `session_id` in request context field |
| "Session not found" error | Session expired - create new one with /conversation/start |
| Slow responses (>5 sec) | Normal for LLM - this is OpenAI latency |
| API key errors | Check key is valid, has billing, not expired |

## Next Steps

Once context-aware LLM is working:

1. **Integrate with UI** - Update Streamlit app (app.py) to:
   - Show session management UI
   - Display conversation history panel
   - Pass session_id between queries

2. **Add Conversation Persistence** - Store sessions in DB instead of memory

3. **Enhance Prompts** - Fine-tune LLM prompts in `response_generator.py` for your use case

4. **Add Follow-up Suggestions** - Have LLM suggest next questions

5. **Implement Query Caching** - Cache identical queries for faster response

## Quick Reference: API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /query` | Submit query (include `session_id` in context) |
| `POST /conversation/start` | Create new session |
| `GET /conversation/{session_id}` | View conversation history |
| `DELETE /conversation/{session_id}` | End conversation |
| `POST /conversation/{session_id}/reset` | Clear history |

## Expected LLM Performance

**Without LLM (Template):**
- Response time: <100ms
- Response quality: Generic, limited context

**With LLM (GPT-3.5-Turbo):**
- Response time: 1-3 seconds
- Response quality: Conversational, context-aware, natural language

---

🎉 **You're ready!** Your InsightX system now supports context-aware conversational queries.

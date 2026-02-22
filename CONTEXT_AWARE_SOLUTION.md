# Context-Aware LLM Solution for Follow-up Questions

## Overview

A comprehensive solution has been implemented to handle **conversation context** and **follow-up questions** using LLM (OpenAI GPT-3.5). This enables the system to understand follow-up queries like "How about Entertainment?" with proper context from previous questions.

## Key Changes

### 1. Enhanced ConversationManager (`src/api/conversation.py`)

**New Features:**
- **Full conversation history tracking** - Maintains complete Q&A history
- **Context extraction** - Automatically extracts valuable context from previous responses
- **Entity merging** - Intelligently merges entities from current and previous queries
- **Context retrieval** - Provides formatted conversation context for LLM

**Key Methods:**
```python
# Get full conversation history for LLM context
context = conversation_manager.get_conversation_context(session_id)

# Get accumulated entities from all turns
resolved_entities = conversation_manager.get_resolved_entities(session_id)

# Update session with full turn information
conversation_manager.update_session(
    session_id, 
    user_query,
    intent, 
    entities, 
    result,
    ai_response  # Now includes AI response for history
)
```

### 2. Context-Aware ResponseGenerator (`src/api/response_generator.py`)

**New Features:**
- **LLM Integration with Context** - Actually calls OpenAI API (not just fallback)
- **Conversation History in Prompts** - Includes previous Q&A in LLM context
- **Context-Aware Prompts** - Builds prompts that understand follow-ups
- **Resolved Entities Formatting** - Presents accumulated context to LLM

**Example Prompt:**
```
User Query: "How about Entertainment?"

Resolved Context from Conversation:
- Category: Food
- State: Maharashtra
- Device: iOS

Previous Conversation:
User: What's the average transaction amount for Food category?
Assistant: The average transaction amount for Food is ₹...

[LLM understands this is comparing Entertainment to Food]
```

### 3. Enhanced Intent Recognition (`src/nlp/intent_recognizer.py`)

**New Features:**
- **Follow-up Detection** - Identifies follow-up questions (e.g., "How about...", "vs")
- **Context-Aware Intent** - New method `recognize_intent_with_context()`
- **Smart Entity Inheritance** - Inherits context from previous queries when not explicitly mentioned

**Example:**
```python
# Q1: "Average transaction in Food?"
# Q2: "How about Entertainment?" 
# -> Automatically inherits 'category' context and changes it to Entertainment

intent = recognizer.recognize_intent_with_context(
    "How about Entertainment?",
    conversation_context={"category": "Food"}
)
# Returns: intent with category="Entertainment" (inferred from context)
```

### 4. Enhanced Routes (`src/api/routes.py`)

**Context-Aware Query Processing:**
```
POST /query
{
  "query": "What's the fraud rate for Food?",
  "context": { "session_id": "abc-123" }
}
```

**Response includes:**
```json
{
  "session_id": "abc-123",
  "explanation": "Full context-aware LLM response",
  "insights": [...],
  ...
}
```

**New Conversation Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/conversation/start` | POST | Start new conversation, get session_id |
| `/conversation/{session_id}` | GET | Retrieve conversation history |
| `/conversation/{session_id}` | DELETE | End conversation |
| `/conversation/{session_id}/reset` | POST | Clear history while keeping session |

## Usage Examples

### Example 1: Basic Conversation with Follow-ups

```bash
# Step 1: Start conversation
curl -X POST http://localhost:8000/api/conversation/start

# Response: { "session_id": "abc-123-xyz" }

# Step 2: First question
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the average transaction amount in the Food category?",
    "context": { "session_id": "abc-123-xyz" }
  }'

# Response: Full analysis with session_id

# Step 3: Follow-up question - System uses context!
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How about Entertainment?",
    "context": { "session_id": "abc-123-xyz" }
  }'

# LLM understands this is comparing Entertainment to the previously asked Food category
```

### Example 2: Multi-turn Conversation

```
User: "What is the fraud rate?"
Assistant: "The overall fraud rate is 2.3%..."

User: "By category?"
Assistant: [Uses context: intent=risk_analysis, shows fraud by category]

User: "What about Electronics?"
Assistant: [Uses context: intent=risk_analysis, category=Electronics]

User: "Compare with Food"
Assistant: [Compares Electronics fraud rate to Food fraud rate using history]
```

### Example 3: Retrieve Conversation History

```bash
# Get full conversation history
curl http://localhost:8000/api/conversation/abc-123-xyz

# Response:
{
  "session_id": "abc-123-xyz",
  "created_at": 1234567890,
  "last_updated": 1234567920,
  "total_turns": 3,
  "conversation_history": [
    {
      "timestamp": 1234567890,
      "user_query": "What is the average transaction amount?",
      "intent": "descriptive",
      "entities": { "category": "Food" },
      "response": "The averge transaction...",
      "data_summary": { "total_count": 1500, "key_metrics": {...} }
    },
    ...
  ]
}
```

## Architecture Flow

```
User Query + Session ID
        ↓
    ↓─────────────────────────────────────────────┐
    │                                               │
    ├→ ConversationManager.get_conversation_context()
    │  └→ Formats previous Q&A for LLM context
    │
    ├→ IntentRecognizer.recognize_intent_with_context()
    │  └→ Detects follow-ups, inherits entities
    │
    ├→ QueryBuilder.execute_query()
    │  └→ Runs analysis with merged entities
    │
    ├→ ResponseGenerator.generate_response()
    │  │
    │  ├→ If LLM available:
    │  │  ├→ Build context-aware prompt
    │  │  ├→ Include conversation history
    │  │  ├→ Include resolved entities
    │  │  └→ Call OpenAI API with context
    │  │
    │  └→ Else: Use template responses
    │
    ├→ ConversationManager.update_session()
    │  ├→ Store user query
    │  ├→ Store AI response
    │  ├→ Extract & update context
    │  └→ Maintain conversation history
    │
    └→ Return QueryResponse with session_id
```

## Configuration

### Environment Variables

```env
# Required for LLM context-aware responses
OPENAI_API_KEY=sk-your-key-here

# Optional: Configure session TTL (in seconds)
SESSION_TTL=3600

# Optional: Configure max conversation history per session
MAX_HISTORY=20
```

### Settings in Code

**ConversationManager** (`src/api/conversation.py`):
```python
# TTL for sessions (default: 1 hour)
conversation_manager = ConversationManager(ttl_seconds=3600)

# Max history turns to keep in memory (default: 20)
conversation_manager = ConversationManager(max_history=20)
```

## Follow-up Detection Patterns

The system automatically detects follow-up questions:

- "How about [entity]?"
- "What about [entity]?"
- "Compare [entity] with [previous]"
- "VS", "versus", "between"
- "Like", "similar", "different"
- "What else", "any other"
- "Break it down", "segment"
- "More details", "tell me more"

**Example Flow:**
```
Q1: "Average transaction in Food?"
    └→ Stores: intent=descriptive, category=Food

Q2: "How about Entertainment?" 
    └→ Detected as follow-up
    └→ Inherits category context from Q1
    └→ Automatically infers: category=Entertainment
    └→ Compares both in response with history context
```

## Benefits of This Solution

✅ **Follow-up Question Support** - "How about X?" works because context is maintained  
✅ **True Conversation Context** - LLM sees previous Q&A  
✅ **Smart Entity Inheritance** - Avoids repeating "category=Food" in every query  
✅ **Conversation History** - Full trace of dialogue for user and system  
✅ **Multi-turn Dialogue** - Supports complex back-and-forth analysis  
✅ **Confidence in Responses** - LLM understands what was asked before  
✅ **Implicit Reference Resolution** - "That" and "it" understood from context  

## Testing the Solution

### Manual Testing with cURL

```bash
# 1. Start conversation
SESSION=$(curl -s -X POST http://localhost:8000/api/conversation/start | jq -r .session_id)

# 2. First query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What's the average transaction for Food?\",
    \"context\": { \"session_id\": \"$SESSION\" }
  }" | jq .explanation

# 3. Follow-up - LLM should understand context!
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"How about Entertainment?\",
    \"context\": { \"session_id\": \"$SESSION\" }
  }" | jq .explanation

# 4. View conversation history
curl http://localhost:8000/api/conversation/$SESSION | jq .
```

### Python Testing

```python
import requests
import json

API_URL = "http://localhost:8000/api"

# Start conversation
session_resp = requests.post(f"{API_URL}/conversation/start").json()
session_id = session_resp["session_id"]

# First query
q1 = {
    "query": "Average transaction amount for Food?",
    "context": {"session_id": session_id}
}
r1 = requests.post(f"{API_URL}/query", json=q1).json()
print(f"Q1 Response:\n{r1['explanation']}\n")

# Follow-up query (uses context!)
q2 = {
    "query": "How about Entertainment?",
    "context": {"session_id": session_id}
}
r2 = requests.post(f"{API_URL}/query", json=q2).json()
print(f"Q2 Response (with context):\n{r2['explanation']}\n")

# View history
history = requests.get(f"{API_URL}/conversation/{session_id}").json()
print(f"Conversation turns: {history['total_turns']}")
```

## Troubleshooting

### Issue: "LLM integration not available" warning

**Solution:**
1. Check `OPENAI_API_KEY` is set in `.env`
2. Restart the server
3. Check API key is valid (test in OpenAI dashboard)

### Issue: Follow-ups not understanding context

**Solution:**
1. Ensure session_id is passed in `context`
2. Check conversation history: `GET /conversation/{session_id}`
3. Verify entities are being extracted in first query
4. Check LLM is enabled (see warning above)

### Issue: Slow responses

**Solution:**
1. LLM calls take 1-3 seconds - this is normal
2. Use template responses by not setting OPENAI_API_KEY for faster responses
3. Increase timeout in client if needed

## Future Enhancements

- [ ] Implement query caching for identical questions
- [ ] Add multi-session resumption (load old sessions)
- [ ] Enhance context with temporal understanding
- [ ] Add semantic similarity for context relevance
- [ ] Implement intent clarification when ambiguous
- [ ] Support explicit context override ("ignore Food, focus on...")
- [ ] Analytics on follow-up patterns
- [ ] Persistent session storage (database)

## Integration Checklist

✅ ConversationManager enhanced with full history  
✅ ResponseGenerator uses LLM with context  
✅ IntentRecognizer detects follow-ups  
✅ Routes process context in queries  
✅ New conversation management endpoints  
✅ Proper entity merging and resolution  
✅ LLM prompt engineering for context awareness  
✅ Session TTL and memory management  

## API Response Structure (Comparison)

### Before (No Context)
```json
{
  "query": "How about Entertainment?",
  "explanation": "Unable to determine what category to compare",
  "insights": []
}
```

### After (With Context)
```json
{
  "query": "How about Entertainment?",
  "session_id": "abc-123",
  "explanation": "Based on our previous analysis of Food (avg: ₹450), Entertainment shows a higher average transaction of ₹520...",
  "insights": [
    "Entertainment avg: ₹520 vs Food avg: ₹450",
    "29% higher transaction values in Entertainment",
    "Both show similar fraud rates..."
  ]
}
```

---

## Summary

This solution transforms InsightX from a **stateless query processor** to a **stateful conversational AI** that:

1. **Understands conversation context** - Remembers previous questions
2. **Handles follow-ups naturally** - "How about X?" works seamlessly  
3. **Uses LLM effectively** - Provides rich context to GPT-3.5
4. **Maintains conversation history** - Full trace for debugging and insights
5. **Supports multi-turn dialogue** - Complex analysis through back-and-forth

**Key enabler:** Session-based conversation context that merges entity tracking with LLM prompt engineering.

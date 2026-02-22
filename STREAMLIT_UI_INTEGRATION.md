# Streamlit UI Integration for Context-Aware Conversations

This guide shows how to update the Streamlit app (`app.py`) to leverage the new context-aware conversation features.

## Current State vs Improved State

### Before
- ❌ Each query is independent
- ❌ No conversation history shown
- ❌ Can't handle "How about X?" follow-ups
- ❌ No session management

### After  
- ✅ Conversations with context
- ✅ Conversation history panel
- ✅ Automatic follow-up understanding
- ✅ Visual session management

## Updated Streamlit App Structure

```python
import streamlit as st
import requests
import json
from datetime import datetime

# ============================================================
# 1. PAGE CONFIG & SESSION STATE
# ============================================================

st.set_page_config(
    page_title="InsightX - Conversational AI",
    page_icon="💬",
    layout="wide"
)

# Initialize Streamlit session state (different from API session!)
if "api_session_id" not in st.session_state:
    st.session_state.api_session_id = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

API_URL = "http://localhost:8000/api"

# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def start_new_conversation():
    """Start a new API conversation session"""
    try:
        response = requests.post(f"{API_URL}/conversation/start")
        session_data = response.json()
        st.session_state.api_session_id = session_data["session_id"]
        st.session_state.conversation_history = []
        st.success(f"✓ New conversation started (ID: {session_data['session_id'][:8]}...)")
    except Exception as e:
        st.error(f"Failed to start conversation: {e}")

def end_conversation():
    """End current conversation"""
    if st.session_state.api_session_id:
        try:
            requests.delete(f"{API_URL}/conversation/{st.session_state.api_session_id}")
            st.session_state.api_session_id = None
            st.session_state.conversation_history = []
            st.info("Conversation ended")
        except Exception as e:
            st.error(f"Failed to end conversation: {e}")

def submit_query(query_text: str) -> dict:
    """
    Submit query with conversation context
    Returns the response JSON
    """
    if not query_text.strip():
        st.warning("Please enter a query")
        return None
    
    # Ensure we have a session
    if not st.session_state.api_session_id:
        start_new_conversation()
    
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={
                "query": query_text,
                "context": {
                    "session_id": st.session_state.api_session_id
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Store in local history for display
            st.session_state.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "user",
                "content": query_text,
                "intent": result.get("intent"),
                "confidence": result.get("confidence_score")
            })
            
            st.session_state.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "assistant",
                "content": result.get("explanation"),
                "insights": result.get("insights"),
                "raw_data": result.get("raw_data")
            })
            
            return result
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. Server may be processing - try again.")
        return None
    except Exception as e:
        st.error(f"Error submitting query: {e}")
        return None

# ============================================================
# 3. SIDEBAR CONTROLS
# ============================================================

with st.sidebar:
    st.title("💬 InsightX Chat")
    
    st.subheader("Conversation Management")
    
    # Session info
    if st.session_state.api_session_id:
        st.info(f"📌 Session: {st.session_state.api_session_id[:12]}...")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Chat", use_container_width=True):
                start_new_conversation()
        with col2:
            if st.button("❌ End Chat", use_container_width=True):
                end_conversation()
    else:
        if st.button("▶ Start Conversation", use_container_width=True):
            start_new_conversation()
    
    st.divider()
    
    # Instructions
    st.subheader("💡 Tips for Follow-ups")
    st.markdown("""
    - **First query:** Ask about any metric
    - **Follow-up:** Say "How about X?" to compare
    - **Comparisons:** "Compare with Y" works!
    - **Context**: System remembers previous queries
    
    **Examples:**
    1. "Average transaction for Food?"
    2. "How about Entertainment?"
    3. "By state?" (uses previous context)
    """)
    
    st.divider()
    
    # Settings
    st.subheader("⚙ Settings")
    show_raw_data = st.checkbox("Show raw data", value=False)
    show_insights = st.checkbox("Show insights", value=True)

# ============================================================
# 4. MAIN CHAT INTERFACE
# ============================================================

st.title("🤖 InsightX Conversational AI")
st.markdown("Ask questions about transaction data using natural language")

# Display conversation history
if st.session_state.conversation_history:
    st.subheader("📝 Conversation")
    
    for i, msg in enumerate(st.session_state.conversation_history):
        if msg["type"] == "user":
            # User message
            with st.chat_message("user"):
                st.write(msg["content"])
                if msg.get("intent"):
                    st.caption(f"Intent: {msg['intent'][:20]} | Confidence: {msg['confidence']:.1%}")
        
        else:
            # Assistant message
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                
                # Show insights if enabled
                if show_insights and msg.get("insights"):
                    with st.expander("📊 Key Insights"):
                        for insight in msg["insights"]:
                            st.write(f"• {insight}")
                
                # Show raw data if enabled
                if show_raw_data and msg.get("raw_data"):
                    with st.expander("📋 Raw Data"):
                        st.json(msg["raw_data"])

# ============================================================
# 5. INPUT & QUERY SUBMISSION
# ============================================================

st.divider()

# Input area
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Ask a question about the transaction data:",
        placeholder="e.g., What's the average transaction amount for Food?",
        key="user_input"
    )

with col2:
    submit_button = st.button("Send", use_container_width=True, type="primary")

# Process submission
if submit_button and user_input:
    with st.spinner("🤔 Processing your query..."):
        result = submit_query(user_input)
        
        if result:
            st.rerun()  # Refresh to show new message

# ============================================================
# 6. QUICK ACTIONS
# ============================================================

st.divider()
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

example_queries = [
    "Average transaction amount?",
    "Compare iOS vs Android",
    "Fraud rate by category?",
    "Peak hours for transactions?",
    "Age group segmentation?",
    "Risk analysis summary?"
]

for idx, query in enumerate(example_queries):
    col = col1 if idx % 3 == 0 else (col2 if idx % 3 == 1 else col3)
    with col:
        if st.button(query, use_container_width=True, key=f"quick_{idx}"):
            st.session_state.user_input = query
            with st.spinner("🤔 Processing..."):
                result = submit_query(query)
                if result:
                    st.rerun()

# ============================================================
# 7. CONVERSATION EXPORT (OPTIONAL)
# ============================================================

if st.session_state.conversation_history:
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as JSON
        if st.button("📥 Export Conversation"):
            export_data = {
                "session_id": st.session_state.api_session_id,
                "exported_at": datetime.now().isoformat(),
                "conversation": st.session_state.conversation_history
            }
            st.json(export_data)
    
    with col2:
        # Clear local history
        if st.button("🗑 Clear Display"):
            st.session_state.conversation_history = []
            st.rerun()
```

## Key Features Explained

### 1. **Session Management**
```python
# Automatically manages API session (different from Streamlit's)
st.session_state.api_session_id  # Your conversation session at backend
```

### 2. **Context-Aware Queries**
```python
# Each query includes the session_id so backend understands context
response = requests.post(
    f"{API_URL}/query",
    json={
        "query": user_input,
        "context": {"session_id": st.session_state.api_session_id}  # ← KEY!
    }
)
```

### 3. **Conversation History Display**
```python
# Shows Q&A in chat-like format
for msg in st.session_state.conversation_history:
    if msg["type"] == "user":
        st.chat_message("user")  # Shows as user message
    else:
        st.chat_message("assistant")  # Shows as assistant message
```

### 4. **Intent & Confidence Display**
```python
# Shows what the system understood
st.caption(f"Intent: {intent} | Confidence: {confidence:.0%}")
```

## Installation Steps

1. **Update app.py** with the code above
2. **Restart Streamlit:**
   ```bash
   streamlit run app.py
   ```
3. **Test a conversation:**
   - Click "Start Conversation"
   - Ask "Average transaction for Food?"
   - Ask "How about Entertainment?" → Should work with context!

## Advanced Customizations

### Show Conversation Summary

```python
# In sidebar, show conversation stats
if st.session_state.conversation_history:
    st.sidebar.metric(
        "Turns",
        len([m for m in st.session_state.conversation_history if m["type"] == "user"])
    )
```

### Auto-suggest Follow-ups

```python
# Get LLM to suggest next questions
def get_follow_up_suggestions(session_id: str):
    """Ask LLM what follow-up questions make sense"""
    # This would require a new API endpoint
    pass

# In chat, show suggestions
if last_assistant_message:
    suggestions = get_follow_up_suggestions(st.session_state.api_session_id)
    st.info(f"💡 You could also ask: {suggestions}")
```

### Dark Mode Support

```python
st.markdown("""
<style>
    .stChat {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)
```

### Context Visualization

```python
# Show accumulated context
if st.session_state.api_session_id:
    st.sidebar.subheader("🎯 Current Context")
    
    # Get session details
    history = requests.get(f"{API_URL}/conversation/{st.session_state.api_session_id}").json()
    
    # Extract and display context
    for turn in history["conversation_history"]:
        if turn.get("entities"):
            st.sidebar.write(f"**{turn['intent']}**")
            for key, val in turn["entities"].items():
                st.sidebar.write(f"  - {key}: {val}")
```

## Testing the UI

### Test Flow

```
1. Browser opens: http://localhost:8000/docs or localhost:8501 (Streamlit)
2. Click "Start Conversation"
3. Enter: "Average transaction amount for Food?"
   ✓ Should see response with "Food" context
4. Enter: "How about Entertainment?"
   ✓ Should see comparison (shows Entertainment vs Food)
5. Enter: "By state?"
   ✓ Should segment by state (retains Food context)
```

### Debugging

If context doesn't work:
1. Check browser console (F12)
2. Check API logs: `http://localhost:8000/docs`
3. Verify session_id is being passed
4. Test API directly with curl (use SETUP_CONTEXT_AWARE_LLM.md)

## Performance Optimization

### Lazy Load Conversation History

```python
# Only show last 5 turns for performance
display_history = st.session_state.conversation_history[-10:]
for msg in display_history:
    # Display...
```

### Cache API Responses

```python
@st.cache_data
def fetch_supported_entities():
    return requests.get(f"{API_URL}/supported-entities").json()

entities = fetch_supported_entities()
```

## Mobile Responsiveness

Streamlit is mobile-responsive by default, but for better chat UX:

```python
# Better mobile chat layout
if st.session_state.conversation_history:
    for msg in st.session_state.conversation_history:
        if msg["type"] == "user":
            st.write(f"👤 {msg['content']}")
        else:
            st.info(msg['content'])  # Better visual separation on mobile
```

---

## Summary

By integrating the updated Streamlit app with the context-aware API:

✅ Users can have natural multi-turn conversations  
✅ Follow-up questions like "How about X?" work seamlessly  
✅ Full conversation history is visible and traceable  
✅ Intent and confidence scores shown for transparency  
✅ Session management is simple and intuitive  

This transforms InsightX from a simple query tool into a **full conversational analytics platform**! 🚀

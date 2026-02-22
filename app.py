import streamlit as st
import requests
import json
import os
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="InsightX - Payment Analytics AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .header-title {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .query-input {
        border: 2px solid #667eea;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Load API URL from environment or Streamlit secrets, fall back to localhost
def get_api_url():
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        return st.secrets.get("api_url", "http://localhost:8000")
    except:
        # Fall back to environment variable
        return os.getenv("API_URL", "http://localhost:8000")

if "api_url" not in st.session_state:
    st.session_state.api_url = get_api_url()
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "api_session_status" not in st.session_state:
    st.session_state.api_session_status = "No session"

# Sidebar
with st.sidebar:
    st.title("💬 InsightX Chat")
    
    # Conversation Management
    st.subheader("🎯 Conversation")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Start New", use_container_width=True, help="Begin a new conversation"):
            try:
                response = requests.post(
                    f"{st.session_state.api_url}/api/conversation/start",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.conversation_history = []
                    st.session_state.query_history = []
                    st.success(f"✓ Started: {data['session_id'][:12]}...")
                    st.rerun()
            except Exception as e:
                st.error(f"Failed: {e}")
    
    with col2:
        if st.button("❌ End", use_container_width=True, help="End current conversation"):
            if st.session_state.session_id:
                try:
                    requests.delete(
                        f"{st.session_state.api_url}/api/conversation/{st.session_state.session_id}",
                        timeout=5
                    )
                except:
                    pass
                st.session_state.session_id = None
                st.session_state.conversation_history = []
                st.session_state.query_history = []
                st.info("Conversation ended")
                st.rerun()
    
    # Session status
    if st.session_state.session_id:
        st.info(f"📌 Session: {st.session_state.session_id[:20]}...")
    else:
        st.warning("No active session")
    
    st.divider()
    
    st.subheader("💡 Tips for Follow-ups")
    st.markdown("""
    - **Q1:** Ask about any metric
    - **Q2:** Say "How about X?" to compare
    - **Q3:** "By state?" reuses previous context
    
    **Example Flow:**
    1. "Average for Food?"
    2. "How about Travel?"  ← Compares to Food!
    3. "By state?" ← Still about Travel
    """)
    
    st.divider()
    
    st.subheader("📚 Example Queries")
    example_queries = [
        "What's the average transaction amount?",
        "Food category transactions?",
        "How about Travel?",
        "Fraud rate?",
        "By state?"
    ]
    
    for i, query in enumerate(example_queries, 1):
        if st.button(f"📌 {query}", key=f"example_{i}", use_container_width=True):
            st.session_state.user_query = query
            st.rerun()
    
    st.divider()
    
    st.subheader("⚙️ Settings")
    
    api_url = st.text_input(
        "API Endpoint",
        value=st.session_state.api_url,
        help="Enter the FastAPI server URL"
    )
    st.session_state.api_url = api_url
    
    show_raw = st.checkbox("Show raw data", value=False)
    show_insights = st.checkbox("Show insights", value=True)

# Main Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="header-title">💳 InsightX</div>', unsafe_allow_html=True)
    st.markdown("**Natural Language Interface for Payment Analytics**")
with col2:
    # Health check
    try:
        response = requests.get(f"{st.session_state.api_url}/api/health", timeout=2)
        if response.status_code == 200:
            st.success("✓ API Connected")
        else:
            st.error("✗ API Error")
    except:
        st.error("✗ API Down")

st.divider()

# Display conversation history (chat-like format)
if st.session_state.conversation_history:
    st.subheader("💬 Conversation")
    
    for msg in st.session_state.conversation_history:
        if msg["type"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
                if msg.get("intent"):
                    st.caption(f"Intent: **{msg['intent']}** | Confidence: **{msg['confidence']:.0%}**")
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                if msg.get("insights") and show_insights:
                    with st.expander("📊 Key Insights"):
                        for insight in msg["insights"]:
                            st.write(f"• {insight}")

st.divider()

# Main query section
st.subheader("🤔 Ask Your Question")

user_query = st.text_area(
    "Enter your question about transaction data:",
    placeholder="E.g., What's the average transaction amount for Food category?",
    height=100,
    key="user_query"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit_button = st.button("🚀 Analyze", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)
with col3:
    if st.button("📞 Get Examples", use_container_width=True):
        st.info("Check the sidebar for example queries!")

if clear_button:
    st.session_state.user_query = ""
    st.rerun()

# Process query
if submit_button and user_query:
    
    with st.spinner("🔍 Analyzing with LLM context..."):
        try:
            api_response = requests.post(
                f"{st.session_state.api_url}/api/query",
                json={"query": user_query, "context": {"session_id": st.session_state.session_id}},
                timeout=30
            )
            
            if api_response.status_code == 200:
                result = api_response.json()

                # Persist session id for follow-ups
                returned_session = result.get("session_id")
                if returned_session:
                    st.session_state.session_id = returned_session
                
                # Store in conversation history
                st.session_state.conversation_history.append({
                    "type": "user",
                    "content": user_query,
                    "intent": result.get("intent"),
                    "confidence": result.get("confidence_score", 0)
                })
                
                st.session_state.conversation_history.append({
                    "type": "assistant",
                    "content": result.get("explanation", ""),
                    "insights": result.get("insights", []),
                    "raw_data": result.get("raw_data", {})
                })
                
                # Add to legacy history
                st.session_state.query_history.append({
                    "query": user_query,
                    "intent": result.get("intent"),
                    "timestamp": datetime.now()
                })
                
                st.success("✓ Analysis Complete!")
                st.rerun()
                
            else:
                st.error(f"API Error: {api_response.status_code}")
                st.error(api_response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
            st.info("Run `python main.py` in another terminal to start the server")
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout. The server is taking too long to respond.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 FastAPI + Streamlit")
with col2:
    st.caption(f"📅 {datetime.now().strftime('%b %d, %Y')}")
with col3:
    if st.session_state.session_id:
        st.caption(f"✅ Session Active")
    else:
        st.caption(f"⏸️ Start a conversation to begin")

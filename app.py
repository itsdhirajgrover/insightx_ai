import streamlit as st
import requests
import json
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
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    api_url = st.text_input(
        "API Endpoint",
        value=st.session_state.api_url,
        help="Enter the FastAPI server URL"
    )
    st.session_state.api_url = api_url
    
    st.divider()
    
    st.subheader("📚 Example Queries")
    example_queries = [
        "What's the average transaction amount for Food category?",
        "Compare transaction amounts between iOS and Android",
        "Show me transaction patterns by state",
        "What's the fraud rate for Shopping category?",
        "Which age group has most transactions?"
    ]
    
    for i, query in enumerate(example_queries, 1):
        if st.button(f"📌 {i}. {query[:45]}...", key=f"example_{i}"):
            st.session_state.user_query = query
            st.rerun()
    st.divider()
    if st.button("🔁 Reset Conversation", help="Clear current session and start fresh"):
        st.session_state.session_id = None
        st.session_state.query_history = []
        st.experimental_rerun()

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
    st.divider()
    
    with st.spinner("🔍 Analyzing your query..."):
        try:
            api_response = requests.post(
                f"{st.session_state.api_url}/api/query",
                json={"query": user_query, "context": {"session_id": st.session_state.session_id}},
                timeout=30
            )
            
            if api_response.status_code == 200:
                result = api_response.json()

                # persist session id for follow-ups
                returned_session = result.get("session_id")
                if returned_session:
                    st.session_state.session_id = returned_session
                
                # Add to history
                st.session_state.query_history.append({
                    "query": user_query,
                    "intent": result.get("intent"),
                    "timestamp": datetime.now()
                })
                
                # Display results
                st.success("✓ Analysis Complete!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence Score", f"{result.get('confidence_score', 0)*100:.1f}%")
                with col2:
                    intent = result.get("intent", "unknown")
                    intent_emojis = {
                        "descriptive": "📊",
                        "comparative": "⚖️",
                        "user_segmentation": "👥",
                        "risk_analysis": "⚠️"
                    }
                    st.metric("Intent Type", f"{intent_emojis.get(intent, '❓')} {intent.title()}")
                with col3:
                    st.metric("Data Points", result.get("raw_data", {}).get("total_count", 0))
                
                st.divider()
                
                # Main explanation
                st.subheader("📈 Analysis Result")
                st.markdown(f"""
                <div class="insight-box">
                {result.get('explanation', 'No explanation available')}
                </div>
                """, unsafe_allow_html=True)
                
                # Insights
                st.subheader("💡 Key Insights")
                insights = result.get("insights", [])
                if insights:
                    for insight in insights[:5]:
                        st.info(f"• {insight}")
                else:
                    st.warning("No insights available")
                
                # Visualizations
                raw = result.get("raw_data", {}) or {}

                # Segmentation charts
                if raw.get("segments"):
                    df_seg = pd.DataFrame(raw["segments"])
                    if not df_seg.empty:
                        df_seg = df_seg.sort_values("transaction_count", ascending=False)
                        st.subheader("📊 Segment Distribution")
                        c1, c2 = st.columns([2, 2])
                        with c1:
                            st.write("Transaction count by segment")
                            st.bar_chart(df_seg.set_index("segment")["transaction_count"]) 
                        with c2:
                            st.write("Average transaction value by segment")
                            st.bar_chart(df_seg.set_index("segment")["average_transaction_value"]) 

                # Comparative charts
                elif raw.get("data"):
                    df_comp = pd.DataFrame(raw["data"])
                    if not df_comp.empty:
                        st.subheader(f"📊 Comparison by {raw.get('comparison_key','dimension')}")
                        st.bar_chart(df_comp.set_index("category")["transaction_count"]) 

                # Risk charts
                if raw.get("fraud_by_category"):
                    df_fraud = pd.DataFrame(raw["fraud_by_category"])
                    if not df_fraud.empty:
                        st.subheader("⚠️ Fraud by Category")
                        st.bar_chart(df_fraud.set_index("category")["fraud_count"]) 

                # Descriptive sample transactions chart
                if raw.get("statistics") and raw["statistics"].get("sample_transactions"):
                    sample = raw["statistics"]["sample_transactions"]
                    if sample:
                        df_sample = pd.DataFrame(sample, columns=["transaction_id", "amount", "category", "timestamp"]) 
                        st.subheader("🔎 Sample Transaction Amounts")
                        st.bar_chart(df_sample.set_index("transaction_id")["amount"]) 

                # Detailed data
                with st.expander("📊 Detailed Analysis Data"):
                    st.json(raw)
                
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

# Query History
if st.session_state.query_history:
    st.divider()
    st.subheader("📜 Query History")
    
    history_df = pd.DataFrame(st.session_state.query_history)
    history_df["timestamp"] = history_df["timestamp"].dt.strftime("%H:%M:%S")
    
    st.dataframe(
        history_df[["timestamp", "intent", "query"]],
        use_container_width=True,
        hide_index=True
    )

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 Built with FastAPI + Streamlit")
with col2:
    st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")
with col3:
    st.caption("💻 InsightX v1.0")

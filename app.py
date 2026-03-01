import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="FinTalk - Payment Analytics AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with fixed header and modern styling
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Hide the top streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container styling */
    .main {
        padding-top: 0;
    }
    
    /* Fixed header - modern gradient */
    .header-container {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 15px 25px;
        z-index: 9999 !important;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        box-sizing: border-box;
        height: 70px;
        backdrop-filter: blur(10px);
    }
    
    /* Push main content down */
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main {
        margin-top: 70px !important;
        padding-top: 20px !important;
        padding-bottom: 70px !important;
    }

    /* Ensure chat input is fully visible */
    [data-testid="stChatInput"] {
        margin-bottom: 10px !important;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
        flex: 1;
    }
    
    .header-title {
        color: white;
        font-size: 1.6em;
        font-weight: 800;
        margin: 0;
        white-space: nowrap;
        font-family: 'Poppins', sans-serif;
        letter-spacing: -1px;
    }
    
    .header-tagline {
        color: rgba(255,255,255,0.9);
        font-size: 0.9em;
        margin: 0;
        white-space: nowrap;
        font-weight: 500;
    }
    
    .header-status {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    
    .status-badge {
        color: white;
        font-size: 0.85em;
        padding: 6px 14px;
        border-radius: 20px;
        background: rgba(255,255,255,0.25);
        white-space: nowrap;
        font-weight: 600;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
    }
    
    .status-active {
        background: rgba(76, 175, 80, 0.8) !important;
        border-color: rgba(76, 175, 80, 0.5) !important;
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.4);
    }
    
    .status-connected {
        background: rgba(76, 175, 80, 0.8) !important;
        border-color: rgba(76, 175, 80, 0.5) !important;
    }
    
    .status-error {
        background: rgba(244, 67, 54, 0.8) !important;
        border-color: rgba(244, 67, 54, 0.5) !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(240, 147, 251, 0.15) 100%);
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 0.9em;
        color: rgba(0, 0, 0, 0.6);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: 800;
        color: #667eea;
        font-family: 'Poppins', sans-serif;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        border-left: 4px solid rgba(255,255,255,0.5);
    }
    
    .insight-box h3 {
        margin-top: 0;
        color: white;
        font-size: 1.2em;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
        font-weight: 600;
    }
    
    .query-input {
        border: 2px solid #667eea;
        padding: 12px;
        border-radius: 8px;
        font-size: 1em;
    }
    
    /* Charts styling */
    .chart-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(240, 147, 251, 0.05) 100%);
        border: 1px solid rgba(102, 126, 234, 0.15);
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.05) 0%, rgba(240, 147, 251, 0.05) 100%);
    }
    
    /* Button styling */
    button[kind="primary"] {
        font-weight: 600 !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Response styling */
    .response-message {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(240, 147, 251, 0.08) 100%);
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 0.95em;
        line-height: 1.6;
    }
    
    .error-message {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #f44336;
    }
    
    .success-message {
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

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
if "last_chart" not in st.session_state:
    st.session_state.last_chart = None

# Sidebar
with st.sidebar:
    st.title("💬 FinTalk Chat")
    
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
    
    st.subheader("💡 Ask Better Questions")
    st.markdown("""
    - **Start with outcomes:** total value, growth, risk, or efficiency
    - **Add a lens:** bank, category, state, age group, device, network, or time
    - **Follow-up works:** "How about X?" or "By state?"

    **Common scopes:**
    banks, categories, age groups, states, devices, networks
    
    **Example Flow:**
    1. "Total transaction value by state"
    2. "How about only Food?"
    3. "Show top 3 states"
    """)
    
    st.divider()
    
    st.subheader("📚 Example Questions")
    example_queries = [
        "Top banks by total transaction value",
        "Total transaction value by state",
        "Average transaction amount by state",
        "Compare iOS vs Android by total amount",
        "Fraud rate by state",
        "Where is failure rate highest by bank?",
        "Top 3 fraud categories in Delhi",
        "Transactions from Karnataka by receiver bank",
        "Average Food amount per state",
        "Peak hours for Food transactions",
        "Day of week pattern for Entertainment",
        "Transaction count by device type",
        "Compare UPI networks by average amount",
        "Age group trends in Maharashtra",
        "Sender vs receiver age group for failed transactions",
        "Weekend vs weekday transaction volume"
    ]
    
    for i, query in enumerate(example_queries, 1):
        if st.button(f"📌 {query}", key=f"example_{i}", use_container_width=True):
            st.session_state.pending_query = query
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
    # Chart options
    top_n = st.slider("Top N for charts", min_value=3, max_value=20, value=10)

# Fixed Header - Render immediately after CSS
# Check API status
api_status = "not connected"
try:
    response = requests.get(f"{st.session_state.api_url}/api/health", timeout=1)
    api_status = "connected" if response.status_code == 200 else "error"
except:
    api_status = "error"

# Build header status
session_status = "🔑 Active" if st.session_state.session_id else "📋 New"
api_indicator = "✅ Connected" if api_status == "connected" else "❌ Error"

# Render fixed header using HTML - appears at top of main content
st.markdown(f"""
<div class="header-container">
    <div class="header-left">
        <div>
            <p class="header-title">💳 FinTalk</p>
            <p class="header-tagline">Payment Analytics AI</p>
        </div>
    </div>
    <div class="header-status">
        <span class="status-badge status-active">{session_status}</span>
        <span class="status-badge status-connected">{api_indicator}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Function to render chart from raw_data with Plotly
def render_chart(chart_data, top_n=10):
    """Render interactive charts using Plotly"""
    if not chart_data:
        return
    
    try:
        color_palette = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#fa709a']
        
        def get_color_scale():
            """Return a professional color scale"""
            return ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#fa7ce1', '#00f2fe', '#4facfe', '#43e97b']
        
        if 'data' in chart_data and isinstance(chart_data['data'], list):
            rows = chart_data['data']
            if not rows:
                return
            df = pd.DataFrame(rows)
            metric = chart_data.get('metric') or ''
            
            # Check for total/amount FIRST
            if metric in ('amount','total_amount','total') or (metric == '' and 'total_amount' in df.columns):
                df = df.sort_values('total_amount', ascending=False).head(top_n)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['category'],
                        y=df['total_amount'],
                        marker=dict(
                            color=df['total_amount'],
                            colorscale=get_color_scale(),
                            showscale=True,
                            colorbar=dict(title="Amount")
                        ),
                        hovertemplate='<b>%{x}</b><br>Total: ₹%{y:,.0f}<extra></extra>',
                        text=df['total_amount'].apply(lambda x: f'₹{x/100000:.1f}L'),
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Transaction Amount by Category</b>',
                    xaxis_title='Category',
                    yaxis_title='Total Amount (₹)',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    margin=dict(t=60, b=50, l=60, r=20),
                    showlegend=False
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif metric == 'count' or ('transaction_count' in df.columns and metric == 'count'):
                df = df.sort_values('transaction_count', ascending=False).head(top_n)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['category'],
                        y=df['transaction_count'],
                        marker=dict(
                            color=df['transaction_count'],
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="Count")
                        ),
                        hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>',
                        text=df['transaction_count'],
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Transaction Count by Category</b>',
                    xaxis_title='Category',
                    yaxis_title='Transaction Count',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    showlegend=False
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif (metric and metric.startswith('avg')) or ('average_amount' in df.columns and metric == ''):
                df = df.sort_values('average_amount', ascending=False).head(top_n)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['category'],
                        y=df['average_amount'],
                        marker=dict(
                            color=color_palette,
                            line=dict(color='rgba(0,0,0,0.1)', width=1)
                        ),
                        hovertemplate='<b>%{x}</b><br>Avg: ₹%{y:,.0f}<extra></extra>',
                        text=df['average_amount'].apply(lambda x: f'₹{x:,.0f}'),
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Average Transaction Amount by Category</b>',
                    xaxis_title='Category',
                    yaxis_title='Average Amount (₹)',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    showlegend=False
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif 'transaction_count' in df.columns:
                df = df.sort_values('transaction_count', ascending=False).head(top_n)
                
                # Use pie chart for counts if only few categories
                if len(df) <= 8:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=df['category'],
                            values=df['transaction_count'],
                            marker=dict(colors=color_palette),
                            hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>',
                            textposition='inside',
                            textinfo='label+percent'
                        )
                    ])
                    fig.update_layout(
                        title='<b>Transaction Distribution by Category</b>',
                        template='plotly_white',
                        height=450,
                        font=dict(family='Inter, sans-serif', size=12),
                    )
                else:
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df['category'],
                            y=df['transaction_count'],
                            marker=dict(color=df['transaction_count'], colorscale='Turbo'),
                            text=df['transaction_count'],
                            textposition='outside',
                            hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>',
                        )
                    ])
                    fig.update_layout(
                        title='<b>Transaction Count by Category</b>',
                        xaxis_title='Category',
                        yaxis_title='Transaction Count',
                        template='plotly_white',
                        height=450,
                        hovermode='x unified',
                        font=dict(family='Inter, sans-serif', size=12),
                    )
                
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
        elif 'segments' in chart_data and isinstance(chart_data['segments'], list):
            rows = chart_data['segments']
            if not rows:
                return
            df = pd.DataFrame(rows)
            
            if 'transaction_count' in df.columns:
                df = df.sort_values('transaction_count', ascending=False).head(top_n)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['segment'],
                        y=df['transaction_count'],
                        marker=dict(
                            color=color_palette[:len(df)],
                            line=dict(color='rgba(0,0,0,0.1)', width=1)
                        ),
                        hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>',
                        text=df['transaction_count'],
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Transaction Count by Segment</b>',
                    xaxis_title='Segment',
                    yaxis_title='Transaction Count',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    showlegend=False
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif 'average_transaction_value' in df.columns:
                df = df.sort_values('average_transaction_value', ascending=False).head(top_n)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['segment'],
                        y=df['average_transaction_value'],
                        marker=dict(
                            color=df['average_transaction_value'],
                            colorscale='Electric',
                            showscale=True,
                            colorbar=dict(title="Avg Value")
                        ),
                        hovertemplate='<b>%{x}</b><br>Avg: ₹%{y:,.0f}<extra></extra>',
                        text=df['average_transaction_value'].apply(lambda x: f'₹{x:,.0f}'),
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Average Transaction Value by Segment</b>',
                    xaxis_title='Segment',
                    yaxis_title='Average Transaction Value (₹)',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    showlegend=False
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
        elif 'groups' in chart_data and isinstance(chart_data['groups'], list):
            rows = chart_data['groups']
            if not rows:
                return
            df = pd.DataFrame(rows)
            
            if 'fraud_rate' in df.columns:
                df = df.sort_values('fraud_rate', ascending=False).head(top_n)
                
                # Color code by risk level
                colors = ['#f5576c' if x > 5 else '#ffa502' if x > 2 else '#43e97b' for x in df['fraud_rate']]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['group'],
                        y=df['fraud_rate'],
                        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.1)', width=1)),
                        hovertemplate='<b>%{x}</b><br>Fraud Rate: %{y:.2f}%<extra></extra>',
                        text=df['fraud_rate'].apply(lambda x: f'{x:.2f}%'),
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Fraud Rate by Group</b>',
                    xaxis_title='Group',
                    yaxis_title='Fraud Rate (%)',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    showlegend=False,
                    yaxis=dict(
                        range=[0, df['fraud_rate'].max() * 1.2]
                    )
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif 'failure_rate' in df.columns:
                df = df.sort_values('failure_rate', ascending=False).head(top_n)
                
                colors = ['#f5576c' if x > 10 else '#ffa502' if x > 5 else '#43e97b' for x in df['failure_rate']]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['group'],
                        y=df['failure_rate'],
                        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.1)', width=1)),
                        hovertemplate='<b>%{x}</b><br>Failure Rate: %{y:.2f}%<extra></extra>',
                        text=df['failure_rate'].apply(lambda x: f'{x:.2f}%'),
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Failure Rate by Group</b>',
                    xaxis_title='Group',
                    yaxis_title='Failure Rate (%)',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    showlegend=False,
                    yaxis=dict(
                        range=[0, df['failure_rate'].max() * 1.2]
                    )
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif 'total' in df.columns:
                df = df.sort_values('total', ascending=False).head(top_n)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['group'],
                        y=df['total'],
                        marker=dict(
                            color=color_palette[:len(df)],
                            line=dict(color='rgba(0,0,0,0.1)', width=1)
                        ),
                        hovertemplate='<b>%{x}</b><br>Total: %{y:,}<extra></extra>',
                        text=df['total'],
                        textposition='outside',
                    )
                ])
                fig.update_layout(
                    title='<b>Total by Group</b>',
                    xaxis_title='Group',
                    yaxis_title='Total',
                    template='plotly_white',
                    height=450,
                    hovermode='x unified',
                    font=dict(family='Inter, sans-serif', size=12),
                    showlegend=False
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
        elif 'temporal' in chart_data and isinstance(chart_data['temporal'], dict):
            temporal = chart_data['temporal']
            
            hourly = temporal.get('hourly') or []
            if hourly:
                df = pd.DataFrame(hourly)
                if 'hour' in df.columns and 'transaction_count' in df.columns:
                    df = df.sort_values('hour')
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df['hour'],
                        y=df['transaction_count'],
                        mode='lines+markers',
                        name='Transaction Count',
                        line=dict(color='#667eea', width=3),
                        marker=dict(size=8, color='#667eea', symbol='circle'),
                        fill='tozeroy',
                        fillcolor='rgba(102, 126, 234, 0.2)',
                        hovertemplate='<b>Hour %{x}</b><br>Count: %{y:,}<extra></extra>'
                    ))
                    fig.update_layout(
                        title='<b>Hourly Transaction Distribution</b>',
                        xaxis_title='Hour of Day',
                        yaxis_title='Transaction Count',
                        template='plotly_white',
                        height=450,
                        hovermode='x unified',
                        font=dict(family='Inter, sans-serif', size=12),
                        showlegend=False,
                        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
                    )
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)

            daily = temporal.get('day_of_week') or []
            if daily:
                df = pd.DataFrame(daily)
                if 'day_of_week' in df.columns and 'transaction_count' in df.columns:
                    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    df['day_name'] = df['day_of_week'].apply(lambda x: day_names[int(x)] if int(x) < 7 else str(x))
                    df = df.sort_values('day_of_week')
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df['day_name'],
                            y=df['transaction_count'],
                            marker=dict(
                                color=df['transaction_count'],
                                colorscale='RdYlGn_r',
                                showscale=False
                            ),
                            hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>',
                            text=df['transaction_count'],
                            textposition='outside',
                        )
                    ])
                    fig.update_layout(
                        title='<b>Day-of-Week Transaction Distribution</b>',
                        xaxis_title='Day of Week',
                        yaxis_title='Transaction Count',
                        template='plotly_white',
                        height=450,
                        hovermode='x unified',
                        font=dict(family='Inter, sans-serif', size=12),
                        showlegend=False,
                    )
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
                    
    except Exception as e:
        st.error(f"Chart rendering error: {str(e)}")


# Display conversation history (chat-like format)
if st.session_state.conversation_history:
    st.subheader("💬 Conversation")
    
    for msg in st.session_state.conversation_history:
        if msg["type"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
                if msg.get("intent"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"🎯 Intent: **{msg['intent'].replace('_', ' ').title()}**")
                    with col2:
                        confidence_pct = f"{msg['confidence']:.0%}"
                        confidence_color = "🟢" if msg['confidence'] > 0.8 else "🟡" if msg['confidence'] > 0.6 else "🔴"
                        st.caption(f"{confidence_color} Confidence: **{confidence_pct}**")
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                
                # Display insights with better styling
                if msg.get("insights"):
                    insights_list = msg.get("insights", [])[:3]
                    if insights_list:
                        st.markdown("**✨ Key Insights:**")
                        for insight in insights_list:
                            st.markdown(f"• {insight}")
                
                # Render chart for this response
                if msg.get("raw_data"):
                    render_chart(msg["raw_data"], st.session_state.get('top_n', 10))

st.divider()

# Main query section is now at bottom using chat_input for ChatGPT-style layout

# Process query when user submits via chat_input or clicks an example
user_query = st.chat_input("Ask a question about the transaction data...")

# If example question was clicked, use pending_query instead
if st.session_state.pending_query:
    user_query = st.session_state.pending_query
    st.session_state.pending_query = None  # Clear pending query

if user_query:
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
                # No longer needed - chart is rendered in conversation loop
                st.session_state.last_chart = None

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
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.markdown("<div style='text-align: center;'><small>⚡ FastAPI + Streamlit</small></div>", unsafe_allow_html=True)
with footer_col2:
    st.markdown(f"<div style='text-align: center;'><small>📅 {datetime.now().strftime('%b %d, %Y')}</small></div>", unsafe_allow_html=True)
with footer_col3:
    session_text = "✅ Session Active" if st.session_state.session_id else "⏸️ Start a conversation"
    st.markdown(f"<div style='text-align: center;'><small>{session_text}</small></div>", unsafe_allow_html=True)

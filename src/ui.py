import streamlit as st
from streamlit_float import float_init, float_css_helper
import pandas as pd
from src.ai_engine import MockAIEngine
from src.armoriq_guard import ArmorIQGuard

ai_engine = MockAIEngine()
armor_iq = ArmorIQGuard()

def init_accessibility_state():
    """Initialize session state for accessibility options."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "font_size" not in st.session_state:
        st.session_state.font_size = 16  # Default font size in px
    if "language" not in st.session_state:
        st.session_state.language = "EN"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def apply_accessibility_styles():
    """Apply CSS based on current accessibility settings."""
    dark_mode = st.session_state.get("dark_mode", False)
    font_size = st.session_state.get("font_size", 16)
    
    # Theme colors
    if dark_mode:
        bg_color = "#0e1117"     # Streamlit's default dark bg (very dark blue-ish gray)
        text_color = "#ffffff"   # Pure white for max contrast
        card_bg = "#262730"      # Slightly lighter for cards/sidebar
        accent = "#4fc3f7"
    else:
        bg_color = "#ffffff"
        text_color = "#31333F"   # Streamlit default light text
        card_bg = "#f0f2f6"      # Light gray for sidebar
        accent = "#1976d2"
    
    css = f"""
    <style>
    /* Font Size Adjustment */
    .stApp, .stMarkdown, p, span, div {{
        font-size: {font_size}px !important;
    }}
    h1 {{ font-size: {font_size + 16}px !important; }}
    h2 {{ font-size: {font_size + 12}px !important; }}
    h3 {{ font-size: {font_size + 8}px !important; }}
    h4 {{ font-size: {font_size + 4}px !important; }}
    
    /* Dark Mode Overrides */
    {"" if not dark_mode else f'''
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {card_bg} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}
    .stMetric, [data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}
    .stMarkdown, .stMarkdown p {{
        color: {text_color} !important;
    }}
    '''}
    
    /* Hide sidebar dividers */
    [data-testid="stSidebar"] hr {{
        display: none !important;
    }}
    
    /* Larger sidebar navigation titles */
    [data-testid="stSidebarNav"] span {{
        font-size: 18px !important;
        font-weight: 600 !important;
    }}
    /* Compact sidebar - no scrollbar */
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        overflow: hidden !important; /* Force hide scrollbar */
    }}
    [data-testid="stSidebar"] [data-testid="stExpander"] {{
        margin-bottom: 0.25rem !important;
    }}
    
    /* Fix weird tab switching animation */
    [data-testid="stSidebarNav"] a {{
        padding: 5px 8px !important;
        transition: none !important; /* Disable transition to stop size jitter */
    }}
    [data-testid="stSidebarNav"] span {{
        font-size: 13px !important;
        font-weight: 600 !important;
        transition: none !important;
        transform: none !important;
    }}
    
    /* Large logo spanning most of sidebar width */
    [data-testid="stSidebar"] [data-testid="stLogo"] img {{
        width: 90% !important;
        max-width: 100% !important;
        height: auto !important;
        min-height: 50px !important;
        max-height: 60px !important;
        object-fit: contain !important;
        margin: 0 auto !important;
        display: block !important;
    }}
    
    /* Larger page titles */
    h1 {{
        font-size: {font_size + 20}px !important;
        font-weight: 700 !important;
    }}
    h2 {{
        font-size: {font_size + 14}px !important;
        font-weight: 600 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_accessibility_controls():
    """Render accessibility controls in the sidebar."""
    with st.sidebar:
        with st.expander("⚙️ Accessibility", expanded=False):
            # Dark Mode Toggle
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light", 
                             key="theme_toggle", width="stretch"):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()
            
            # Font Size Controls
            with col2:
                font_col1, font_col2 = st.columns(2)
                with font_col1:
                    if st.button("A-", key="font_decrease", width="stretch"):
                        if st.session_state.font_size > 12:
                            st.session_state.font_size -= 2
                            st.rerun()
                with font_col2:
                    if st.button("A+", key="font_increase", width="stretch"):
                        if st.session_state.font_size < 24:
                            st.session_state.font_size += 2
                            st.rerun()
            
            # Language Selector
            st.selectbox(
                "Language",
                options=["EN"],  # Placeholder for more languages
                key="language",
                label_visibility="collapsed"
            )

def render_sidebar():
    """
    Renders the consistent sidebar content for all pages.
    """
    # Initialize accessibility state
    init_accessibility_state()
    
    # Logo for top-level branding
    # Logo for top-level branding
    st.logo("assets/CiviNigrani.png", size="large", icon_image="assets/CiviNigrani.png")
    
    # Apply accessibility styles
    apply_accessibility_styles()

    with st.sidebar:
        # Context Info (minimal, compact)
        st.markdown("**Policy:** PDS &nbsp;•&nbsp; **State:** Uttar Pradesh", unsafe_allow_html=True)
    
    # Accessibility Controls
    render_accessibility_controls()

    with st.sidebar:
        st.caption("Public data only • No personal data")
    
    # Floating AI Bubble (appears on ALL pages via sidebar call)
    _render_floating_ai_bubble()

def _render_floating_ai_bubble():
    """
    Renders AI Assistant as a button in sidebar that opens a dialog popup.
    Dialog has close button (X) at top right. Stays open after sending messages.
    """
    # Initialize dialog state
    if "ai_dialog_open" not in st.session_state:
        st.session_state.ai_dialog_open = False

    # Initialize Test Mode state
    if "test_mode" not in st.session_state:
        st.session_state.test_mode = False
    
    # Initialize agent if not already done
    if "query_agent" not in st.session_state:
        try:
            from src.agent import QueryAgent, DataTools
            from src.loaders import load_pds_data, load_grievance_data
            from src.prgi import compute_prgi
            
            # Load data for agent (Test Mode aware)
            is_test = st.session_state.test_mode
            pds_data = load_pds_data(test_mode=is_test)
            
            # Compute PRGI
            prgi_data = compute_prgi(pds_data) # Handles test data structure via state_name fix
            
            # Grievance data (only real, or empty for test)
            grievance_data = load_grievance_data() if not is_test else pd.DataFrame()
            
            # Initialize tools and agent
            tools = DataTools(prgi_data, grievance_data)
            st.session_state.query_agent = QueryAgent(tools, use_gemini=True)
            st.session_state.agent_ready = True
            
            if is_test:
                print("🧪 Agent initialized in TEST MODE with dummy data.")
                
        except Exception as e:
            st.session_state.agent_ready = False
            st.session_state.agent_error = str(e)
    
    # Define the dialog content (not using decorator to avoid duplicate ID)
    def show_ai_dialog():
        @st.dialog("🤖 AI Assistant", width="large")
        def _dialog_content():
            st.caption("🛡️ Verified by ArmorIQ SDK • Natural Language Data Explorer")
            
            # Test Mode Toggle
            def on_test_mode_change():
                # Clear agent to force reload on next run
                if "query_agent" in st.session_state:
                    del st.session_state.query_agent
                st.session_state.agent_ready = False  # Reset readiness flag
                st.session_state.chat_history = []  # Clear history context
                
            st.toggle("🧪 Test Database (Safe Mode)", key="test_mode", on_change=on_test_mode_change)
            
            if st.session_state.test_mode:
                st.info("⚠️ Using **Test Database** (5 dummy districts). Real data is protected. Admin writes allowed.")

            if not st.session_state.get("agent_ready", False):
                # If agent not ready, try to re-initialize immediately (for dialog context)
                # This handles cases where sidebar re-run hasn't happened yet or failed
                 try:
                    from src.agent import QueryAgent, DataTools
                    from src.loaders import load_pds_data, load_grievance_data
                    from src.prgi import compute_prgi
                    
                    is_test = st.session_state.test_mode
                    pds_data = load_pds_data(test_mode=is_test)
                    prgi_data = compute_prgi(pds_data) # Handles test data structure via state_name fix
                    grievance_data = load_grievance_data() if not is_test else pd.DataFrame()
                    
                    tools = DataTools(prgi_data, grievance_data)
                    st.session_state.query_agent = QueryAgent(tools, use_gemini=True)
                    st.session_state.agent_ready = True
                 except Exception as e:
                    st.error(f"⚠️ Agent initialization failed: {str(e)}")
                    return
            
            # Double check agent existence to avoid AttributeError
            if "query_agent" not in st.session_state:
                st.error("⚠️ System Error: Agent state missing. Please refresh the page.")
                return
            
            # Role Selection (Hackathon Demo)
            st.divider()
            st.markdown("### 👤 User Identity")
            if "user_role" not in st.session_state:
                st.session_state.user_role = "Analyst"
            
            role = st.selectbox(
                "Select Role", 
                ["Analyst", "Admin"], 
                index=0 if st.session_state.user_role == "Analyst" else 1,
                key="role_selector",
                on_change=lambda: st.session_state.update({"user_role": st.session_state.role_selector})
            )
            
            role_desc = "Read-only access" if role == "Analyst" else "Full read/write access"
            st.caption(f"Permissions: {role_desc}")
            st.divider()

            # Example queries
            with st.expander("💡 Example Queries", expanded=False):
                st.markdown("""
                - "**Analyst**: Show top 5 districts by PRGI"
                - "**Analyst**: Summarize performance"
                - "**Admin**: Update Lucknow PRGI to 0.9" (Try as Analyst to see blocking!)
                """)
            
            # Chat history
            chat_container = st.container(height=350)
            with chat_container:
                history = st.session_state.get("chat_history", [])
                if history:
                    for msg in history[-8:]:
                        if msg["role"] == "user":
                            st.markdown(f"**You ({st.session_state.user_role}):** {msg['content']}")
                        else:
                            badge = " ✓ Verified" if msg.get("verified") else ""
                            st.markdown(f"**AI:** {msg['content']} `{badge}`")
                else:
                    st.info(f"👋 Hello {role}! Ask about PDS delivery gaps or try updating data.")
            
            # Input form
            with st.form("dialog_ai_form", clear_on_submit=True):
                q = st.text_input("Ask", key="dialog_ai_q", label_visibility="collapsed", placeholder="Type your question...")
                if st.form_submit_button("Send", type="primary", use_container_width=True):
                    if q:
                        if "chat_history" not in st.session_state:
                            st.session_state.chat_history = []
                        
                        st.session_state.chat_history.append({"role": "user", "content": q})
                        
                        # Query agent with ArmorIQ validation
                        agent = st.session_state.query_agent
                        # Pass user role to query()
                        response = agent.query(q, user_role=st.session_state.user_role)
                        
                        if response.get("success", False):
                            st.session_state.chat_history.append({
                                "role": "ai", 
                                "content": response.get("answer", "No answer available."),
                                "verified": response.get("armoriq_verified", False)
                            })
                        else:
                            st.session_state.chat_history.append({
                                "role": "ai", 
                                "content": f"⚠️ {response.get('error', 'Query failed')}",
                                "verified": True
                            })
                        
                        st.session_state.ai_dialog_open = True
                        st.rerun()
        
        _dialog_content()
    
    # Render button in sidebar
    with st.sidebar:
        st.divider()
        if st.button("🤖 **AI Assistant**", use_container_width=True, type="secondary"):
            st.session_state.ai_dialog_open = True
    
    # Show dialog if flag is set, then reset flag
    if st.session_state.ai_dialog_open:
        st.session_state.ai_dialog_open = False  # Reset immediately to prevent auto-open on page switch
        show_ai_dialog()


# Deprecated function for backward compatibility
def render_ai_bubble():
    """Deprecated: Use render_sidebar() which auto-includes the AI tab."""
    pass

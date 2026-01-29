import streamlit as st
from streamlit_float import float_init, float_css_helper
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
    
    # Define the dialog content (not using decorator to avoid duplicate ID)
    def show_ai_dialog():
        # Use fragment to contain the dialog
        @st.dialog("🤖 AI Assistant", width="small")
        def _dialog_content():
            # Simple header
            st.caption("🛡️ Verified by ArmorIQ SDK")
            
            # Chat history display in a container
            chat_container = st.container(height=300)
            with chat_container:
                history = st.session_state.get("chat_history", [])
                if history:
                    for msg in history[-8:]:
                        if msg["role"] == "user":
                            st.markdown(f"**You:** {msg['content']}")
                        else:
                            badge = " ✓" if msg.get("verified") else ""
                            st.markdown(f"**AI:** {msg['content']}{badge}")
                else:
                    st.write("Ask about PDS gaps, district trends, or best performers!")
            
            # Input form
            with st.form("dialog_ai_form", clear_on_submit=True):
                q = st.text_input(
                    "Ask", 
                    key="dialog_ai_q", 
                    label_visibility="collapsed", 
                    placeholder="Type your question..."
                )
                if st.form_submit_button("Send", type="primary", width="stretch"):
                    if q:
                        if "chat_history" not in st.session_state:
                            st.session_state.chat_history = []
                        st.session_state.chat_history.append({"role": "user", "content": q})
                        resp = ai_engine.query(q)
                        scan = armor_iq.scan(resp)
                        st.session_state.chat_history.append({
                            "role": "ai", 
                            "content": resp if scan["safe"] else f"⚠️ {scan['flagged_for']}",
                            "verified": scan["safe"]
                        })
                        st.session_state.ai_dialog_open = True
                        st.rerun()
        
        _dialog_content()
    
    # Render button in sidebar to open dialog
    with st.sidebar:
        st.divider()
        if st.button("🤖 **AI Assistant**", width="stretch", type="secondary"):
            st.session_state.ai_dialog_open = True
    
    # Show dialog if flag is set, then reset flag
    if st.session_state.ai_dialog_open:
        st.session_state.ai_dialog_open = False  # Reset immediately to prevent auto-open on page switch
        show_ai_dialog()


# Deprecated function for backward compatibility
def render_ai_bubble():
    """Deprecated: Use render_sidebar() which auto-includes the AI tab."""
    pass

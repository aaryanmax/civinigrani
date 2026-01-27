import streamlit as st

def init_accessibility_state():
    """Initialize session state for accessibility options."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "font_size" not in st.session_state:
        st.session_state.font_size = 16  # Default font size in px
    if "language" not in st.session_state:
        st.session_state.language = "EN"

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
                             key="theme_toggle", use_container_width=True):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()
            
            # Font Size Controls
            with col2:
                font_col1, font_col2 = st.columns(2)
                with font_col1:
                    if st.button("A-", key="font_decrease", use_container_width=True):
                        if st.session_state.font_size > 12:
                            st.session_state.font_size -= 2
                            st.rerun()
                with font_col2:
                    if st.button("A+", key="font_increase", use_container_width=True):
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
    st.logo("assets/logo.png", size="large", icon_image="assets/logo.png")
    
    # Apply accessibility styles
    apply_accessibility_styles()

    with st.sidebar:
        # Context Info (minimal, compact)
        st.markdown("**Policy:** PDS &nbsp;•&nbsp; **State:** Uttar Pradesh", unsafe_allow_html=True)
    
    # Accessibility Controls
    render_accessibility_controls()
    
    with st.sidebar:
        st.caption("Public data only • No personal data")

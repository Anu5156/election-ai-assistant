"""
Styles Module - CivicGuide AI
Contains the global CSS and design tokens for the premium dark civic aesthetic.
"""

def get_global_styles() -> str:
    """
    Returns the comprehensive CSS string for the application.
    """
    # Using a raw string with zero indentation to ensure Streamlit doesn't interpret it as a code block.
    return """<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700&family=DM+Sans:wght@400;500&family=DM+Mono&display=swap" rel="stylesheet"><style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #08101e !important;
    color: #e2eaf5 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] {
    background-color: #0d1828 !important;
    border-right: 1px solid #1e3050 !important;
}
[data-high-contrast="true"] body, [data-high-contrast="true"] [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
.cg-card {
    background: rgba(13, 24, 40, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(30, 48, 80, 0.5);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.metric-card {
    background: rgba(13, 24, 40, 0.7);
    border: 1px solid rgba(30, 48, 80, 0.5);
    border-radius: 14px;
    padding: 20px;
    position: relative;
}
.cg-topbar {
    display:flex; align-items:center; justify-content:space-between;
    padding-bottom:20px; border-bottom:1px solid #1e3050; margin-bottom:20px;
}
.cg-chip {
    padding:4px 12px; border-radius:20px; background:#111f33; 
    border:1px solid #1e3050; font-size:11px;
}
.journey-step { display: flex; gap: 15px; margin-bottom: 20px; }
.jnode { width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.jnode-done { background: #22c55e; color: white; }
.jnode-active { background: #3b82f6; color: white; border: 2px solid #0d1828; }
.jnode-pending { background: #1e3050; color: #4d6585; }
</style>"""

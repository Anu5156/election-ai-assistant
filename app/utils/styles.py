"""
Styles Module - CivicGuide AI
FAANG-Standard Design System v3.0
Contains high-fidelity CSS for a premium, hyper-modern civic tech experience.
"""

def get_global_styles() -> str:
    """
    Returns the comprehensive CSS string for the application.
    """
    return """<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet"><style>
/* ── FAANG Design Tokens ── */
:root {
    --bg-main: #050a14;
    --bg-card: rgba(13, 24, 40, 0.7);
    --accent-primary: #6366f1; /* Indigo */
    --accent-secondary: #10b981; /* Emerald */
    --accent-error: #f43f5e; /* Rose */
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border: rgba(255, 255, 255, 0.1);
    --glass-blur: blur(16px);
}

/* ── Global Reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Sidebar FAANG Upgrade ── */
[data-testid="stSidebar"] {
    background-color: #08101e !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarNav"] {
    background-color: transparent !important;
}

/* ── Premium Glassmorphism ── */
.cg-card {
    background: var(--bg-card);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
}
.cg-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6);
}

.cg-card.blue { border-left: 5px solid var(--accent-primary); }
.cg-card.green { border-left: 5px solid var(--accent-secondary); }
.cg-card.red { border-left: 5px solid var(--accent-error); }

/* ── Metric Grid FAANG ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
}
.metric-card {
    background: var(--bg-card);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease;
}
.metric-card:hover { transform: scale(1.02); }

.top-bar {
    position: absolute; top: 0; left: 0; width: 100%; height: 4px;
}

.m-label { font-size: 13px; color: var(--text-muted); font-weight: 400; text-transform: uppercase; letter-spacing: 1px; }
.m-value { font-size: 32px; font-weight: 700; margin: 8px 0; color: #fff; }
.m-sub { font-size: 12px; color: var(--text-muted); }

/* ── Chips & Badges ── */
.cg-chip {
    padding: 6px 14px; border-radius: 100px; background: rgba(255,255,255,0.05);
    border: 1px solid var(--border); font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
}
.badge {
    position: absolute; top: 16px; right: 16px; font-size: 10px; font-weight: 700;
    padding: 4px 10px; border-radius: 6px; text-transform: uppercase;
}
.badge-green { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.badge-blue { background: rgba(99, 102, 241, 0.2); color: #6366f1; }
.badge-amber { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.badge-red { background: rgba(244, 63, 94, 0.2); color: #f43f5e; }

/* ── Interactive Elements ── */
.stButton>button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}
.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
}

/* ── Typography Upgrade ── */
h1, h2, h3 { font-weight: 700 !important; letter-spacing: -0.5px !important; color: #fff !important; }
.cg-page-title { font-size: 28px; font-weight: 700; background: linear-gradient(90deg, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* ── Journey Timeline Upgrade ── */
.journey-step { position: relative; padding-left: 50px; margin-bottom: 30px; }
.journey-step::before {
    content: ''; position: absolute; left: 19px; top: 35px; width: 2px; height: calc(100% - 15px);
    background: var(--border);
}
.journey-step:last-child::before { display: none; }
.jnode {
    position: absolute; left: 0; top: 0; width: 40px; height: 40px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center; font-size: 18px;
    background: #1e293b; border: 1px solid var(--border); transition: all 0.3s ease;
}
.jnode-done { background: var(--accent-secondary) !important; color: #050a14 !important; box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
.jnode-active { background: var(--accent-primary) !important; color: #fff !important; box-shadow: 0 0 15px rgba(99, 102, 241, 0.3); }
</style>"""

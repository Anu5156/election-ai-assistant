"""
UI Components Module - CivicGuide AI
Contains reusable Streamlit-based UI elements and CSS-in-JS components.
"""

import streamlit as st
from typing import List, Tuple, Optional
from datetime import datetime

def metric_card(label: str, value: str, sub: str, badge: str, badge_cls: str, bar_color: str) -> str:
    """
    Generates a high-fidelity metric card with ARIA accessibility.
    """
    return f'<div class="metric-card" role="region" aria-label="{label} metric"><div class="top-bar" style="background:linear-gradient(90deg,{bar_color},transparent 70%)"></div><div class="m-label">{label}</div><div class="m-value" aria-live="polite">{value}</div><div class="m-sub">{sub}</div><div class="badge {badge_cls}" role="status">{badge}</div></div>'

def render_metrics_row(t_func, countdown_display: str, election_date: datetime):
    """
    Renders the top row of metrics on the dashboard.
    """
    html = f'<div class="metric-grid">{metric_card(t_func("Registration"), "✓", t_func("Voter ID verified"), t_func("Active"), "badge-green", "#22c55e")}{metric_card(t_func("Stations Nearby"), "3", t_func("Within 2 km radius"), t_func("Mapped"), "badge-blue", "#3b82f6")}{metric_card(t_func("Crowd Level"), t_func("Low"), t_func("Best time: 9–11 AM"), t_func("Updated"), "badge-amber", "#f59e0b")}{metric_card(t_func("Election Countdown"), countdown_display, t_func(election_date.strftime("%B %d, %Y")), t_func("Lok Sabha"), "badge-red", "#ef4444")}</div>'
    st.markdown(html, unsafe_allow_html=True)

def topbar(title: str, chips: Optional[List[Tuple[str, str]]] = None):
    """
    Renders a premium topbar with page title and dynamic status chips.
    """
    chip_html = ""
    for label, extra_cls in (chips or []):
        chip_html += f'<span class="cg-chip {extra_cls}">{label}</span> '
    
    st.markdown(f'<div class="cg-topbar"><div class="cg-page-title">{title}</div><div style="display:flex;gap:8px;align-items:center">{chip_html}</div></div>', unsafe_allow_html=True)

def render_journey_steps(t_func, is_reg: bool):
    """
    Renders the vertical progress timeline for the voter journey.
    """
    steps = [
        ("done" if is_reg else "active", "✓" if is_reg else "→", t_func("Register to Vote"), t_func("Voter ID obtained · EPIC card issued")),
        ("done" if is_reg else "pending", "✓" if is_reg else "○", t_func("Verify your details"), t_func("Name, photo & address confirmed")),
        ("active" if is_reg else "pending", "→" if is_reg else "○", t_func("Find your polling booth"), t_func("Use location finder · Confirm booth no.")),
        ("pending", "○", t_func("Collect voter slip"), t_func("From BLO or voters.eci.gov.in")),
        ("pending", "○", t_func("Cast your vote"), t_func("Carry EPIC + one more ID on poll day")),
    ]
    rows = ""
    for state, icon, title, desc in steps:
        rows += f'<div class="journey-step"><div class="jnode jnode-{state}">{icon}</div><div><div class="j-title">{title}</div><div class="j-desc">{desc}</div></div></div>'
    st.markdown(rows, unsafe_allow_html=True)

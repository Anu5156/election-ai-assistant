"""
UI Components Module - CivicGuide AI
FAANG-Standard Component Library v3.0
"""

import streamlit as st
from typing import List, Tuple, Optional
from datetime import datetime

def metric_card(label: str, value: str, sub: str, badge: str, badge_cls: str, bar_color: str) -> str:
    """Generates a high-fidelity metric card."""
    return f'<div class="metric-card"><div class="top-bar" style="background:{bar_color}"></div><div class="m-label">{label}</div><div class="m-value">{value}</div><div class="m-sub">{sub}</div><div class="badge {badge_cls}">{badge}</div></div>'

def render_metrics_row(t_func, countdown_display: str, election_date: datetime):
    """Renders the top row of metrics."""
    m1 = metric_card(t_func("Registration"), "✓", t_func("Voter ID verified"), t_func("Active"), "badge-green", "#10b981")
    m2 = metric_card(t_func("Stations Nearby"), "3", t_func("Within 2 km radius"), t_func("Mapped"), "badge-blue", "#6366f1")
    m3 = metric_card(t_func("Crowd Level"), t_func("Low"), t_func("Best time: 9–11 AM"), t_func("Updated"), "badge-amber", "#f59e0b")
    m4 = metric_card(t_func("Election Countdown"), countdown_display, t_func(election_date.strftime("%B %d, %Y")), t_func("Lok Sabha"), "badge-red", "#f43f5e")
    st.markdown(f'<div class="metric-grid">{m1}{m2}{m3}{m4}</div>', unsafe_allow_html=True)

def topbar(title: str, chips: Optional[List[Tuple[str, str]]] = None):
    """Renders a premium topbar."""
    chip_html = "".join([f'<span class="cg-chip {c[1]}">{c[0]}</span>' for c in (chips or [])])
    st.markdown(f'<div class="cg-topbar"><div class="cg-page-title">{title}</div><div style="display:flex;gap:12px;">{chip_html}</div></div>', unsafe_allow_html=True)

def render_journey_steps(t_func, is_reg: bool):
    """Renders the vertical progress timeline."""
    steps = [
        ("done" if is_reg else "active", "✓" if is_reg else "→", t_func("Register to Vote"), t_func("Voter ID obtained")),
        ("done" if is_reg else "pending", "✓" if is_reg else "○", t_func("Verify your details"), t_func("Details confirmed")),
        ("active" if is_reg else "pending", "→" if is_reg else "○", t_func("Find your polling booth"), t_func("Booth confirmed")),
    ]
    rows = "".join([f'<div class="journey-step"><div class="jnode jnode-{s[0]}">{s[1]}</div><div><div style="font-weight:600;">{s[2]}</div><div style="color:#94a3b8;font-size:12px;">{s[3]}</div></div></div>' for s in steps])
    st.markdown(f'<div>{rows}</div>', unsafe_allow_html=True)

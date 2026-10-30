"""
Novalink Bespoke Apps - showcase & live demo site.

Run locally:   streamlit run app.py
Deploy:        push app.py, demos.py, requirements.txt and .streamlit/config.toml
               to GitHub, then point Streamlit Community Cloud at app.py.
No secrets needed - every demo runs on fictitious data generated in-session.
"""
import html as html_lib
import inspect
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import demos as D

st.set_page_config(page_title="Novalink · Bespoke Apps", page_icon="◆", layout="wide",
                   initial_sidebar_state="collapsed")

CONTACT_EMAIL = "info@novalinkhardware.co.uk"

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#0A0E1A;--surface:#111827;--surface-2:#161F33;--surface-3:#1C2740;--border:rgba(148,163,184,.14);--border-strong:rgba(148,163,184,.26);--text:#E7EAF3;--muted:#8C98B0;--faint:#5E6A82;--accent:#7C83FF;--accent-2:#38D6F5;--accent-soft:rgba(124,131,255,.14);--good:#34D399;--warn:#FBBF24;--risk:#FB923C;--bad:#F87171;--radius:14px;--grad:linear-gradient(135deg,#7C83FF 0%,#38D6F5 100%);}
html,body,[class*="css"],.stApp,button,input,textarea,select{font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif!important}
.stApp{background:radial-gradient(1200px 500px at 85% -10%,rgba(56,214,245,.07),transparent 60%),radial-gradient(900px 500px at 10% -20%,rgba(124,131,255,.10),transparent 60%),var(--bg)}
[data-testid="stHeader"]{background:transparent}[data-testid="stDecoration"]{display:none}footer{visibility:hidden}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{display:none}
.block-container{padding-top:1.2rem!important;padding-bottom:3rem!important;max-width:1360px}
[data-testid="stWidgetLabel"] p{font-size:.76rem!important;font-weight:600!important;color:var(--muted)!important;text-transform:uppercase;letter-spacing:.06em}
[data-testid="stCaptionContainer"]{color:var(--muted)!important}
[class*="st-key-card-"]{background:linear-gradient(180deg,rgba(22,31,51,.85) 0%,rgba(17,24,39,.85) 100%);border:1px solid var(--border)!important;border-radius:var(--radius);padding:22px 22px 18px;box-shadow:0 1px 0 rgba(255,255,255,.03) inset,0 20px 40px -24px rgba(0,0,0,.6);margin-bottom:6px}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{background:var(--surface)!important;border:1px solid var(--border-strong)!important;border-radius:10px!important}
[data-baseweb="input"]:focus-within,[data-baseweb="select"]>div:focus-within{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--accent-soft)!important}
[data-baseweb="input"]>div,[data-baseweb="base-input"]{background:transparent!important}
.stButton button,.stDownloadButton button,.stLinkButton a{border-radius:10px!important;font-weight:600!important;border:1px solid var(--border-strong)!important;background:var(--surface-2)!important;color:var(--text)!important;transition:all .15s ease}
.stButton button:hover,.stDownloadButton button:hover,.stLinkButton a:hover{border-color:var(--accent)!important;transform:translateY(-1px)}
.stButton button[kind="primary"],.stDownloadButton button[kind="primary"],[data-testid="stBaseButton-primary"],[data-testid="stBaseLinkButton-primary"],.stLinkButton a[data-testid="stBaseLinkButton-primary"]{background:var(--grad)!important;border:none!important;color:#0A0E1A!important;box-shadow:0 8px 24px -10px rgba(124,131,255,.8)}
.stButton button[kind="primary"] p,[data-testid="stBaseButton-primary"] p,[data-testid="stBaseLinkButton-primary"] p,.stLinkButton a[data-testid="stBaseLinkButton-primary"] p{color:#0A0E1A!important;font-weight:700!important}
[data-testid="stTabs"] [role="tablist"],[data-baseweb="tab-list"]{gap:4px;background:var(--surface);padding:4px;border-radius:12px;border:1px solid var(--border);width:fit-content}
[data-testid="stTabs"] [role="tab"],[data-baseweb="tab"]{border-radius:9px!important;padding:8px 16px!important;color:var(--muted)!important;background:transparent!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"],[data-baseweb="tab"][aria-selected="true"]{background:var(--surface-3)!important;color:var(--text)!important}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"],[data-testid="stTabs"] .react-aria-SelectionIndicator{display:none!important}
[data-testid="stDataFrame"]{border:1px solid var(--border);border-radius:12px;overflow:hidden}
[data-testid="stExpander"] details{background:var(--surface);border:1px solid var(--border)!important;border-radius:12px!important}

/* ---------- top nav ---------- */
.st-key-topnav{border-bottom:1px solid var(--border);padding-bottom:12px;margin-bottom:8px}
.st-key-topnav .stButton button{padding:6px 14px!important;min-height:38px}
.nv-brand{display:flex;align-items:center;gap:12px}
.nv-brand .t{font-weight:800;font-size:1.08rem;letter-spacing:-.02em;color:var(--text);line-height:1.1}
.nv-brand .s{font-size:.72rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;font-weight:600}
.pe-logo{width:40px;height:40px;border-radius:12px;background:var(--grad);display:grid;place-items:center;color:#0A0E1A;box-shadow:0 10px 24px -10px rgba(124,131,255,.9);flex:none}

/* ---------- typography ---------- */
.pe-eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.72rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--accent-2);margin-bottom:10px}
.pe-eyebrow .dot{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 0 4px rgba(52,211,153,.15)}
.nv-hero-t{font-size:clamp(2.2rem,4.4vw,3.6rem);font-weight:800;letter-spacing:-.045em;line-height:1.02;color:var(--text);margin:4px 0 16px}
.nv-hero-t span,.pe-title span,.nv-h2 span{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.nv-hero-s{color:var(--muted);font-size:1.08rem;line-height:1.6;max-width:560px;margin-bottom:22px}
.nv-h2{font-size:clamp(1.5rem,2.6vw,2.05rem);font-weight:800;letter-spacing:-.035em;color:var(--text);line-height:1.15;margin-bottom:8px}
.nv-lead{color:var(--muted);font-size:.98rem;max-width:720px;line-height:1.6;margin-bottom:22px}
.nv-sec{margin:56px 0 0}
.pe-title{font-size:2.05rem;font-weight:800;letter-spacing:-.035em;line-height:1.1;color:var(--text)}
.pe-sub{color:var(--muted);font-size:.95rem;margin-top:8px;max-width:640px}

/* ---------- hero mock ---------- */
.nv-mock{position:relative;background:linear-gradient(180deg,#141C30 0%,#0F1526 100%);border:1px solid var(--border-strong);border-radius:18px;padding:18px;box-shadow:0 40px 80px -30px rgba(56,214,245,.25),0 30px 60px -30px rgba(0,0,0,.8);transform:perspective(1400px) rotateY(-6deg) rotateX(3deg)}
.nv-mock .bar{display:flex;align-items:center;gap:6px;margin-bottom:14px}
.nv-mock .bar i{width:9px;height:9px;border-radius:50%;background:#2A3550;display:block}
.nv-mock .bar .ttl{margin-left:10px;font-size:.78rem;color:var(--muted);font-weight:600}
.nv-mock .kp{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.nv-mock .kp div{background:var(--surface);border:1px solid var(--border);border-top:2px solid var(--accent);border-radius:10px;padding:10px 12px}
.nv-mock .kp b{display:block;font-size:1.25rem;color:var(--text);letter-spacing:-.03em}
.nv-mock .kp span{font-size:.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-weight:700}
.nv-mock .chart{display:flex;align-items:flex-end;gap:7px;height:120px;padding:12px;background:var(--surface);border:1px solid var(--border);border-radius:10px}
.nv-mock .chart div{flex:1;border-radius:5px 5px 2px 2px;background:var(--grad);opacity:.9}
.nv-mock .chart div.m{background:linear-gradient(180deg,#F87171,#FB923C)}
.nv-mock .alert{margin-top:12px;display:flex;gap:10px;align-items:center;background:rgba(248,113,113,.10);border:1px solid rgba(248,113,113,.3);border-radius:10px;padding:10px 12px;font-size:.8rem;color:#FCA5A5}
.nv-float{position:absolute;right:-14px;bottom:-22px;background:var(--surface-2);border:1px solid var(--border-strong);border-radius:12px;padding:10px 14px;font-size:.78rem;color:var(--text);box-shadow:0 20px 40px -18px rgba(0,0,0,.8);display:flex;gap:10px;align-items:center}
.nv-float .g{width:26px;height:26px;border-radius:8px;background:rgba(52,211,153,.15);color:var(--good);display:grid;place-items:center}

/* ---------- tiles & grids ---------- */
.nv-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
.nv-grid.g3{grid-template-columns:repeat(auto-fit,minmax(290px,1fr))}
.nv-tile{background:linear-gradient(180deg,rgba(22,31,51,.85) 0%,rgba(17,24,39,.85) 100%);border:1px solid var(--border);border-radius:var(--radius);padding:22px;position:relative;overflow:hidden}
.nv-tile .ic{width:42px;height:42px;border-radius:12px;background:var(--accent-soft);border:1px solid rgba(124,131,255,.3);display:grid;place-items:center;color:var(--accent);margin-bottom:16px}
.nv-tile .ic.c{background:rgba(56,214,245,.12);border-color:rgba(56,214,245,.3);color:var(--accent-2)}
.nv-tile .h{font-size:1.02rem;font-weight:700;color:var(--text);margin-bottom:6px;letter-spacing:-.01em}
.nv-tile .p{font-size:.88rem;color:var(--muted);line-height:1.55}
.nv-tile .num{position:absolute;right:18px;top:14px;font-size:2.6rem;font-weight:800;letter-spacing:-.05em;color:rgba(124,131,255,.12)}
.nv-step-line{height:2px;background:var(--grad);border-radius:2px;margin:-2px 0 18px;opacity:.6}
.nv-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:40px}@media(max-width:640px){.nv-stats{grid-template-columns:1fr}}
.nv-stat{border-left:2px solid var(--accent);padding:4px 0 4px 16px}
.nv-stat b{display:block;font-size:1.25rem;font-weight:800;letter-spacing:-.03em;color:var(--text)}
.nv-stat span{font-size:.84rem;color:var(--muted)}

/* app showcase cards */
.nv-app .top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.nv-app .lbl{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--faint);margin:14px 0 4px}
.nv-app .out{margin-top:14px;padding:10px 12px;border-radius:10px;background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.25);color:#A7F3D0;font-size:.84rem;line-height:1.45}

/* compare */
.nv-cmp{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:760px){.nv-cmp{grid-template-columns:1fr}.nv-mock{transform:none}}
.nv-cmp ul{list-style:none;padding:0;margin:10px 0 0}
.nv-cmp li{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);font-size:.9rem;color:var(--text)}
.nv-cmp li:last-child{border:none}
.nv-cmp .x{color:var(--bad)}.nv-cmp .y{color:var(--good)}

/* CTA band */
[class*="st-key-ctaband"]{margin-top:56px;padding:36px 40px 40px;border-radius:20px;background:radial-gradient(600px 200px at 80% 0%,rgba(56,214,245,.18),transparent 70%),linear-gradient(135deg,rgba(124,131,255,.18),rgba(56,214,245,.06));border:1px solid rgba(124,131,255,.35)}

/* chips */
.pe-chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;font-size:.74rem;font-weight:600;background:var(--surface-3);color:var(--text);border:1px solid var(--border);white-space:nowrap}
.pe-chip.accent{background:var(--accent-soft);color:#B9BDFF;border-color:rgba(124,131,255,.3)}
.pe-chip.good{background:rgba(52,211,153,.12);color:var(--good);border-color:rgba(52,211,153,.3)}
.pe-chip.warn{background:rgba(251,191,36,.12);color:var(--warn);border-color:rgba(251,191,36,.3)}
.pe-chip.bad{background:rgba(248,113,113,.12);color:var(--bad);border-color:rgba(248,113,113,.3)}

/* stepper hero */
.pe-hero{display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap;padding:14px 2px 22px;margin-bottom:18px;border-bottom:1px solid var(--border)}
.pe-stepper{display:flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:6px;flex-wrap:wrap}
.pe-step{display:flex;align-items:center;gap:8px;padding:7px 14px 7px 7px;border-radius:999px;font-size:.82rem;font-weight:600;color:var(--faint);white-space:nowrap}
.pe-step .num{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-size:.72rem;font-weight:700;border:1px solid var(--border-strong)}
.pe-step.done{color:var(--muted)}.pe-step.done .num{background:rgba(52,211,153,.14);border-color:rgba(52,211,153,.45);color:var(--good)}
.pe-step.active{background:var(--surface-3);color:var(--text)}.pe-step.active .num{background:var(--grad);border:none;color:#0A0E1A}
.pe-step-sep{width:14px;height:1px;background:var(--border-strong)}
.pe-section{display:flex;align-items:center;gap:12px;margin-bottom:16px}
.pe-section .badge{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent);font-weight:800;font-size:.85rem;border:1px solid rgba(124,131,255,.3)}
.pe-section .t{font-size:1.08rem;font-weight:700;color:var(--text)}.pe-section .s{font-size:.82rem;color:var(--muted);margin-top:2px}

/* scenario picker cards */
[class*="st-key-scn-"]{background:var(--surface);border:1px solid var(--border)!important;border-radius:var(--radius);padding:18px 18px 14px;transition:all .15s ease;height:100%}
[class*="st-key-scn-"]:hover{border-color:var(--border-strong)!important}
[class*="st-key-scn-on-"]{border-color:rgba(56,214,245,.55)!important;box-shadow:0 0 0 3px rgba(56,214,245,.10),0 20px 40px -24px rgba(56,214,245,.45);background:linear-gradient(180deg,rgba(28,39,64,.9),rgba(17,24,39,.9))}
.nv-scn .h{font-weight:700;color:var(--text);margin:12px 0 4px}.nv-scn .p{font-size:.82rem;color:var(--muted);line-height:1.45;min-height:58px}

/* KPI tiles */
.nv-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:6px 0 18px}
.pe-kpi{background:var(--surface);border:1px solid var(--border);border-top:2px solid var(--accent);border-radius:14px;padding:16px 18px}
.pe-kpi.b{border-top-color:var(--bad)}.pe-kpi.g{border-top-color:var(--good)}.pe-kpi.c{border-top-color:var(--accent-2)}
.pe-kpi .l{font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.pe-kpi .v{font-size:1.8rem;font-weight:800;letter-spacing:-.03em;color:var(--text);margin-top:6px}
.pe-kpi .s{font-size:.8rem;color:var(--faint);margin-top:2px}

/* observations */
.nv-obs{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid var(--border);font-size:.9rem;line-height:1.5;color:var(--text)}
.nv-obs:last-child{border:none}
.nv-obs .d{width:8px;height:8px;border-radius:50%;margin-top:7px;flex:none}
.nv-rec{display:flex;gap:12px;padding:9px 0;font-size:.88rem;color:var(--text);line-height:1.5}
.nv-rec b{width:24px;height:24px;border-radius:7px;background:var(--accent-soft);color:var(--accent);display:grid;place-items:center;font-size:.75rem;flex:none}

/* transcript */
.nv-tr{display:flex;flex-direction:column;gap:10px;max-height:520px;overflow:auto;padding-right:6px}
.nv-msg{max-width:86%;padding:10px 14px;border-radius:14px;font-size:.88rem;line-height:1.5;border:1px solid var(--border)}
.nv-msg .meta{font-size:.68rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:3px;display:flex;gap:8px;align-items:center}
.nv-msg.a{align-self:flex-start;background:var(--surface-3)}
.nv-msg.a.weak{border-color:rgba(251,191,36,.45);background:rgba(251,191,36,.06)}
.nv-msg.c{align-self:flex-end;background:rgba(124,131,255,.10);border-color:rgba(124,131,255,.25)}
.nv-coach{border:1px solid var(--border);border-radius:12px;padding:14px 16px;margin-bottom:12px;background:var(--surface)}
.nv-coach .q{font-size:.86rem;color:#FCD34D;margin:8px 0;font-style:italic}
.nv-coach .t{font-size:.86rem;color:var(--muted);line-height:1.5}
.nv-coach .try{margin-top:10px;padding:10px 12px;border-radius:10px;background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.25);color:#A7F3D0;font-size:.86rem}

/* upload zone (illustrative) */
.nv-drop{border:1.5px dashed var(--border-strong);border-radius:14px;padding:18px;display:flex;gap:14px;align-items:center;color:var(--muted);font-size:.86rem;background:rgba(17,24,39,.5)}
.nv-drop .ic{width:40px;height:40px;border-radius:12px;background:var(--accent-soft);color:var(--accent);display:grid;place-items:center;flex:none}
.nv-empty{text-align:center;padding:40px 20px}
.nv-empty .ic{width:56px;height:56px;border-radius:16px;margin:0 auto 14px;background:var(--accent-soft);color:var(--accent);display:grid;place-items:center}
.nv-empty .h{font-weight:700;color:var(--text);font-size:1.05rem}
.nv-empty ol{display:inline-block;text-align:left;color:var(--muted);font-size:.88rem;margin-top:10px}
.nv-foot{margin-top:60px;padding-top:20px;border-top:1px solid var(--border);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;color:var(--faint);font-size:.8rem}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def esc(v):
    return html_lib.escape(str(v if v is not None else ""), quote=True)


def render_html(markup, target=None):
    (target or st).markdown(" ".join(l.strip() for l in markup.splitlines()), unsafe_allow_html=True)


def chip(text, tone=""):
    return f'<span class="pe-chip {tone}">{esc(text)}</span>'


def section_header(num, title, subtitle=""):
    render_html(f'<div class="pe-section"><div class="badge">{num}</div><div><div class="t">{esc(title)}</div>'
                + (f'<div class="s">{esc(subtitle)}</div>' if subtitle else "") + "</div></div>")


def _kw(fn):
    try:
        if "width" in inspect.signature(fn).parameters:
            return {"width": "stretch"}
    except (TypeError, ValueError):
        pass
    return {"use_container_width": True}


BTN_W, DF_W = _kw(st.button), _kw(st.dataframe)


def show_fig(fig):
    st.plotly_chart(fig, config={"displayModeBar": False}, **_kw(st.plotly_chart))


def show_df(df, height=None, **kw):
    if height:
        kw["height"] = height
    st.dataframe(df, hide_index=True, **DF_W, **kw)


def go_to(page, scenario=None):
    st.session_state.page = page
    if scenario:
        st.session_state.scenario = scenario


# Feather-style icons
I = {
    "logo": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V4l16 16V4"/></svg>',
    "phone": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "mic": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>',
    "pound": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7a4 4 0 0 0-7-2.6C9.8 5.6 10 8 10 10v4c0 2-1 4-3 5h11"/><line x1="6" y1="12" x2="15" y2="12"/></svg>',
    "trend": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "calc": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="11" x2="8" y2="11"/><line x1="12" y1="11" x2="12" y2="11"/><line x1="16" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="8" y2="15"/><line x1="12" y1="15" x2="12" y2="15"/><line x1="16" y1="15" x2="16" y2="18"/></svg>',
    "clip": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><polyline points="9 14 11 16 15 12"/></svg>',
    "upload": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "chat": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "code": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    "bulb": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 .4-1.8 1-2.3A7 7 0 0 0 12 2z"/></svg>',
    "shield": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "table": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/></svg>',
    "clock": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "puzzle": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12h-2a2 2 0 1 0-4 0h-2V8a2 2 0 1 0 0-4V2H4v8h2a2 2 0 1 1 0 4H4v8h8v-2a2 2 0 1 1 4 0v2h4z"/></svg>',
    "check": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "x": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "alert": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12" y2="17"/></svg>',
}

TONE_COL = {"good": "#34D399", "warn": "#FBBF24", "bad": "#F87171", "accent": "#7C83FF"}
COL = dict(a="#7C83FF", c="#38D6F5", g="#34D399", w="#FBBF24", b="#F87171", r="#FB923C", m="#8C98B0")


def style_fig(fig, h=330, title=None):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#C9D1E3", size=12), height=h,
        margin=dict(l=8, r=8, t=46 if title else 16, b=8 if len(fig.data) < 2 else 30),
        title=dict(text=f"<b>{title}</b>" if title else None, x=0, font=dict(size=14, color="#E7EAF3")),
        legend=dict(orientation="h", y=-0.16, yanchor="top", x=0, xanchor="left", font=dict(size=11),
                    traceorder="normal"),
        hoverlabel=dict(bgcolor="#161F33", bordercolor="#2A3550", font=dict(family="Inter")),
        bargap=0.28)
    fig.update_xaxes(gridcolor="rgba(148,163,184,.08)", zeroline=False, linecolor="rgba(148,163,184,.2)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.08)", zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# App catalogue - used by Home + Showcase
# ---------------------------------------------------------------------------
APPS = [
    dict(key="calls", icon="phone", name="Call Insights", tag="Telephony analytics", live=True,
         problem="Your phone system exports thousands of call records, but nobody can tell you how many customers actually gave up.",
         does="Upload a raw CDR export from any PBX. The app finds true missed calls, unreturned callers, peak hours and cover gaps.",
         out="One-click PDF: missed-call heatmap, value at risk, per-extension league table, recommendations."),
    dict(key="quality", icon="mic", name="Call Quality Analyser", tag="AI coaching", live=True,
         problem="Managers can't listen to every call, so coaching is based on gut feel and the odd complaint.",
         does="Upload a call recording. AI transcribes it and scores empathy, clarity, compliance, pace and outcome.",
         out="Scorecard, sentiment timeline and 'try saying this instead' coaching for every weak moment."),
    dict(key="bills", icon="pound", name="Bill Run & Profit", tag="Finance & reconciliation", live=True,
         problem="Supplier invoices and customer billing live in different systems, and margin quietly leaks between them.",
         does="Upload supplier and billing files. The app matches every line and flags unbilled, under-billed and below-cost services.",
         out="Profit by product and customer, recoverable revenue, and an exceptions list ready to action."),
    dict(key="pipeline", icon="trend", name="Sales Pipeline", tag="Sales performance", live=True,
         problem="The pipeline is a spreadsheet that's always out of date, so forecasts are guesses.",
         does="Upload a simple deals list (or connect your CRM). The app builds the forecast, funnel and team leaderboard.",
         out="Weighted forecast by month, stalled-deal alerts with next best actions, win rates by person."),
    dict(key="pricing", icon="calc", name="Pricing & Quote Engine", tag="Sales tools", live=False,
         problem="Quotes take hours, prices vary by person, and paperwork is retyped from scratch every time.",
         does="Your price book, rules and margins built into a guided quote builder that anyone on the team can use.",
         out="Consistent, branded quotes and contracts in minutes, with margin protected on every deal."),
    dict(key="forms", icon="clip", name="Field Job Sheets", tag="Operations", live=False,
         problem="Paper job sheets get lost, are hard to read, and the office retypes everything.",
         does="A mobile form built around your exact job types: photos, signatures, parts used, time on site.",
         out="Instant PDF job sheet for the customer and a clean record for the office, synced to your systems."),
]
DEMO_KEYS = ["calls", "quality", "bills", "pipeline"]
APP = {a["key"]: a for a in APPS}

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("page", "Home")
ss.setdefault("scenario", "calls")
ss.setdefault("results", {})
ss.setdefault("runs", 0)
PAGES = ["Home", "What we build", "Try it now", "Get started"]

# ---------------------------------------------------------------------------
# Top navigation
# ---------------------------------------------------------------------------
with st.container(key="topnav"):
    cols = st.columns([3.2, 1, 1.25, 1.05, 1.1])
    render_html(f'''<div class="nv-brand"><div class="pe-logo">{I["logo"]}</div>
        <div><div class="t">Novalink</div><div class="s">Bespoke business apps</div></div></div>''', cols[0])
    for c, p in zip(cols[1:], PAGES):
        c.button(p, key=f"nav-{p}", on_click=go_to, args=(p,), type="primary" if ss.page == p else "secondary",
                 **BTN_W)


def footer():
    render_html(f'''<div class="nv-foot"><div>© Novalink · Bespoke business apps</div>
        <div>All demo data on this site is fictitious and generated on the fly.</div>
        <div>{esc(CONTACT_EMAIL)}</div></div>''')


# ===========================================================================
# PAGE: HOME
# ===========================================================================
def page_home():
    st.write("")
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        render_html(f'''<div style="padding-top:28px"><div class="pe-eyebrow"><span class="dot"></span>Bespoke apps · built around your business</div>
            <div class="nv-hero-t">Your process.<br>Your data.<br><span>Your app.</span></div>
            <div class="nv-hero-s">We turn the spreadsheets, exports and paper forms your team wrestles with into
            simple web apps. Upload your data, get clear answers, beautiful reports and actions you can take today.</div></div>''')
        b1, b2, _ = st.columns([1.15, 1.15, 1])
        b1.button("Try a live demo  →", type="primary", on_click=go_to, args=("Try it now",), **BTN_W)
        b2.button("See what we build", on_click=go_to, args=("What we build",), **BTN_W)
        render_html('''<div class="nv-stats">
            <div class="nv-stat"><b>Minutes</b><span>from file upload to finished report</span></div>
            <div class="nv-stat"><b>No new systems</b><span>works with the exports you already have</span></div>
            <div class="nv-stat"><b>Built for you</b><span>your terms, your branding, your rules</span></div></div>''')
    with right:
        bars = [38, 62, 88, 74, 52, 30, 46, 70, 64, 40]
        miss = {5, 6}
        bar_html = "".join(f'<div class="{"m" if i in miss else ""}" style="height:{h}%"></div>' for i, h in enumerate(bars))
        render_html(f'''<div style="padding:30px 20px 40px 10px"><div class="nv-mock">
            <div class="bar"><i></i><i></i><i></i><span class="ttl">Call Insights · Harbour Dental</span></div>
            <div class="kp"><div><span>Answer rate</span><b>87%</b></div><div><span>True missed</span><b style="color:#F87171">46</b></div>
            <div><span>Value at risk</span><b>£2,070</b></div></div>
            <div class="chart">{bar_html}</div>
            <div class="alert">{I["alert"]}<span>Lunch cover gap: 28% of calls missed 12-2pm</span></div>
            <div class="nv-float"><div class="g">{I["check"]}</div><div><b>Report ready</b><br><span style="color:#8C98B0">2-page PDF · 4 actions</span></div></div>
            </div></div>''')

    # problem
    render_html(f'''<div class="nv-sec"><div class="pe-eyebrow">The problem</div>
        <div class="nv-h2">Every business has data it <span>can't use.</span></div>
        <div class="nv-lead">The answers are already in your phone system, your invoices and your spreadsheets. They're just
        buried in exports nobody has time to read, or in software that almost fits but never quite does.</div>
        <div class="nv-grid g3">
        <div class="nv-tile"><div class="ic">{I["table"]}</div><div class="h">Stuck in exports</div>
        <div class="p">Systems spit out CSVs with thousands of rows. Nobody opens them, so nobody acts on them.</div></div>
        <div class="nv-tile"><div class="ic">{I["clock"]}</div><div class="h">Days of spreadsheet work</div>
        <div class="p">Month-end reconciliations, reports and quotes eat hours of skilled people's time, every single month.</div></div>
        <div class="nv-tile"><div class="ic">{I["puzzle"]}</div><div class="h">Software that almost fits</div>
        <div class="p">Off-the-shelf tools make you change how you work. Bespoke software used to cost a fortune. Not any more.</div></div>
        </div></div>''')

    # how it works
    render_html(f'''<div class="nv-sec"><div class="pe-eyebrow">How it works</div>
        <div class="nv-h2">From headache to working app <span>in four steps.</span></div>
        <div class="nv-lead">No long IT project, no access to your systems needed to get started. If you can export it, we can build on it.</div>
        <div class="nv-step-line"></div>
        <div class="nv-grid">
        <div class="nv-tile"><span class="num">01</span><div class="ic">{I["chat"]}</div><div class="h">Tell us the headache</div>
        <div class="p">A short call about what takes too long, what you can't see, and what a great answer looks like.</div></div>
        <div class="nv-tile"><span class="num">02</span><div class="ic c">{I["code"]}</div><div class="h">We build it around you</div>
        <div class="p">Your terminology, your rules, your branding. You see working versions early and shape them as we go.</div></div>
        <div class="nv-tile"><span class="num">03</span><div class="ic">{I["upload"]}</div><div class="h">Upload your data</div>
        <div class="p">Drop in a call log, a recording, a bill file or a deals list. The app does the heavy lifting in seconds.</div></div>
        <div class="nv-tile"><span class="num">04</span><div class="ic c">{I["bulb"]}</div><div class="h">Act on the answers</div>
        <div class="p">Dashboards, branded PDF reports and clear next actions, ready for your team, your board or your customers.</div></div>
        </div></div>''')

    # app types preview
    render_html('''<div class="nv-sec"><div class="pe-eyebrow">Proven in daily use</div>
        <div class="nv-h2">Built from <span>real business problems.</span></div>
        <div class="nv-lead">Each of these started as a genuine headache and is now a working tool used every day.
        Four of them can be tried live on this site with sample data.</div></div>''')
    cols = st.columns(3)
    for i, a in enumerate(APPS):
        with cols[i % 3]:
            with st.container(key=f"card-home-{a['key']}"):
                render_html(f'''<div class="nv-app"><div class="top"><div class="ic" style="width:40px;height:40px;border-radius:11px;
                    background:var(--accent-soft);color:var(--accent);display:grid;place-items:center">{I[a["icon"]]}</div>
                    {chip("Live demo", "good") if a["live"] else chip("Example", "")}</div>
                    <div class="h" style="font-weight:700;margin-top:14px;color:var(--text)">{esc(a["name"])}</div>
                    <div style="font-size:.86rem;color:var(--muted);line-height:1.5;margin-top:4px;min-height:64px">{esc(a["does"])}</div></div>''')
                if a["live"]:
                    st.button("Try it with sample data", key=f"home-try-{a['key']}", on_click=go_to,
                              args=("Try it now", a["key"]), **BTN_W)
                else:
                    st.button("See how it works", key=f"home-see-{a['key']}", on_click=go_to,
                              args=("What we build",), **BTN_W)

    # why bespoke + safety
    render_html(f'''<div class="nv-sec"><div class="pe-eyebrow">Why bespoke</div>
        <div class="nv-h2">Software that fits, <span>not the other way round.</span></div>
        <div class="nv-cmp" style="margin-top:18px">
        <div class="nv-tile"><div class="h" style="color:var(--muted)">Off-the-shelf software</div><ul>
        <li><span class="x">{I["x"]}</span>Change your process to fit the tool</li>
        <li><span class="x">{I["x"]}</span>Pay for features you never use</li>
        <li><span class="x">{I["x"]}</span>Generic reports that miss what matters to you</li>
        <li><span class="x">{I["x"]}</span>Per-user licences that grow with your headcount</li></ul></div>
        <div class="nv-tile" style="border-color:rgba(124,131,255,.4)"><div class="h">A Novalink bespoke app</div><ul>
        <li><span class="y">{I["check"]}</span>Built around how you already work</li>
        <li><span class="y">{I["check"]}</span>Only the features you actually need</li>
        <li><span class="y">{I["check"]}</span>Reports in your language, with your branding</li>
        <li><span class="y">{I["check"]}</span>Grows with you: add integrations when you're ready</li></ul></div>
        </div></div>''')
    render_html(f'''<div class="nv-sec"><div class="nv-grid g3">
        <div class="nv-tile"><div class="ic">{I["shield"]}</div><div class="h">Your data, handled properly</div>
        <div class="p">Upload-based apps mean we never need logins to your core systems. How your data is processed and retained is agreed with you up front.</div></div>
        <div class="nv-tile"><div class="ic c">{I["upload"]}</div><div class="h">Start with a file, connect later</div>
        <div class="p">Begin with simple uploads. When you're ready, we can connect directly to your CRM or phone system for live data.</div></div>
        <div class="nv-tile"><div class="ic">{I["bulb"]}</div><div class="h">One build, ongoing value</div>
        <div class="p">A one-off build with optional monthly hosting and support, so the app keeps evolving as your business does.</div></div>
        </div></div>''')
    cta_band()


def cta_band():
    with st.container(key=f"ctaband-{ss.page.replace(' ', '')}"):
        cta_inner()


def cta_inner():
    render_html('''<div class="pe-eyebrow"><span class="dot"></span>Let's build yours</div>
        <div class="nv-h2">What's the one task that eats <span>your team's week?</span></div>
        <div class="nv-lead" style="margin-bottom:10px">Tell us about it. If there's data behind it, there's probably an app in it.</div>''')
    c1, c2, _ = st.columns([1, 1, 2.2])
    c1.link_button("Email us your headache", f"mailto:{CONTACT_EMAIL}?subject=Bespoke%20app%20enquiry",
                   type="primary", **_kw(st.link_button))
    c2.button("Try a live demo first", key=f"cta-try-{ss.page}", on_click=go_to, args=("Try it now",), **BTN_W)


# ===========================================================================
# PAGE: WHAT WE BUILD
# ===========================================================================
def page_build():
    render_html('''<div class="pe-hero"><div><div class="pe-eyebrow"><span class="dot"></span>What we build</div>
        <div class="pe-title">Apps that turn your data into <span>decisions.</span></div>
        <div class="pe-sub">Six examples from our own portfolio. Every one is tailored, so yours will speak your
        language, follow your rules and carry your brand.</div></div></div>''')
    cols = st.columns(2, gap="medium")
    for i, a in enumerate(APPS):
        with cols[i % 2]:
            with st.container(key=f"card-build-{a['key']}"):
                render_html(f'''<div class="nv-app"><div class="top"><div style="display:flex;gap:14px;align-items:center">
                    <div style="width:46px;height:46px;border-radius:13px;background:var(--accent-soft);border:1px solid rgba(124,131,255,.3);
                    color:var(--accent);display:grid;place-items:center">{I[a["icon"]]}</div>
                    <div><div style="font-weight:800;font-size:1.12rem;color:var(--text);letter-spacing:-.02em">{esc(a["name"])}</div>
                    <div style="font-size:.78rem;color:var(--muted)">{esc(a["tag"])}</div></div></div>
                    {chip("Live demo", "good") if a["live"] else chip("Example", "")}</div>
                    <div class="lbl">The headache</div><div style="color:var(--text);font-size:.9rem;line-height:1.5">{esc(a["problem"])}</div>
                    <div class="lbl">What the app does</div><div style="color:var(--muted);font-size:.9rem;line-height:1.5">{esc(a["does"])}</div>
                    <div class="out"><b>You get:</b> {esc(a["out"])}</div></div>''')
                if a["live"]:
                    st.button(f"Try {a['name']} live  →", key=f"build-try-{a['key']}", type="primary",
                              on_click=go_to, args=("Try it now", a["key"]), **BTN_W)
                else:
                    st.button("Talk to us about this", key=f"build-talk-{a['key']}", on_click=go_to,
                              args=("Get started",), **BTN_W)
            st.write("")
    render_html('''<div class="nv-sec"><div class="pe-eyebrow">And beyond</div>
        <div class="nv-h2">If it lives in a spreadsheet, <span>it can be an app.</span></div></div>''')
    ideas = ["Stock & asset tracking", "Contract renewals tracker", "Commission calculators", "Customer onboarding forms",
             "Site survey tools", "Supplier price comparisons", "Timesheet & job costing", "Compliance checklists",
             "Customer satisfaction reports", "Board-pack dashboards", "Lead scoring", "Engineer scheduling"]
    render_html('<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:6px">'
                + "".join(chip(x, "accent") for x in ideas) + "</div>")
    cta_band()


# ===========================================================================
# PAGE: TRY IT NOW
# ===========================================================================
SCN_TEXT = {
    "calls": "Generate a month of call records and get a full call-handling assessment.",
    "quality": "Analyse a sample customer call: scores, sentiment and coaching.",
    "bills": "Reconcile supplier costs against customer billing and find the leaks.",
    "pipeline": "Turn a list of deals into a forecast, funnel and team leaderboard.",
}
UPLOAD_TEXT = {
    "calls": "In your own app you'd drop in a CDR export from your phone system (CSV / Excel).",
    "quality": "In your own app you'd upload an MP3 or WAV call recording.",
    "bills": "In your own app you'd upload supplier invoices and your billing export.",
    "pipeline": "In your own app you'd upload a deals list, or connect your CRM directly.",
}


def page_try():
    hero = st.empty()
    scn = ss.scenario
    app = APP[scn]

    # 01 choose
    with st.container(key="card-choose"):
        section_header("01", "Choose a scenario", "Four real apps from our portfolio, running on sample data")
        cols = st.columns(4)
        for c, k in zip(cols, DEMO_KEYS):
            a = APP[k]
            with c:
                with st.container(key=f"scn-{'on' if k == scn else 'off'}-{k}"):
                    render_html(f'''<div class="nv-scn"><div style="width:38px;height:38px;border-radius:11px;background:var(--accent-soft);
                        color:var(--accent);display:grid;place-items:center">{I[a["icon"]]}</div>
                        <div class="h">{esc(a["name"])}</div><div class="p">{esc(SCN_TEXT[k])}</div></div>''')
                    st.button("Selected" if k == scn else "Choose", key=f"pick-{k}", on_click=go_to,
                              args=("Try it now", k), type="primary" if k == scn else "secondary", **BTN_W)

    # 02 personalise
    st.write("")
    with st.container(key="card-config"):
        section_header("02", "Make it yours", "Personalise the sample so the output looks like your business")
        c1, c2, c3 = st.columns([1.2, 1.2, 1])
        company = c1.text_input("Your company name", value=ss.get("company", "Harbour Dental"), max_chars=40,
                                key="w_company").strip() or "Your Company"
        ss.company = company
        industry = c2.selectbox("Industry", list(D.INDUSTRIES), key="w_industry")
        extra = {}
        if scn == "quality":
            extra["call"] = c3.selectbox("Call type", list(D.SCRIPTS), key="w_call")
            d1, d2, _ = st.columns([1.2, 1.2, 1])
            extra["level"] = d1.selectbox("How did the agent do?", ["Strong", "Average", "Needs coaching"], index=1,
                                          key="w_level")
            extra["agent"] = d2.text_input("Agent's first name", value="Jordan", max_chars=20, key="w_agent").strip() or "Jordan"
        elif scn != "quality":
            extra["size"] = c3.selectbox("Business size", list(D.SIZES), index=1, key="w_size",
                                         help="Scales call volumes, customer numbers and deal counts")
        render_html(f'''<div class="nv-drop" style="margin-top:8px"><div class="ic">{I["upload"]}</div>
            <div><b style="color:var(--text)">Using sample data for this demo.</b> {esc(UPLOAD_TEXT[scn])}</div></div>''')
        st.write("")
        g1, g2, _ = st.columns([1.2, 1, 2])
        run = g1.button(f"Generate {app['name']} report  →", type="primary", key="run", **BTN_W)
        if g2.button("New sample data", key="reroll", **BTN_W):
            ss.runs += 1
            run = True

    if run:
        with st.spinner("Crunching the numbers..."):
            ss.results[scn] = build_result(scn, company, industry, extra)

    # 03 results
    st.write("")
    res = ss.results.get(scn)
    if res is None:
        with st.container(key="card-empty"):
            render_html(f'''<div class="nv-empty"><div class="ic">{I[app["icon"]]}</div>
                <div class="h">Your {esc(app["name"])} report will appear here</div>
                <ol><li>Pick a scenario above</li><li>Add your company name and industry</li>
                <li>Press <b>Generate</b> to see the full output and download the PDF</li></ol></div>''')
    else:
        render_results(scn, res)

    steps = ["Choose a scenario", "Make it yours", "See the results"]
    state = 3 if res is not None else 2
    sh = []
    for i, s in enumerate(steps, 1):
        cls = "done" if i < state or (res is not None) else ("active" if i == state else "")
        num = I["check"] if cls == "done" else str(i)
        sh.append(f'<div class="pe-step {cls}"><span class="num">{num}</span>{esc(s)}</div>')
    render_html(f'''<div class="pe-hero"><div><div class="pe-eyebrow"><span class="dot"></span>Live demo · sample data</div>
        <div class="pe-title">See it working for <span>{esc(company)}.</span></div>
        <div class="pe-sub">Everything below is generated from fictitious data in seconds. It's exactly the kind of output
        your own bespoke app would produce from your real files.</div></div>
        <div class="pe-stepper">{'<div class="pe-step-sep"></div>'.join(sh)}</div></div>''', hero)


def build_result(scn, company, industry, extra):
    seed = D.seed_for(scn, company, industry, extra, ss.runs)
    if scn == "calls":
        df = D.generate_cdr(industry, extra["size"], seed)
        r = D.analyse_cdr(df, industry, company)
    elif scn == "quality":
        r = D.analyse_call(extra["call"], extra["level"], company, extra["agent"], seed)
        r["period"] = f"{extra['call']} · Agent: {extra['agent']}"
    elif scn == "bills":
        sup, bil = D.generate_bills(extra["size"], seed)
        r = D.analyse_bills(sup, bil)
        r["period"] = "Monthly bill run · sample period"
    else:
        r = D.analyse_pipeline(D.generate_pipeline(industry, extra["size"], seed))
        r["period"] = f"Pipeline snapshot · {pd.Timestamp.today():%d %b %Y}"
    r.update(company=company, industry=industry, extra=extra)
    return r


def kpi_row(kpis, tones=("", "c", "b", "g")):
    render_html('<div class="nv-kpis">' + "".join(
        f'<div class="pe-kpi {t}"><div class="l">{esc(l)}</div><div class="v">{esc(v)}</div><div class="s">{esc(s)}</div></div>'
        for (l, v, s), t in zip(kpis, tones)) + "</div>")


def findings(obs, recs):
    c1, c2 = st.columns([1.35, 1], gap="medium")
    with c1:
        with st.container(key="card-findings"):
            section_header("✦", "Key findings", "Written automatically from the data")
            render_html("".join(f'<div class="nv-obs"><span class="d" style="background:{TONE_COL[t]}"></span>'
                                f'<div>{esc(o)}</div></div>' for t, o in obs))
    with c2:
        with st.container(key="card-recs"):
            section_header("→", "Recommended actions")
            render_html("".join(f'<div class="nv-rec"><b>{i}</b><div>{esc(r)}</div></div>'
                                for i, r in enumerate(recs, 1)))


def downloads(scn, res, title, table_df, table_title, raw_csv=None, raw_name="sample_data.csv"):
    st.write("")
    with st.container(key="card-dl"):
        section_header("⇩", "Take it away", "The branded report your team or customer would receive")
        pdf = D.build_pdf(title, res["company"], res.get("period", ""), res["kpis"], D.chart_png(scn, res),
                          res["obs"], res.get("recs", []), table_df, table_title)
        c1, c2, _ = st.columns([1.2, 1.2, 2])
        fname = f"{res['company'].replace(' ', '_')}_{title.replace(' ', '_')}.pdf"
        c1.download_button("Download PDF report", pdf, file_name=fname, mime="application/pdf", type="primary",
                           key=f"pdf-{scn}", **_kw(st.download_button))
        if raw_csv is not None:
            c2.download_button("Download the sample data", raw_csv, file_name=raw_name, mime="text/csv",
                               key=f"csv-{scn}", **_kw(st.download_button))


def render_results(scn, res):
    section_header("03", "Your results", f"{APP[scn]['name']} · {res['company']} · {res.get('period', '')}")
    {"calls": results_calls, "quality": results_quality, "bills": results_bills,
     "pipeline": results_pipeline}[scn](res)
    render_html('<div style="margin-top:26px"></div>')
    cta_band()


# ---------------- Call Insights ----------------
def results_calls(r):
    kpi_row(r["kpis"])
    c1, c2 = st.columns([1.25, 1], gap="medium")
    with c1:
        with st.container(key="card-heat"):
            h = r["heat"]
            fig = go.Figure(go.Heatmap(z=h.values, x=[f"{c}:00" for c in h.columns], y=list(h.index),
                                       colorscale=[[0, "#131A2B"], [0.35, "#3B3F8F"], [0.7, "#FB923C"], [1, "#F87171"]],
                                       hovertemplate="%{y} %{x}<br>%{z:.0f}% missed<extra></extra>",
                                       colorbar=dict(title="% missed", thickness=10, outlinewidth=0)))
            fig.update_yaxes(autorange="reversed")
            show_fig(style_fig(fig, 320, "When are calls being missed?"))
    with c2:
        with st.container(key="card-hourly"):
            hr = r["hourly"]
            fig = go.Figure([go.Bar(x=[f"{i}:00" for i in hr.index], y=hr.get("Answered", 0), name="Answered",
                                    marker_color=COL["a"]),
                             go.Bar(x=[f"{i}:00" for i in hr.index], y=hr.get("Missed", 0), name="Missed",
                                    marker_color=COL["b"])])
            fig.update_layout(barmode="stack")
            show_fig(style_fig(fig, 320, "Inbound calls by hour"))
    with st.container(key="card-daily"):
        d = r["daily"]
        fig = go.Figure([go.Bar(x=list(d.index), y=d.get("Answered", 0), name="Answered", marker_color=COL["a"]),
                         go.Bar(x=list(d.index), y=d.get("Missed", 0), name="Missed", marker_color=COL["b"])])
        fig.update_layout(barmode="stack")
        show_fig(style_fig(fig, 260, "Daily inbound volume, last 30 days"))
    findings(r["obs"], r["recs"])
    st.write("")
    c1, c2 = st.columns([1.35, 1], gap="medium")
    with c1:
        with st.container(key="card-ext"):
            section_header("☰", "Extension league table")
            show_df(r["ext_df"])
    with c2:
        with st.container(key="card-tm"):
            section_header("!", "Callers to call back now", f"{len(r['true_missed'])} true missed calls")
            show_df(r["true_missed"], height=250)
    downloads("calls", r, "Call Handling Assessment", r["ext_df"], "Extension performance",
              r["raw"].to_csv(index=False).encode(), "sample_cdr_export.csv")


# ---------------- Call Quality ----------------
def results_quality(r):
    kpi_row(r["kpis"], tones=("", "c", "g" if r["wpm"] < 160 else "b", "g" if r["talk"] <= 58 else "b"))
    c1, c2 = st.columns([1.3, 1], gap="medium")
    with c1:
        with st.container(key="card-sent"):
            pts = [(l["t"], l["sentiment"]) for l in r["lines"] if l["sentiment"] is not None]
            x = [p[0] for p in pts]
            y = [p[1] for p in pts]
            fig = go.Figure()
            fig.add_hrect(y0=0, y1=1, fillcolor="rgba(52,211,153,.05)", line_width=0)
            fig.add_hrect(y0=-1, y1=0, fillcolor="rgba(248,113,113,.05)", line_width=0)
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=COL["c"], width=3, shape="spline"),
                                     marker=dict(size=9, color=[COL["g"] if v >= 0 else COL["b"] for v in y],
                                                 line=dict(width=2, color="#0A0E1A")),
                                     hovertemplate="%{x:.0f}s · sentiment %{y:+.2f}<extra></extra>", name="Customer"))
            for cch in r["coaching"]:
                fig.add_vline(x=cch["at"], line=dict(color="rgba(251,191,36,.5)", dash="dot", width=1))
            fig.update_yaxes(range=[-1.05, 1.05], tickvals=[-1, 0, 1], ticktext=["Negative", "Neutral", "Positive"])
            fig.update_xaxes(title="Seconds into call")
            show_fig(style_fig(fig, 320, "Customer sentiment through the call"))
            st.caption("Dotted lines mark moments flagged for coaching.")
    with c2:
        with st.container(key="card-radar"):
            cats = list(r["scores"])
            vals = [r["scores"][c] for c in cats]
            fig = go.Figure(go.Scatterpolar(r=vals + vals[:1], theta=cats + cats[:1], fill="toself",
                                            fillcolor="rgba(124,131,255,.25)", line=dict(color=COL["a"], width=2),
                                            hovertemplate="%{theta}: %{r}<extra></extra>"))
            fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                         radialaxis=dict(range=[0, 100], gridcolor="rgba(148,163,184,.15)",
                                                         showticklabels=False, showline=False),
                                         angularaxis=dict(gridcolor="rgba(148,163,184,.15)")), showlegend=False)
            style_fig(fig, 320, "Scorecard").update_layout(margin=dict(l=60, r=60, t=50, b=30))
            show_fig(fig)
    c1, c2 = st.columns([1.15, 1], gap="medium")
    with c1:
        with st.container(key="card-transcript"):
            section_header("❝", "Transcript", f"Auto-transcribed · {r['duration'] / 60:.1f} min · weak moments highlighted")
            msgs = []
            for l in r["lines"]:
                ts = f"{int(l['t'] // 60)}:{int(l['t'] % 60):02d}"
                if l["speaker"] == "Agent":
                    cls = "a weak" if l["good"] is False else "a"
                    tag = chip(l["cat"], "warn" if l["good"] is False else "")
                else:
                    cls = "c"
                    s = l["sentiment"]
                    tag = chip(f"{s:+.1f}", "good" if s >= 0.2 else "bad" if s <= -0.2 else "")
                msgs.append(f'<div class="nv-msg {cls}"><div class="meta">{ts} · {esc(l["speaker"])} {tag}</div>'
                            f'{esc(l["text"])}</div>')
            render_html('<div class="nv-tr">' + "".join(msgs) + "</div>")
    with c2:
        with st.container(key="card-coach"):
            section_header("★", "Coaching", r["verdict"])
            if not r["coaching"]:
                render_html(f'''<div class="nv-coach"><div class="t" style="color:var(--good)"><b>No coaching points.</b>
                    This call hit every standard. Consider using it as a training example for the team.</div></div>''')
            for c in r["coaching"]:
                render_html(f'''<div class="nv-coach">{chip(c["cat"], "warn")}<div class="q">"{esc(c["said"])}"</div>
                    <div class="t">{esc(c["tip"])}</div><div class="try"><b>Try saying:</b> "{esc(c["try_saying"])}"</div></div>''')
    st.write("")
    with st.container(key="card-qobs"):
        section_header("✦", "Summary", "Written automatically from the analysis")
        render_html("".join(f'<div class="nv-obs"><span class="d" style="background:{TONE_COL[t]}"></span>'
                            f'<div>{esc(o)}</div></div>' for t, o in r["obs"]))
    r["recs"] = [f"{c['cat']}: {c['tip']}" for c in r["coaching"]][:5]
    tbl = pd.DataFrame([{"Category": k, "Score": v, "Rating": "Strong" if v >= 82 else "OK" if v >= 65 else "Coach"}
                        for k, v in r["scores"].items()])
    tr_csv = pd.DataFrame([{"Time (s)": round(l["t"], 1), "Speaker": l["speaker"], "Text": l["text"],
                            "Sentiment": l["sentiment"]} for l in r["lines"]]).to_csv(index=False).encode()
    downloads("quality", r, "Call Quality Assessment", tbl, "Scorecard", tr_csv, "sample_transcript.csv")


# ---------------- Bill run ----------------
def results_bills(r):
    kpi_row(r["kpis"], tones=("", "g", "c", "b"))
    c1, c2 = st.columns([1, 1], gap="medium")
    with c1:
        with st.container(key="card-wf"):
            g = r["gain"]
            fig = go.Figure(go.Waterfall(
                x=["Current<br>profit", "Unbilled<br>services", "Under-billed<br>qty", "Repricing", "Potential<br>profit"],
                y=[r["profit"], g["unbilled"], g["qty"], g["price"], 0],
                measure=["absolute", "relative", "relative", "relative", "total"],
                connector=dict(line=dict(color="rgba(148,163,184,.3)")),
                increasing=dict(marker=dict(color=COL["g"])), totals=dict(marker=dict(color=COL["c"])),
                decreasing=dict(marker=dict(color=COL["b"])),
                text=[D.gbp(v) for v in [r["profit"], g["unbilled"], g["qty"], g["price"], r["profit"] + r["recover"]]],
                textposition="outside", hovertemplate="%{x}: %{text}<extra></extra>"))
            fig.update_yaxes(tickprefix="£", range=[0, (r["profit"] + r["recover"]) * 1.18])
            show_fig(style_fig(fig, 340, "Monthly profit: now vs. after fixes"))
    with c2:
        with st.container(key="card-cat"):
            c = r["cat"]
            fig = go.Figure([go.Bar(x=list(c.index), y=c.Revenue, name="Revenue", marker_color=COL["a"]),
                             go.Bar(x=list(c.index), y=c.Cost, name="Cost", marker_color=COL["c"]),
                             go.Scatter(x=list(c.index), y=c.Margin, name="Margin %", yaxis="y2", mode="lines+markers",
                                        line=dict(color=COL["g"], width=2), marker=dict(size=8))])
            fig.update_layout(barmode="group", yaxis=dict(tickprefix="£"),
                              yaxis2=dict(overlaying="y", side="right", ticksuffix="%", showgrid=False, range=[-20, 80],
                                          tickvals=[0, 20, 40, 60, 80],
                                          ticktext=["0%", "20%", "40%", "60%", "80%"]))
            show_fig(style_fig(fig, 340, "Revenue, cost & margin by category"))
    with st.container(key="card-cust"):
        cu = r["cust"].sort_values("Profit", ascending=False)
        top = pd.concat([cu.head(8), cu.tail(4)]).drop_duplicates()
        top = top.iloc[::-1]
        fig = go.Figure(go.Bar(y=list(top.index), x=top.Profit, orientation="h",
                               marker_color=[COL["g"] if v >= 0 else COL["b"] for v in top.Profit],
                               text=[D.gbp(v) for v in top.Profit], textposition="outside",
                               hovertemplate="%{y}: %{text}<extra></extra>"))
        fig.update_xaxes(tickprefix="£")
        show_fig(style_fig(fig, 380, "Most and least profitable customers (£/month)"))
    findings(r["obs"], r["recs"])
    st.write("")
    with st.container(key="card-ex"):
        section_header("!", "Exceptions to action", f"{len(r['ex'])} lines · sorted by monthly impact")
        show_df(r["ex"], height=320, column_config={
            "Monthly impact £": st.column_config.NumberColumn(format="£%.2f")})
    raw = r["sup"].merge(r["bil"], on=["Customer", "Product", "Category"], how="outer", suffixes=(" (supplier)", " (billed)"))
    downloads("bills", r, "Bill Run Reconciliation", r["ex"], "Top exceptions",
              raw.to_csv(index=False).encode(), "sample_billing_data.csv")


# ---------------- Pipeline ----------------
def results_pipeline(r):
    kpi_row(r["kpis"])
    c1, c2 = st.columns([1, 1.25], gap="medium")
    with c1:
        with st.container(key="card-funnel"):
            f = r["funnel"]
            fig = go.Figure(go.Funnel(y=list(f.index), x=f.Value, textinfo="text",
                                      text=[f"{D.gbp(v)} · {int(n)} deals" for v, n in zip(f.Value, f.Deals)],
                                      marker=dict(color=["#9BA1F2", COL["a"], "#5AA8F0", COL["c"]]),
                                      connector=dict(fillcolor="rgba(124,131,255,.08)"),
                                      hovertemplate="%{y}: %{text}<extra></extra>"))
            show_fig(style_fig(fig, 330, "Open pipeline by stage"))
    with c2:
        with st.container(key="card-fc"):
            fc = r["fc"]
            cols = {"Lead": "#4B4F8A", "Qualified": "#9BA1F2", "Proposal": COL["a"], "Negotiation": COL["c"]}
            fig = go.Figure([go.Bar(x=list(fc.index), y=fc[s], name=s, marker_color=cl)
                             for s, cl in cols.items() if s in fc])
            fig.update_layout(barmode="stack")
            fig.update_yaxes(tickprefix="£")
            show_fig(style_fig(fig, 330, "Weighted forecast by expected close month"))
    with st.container(key="card-owners"):
        o = r["owners"]
        fig = go.Figure([go.Bar(x=list(o.index), y=o["Won value"], name="Won", marker_color=COL["g"]),
                         go.Bar(x=list(o.index), y=o["Weighted"], name="Weighted open", marker_color=COL["a"]),
                         go.Scatter(x=list(o.index), y=o["Win rate"], name="Win rate %", yaxis="y2",
                                    mode="markers+text", text=[f"{v:.0f}%" for v in o["Win rate"]],
                                    textposition="top center", marker=dict(size=12, color=COL["w"]))])
        fig.update_layout(barmode="group", yaxis=dict(tickprefix="£"),
                          yaxis2=dict(overlaying="y", side="right", range=[0, 110], ticksuffix="%", showgrid=False,
                                      tickvals=[0, 25, 50, 75, 100]))
        show_fig(style_fig(fig, 300, "Team leaderboard"))
    findings(r["obs"], r["recs"])
    st.write("")
    with st.container(key="card-stalled"):
        section_header("!", "Stalled deals to chase", "No activity for 3+ weeks · highest value first")
        show_df(r["stalled"], height=300, column_config={"Value £": st.column_config.NumberColumn(format="£%d")})
    raw = r["raw"].drop(columns=["Prob", "Weighted"])
    downloads("pipeline", r, "Sales Pipeline Review", r["stalled"].head(12), "Stalled deals",
              raw.to_csv(index=False).encode(), "sample_deals.csv")


# ===========================================================================
# PAGE: GET STARTED
# ===========================================================================
def page_start():
    render_html('''<div class="pe-hero"><div><div class="pe-eyebrow"><span class="dot"></span>Get started</div>
        <div class="pe-title">Let's find the app <span>hiding in your data.</span></div>
        <div class="pe-sub">A short, no-obligation conversation is all it takes. Here's what happens next.</div></div></div>''')
    render_html(f'''<div class="nv-grid">
        <div class="nv-tile"><span class="num">01</span><div class="ic">{I["chat"]}</div><div class="h">Discovery call</div>
        <div class="p">30 minutes on what slows you down and what "great" would look like. No jargon, no hard sell.</div></div>
        <div class="nv-tile"><span class="num">02</span><div class="ic c">{I["table"]}</div><div class="h">Send a sample</div>
        <div class="p">An anonymised export or example file is enough for us to show you what's possible.</div></div>
        <div class="nv-tile"><span class="num">03</span><div class="ic">{I["code"]}</div><div class="h">See a working prototype</div>
        <div class="p">We build a first version on your sample so you can judge it on results, not promises.</div></div>
        <div class="nv-tile"><span class="num">04</span><div class="ic c">{I["bulb"]}</div><div class="h">Launch & evolve</div>
        <div class="p">Your app goes live for your team, with hosting and support so it keeps improving.</div></div>
        </div>''')
    st.write("")
    c1, c2 = st.columns([1.1, 1], gap="medium")
    with c1:
        with st.container(key="card-ask"):
            section_header("?", "Helpful to tell us", "Not essential, but it speeds things up")
            for q in ["Which task or report takes your team the most time each month?",
                      "Where does the data come from today (phone system, billing, CRM, spreadsheets, paper)?",
                      "Who would use the app, and who would read its reports?",
                      "What decision would you make differently if you had the answer instantly?"]:
                render_html(f'<div class="nv-rec"><b>{I["check"]}</b><div>{esc(q)}</div></div>')
    with c2:
        with st.container(key="card-contact"):
            section_header("@", "Talk to us")
            render_html(f'''<div style="color:var(--muted);font-size:.92rem;line-height:1.6;margin-bottom:14px">
                Email us a line or two about your headache and we'll come back to arrange a call.</div>
                <div style="font-size:1.25rem;font-weight:800;letter-spacing:-.02em;color:var(--text);margin-bottom:16px">{esc(CONTACT_EMAIL)}</div>''')
            st.link_button("Email Novalink", f"mailto:{CONTACT_EMAIL}?subject=Bespoke%20app%20enquiry",
                           type="primary", **_kw(st.link_button))
            st.button("Try a live demo first", key="start-try", on_click=go_to, args=("Try it now",), **BTN_W)


# ---------------------------------------------------------------------------
{"Home": page_home, "What we build": page_build, "Try it now": page_try, "Get started": page_start}[ss.page]()
footer()

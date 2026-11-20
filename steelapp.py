import streamlit as st
import math
import tempfile
import os
import ezdxf
import pandas as pd
import re
from datetime import datetime

# =====================================================
# 페이지 기본 설정 및 커스텀 CSS
# =====================================================
st.set_page_config(
    page_title="RC 보 이어치기 검토 시스템",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

    /* 전체 기본 폰트: 1순위 Pretendard, 2순위 Noto Sans KR 통일 (영문/숫자/한글 크기 및 굵기 일관성 확보) */
    html, body, .stApp, h1, h2, h3, h4, button, input, textarea, label, p, li, td, th, svg text {
        font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stIconMaterial"], .material-symbols-rounded, .material-symbols-outlined {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
    }
    .stApp {
        background-color: #f6f7f8 !important;
        color: #111418 !important;
    }
    .block-container {
        max-width: 1560px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* 좌측 사이드바 (역기획: 280px 화이트 패널, #f0f2f4 경계선, DAEWOO E&C 헤더) */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #f0f2f4 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }
    .dw-sidebar-brand {
        padding: 1.25rem 1.25rem 1.1rem 1.25rem;
        border-bottom: 1px solid #f0f2f4;
        margin-bottom: 1rem;
        background: #ffffff;
    }
    .dw-sidebar-brand .brand-title {
        font-size: 1.35rem;
        font-weight: 900;
        color: #137fec;
        letter-spacing: -0.05em;
        font-style: italic;
        line-height: 1;
        margin: 0;
    }
    .dw-sidebar-brand .brand-sub {
        font-size: 10px;
        color: #9ca3af;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 5px;
        letter-spacing: 0.04em;
    }
    .dw-sidebar-sec-title {
        font-size: 0.85rem;
        font-weight: 800;
        color: #111418;
        padding: 0.55rem 0.75rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #137fec;
        border-radius: 8px;
        margin: 0.65rem 0 0.2rem 0;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        margin-top: -0.75rem !important;
    }
    .dw-sidebar-footer {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #f0f2f4;
        font-size: 11px;
        color: #9ca3af;
        text-align: center;
        font-weight: 600;
    }

    /* 상단 헤더 바 및 페이지 타이틀 (역기획: 화이트 상단바 + 3xl Black 타이틀) */
    .dw-topbar {
        background: #ffffff;
        border: 1px solid #f0f2f4;
        border-radius: 12px;
        padding: 0.85rem 1.5rem;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .dw-topbar-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.45rem 0.95rem;
        background-color: #137fec;
        color: #ffffff !important;
        font-size: 0.78rem;
        font-weight: 700;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(19, 127, 236, 0.25);
    }
    .dw-topbar-right {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #111418;
    }
    .dw-page-header {
        display: flex;
        flex-wrap: wrap;
        align-items: flex-end;
        justify-content: space-between;
        gap: 1rem;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 1rem;
        margin-bottom: 1.25rem;
    }
    .dw-page-header h1 {
        color: #111418 !important;
        font-size: 1.85rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.03em !important;
        line-height: 1.2 !important;
        margin: 0 !important;
    }
    .dw-page-header p {
        color: #617589 !important;
        font-size: 0.95rem !important;
        margin: 0.35rem 0 0 0 !important;
        font-weight: 500;
    }
    .dw-member-pill {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.45rem 0.9rem;
        font-size: 0.78rem;
        font-weight: 700;
        color: #334155;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    /* 섹션 카드 디자인 (역기획: bg-white rounded-xl shadow-sm border border-slate-200) */
    .dw-section-card {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        overflow: hidden;
        margin-bottom: 1.1rem;
    }
    .dw-section-header {
        padding: 0.85rem 1.35rem;
        border-bottom: 1px solid #f1f5f9;
        background: rgba(248, 250, 252, 0.75);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .dw-section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .dw-accent-bar {
        width: 6px;
        height: 20px;
        background-color: #137fec;
        border-radius: 999px;
        display: inline-block;
    }
    .dw-pill-blue {
        background-color: #dbeafe;
        color: #1d4ed8;
        padding: 0.22rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* 입력 컨트롤 및 버튼 스타일 (역기획: #f6f7f8 입력창 배경, #dbe0e6 테두리, #137fec 버튼) */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background-color: #f6f7f8 !important;
        border-color: #dbe0e6 !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #111418 !important;
    }
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #137fec !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 2px rgba(19, 127, 236, 0.15) !important;
    }
    .stNumberInput label, .stSelectbox label, .stTextInput label, .stRadio > label {
        color: #111418 !important;
        font-weight: 700 !important;
        font-size: 0.84rem !important;
    }
    div[role="radiogroup"] label,
    div[role="radiogroup"] label p {
        font-size: 0.90rem !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
        color: #1e293b !important;
    }
    button[kind="primary"] {
        background-color: #137fec !important;
        border-color: #137fec !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(19, 127, 236, 0.22) !important;
        transition: all 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #0c6bce !important;
        border-color: #0c6bce !important;
    }

    /* ── 1단계 메인 기능 전환 탭 (수직 이어치기 vs 수평 이어치기 — 대형 2분할 세그먼트) ── */
    [data-testid="stTabs"] [role="tablist"],
    [data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        gap: 10px !important;
        background: #e2e8f0 !important;
        padding: 7px !important;
        border-radius: 14px !important;
        border: 1.5px solid #cbd5e1 !important;
        margin-top: 0.65rem !important;
        margin-bottom: 1.05rem !important;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.06) !important;
    }
    [data-testid="stTabs"] [data-testid="stTab"],
    [data-testid="stTabs"] [role="tab"] {
        flex: 1 1 0% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: auto !important;
        min-height: 46px !important;
        border-radius: 10px !important;
        padding: 0.72rem 1.25rem !important;
        background: rgba(255, 255, 255, 0.88) !important;
        border: 1px solid #cbd5e1 !important;
        color: #334155 !important;
        cursor: pointer !important;
        transition: all 0.16s ease !important;
    }
    [data-testid="stTabs"] [data-testid="stTab"] > :not(:first-child),
    [data-testid="stTabs"] [role="tab"] > :not(:first-child),
    [data-baseweb="tab-highlight"],
    [data-baseweb="tab-border"] {
        display: none !important;
        height: 0 !important;
    }
    [data-testid="stTabs"] [data-testid="stTab"] p,
    [data-testid="stTabs"] [role="tab"] p {
        font-size: 1.02rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        color: inherit !important;
        margin: 0 !important;
    }
    [data-testid="stTabs"] [data-testid="stTab"]:hover,
    [data-testid="stTabs"] [role="tab"]:hover {
        background: #ffffff !important;
        border-color: #137fec !important;
        color: #137fec !important;
    }
    [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"],
    [data-testid="stTabs"] [data-testid="stTab"][data-selected="true"],
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #137fec 0%, #0b5ed7 100%) !important;
        border-color: #0b5ed7 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(19, 127, 236, 0.32) !important;
    }
    [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p,
    [data-testid="stTabs"] [data-testid="stTab"][data-selected="true"] p,
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] p {
        color: #ffffff !important;
    }

    /* ── 2단계 하위 세부 탭 (1. 부재 별 검토 | 2. 전체 보 일괄 구조검토표 | 3. 구조검토 근거 — 독립 알약 버튼형) ── */
    [data-testid="stTabPanel"] [data-testid="stTabs"] [role="tablist"],
    [data-baseweb="tab-panel"] [data-baseweb="tab-list"] {
        width: 100% !important;
        gap: 12px !important;
        background: #ffffff !important;
        padding: 8px 10px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.95rem !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
    }
    [data-testid="stTabPanel"] [data-testid="stTabs"] [data-testid="stTab"],
    [data-testid="stTabPanel"] [data-testid="stTabs"] [role="tab"] {
        flex: 0 1 auto !important;
        min-height: 36px !important;
        padding: 0.45rem 1.15rem !important;
        border-radius: 9px !important;
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        color: #475569 !important;
        box-shadow: none !important;
    }
    [data-testid="stTabPanel"] [data-testid="stTabs"] [data-testid="stTab"] p,
    [data-testid="stTabPanel"] [data-testid="stTabs"] [role="tab"] p {
        font-size: 0.86rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stTabPanel"] [data-testid="stTabs"] [data-testid="stTab"]:hover,
    [data-testid="stTabPanel"] [data-testid="stTabs"] [role="tab"]:hover {
        background: #f1f5f9 !important;
        border-color: #93c5fd !important;
        color: #137fec !important;
    }
    [data-testid="stTabPanel"] [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"],
    [data-testid="stTabPanel"] [data-testid="stTabs"] [data-testid="stTab"][data-selected="true"],
    [data-testid="stTabPanel"] [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: #eff6ff !important;
        border: 1.5px solid #137fec !important;
        color: #137fec !important;
        box-shadow: 0 2px 6px rgba(19, 127, 236, 0.12) !important;
    }
    [data-testid="stTabPanel"] [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p,
    [data-testid="stTabPanel"] [data-testid="stTabs"] [data-testid="stTab"][data-selected="true"] p,
    [data-testid="stTabPanel"] [data-testid="stTabs"] [role="tab"][aria-selected="true"] p {
        color: #137fec !important;
        font-weight: 800 !important;
    }

    /* KPI 카드 (역기획: Step 2 내진 카드 & Step 5 산출결과 카드 스타일) */
    .dw-kpi-card {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        margin-bottom: 0.75rem;
    }
    .dw-kpi-top {
        padding: 1.1rem 1.2rem 0.9rem 1.2rem;
    }
    .dw-kpi-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: -0.01em;
        margin-bottom: 0.35rem;
    }
    .dw-kpi-val {
        font-size: 1.75rem;
        font-weight: 900;
        color: #111418;
        letter-spacing: -0.03em;
        line-height: 1.15;
    }
    .dw-kpi-foot {
        background: #f8fafc;
        border-top: 1px solid #f1f5f9;
        padding: 0.6rem 1.2rem;
        font-size: 0.76rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* 같은 행의 .status-card 및 .dw-kpi-card 좌우 높이 자동 통일 */
    [data-testid="stHorizontalBlock"]:has(.status-card),
    [data-testid="stHorizontalBlock"]:has(.dw-kpi-card) {
        align-items: stretch !important;
    }
    [data-testid="stHorizontalBlock"]:has(.status-card) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.status-card) [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"]:has(.status-card) [data-testid="stElementContainer"],
    [data-testid="stHorizontalBlock"]:has(.status-card) [data-testid="stMarkdownContainer"],
    [data-testid="stHorizontalBlock"]:has(.dw-kpi-card) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.dw-kpi-card) [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"]:has(.dw-kpi-card) [data-testid="stElementContainer"],
    [data-testid="stHorizontalBlock"]:has(.dw-kpi-card) [data-testid="stMarkdownContainer"] {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* 상세 구조검토 카드 (.status-card 역기획 업그레이드) */
    .status-card {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 0.9rem;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .status-card h4 {
        margin: 0;
        padding: 0.9rem 1.35rem;
        background: rgba(248, 250, 252, 0.8);
        border-bottom: 1px solid #f1f5f9;
        font-size: 1rem;
        font-weight: 800;
        color: #1e293b;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .status-card ul {
        list-style: none;
        margin: 0;
        padding: 0.5rem 1.35rem 0.85rem 1.35rem;
        flex: 1;
    }
    .status-card li {
        padding: 0.55rem 0;
        border-bottom: 1px dashed #f1f5f9;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.55;
    }
    .status-card li:last-child {
        border-bottom: none;
    }
    .badge-ok {
        background-color: #dbeafe;
        color: #1d4ed8;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-ng {
        background-color: #fee2e2;
        color: #dc2626;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-warn {
        background-color: #fef3c7;
        color: #b45309;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }

    /* 최종 판정 배너 (역기획: Step 4 Final Conclusion 박스 스타일) */
    .dw-conclusion-ok {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 1.15rem 1.5rem;
        margin: 0.75rem 0 1.1rem 0;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    .dw-conclusion-ng {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 12px;
        padding: 1.15rem 1.5rem;
        margin: 0.75rem 0 1.1rem 0;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    .dw-decision-pill-ok {
        padding: 0.65rem 1.5rem;
        border-radius: 12px;
        background: #137fec;
        color: #ffffff;
        font-weight: 900;
        font-size: 1rem;
        box-shadow: 0 4px 10px rgba(19, 127, 236, 0.25);
        white-space: nowrap;
    }
    .dw-decision-pill-ng {
        padding: 0.65rem 1.5rem;
        border-radius: 12px;
        background: #dc2626;
        color: #ffffff;
        font-weight: 900;
        font-size: 1rem;
        box-shadow: 0 4px 10px rgba(220, 38, 38, 0.25);
        white-space: nowrap;
    }

    /* Expander 아코디언 카드 디자인 (내장 텍스트 아이콘 겹침 원천 차단 및 깔끔한 화살표 적용) */
    div[data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        overflow: hidden !important;
    }
    div[data-testid="stExpander"] summary {
        background: #f8fafc !important;
        padding: 0.75rem 1.1rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    div[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
        display: none !important;
    }
    div[data-testid="stExpander"] details > summary::before {
        content: "▶";
        font-size: 0.75rem;
        color: #137fec;
        margin-right: 6px;
        transition: transform 0.15s ease;
        display: inline-block;
    }
    div[data-testid="stExpander"] details[open] > summary::before {
        content: "▼";
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 0. 공용 접근 코드 인증 게이트 (공용코드: 2788 / 정밀검토 관리자코드: ekaekd)
# =====================================================
ACCESS_CODE = os.environ.get("APP_ACCESS_CODE", "2788")
ADMIN_PRECISION_CODE = os.environ.get("ADMIN_PRECISION_CODE", "ekaekd")

if not st.session_state.get("authenticated", False):
    st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
        .block-container {
            max-width: 460px !important;
            padding-top: 6rem !important;
        }
        .dw-auth-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 2rem 1.85rem 1.4rem 1.85rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
            text-align: center;
            margin-bottom: 1rem;
        }
        .dw-auth-brand {
            font-size: 1.75rem;
            font-weight: 900;
            color: #137fec;
            letter-spacing: -0.05em;
            font-style: italic;
            margin-bottom: 0.35rem;
        }
        .dw-auth-title {
            font-size: 1.12rem;
            font-weight: 800;
            color: #111418;
            margin-bottom: 0.35rem;
        }
        .dw-auth-sub {
            font-size: 0.82rem;
            color: #617589;
            margin-bottom: 0.9rem;
            line-height: 1.45;
        }
        .dw-auth-badge {
            display: inline-block;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            border-radius: 999px;
            padding: 0.22rem 0.75rem;
            font-size: 0.74rem;
            font-weight: 700;
        }
    </style>
    <div class="dw-auth-card">
        <div class="dw-auth-brand">DAEWOO E&C</div>
        <div class="dw-auth-title">RC 보 이어치기 구조검토 시스템</div>
        <div class="dw-auth-sub">CAD(DXF) 보 일람표 · KDS 수직이어치기 검토<br/>접속을 위해 사내 공용 접근 코드를 입력해 주세요.</div>
        <span class="dw-auth-badge">🔒 사내 공용 접근 인증</span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("dw_access_code_form", clear_on_submit=False):
        input_code = st.text_input(
            "공용 접근 코드",
            type="password",
            placeholder="접근 코드 입력 후 Enter 또는 접속하기 클릭",
            max_chars=20,
        )
        submitted = st.form_submit_button("🔓 시스템 접속하기", type="primary", use_container_width=True)
        if submitted:
            if input_code.strip() == ACCESS_CODE:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("접근 코드가 일치하지 않습니다. 공용 접근 코드를 다시 확인해 주세요.")

    st.markdown(
        '<div style="text-align:center; font-size:11.5px; color:#94a3b8; margin-top:1.25rem; font-weight:600;">'
        '© (주)대우건설 건축기술팀 · 사내 기술지원 표준화 시스템'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# =====================================================
# 1. DXF 캐드 도면 분석 엔진 (요청하신 함수 원형 유지)
# =====================================================
def parse_dxf_table(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    
    data = []
    v_lines = []     # 표의 '수직선(벽)' 좌표를 담을 리스트
    h_lines = []     # 표의 '수평선(행 경계)' 좌표를 담을 리스트
    cell_boxes = []  # 일람표 개별 보 셀 외곽 LWPOLYLINE 박스
    cad_segs = []    # 원본 도면 근거 화면 렌더링용 선분 (x1, y1, x2, y2, kind)
    cad_circles = [] # 원본 도면 단면 내 철근 원(CIRCLE) 객체 (cx, cy, r)
    
    def process_entity(e):
        # AutoCAD 동적 블록(Dynamic Block)의 숨겨진 가시성 상태(invisible=1) 객체 제외
        if getattr(e.dxf, 'invisible', 0):
            return
        t = e.dxftype()
        if t == 'INSERT':
            try:
                bname_up = (e.dxf.name if e.dxf.hasattr('name') else '').upper()
                if 'BARDOT' in bname_up:
                    cad_circles.append((float(e.dxf.insert.x), float(e.dxf.insert.y), 18.0))
                else:
                    for sub_e in e.virtual_entities():
                        if getattr(sub_e.dxf, 'invisible', 0):
                            continue
                        sub_t = sub_e.dxftype()
                        if sub_t != 'INSERT': 
                            process_entity(sub_e)
                        else:
                            sub_bname = (sub_e.dxf.name if sub_e.dxf.hasattr('name') else '').upper()
                            if 'BARDOT' in sub_bname:
                                cad_circles.append((float(sub_e.dxf.insert.x), float(sub_e.dxf.insert.y), 18.0))
            except Exception:
                pass
        elif t == 'CIRCLE':
            try:
                cx_c, cy_c = float(e.dxf.center.x), float(e.dxf.center.y)
                r_c = float(e.dxf.radius)
                if 2.0 <= r_c <= 80.0:
                    cad_circles.append((cx_c, cy_c, r_c))
            except Exception:
                pass
            
        elif t in ('TEXT', 'MTEXT'):
            raw_txt = e.dxf.text if e.dxf.hasattr('text') else ''
            val = raw_txt.replace('\\P', ' ').replace('\n', ' ').strip()
            # AutoCAD MTEXT 서식 코드({\f...;...}, \A1; 등) 정리
            val = re.sub(r'\\A\d+;', '', val)
            val = re.sub(r'\{\\[^;]+;([^}]*)\}', r'\1', val).strip()
            if val:
                data.append({'text': val, 'x': float(e.dxf.insert.x), 'y': float(e.dxf.insert.y), 'kind': 'TEXT', 'orient': 'TEXT'})
            
        elif t == 'DIMENSION':
            try:
                val = str(int(round(e.dxf.actual_measurement)))
                x = float(e.dxf.text_midpoint.x if e.dxf.hasattr('text_midpoint') else e.dxf.defpoint.x)
                y = float(e.dxf.text_midpoint.y if e.dxf.hasattr('text_midpoint') else e.dxf.defpoint.y)
                dim_orient = 'UNKNOWN'
                for de in e.virtual_entities():
                    if de.dxftype() == 'LINE':
                        dx1, dy1 = float(de.dxf.start.x), float(de.dxf.start.y)
                        dx2, dy2 = float(de.dxf.end.x), float(de.dxf.end.y)
                        dlen = math.hypot(dx2 - dx1, dy2 - dy1)
                        if dlen > 25:
                            cad_segs.append((dx1, dy1, dx2, dy2, 'DIM'))
                        if dlen > 300:
                            if abs(dy1 - dy2) < 10 and abs(dx2 - dx1) > 300:
                                dim_orient = 'H'
                            elif abs(dx1 - dx2) < 10 and abs(dy2 - dy1) > 300 and dim_orient == 'UNKNOWN':
                                dim_orient = 'V'
                if val:
                    data.append({'text': val, 'x': x, 'y': y, 'kind': 'DIM', 'orient': dim_orient})
            except Exception:
                pass
            
        # [핵심 기술] 표를 구성하는 물리적 '수직선' 및 '수평선' 추출 (오차 50 허용)
        elif t == 'LINE':
            x1, y1 = float(e.dxf.start.x), float(e.dxf.start.y)
            x2, y2 = float(e.dxf.end.x), float(e.dxf.end.y)
            seg_len = math.hypot(x2 - x1, y2 - y1)
            if seg_len > 25:
                cad_segs.append((x1, y1, x2, y2, 'LINE'))
            if abs(x1 - x2) < 50: 
                v_lines.append({'x': (x1+x2)/2, 'y_min': min(y1, y2), 'y_max': max(y1, y2), 'len': abs(y2 - y1)})
            if abs(y1 - y2) < 50:
                h_lines.append({'y': (y1+y2)/2, 'x_min': min(x1, x2), 'x_max': max(x1, x2), 'len': abs(x2 - x1)})
                
        elif t == 'LWPOLYLINE':
            try:
                pts_full = list(e.get_points('xyseb'))
                pts = [(float(p[0]), float(p[1])) for p in pts_full]
                # AutoCAD DONUT 철근 점(2점 폐합 반원 폴리선, bulge≈±1.0) 자동 추출
                if len(pts) == 2 and any(abs(float(p[4])) > 0.5 for p in pts_full):
                    d_poly = math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
                    if 4.0 <= d_poly <= 90.0:
                        cad_circles.append(((pts[0][0] + pts[1][0]) / 2.0, (pts[0][1] + pts[1][1]) / 2.0, d_poly / 2.0))
                if len(pts) >= 2:
                    # 닫힌 폴리선(closed=True)의 마지막-첫번째 폐합 선분(좌측 수직벽 등) 누락 방지
                    pts_loop = pts + [pts[0]] if (e.closed and len(pts) >= 3) else pts
                    for idx in range(len(pts_loop) - 1):
                        x1, y1 = pts_loop[idx]
                        x2, y2 = pts_loop[idx + 1]
                        if math.hypot(x2 - x1, y2 - y1) > 25:
                            cad_segs.append((x1, y1, x2, y2, 'POLY'))
                        if abs(x1 - x2) < 50:
                            v_lines.append({'x': (x1+x2)/2, 'y_min': min(y1, y2), 'y_max': max(y1, y2), 'len': abs(y2 - y1)})
                        if abs(y1 - y2) < 50:
                            h_lines.append({'y': (y1+y2)/2, 'x_min': min(x1, x2), 'x_max': max(x1, x2), 'len': abs(x2 - x1)})
                if len(pts) >= 4:
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    w, h = max(xs) - min(xs), max(ys) - min(ys)
                    if 2000 <= w <= 12000 and 2500 <= h <= 6500:
                        cell_boxes.append({'x_min': min(xs), 'x_max': max(xs), 'y_min': min(ys), 'y_max': max(ys)})
            except Exception:
                pass

    for entity in msp:
        process_entity(entity)

    # CAD 도면 내 동일 좌표에 중복 복사된 텍스트/치수 객체 중복 제거
    dedup_data = []
    seen_items = set()
    for d in data:
        key = (round(d['x'], 0), round(d['y'], 0), d['text'], d['kind'])
        if key not in seen_items:
            seen_items.add(key)
            dedup_data.append(d)
    df = pd.DataFrame(dedup_data)
    if df.empty:
        return {}, df
    
    # [다중 설계사 범용 패턴]
    # 1) 보 부호 패턴: 일반보(G, B, RG, RB), 층접두+지붕/램프보(-1RG12C, -1RWG1 등), 전이보(TG, 1TG, TB), 기초/지중보(FG, FB, MG, MB), 벽보/헌치보(WG, WB, HG, HB, CG, CB, SG, SB, RaG, RaB, RaWG), 콤마 병기('RWG1, -1RWG1') 및 '*' 접미사 모두 인식
    #    (단, 기둥 부호 C1, TC1, PC1 및 프로젝트 코드 C19052A 등은 제외)
    _single_beam_pat = (
        r'(?:(?:-?\d+(?:~-?\d+)?|[B]?\d+F|RF|R|PH\d*)\s*)?'
        r'(?:\d+)?(?:RaWG|RaWB|RWG|RWB|RHG|RHB|RTG|RTB|RG|RB|TG|TB|RaG|RaB|WG|WB|FG|FB|MG|MB|CG|CB|SG|SB|HG|HB|PG|PB|G|B)\d+[A-Z]*(?:-\d+)?\*?(?:\s*\([^)]+\))?'
    )
    beam_token_re = re.compile(
        rf'^{_single_beam_pat}(?:\s*,\s*{_single_beam_pat})*$',
        re.IGNORECASE
    )
    # 2) 단면 위치(영문/한글 모든 설계사 표기 지원): END(INT.), END(EXT.), END, CENTER, BOTH, ALL, 전단면, 전구간, 양단, 단부, 중앙, 좌단, 우단, 내단, 외단 등
    section_pattern = re.compile(
        r'^\s*(END\s*\([^)]+\)|END|CENTER|CEN|MID|BOTH|ALL|EXT\.?|INT\.?|전단면|전구간|양단부?|단부|중앙부?|중간부?|좌단부?|우단부?|외단부?|내단부?)',
        re.IGNORECASE
    )
    sub_sec_pattern = re.compile(r'(연속|불연속|내부|외부|CONT\.?|DISCONT\.?|EXT\.?|INT\.?)', re.IGNORECASE)
    # 3) 스터럽/늑근 패턴: 5-D13@100, 2-HD10@150, D10@200 등 (하이픈/엔대시 및 HD/SD/UHD/SHD 모두 인식)
    stirrup_pattern = re.compile(r'(?:(\d+)\s*[-–~]\s*)?[A-Z]*D(\d+)\s*@\s*(\d+)', re.IGNORECASE)
    # 4) 주근 패턴: 9-D22, 9-HD22, 6+4-D22(2단 배근 합산 표기) 모두 인식
    main_pattern = re.compile(r'(?:(\d+)\s*\+\s*(\d+)|(\d+))\s*[-–~]\s*[A-Z]*D(\d+)(?!\s*@)', re.IGNORECASE)
    # 5) 치수 패턴: 900, 1,900(콤마 포함), (400x600), 900x1900, 900×1,900 모두 인식
    combined_size_pattern = re.compile(r'\(?\s*(\d{3,4})\s*[×xX*]\s*(\d{1},?\d{3}|\d{3,4})\s*\)?')
    size_pattern = re.compile(r'^(\d{1},?\d{3}|\d{3,4})$')

    # 좌측 항목명 헤더 열(부호 / NAME / 형태 / 상부근 / 하부근 / 늑근 / SKIN BAR / TOP BAR / BOT BAR / STIRRUP) 인식 정규식
    lbl_header_re = re.compile(r'^부\s*호|^NAME$|MARK|MEMBER', re.IGNORECASE)
    lbl_top_re = re.compile(r'상\s*부\s*근|상\s*단\s*근|상\s*부\s*철\s*근|TOP\s*BAR|^TOP$', re.IGNORECASE)
    lbl_bot_re = re.compile(r'하\s*부\s*근|하\s*단\s*근|하\s*부\s*철\s*근|BOT(?:TOM)?\s*BAR|^BOT$', re.IGNORECASE)
    lbl_st_re = re.compile(r'늑\s*근|스터럽|스트럽|스타럽|STIRRUP|전\s*단\s*철\s*근|띠\s*철\s*근', re.IGNORECASE)
    lbl_skin_re = re.compile(r'SKIN\s*BAR|SKIN|보\s*조\s*근|복\s*부\s*근|복\s*부\s*철\s*근|측\s*면\s*근|SIDE\s*BAR|WEB\s*BAR', re.IGNORECASE)
    
    text_df = df[df['kind'] == 'TEXT']
    beam_headers_raw = []
    for _, row in text_df.iterrows():
        text = row['text'].strip()
        if len(text) <= 24 and beam_token_re.match(text):
            beam_headers_raw.append({'name': text, 'x': float(row['x']), 'y': float(row['y'])})
            
    beam_headers_raw = sorted(beam_headers_raw, key=lambda h: (-round(h['y'] / 500) * 500, h['x']))
    beam_data = {}
    
    for b_header in beam_headers_raw:
        bx, by = b_header['x'], b_header['y']
        is_left_header_layout = False
        label_col_x0 = None
        
        # 1. 해당 보 부호가 속한 셀 외곽 경계(start_x, end_x, bottom_y, top_y) 탐색
        #    - 유형 A: LWPOLYLINE 개별 박스형 (예: S50-101~115)
        #    - 유형 B: 상단 헤더 + LINE 연속 격자형 (예: S33-001 전이보 일람표)
        #    - 유형 C: 좌측 열에 부재명(G2A, G3A)과 단면치수((400x600))가 표시되고 우측에 END(INT.)/CENTER/END(EXT.)가 배치된 형태 (예: 31BL 일람표)
        matching_boxes = [
            b for b in cell_boxes
            if b['x_min'] - 50 <= bx <= b['x_max'] + 50 and b['y_max'] - 600 <= by <= b['y_max'] + 100
        ]
        if matching_boxes:
            cbox = matching_boxes[0]
            start_x, end_x = cbox['x_min'], cbox['x_max']
            bottom_y, top_y = cbox['y_min'], cbox['y_max']
        else:
            valid_v = [vl['x'] for vl in v_lines if vl['len'] >= 1000 and vl['y_min'] - 150 <= by <= vl['y_max'] + 150]
            left_v = [x for x in valid_v if x < bx - 20]
            right_v = [x for x in valid_v if x > bx + 20]
            v_l = max(left_v) if left_v else bx - 2000.0
            v_r = min(right_v) if right_v else bx + 2000.0

            # [유형 C 감지] 보 부호(G2A, G3A 등)가 폭 250~1450 이하의 좌측 좁은 헤더 열 안에 위치한 경우!
            if 250 <= (v_r - v_l) <= 1450:
                col_below_texts = text_df[
                    (text_df['x'] >= v_l - 30) & (text_df['x'] <= v_r + 30) &
                    (text_df['y'] < by - 30) & (text_df['y'] >= by - 2200)
                ]['text'].tolist()
                has_left_col_indicators = any(
                    combined_size_pattern.search(t) or lbl_top_re.search(t) or lbl_st_re.search(t) or '주철근' in t
                    for t in col_below_texts
                )
                if has_left_col_indicators:
                    is_left_header_layout = True
                    label_col_x0 = v_l
                    start_x = v_r  # 실제 단면/배근 컬럼(END/CENTER)은 좌측 라벨 열 우측 경계(v_r)부터 시작!
                    # 동일 테이블 내 우측 인접 보 부호 탐색 (다른 도면 시트/타이틀블록 너머는 제외하도록 6800 이내로 제한)
                    same_row_right_bh = [
                        h['x'] for h in beam_headers_raw
                        if v_r + 300 < h['x'] <= start_x + 6800.0 and abs(h['y'] - by) < 200
                    ]
                    spanning_h = [
                        hl['x_max'] for hl in h_lines
                        if hl['len'] >= 2000 and hl['x_min'] <= start_x + 100
                        and (start_x + 1200.0 < hl['x_max'] <= start_x + 6600.0)
                        and abs(hl['y'] - by) < 500
                    ]
                    if same_row_right_bh:
                        next_bx = min(same_row_right_bh)
                        next_left_walls = [x for x in valid_v if start_x + 500 < x < next_bx - 20]
                        end_x = max(next_left_walls) if next_left_walls else next_bx - 200.0
                    elif spanning_h:
                        end_x = max(spanning_h)
                    else:
                        right_walls = [x for x in valid_v if start_x + 800 < x <= start_x + 6500.0]
                        end_x = max(right_walls) if right_walls else start_x + 5400.0
                else:
                    start_x, end_x = v_l, v_r
            else:
                start_x, end_x = v_l, v_r

            cell_cx = (start_x + end_x) / 2
            valid_h = sorted(list(set(
                round(hl['y'], 1)
                for hl in h_lines
                if hl['len'] >= (end_x - start_x) * 0.5
                and hl['x_min'] - 300 <= cell_cx <= hl['x_max'] + 300
            )), reverse=True)

            top_candidates = [y for y in valid_h if y > by and (y - by) < 900]
            top_y = min(top_candidates) if top_candidates else by + 150.0

            below_h = [y for y in valid_h if y < by and (by - y) < 8500]
            bottom_y = by - (1500.0 if is_left_header_layout else 3850.0)
            min_sec_zone_h = 650.0 if is_left_header_layout else 1100.0
            if below_h:
                passed_section_zone = False
                curr_y = top_y
                for hy in below_h:
                    step_h = curr_y - hy
                    if step_h >= min_sec_zone_h:
                        if not passed_section_zone:
                            passed_section_zone = True
                            curr_y = hy
                            bottom_y = hy
                        else:
                            break
                    else:
                        if passed_section_zone:
                            chk_x0 = (label_col_x0 - 50) if label_col_x0 is not None else (start_x - 2500)
                            strip_texts = text_df[
                                (text_df['y'] < curr_y - 10) & (text_df['y'] > hy + 10) &
                                (text_df['x'] >= chk_x0) & (text_df['x'] <= end_x)
                            ]
                            if strip_texts.empty:
                                # 일람표 최하단 행 아래의 빈 여백/도면 외곽선 영역으로 내려가는 것 방지
                                break
                            has_next_header = any(
                                lbl_header_re.search(t) or beam_token_re.match(t.strip())
                                for t in strip_texts['text']
                            )
                            if has_next_header:
                                break
                            curr_y = hy
                            bottom_y = hy
                            if any('COMMENT' in t.upper() or '비고' in t for t in strip_texts['text']):
                                # COMMENT(비고) 행 하단 경계선에 도달하면 셀 종료
                                break
                        else:
                            curr_y = hy

        # 같은 부호 칸(같은 Y선상) 우측에 '(201동)' 등 분리된 동/구간 텍스트가 있으면 부재명에 결합
        header_companions = text_df[
            (text_df['x'] > bx + 10) & (text_df['x'] <= (start_x if is_left_header_layout else end_x - 20)) &
            (abs(text_df['y'] - by) < 80)
        ].sort_values(by='x')
        full_header_str = b_header['name'].strip()
        for _, hc in header_companions.iterrows():
            hc_txt = hc['text'].strip()
            if hc_txt.startswith('(') and hc_txt.endswith(')'):
                full_header_str = f"{full_header_str} {hc_txt}"

        base_beam_name = " ".join(full_header_str.split()).upper()
        beam_name = base_beam_name
        if beam_name in beam_data:
            dup_idx = 2
            while f"{beam_name} (#{dup_idx})" in beam_data:
                dup_idx += 1
            beam_name = f"{beam_name} (#{dup_idx})"
            
        beam_df = df[
            (df['x'] >= start_x - 10) & (df['x'] <= end_x + 10) &
            (df['y'] >= bottom_y - 10) & (df['y'] <= top_y + 10)
        ]

        # 좌측 항목 헤더 열(부호 / G2A / (400x600) / 상부근 / 하부근 / 늑근 / SKIN BAR / TOP BAR / BOT BAR / STIRRUP) 텍스트 추출
        left_search_x0 = (label_col_x0 - 100) if label_col_x0 is not None else (start_x - 2200)
        left_label_df = text_df[
            (text_df['x'] >= left_search_x0) & (text_df['x'] < start_x - 10) &
            (text_df['y'] >= bottom_y - 20) & (text_df['y'] <= top_y + 20)
        ]
        _row_lbl_kw_re = re.compile(
            r'부\s*호|NAME|MARK|단\s*면|형\s*태|크\s*기|상\s*부|하\s*부|주\s*근|늑\s*근|스터럽|전\s*단|SKIN|복\s*부|표\s*피|보\s*조|비\s*고|TOP|BOT|STIRRUP|COMMENT|SIZE',
            re.IGNORECASE
        )
        left_row_labels = [
            {'text': r['text'], 'x': float(r['x']), 'y': float(r['y']), 'dy': round(float(r['y'] - bottom_y), 1)}
            for _, r in left_label_df.iterrows()
            if is_left_header_layout or _row_lbl_kw_re.search(r['text'])
        ]

        # 좌측 헤더 열에 '(400x600)' 등 공통 단면 치수가 표기된 경우 추출
        shared_left_size = None
        for lbl in left_row_labels:
            clean_lbl = lbl['text'].replace(',', '').strip()
            cm_left = combined_size_pattern.search(clean_lbl)
            if cm_left and 'D' not in clean_lbl.upper() and '@' not in clean_lbl:
                w_val, h_val = int(cm_left.group(1)), int(cm_left.group(2))
                if 150 <= w_val <= 3500 and 150 <= h_val <= 3500:
                    shared_left_size = {
                        'bw': w_val, 'depth': h_val,
                        'x': lbl['x'], 'y': lbl['y'], 'dy': lbl['dy'],
                        'text': lbl['text'], 'kind': 'TEXT (좌측열)'
                    }
                    break

        # 셀 내 수평 행 구분선(dy) 추출 (원본 뷰어 및 행 구분용)
        cell_cx = (start_x + end_x) / 2
        cell_h_lines_dy = sorted(list(set(
            round(float(hl['y'] - bottom_y), 1)
            for hl in h_lines
            if hl['len'] >= (end_x - start_x) * 0.45
            and hl['x_min'] - 250 <= cell_cx <= hl['x_max'] + 250
            and bottom_y + 30 < hl['y'] < top_y - 30
        )), reverse=True)
        
        # 2. 단면 구간 헤더(END(INT.), CENTER, END(EXT.), BOTH, ALL, 전단면, 양단, 단부, 중앙부 등) 탐색
        #    (좌측 부재명 표기형은 END(INT.)가 부재명 by와 같은 높이에 위치하므로 top_y + 20까지 탐색 허용)
        sec_hdr_upper_y = (top_y + 20) if is_left_header_layout else (by - 60)
        sec_hdr_candidates = []
        for _, r in beam_df[beam_df['kind'] == 'TEXT'].iterrows():
            ry = float(r['y'])
            rtxt = r['text'].strip()
            if bottom_y + (top_y - bottom_y) * 0.45 <= ry <= sec_hdr_upper_y:
                if section_pattern.search(rtxt):
                    sec_hdr_candidates.append({'text': rtxt, 'x': float(r['x']), 'y': ry})
        sec_hdr_candidates = sorted(sec_hdr_candidates, key=lambda item: item['x'])

        sec_cols = []
        for cand in sec_hdr_candidates:
            if not sec_cols or abs(cand['x'] - sec_cols[-1]['x']) > 450:
                sec_cols.append(cand)

        # 구간 헤더가 1개 이하이면 단일 컬럼 유지, 2개 이상이면 인접 헤더 사이의 테이블 수직 구분선으로 분할
        inner_dividers = []
        min_v_div_len = max((top_y - bottom_y) * 0.5, 700.0)
        if len(sec_cols) >= 2:
            for j in range(len(sec_cols) - 1):
                lx, rx = sec_cols[j]['x'], sec_cols[j + 1]['x']
                cand_v = [
                    vl for vl in v_lines
                    if lx + 120 < vl['x'] <= rx - 10
                    and (min(vl['y_max'], top_y + 50) - max(vl['y_min'], bottom_y - 50)) >= min_v_div_len
                ]
                if cand_v:
                    best_v = max(
                        cand_v,
                        key=lambda item: (min(item['y_max'], top_y + 50) - max(item['y_min'], bottom_y - 50))
                    )
                    inner_dividers.append(round(best_v['x'], 1))
                else:
                    inner_dividers.append(round((lx + rx) / 2, 1))
        # 좌측 헤더형(3열 고정 격자 등)에서 BOTH+CENTER 또는 ALL만 기입되고 우측 열이 빈칸인 경우, 빈칸 경계 수직선도 반영하여 하이라이트 폭을 실제 컬럼 폭에 맞춤
        if is_left_header_layout and sec_cols:
            last_hdr_x = sec_cols[-1]['x']
            trailing_v = sorted(list(set(
                round(vl['x'], 1)
                for vl in v_lines
                if last_hdr_x + 700.0 < vl['x'] < end_x - 700.0
                and (min(vl['y_max'], top_y + 30) - max(vl['y_min'], bottom_y - 30)) >= (top_y - bottom_y) * 0.85
            )))
            for tv in trailing_v:
                if not inner_dividers or all(abs(tv - iv) > 400.0 for iv in inner_dividers):
                    inner_dividers.append(tv)
            inner_dividers = sorted(inner_dividers)
        col_bounds = [start_x] + inner_dividers + [end_x]
        inner_dividers_dx = [round(x - start_x, 1) for x in inner_dividers]

        # 원본 CAD 도면 근거 뷰어용 선분, 철근 원(CIRCLE), 텍스트 추출 (셀 내부 상대좌표 dx, dy)
        cell_cad_circles = []
        seen_circles = set()
        for cx_c, cy_c, r_c in cad_circles:
            if start_x <= cx_c <= end_x and bottom_y <= cy_c <= top_y:
                ckey = (round(cx_c - start_x, 0), round(cy_c - bottom_y, 0))
                if ckey not in seen_circles:
                    seen_circles.add(ckey)
                    cell_cad_circles.append((round(cx_c - start_x, 1), round(cy_c - bottom_y, 1), round(r_c, 1)))

        cell_cad_lines = []
        seen_segs = set()
        for x1, y1, x2, y2, skind in cad_segs:
            if abs(y1 - y2) < 20 and bottom_y - 30 <= (y1 + y2) / 2 <= top_y + 30:
                seg_xmin, seg_xmax = min(x1, x2), max(x1, x2)
                if seg_xmax >= start_x + 20 and seg_xmin <= end_x - 20:
                    cx1 = max(seg_xmin, start_x)
                    cx2 = min(seg_xmax, end_x)
                    if cx2 - cx1 > 25:
                        skey = (round(cx1 - start_x, 0), round(y1 - bottom_y, 0), round(cx2 - start_x, 0), round(y2 - bottom_y, 0))
                        if skey not in seen_segs:
                            seen_segs.add(skey)
                            cell_cad_lines.append((round(cx1 - start_x, 1), round(y1 - bottom_y, 1), round(cx2 - start_x, 1), round(y2 - bottom_y, 1), skind))
                continue
            if abs(x1 - x2) < 20 and start_x - 30 <= (x1 + x2) / 2 <= end_x + 30:
                seg_ymin, seg_ymax = min(y1, y2), max(y1, y2)
                if seg_ymax >= bottom_y + 20 and seg_ymin <= top_y - 20:
                    cy1 = max(seg_ymin, bottom_y)
                    cy2 = min(seg_ymax, top_y)
                    if cy2 - cy1 > 25:
                        skey = (round(x1 - start_x, 0), round(cy1 - bottom_y, 0), round(x2 - start_x, 0), round(cy2 - bottom_y, 0))
                        if skey not in seen_segs:
                            seen_segs.add(skey)
                            cell_cad_lines.append((round(x1 - start_x, 1), round(cy1 - bottom_y, 1), round(x2 - start_x, 1), round(cy2 - bottom_y, 1), skind))
                continue
            if (start_x - 30 <= min(x1, x2) and max(x1, x2) <= end_x + 30 and
                bottom_y - 30 <= min(y1, y2) and max(y1, y2) <= top_y + 30):
                skey = (round(x1 - start_x, 0), round(y1 - bottom_y, 0), round(x2 - start_x, 0), round(y2 - bottom_y, 0))
                if skey not in seen_segs:
                    seen_segs.add(skey)
                    cell_cad_lines.append((
                        round(x1 - start_x, 1), round(y1 - bottom_y, 1),
                        round(x2 - start_x, 1), round(y2 - bottom_y, 1),
                        skind
                    ))
        cell_cad_texts = [
            {
                'text': r['text'],
                'dx': round(float(r['x'] - start_x), 1),
                'dy': round(float(r['y'] - bottom_y), 1),
                'x': round(float(r['x']), 1),
                'y': round(float(r['y']), 1),
                'kind': r['kind'],
            }
            for _, r in beam_df.iterrows()
        ]
        
        sections_data = {}
        for col_idx in range(len(col_bounds) - 1):
            s_start_x = col_bounds[col_idx]
            s_end_x = col_bounds[col_idx + 1]
            sec_df = beam_df[(beam_df['x'] >= s_start_x - 5) & (beam_df['x'] < s_end_x + 5)].sort_values(by='y', ascending=False)
            
            # 구간 명칭(END(INT.), CENTER, END(EXT.), BOTH, ALL, 전단면 등) 및 부가 표기 인식
            s_name = "ALL"
            sub_label = ""
            for _, r in sec_df[sec_df['kind'] == 'TEXT'].iterrows():
                ry = float(r['y'])
                if bottom_y + (top_y - bottom_y) * 0.45 <= ry <= sec_hdr_upper_y:
                    m_sec = section_pattern.search(r['text'])
                    if m_sec and s_name == "ALL":
                        raw_sname = m_sec.group(1).upper().replace(' ', '')
                        if raw_sname in ('전단면', '전구간'):
                            s_name = 'ALL(전단면)'
                        elif raw_sname in ('양단', '양단부'):
                            s_name = 'BOTH(양단)'
                        elif raw_sname in ('중앙', '중앙부', '중간', '중간부', 'MID'):
                            s_name = 'CENTER'
                        elif raw_sname in ('단부', '좌단', '좌단부', '우단', '우단부', '외단', '외단부', '내단', '내단부'):
                            s_name = f"END({raw_sname})"
                        else:
                            s_name = raw_sname
                    m_sub = sub_sec_pattern.search(r['text'])
                    if m_sub and not sub_label:
                        sub_label = m_sub.group(1).upper()
            
            display_s_name = f"{s_name}({sub_label})" if (sub_label and sub_label not in s_name) else s_name
            unique_s_name = display_s_name
            if unique_s_name in sections_data:
                unique_s_name = f"{display_s_name}_{col_idx+1}"
                
            # 단면 치수(폭 bw, 춤 H) 추출:
            # 1) 셀 내 통합 치수 텍스트('900x1900', '(400x600)') 우선 인식
            # 2) 단면도 영역 내 수평 치수선(H)=폭(bw), 수직 치수선(V)=춤(H) 인식
            # 3) 좌측 헤더 열에 '(400x600)' 등 공통 치수가 표기된 경우(shared_left_size) 자동 적용!
            rebar_zone_top_y = bottom_y + (top_y - bottom_y) * 0.35
            sizes_found = []
            combined_found = None
            for _, r in sec_df.iterrows():
                ry = float(r['y'])
                clean_t = r['text'].replace(',', '').strip()
                cm = combined_size_pattern.search(clean_t)
                if cm and 'D' not in clean_t.upper() and '@' not in clean_t:
                    combined_found = (int(cm.group(1)), int(cm.group(2).replace(',', '')), r)
                    break
                if ry > rebar_zone_top_y and ry < sec_hdr_upper_y:
                    sm = size_pattern.search(clean_t)
                    if sm:
                        val = int(sm.group(1).replace(',', ''))
                        if val % 10 == 0 and 150 <= val <= 3500:
                            sizes_found.append({
                                'val': val, 'x': float(r['x']), 'y': ry,
                                'dy': round(ry - bottom_y, 0), 'text': r['text'],
                                'kind': r['kind'], 'orient': r.get('orient', 'UNKNOWN'),
                            })
                            
            if combined_found:
                bw, depth = combined_found[0], combined_found[1]
                bw_src = depth_src = {
                    'val': bw, 'x': float(combined_found[2]['x']), 'y': float(combined_found[2]['y']),
                    'dy': round(float(combined_found[2]['y']) - bottom_y, 0),
                    'text': combined_found[2]['text'], 'kind': combined_found[2]['kind']
                }
            elif len(sizes_found) >= 2:
                h_dims = [s for s in sizes_found if s['orient'] == 'H']
                v_dims = [s for s in sizes_found if s['orient'] == 'V']
                if h_dims and v_dims:
                    bw_src, depth_src = h_dims[0], v_dims[0]
                else:
                    sizes_sorted = sorted(sizes_found, key=lambda item: (-item['y'], -item['x']))
                    bw_src, depth_src = sizes_sorted[0], sizes_sorted[1]
                bw, depth = bw_src['val'], depth_src['val']
            elif shared_left_size is not None:
                bw, depth = shared_left_size['bw'], shared_left_size['depth']
                bw_src = depth_src = shared_left_size
            elif len(sizes_found) == 1:
                bw = depth = sizes_found[0]['val']
                bw_src = depth_src = sizes_found[0]
            else:
                bw, depth = 600, 600
                bw_src = depth_src = None
                
            # 배근 정보(상부근/TOP BAR, 하부근/BOT BAR, 늑근/STIRRUP, SKIN BAR/표피·복부철근) 추출
            top_bar_info = None
            bot_bar_info = None
            unassigned_main_bars = []
            st_legs, st_dia, st_spacing = 2, 10, 250
            st_src = None
            extra_bars = []

            # 하단 배근 기입 행(TOP/BOT/STIRRUP)과 상단 단면도 그림 영역을 가르는 수평 경계선(rebar_table_top_dy) 산정
            lower_h_lines = [d for d in cell_h_lines_dy if 20 < d < (top_y - bottom_y) * 0.65]
            rebar_table_top_dy = max(lower_h_lines) if len(lower_h_lines) >= 2 else None
            skin_bar_txt_re = re.compile(
                r'^\s*(?:[Xx×]\s*[:=\-–~]|SKIN|S\.?B\.?\s*[:=\-–~]|SIDE|WEB|표\s*피|복\s*부|측\s*면|보\s*조)',
                re.IGNORECASE
            )
            
            for _, r in sec_df[sec_df['kind'] == 'TEXT'].iterrows():
                txt = r['text'].strip()
                ry = float(r['y'])
                dy = ry - bottom_y
                if not is_left_header_layout and ry >= by - 60:
                    continue

                # 동일 Y선상(±90~120)의 좌측 항목명 라벨 확인
                matched_lbl = ""
                for lbl in left_row_labels:
                    if abs(lbl['y'] - ry) < 95:
                        matched_lbl += " " + lbl['text']

                if len(txt) > 14 and ('적용' in txt or '철근' in txt or '스터럽' in txt):
                    continue

                # [핵심] 단면도 근처의 'X : 42-D10', 'X-42-D10', '× : 22-D10', 'SKIN : ...', '대각근' 등은 표피철근(SKIN BAR)으로 분류 (상/하부 주근 오인식 방지)
                if skin_bar_txt_re.search(txt) or (('X' in txt.upper() or '×' in txt or '대각' in txt) and ('D' in txt.upper() or '@' in txt)):
                    if not re.search(r'^\(?\s*\d{3,4}\s*[xX×*]\s*\d{3,4}\s*\)?$', txt.replace(',', '').strip()):
                        extra_bars.append({'text': txt, 'x': round(float(r['x']), 1), 'y': round(ry, 1), 'dy': round(dy, 0), 'role': 'SKIN BAR(표피/복부철근)'})
                        continue
                
                st_match = stirrup_pattern.search(txt)
                if st_match and (lbl_st_re.search(matched_lbl) or dy < (top_y - bottom_y) * 0.52):
                    if st_src is None:
                        st_legs = int(st_match.group(1)) if st_match.group(1) else 2
                        st_dia = int(st_match.group(2))
                        st_spacing = int(st_match.group(3))
                        st_src = {'text': txt, 'x': round(float(r['x']), 1), 'y': round(ry, 1), 'dy': round(dy, 0)}
                    continue
                    
                main_match = main_pattern.search(txt)
                if main_match and dy < (top_y - bottom_y) * 0.55:
                    if main_match.group(1) and main_match.group(2):
                        l1_t, l2_t = int(main_match.group(1)), int(main_match.group(2))
                        b_cnt = l1_t + l2_t
                        t_layers = [l1_t, l2_t]
                    else:
                        b_cnt = int(main_match.group(3))
                        t_layers = None
                    b_dia = int(main_match.group(4))
                    b_item = {
                        'count': b_cnt,
                        'dia': b_dia,
                        'txt_layers': t_layers,
                        'text': txt,
                        'x': round(float(r['x']), 1),
                        'y': round(ry, 1),
                        'dy': round(dy, 0),
                    }
                    # 하단 배근표 상단 경계선(rebar_table_top_dy) 위쪽(단면 그림 영역)에 기입된 주근 형태 텍스트는 표피철근(SKIN BAR)으로 분류
                    is_above_rebar_table = (rebar_table_top_dy is not None and dy > rebar_table_top_dy + 15.0)
                    if lbl_skin_re.search(matched_lbl) or is_above_rebar_table:
                        extra_bars.append({**b_item, 'role': 'SKIN BAR(표피/복부철근)'})
                    elif lbl_top_re.search(matched_lbl) and top_bar_info is None:
                        top_bar_info = b_item
                    elif lbl_bot_re.search(matched_lbl) and bot_bar_info is None:
                        bot_bar_info = b_item
                    else:
                        unassigned_main_bars.append(b_item)
                        
            for ub in unassigned_main_bars:
                if top_bar_info is None:
                    top_bar_info = ub
                elif bot_bar_info is None:
                    bot_bar_info = ub
                else:
                    extra_bars.append({**ub, 'role': 'SKIN BAR(복부근)'})

            if bot_bar_info is None and top_bar_info is not None:
                bot_bar_info = top_bar_info
            if top_bar_info is None and bot_bar_info is not None:
                top_bar_info = bot_bar_info

            # 빈 컬럼 슬롯(예: 3열 격자에서 BOTH+CENTER만 사용되고 3번째 열이 공란인 경우) 또는 도면 밖 단순 부재명 콜아웃 제외
            if top_bar_info is None and bot_bar_info is None and st_src is None:
                continue
                
            top_count = top_bar_info['count'] if top_bar_info else 3
            bot_count = bot_bar_info['count'] if bot_bar_info else 3
            main_bar_val = top_bar_info['dia'] if top_bar_info else 19
            bot_bar_val = bot_bar_info['dia'] if bot_bar_info else main_bar_val

            # [핵심] 원본 DXF 단면도 내부의 실제 철근 원(CIRCLE / BARDOT) 객체로부터 1열/2열(다단) 열별 개수 정밀 추출!
            col_dx0 = s_start_x - start_x
            col_dx1 = s_end_x - start_x
            col_circles = [
                (cdx, cdy, cr)
                for cdx, cdy, cr in cell_cad_circles
                if col_dx0 + 20 <= cdx <= col_dx1 - 20 and (top_y - bottom_y) * 0.25 <= cdy <= (top_y - bottom_y) * 0.96
            ]
            row_clusters = []
            for cdx, cdy, cr in sorted(col_circles, key=lambda item: item[1]):
                if not row_clusters or abs(cdy - row_clusters[-1]['y_mean']) > 18.0:
                    row_clusters.append({'y_vals': [cdy], 'x_vals': [cdx], 'y_mean': cdy})
                else:
                    rc = row_clusters[-1]
                    rc['y_vals'].append(cdy)
                    rc['x_vals'].append(cdx)
                    rc['y_mean'] = sum(rc['y_vals']) / len(rc['y_vals'])

            dxf_top_layers = []
            dxf_bot_layers = []
            if len(row_clusters) >= 2:
                y_mid = (row_clusters[0]['y_mean'] + row_clusters[-1]['y_mean']) / 2.0
                # 상부근: 바깥쪽(위쪽, y 큰 값 = 1열) -> 안쪽(아래쪽, y 작은 값 = 2열) 순서
                top_cls = sorted([rc for rc in row_clusters if rc['y_mean'] > y_mid], key=lambda item: -item['y_mean'])
                # 하부근: 바깥쪽(아래쪽, y 작은 값 = 1열) -> 안쪽(위쪽, y 큰 값 = 2열) 순서
                bot_cls = sorted([rc for rc in row_clusters if rc['y_mean'] <= y_mid], key=lambda item: item['y_mean'])
                dxf_top_layers = [len(rc['x_vals']) for rc in top_cls]
                dxf_bot_layers = [len(rc['x_vals']) for rc in bot_cls]

            # 도면 내 1단(1열) 최대 수용 개수 추정 (원본 CIRCLE 총합이 일치하는 경우 우선, 없으면 CAD 표준 중심간격 3.6*db 적용)
            w_ctc_est = max(float(bw) - 100.0 - 2.0 * float(st_dia) - float(main_bar_val), 40.0)
            s_ctc_est = max(3.6 * float(main_bar_val), float(main_bar_val) + 25.0)
            cad_l1_cap = max(int(w_ctc_est // s_ctc_est) + 1, 2)
            if len(dxf_top_layers) >= 2 and sum(dxf_top_layers) == top_count:
                cad_l1_cap = dxf_top_layers[0]
            elif len(dxf_bot_layers) >= 2 and sum(dxf_bot_layers) == bot_count:
                cad_l1_cap = dxf_bot_layers[0]

            def _resolve_bar_layers(total_cnt, dxf_lyrs, txt_lyrs, l1_cap):
                if txt_lyrs and sum(txt_lyrs) == total_cnt:
                    return list(txt_lyrs)
                if dxf_lyrs and sum(dxf_lyrs) == total_cnt:
                    return list(dxf_lyrs)
                if dxf_lyrs and len(dxf_lyrs) >= 2 and dxf_lyrs[0] < total_cnt:
                    l1_c = dxf_lyrs[0]
                    rem = total_cnt - l1_c
                    return [l1_c, rem] if rem <= l1_c else [l1_c, l1_c, rem - l1_c]
                if total_cnt <= l1_cap:
                    return [int(total_cnt)]
                rem = int(total_cnt) - l1_cap
                return [l1_cap, rem] if rem <= l1_cap else [l1_cap, l1_cap, rem - l1_cap]

            top_layers = _resolve_bar_layers(
                top_count, dxf_top_layers, top_bar_info.get('txt_layers') if top_bar_info else None, cad_l1_cap
            )
            bot_layers = _resolve_bar_layers(
                bot_count, dxf_bot_layers, bot_bar_info.get('txt_layers') if bot_bar_info else None, cad_l1_cap
            )
            top_layer_desc = f" (1열 {top_layers[0]} + 2열 {top_layers[1]})" if len(top_layers) == 2 else (
                f" ({'+'.join(str(x) for x in top_layers)})" if len(top_layers) > 2 else ""
            )
            bot_layer_desc = f" (1열 {bot_layers[0]} + 2열 {bot_layers[1]})" if len(bot_layers) == 2 else (
                f" ({'+'.join(str(x) for x in bot_layers)})" if len(bot_layers) > 2 else ""
            )
            
            evidence_rows = [
                {
                    "구분": "부재 부호 (Header)",
                    "DXF 원본 텍스트": full_header_str,
                    "CAD 원본 좌표 (X, Y)": f"({bx:.0f}, {by:.0f})",
                    "셀 내 높이 (dy)": f"{by - bottom_y:.0f}",
                    "파싱 반영 결과": beam_name,
                },
                {
                    "구분": "단면 위치 (Zone)",
                    "DXF 원본 텍스트": unique_s_name,
                    "CAD 원본 좌표 (X, Y)": f"X={s_start_x:.0f}~{s_end_x:.0f}",
                    "셀 내 높이 (dy)": "단면 상단 구분",
                    "파싱 반영 결과": unique_s_name,
                },
                {
                    "구분": "보 폭 (bw)",
                    "DXF 원본 텍스트": f"{bw_src['kind']}: {bw_src['text']}" if bw_src else "기본값",
                    "CAD 원본 좌표 (X, Y)": f"({bw_src['x']:.0f}, {bw_src['y']:.0f})" if bw_src else "-",
                    "셀 내 높이 (dy)": f"{bw_src['dy']:.0f} (단면 상단 수평치수)" if bw_src else "-",
                    "파싱 반영 결과": f"{bw:.0f} mm",
                },
                {
                    "구분": "보 춤 (H)",
                    "DXF 원본 텍스트": f"{depth_src['kind']}: {depth_src['text']}" if depth_src else "기본값",
                    "CAD 원본 좌표 (X, Y)": f"({depth_src['x']:.0f}, {depth_src['y']:.0f})" if depth_src else "-",
                    "셀 내 높이 (dy)": f"{depth_src['dy']:.0f} (단면 좌측 수직치수)" if depth_src else "-",
                    "파싱 반영 결과": f"{depth:.0f} mm",
                },
                {
                    "구분": "상부 주근 (TOP BAR)",
                    "DXF 원본 텍스트": top_bar_info['text'] if top_bar_info else "-",
                    "CAD 원본 좌표 (X, Y)": f"({top_bar_info['x']:.0f}, {top_bar_info['y']:.0f})" if top_bar_info else "-",
                    "셀 내 높이 (dy)": f"{top_bar_info['dy']:.0f} (상부근 행)" if top_bar_info else "-",
                    "파싱 반영 결과": f"{top_count}-D{main_bar_val}{top_layer_desc}",
                },
                {
                    "구분": "하부 주근 (BOT BAR)",
                    "DXF 원본 텍스트": bot_bar_info['text'] if bot_bar_info else "-",
                    "CAD 원본 좌표 (X, Y)": f"({bot_bar_info['x']:.0f}, {bot_bar_info['y']:.0f})" if bot_bar_info else "-",
                    "셀 내 높이 (dy)": f"{bot_bar_info['dy']:.0f} (하부근 행)" if bot_bar_info else "-",
                    "파싱 반영 결과": f"{bot_count}-D{bot_bar_val}{bot_layer_desc}",
                },
                {
                    "구분": "전단 스터럽 (늑근/STIRRUP)",
                    "DXF 원본 텍스트": st_src['text'] if st_src else "-",
                    "CAD 원본 좌표 (X, Y)": f"({st_src['x']:.0f}, {st_src['y']:.0f})" if st_src else "-",
                    "셀 내 높이 (dy)": f"{st_src['dy']:.0f} (늑근/STIRRUP 행)" if st_src else "-",
                    "파싱 반영 결과": f"{st_legs}-D{st_dia}@{st_spacing:.0f}",
                },
            ]
            if extra_bars:
                evidence_rows.append({
                    "구분": "SKIN BAR / 복부·보조근",
                    "DXF 원본 텍스트": ", ".join(eb['text'] for eb in extra_bars),
                    "CAD 원본 좌표 (X, Y)": f"({extra_bars[0]['x']:.0f}, {extra_bars[0]['y']:.0f})",
                    "셀 내 높이 (dy)": f"{extra_bars[0]['dy']:.0f} ({extra_bars[0].get('role', '보조근')})",
                    "파싱 반영 결과": ", ".join(eb['text'] for eb in extra_bars),
                })

            sections_data[unique_s_name] = {
                'bw': float(bw), 'depth': float(depth),
                'main_bar_idx': [10, 13, 16, 19, 22, 25, 29, 32].index(main_bar_val) if main_bar_val in [10, 13, 16, 19, 22, 25, 29, 32] else 3,
                'top_dia': int(main_bar_val), 'bot_dia': int(bot_bar_val),
                'top_count': int(top_count), 'bot_count': int(bot_count),
                'top_layers': top_layers, 'bot_layers': bot_layers,
                'st_legs': int(st_legs), 'st_dia': int(st_dia), 'st_spacing': float(st_spacing),
                'extra_bars': [eb['text'] for eb in extra_bars],
                'raw_texts': sec_df['text'].tolist(),
                'evidence_rows': evidence_rows,
                'col_dx_range': (round(s_start_x - start_x, 1), round(s_end_x - start_x, 1)),
                'cell_meta': {
                    'start_x': round(start_x, 1), 'end_x': round(end_x, 1),
                    'bottom_y': round(bottom_y, 1), 'top_y': round(top_y, 1),
                    'width': round(end_x - start_x, 1), 'height': round(top_y - bottom_y, 1),
                    'header_dy': round(by - bottom_y, 1),
                    'h_lines_dy': cell_h_lines_dy,
                    'left_labels': left_row_labels,
                    'inner_dividers_dx': inner_dividers_dx,
                    'cad_lines': cell_cad_lines,
                    'cad_circles': cell_cad_circles,
                    'cad_texts': cell_cad_texts,
                }
            }
        if sections_data:
            beam_data[beam_name] = sections_data
    return beam_data, df


@st.cache_data(show_spinner=False)
def cached_parse_dxf(file_bytes, file_name, schema_ver=12):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        beams, df = parse_dxf_table(tmp_path)
        return beams, len(df)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def split_floor_and_beam(full_name: str):
    """'-6~-4 G1', '-3 G11A', '1TG1 (201동)', 'R G12', 'RG2A*', '-1RG12C', 'RWG1, -1RWG1' 등에서 층/동 표기와 보 부호를 분리"""
    s = full_name.strip()
    # 괄호로 동 표기가 뒤에 붙은 경우 (예: '1TG1 (201동)')
    m_dong = re.match(r'^(\S+)\s+\(([^)]+)\)(.*)$', s)
    if m_dong:
        return m_dong.group(2), s
    # 콤마로 병기된 부재명 (예: 'RWG1, -1RWG1') -> 첫 번째 부재명 기준으로 층 판별
    s_first = s.split(',')[0].strip() if ',' in s else s
    parts = s_first.split()
    if len(parts) >= 2:
        return parts[0], s if ',' in s else " ".join(parts[1:])
    # '-1RG12C', '-1HG1', '-1WG1', 'B2G1' 등 앞에 층 표기가 붙어 있는 경우
    m_fl_attached = re.match(
        r'^(-?\d+F?|B\d+F?)(RWG\d+.*|RWB\d+.*|RHG\d+.*|RHB\d+.*|RTG\d+.*|RTB\d+.*|RG\d+.*|RB\d+.*|TG\d+.*|TB\d+.*|HG\d+.*|HB\d+.*|WG\d+.*|WB\d+.*|CG\d+.*|CB\d+.*|SG\d+.*|SB\d+.*|FG\d+.*|FB\d+.*|MG\d+.*|MB\d+.*|G\d+.*|B\d+.*)$',
        s_first, re.IGNORECASE
    )
    if m_fl_attached:
        fl_tok = m_fl_attached.group(1)
        if fl_tok.isdigit():
            return f"{fl_tok}층", s
        return fl_tok, s
    # 'RG2A*', 'RB1', 'RWG1', 'RHG2A' 등 지붕층(R) 접두사가 붙은 경우
    m_roof = re.match(r'^R(TG\d+.*|TB\d+.*|HG\d+.*|HB\d+.*|WG\d+.*|WB\d+.*|G\d+.*|B\d+.*)$', s_first, re.IGNORECASE)
    if m_roof:
        return "R", s
    return "공통", s


def render_dxf_cell_svg(beam_name: str, selected_section: str, sections_dict: dict) -> str:
    """설계사별 양식(개별 박스형 / 연속 격자형 / 한글·영문 항목명)을 그대로 반영하여 실제 CAD 셀 원본을 렌더링"""
    sec_info = sections_dict.get(selected_section) or list(sections_dict.values())[0]
    meta = sec_info.get("cell_meta")
    if not meta:
        return "<div>원본 CAD 셀 좌표 정보가 없습니다.</div>"

    cell_w = max(float(meta.get("width", 5000.0)), 1000.0)
    cell_h = max(float(meta.get("height", 3850.0)), 1000.0)
    label_col_w = max(cell_w * 0.24, 950.0)  # 좌측 항목 헤더 열 폭

    svg_w = 680
    svg_h = 450
    pad_l, pad_r, pad_t, pad_b = 18, 18, 22, 22
    total_cad_w = label_col_w + cell_w
    scale = min((svg_w - pad_l - pad_r) / total_cad_w, (svg_h - pad_t - pad_b) / cell_h)

    ox = pad_l + label_col_w * scale  # 보 셀 dx=0 의 SVG X 좌표
    oy = svg_h - pad_b                # 보 셀 dy=0 의 SVG Y 좌표

    def tx(dx):
        return ox + dx * scale

    def ty(dy):
        return oy - dy * scale

    # 1. 좌측 항목명 헤더 열 & 셀 외곽 테두리(도면의 실제 행 구분선 h_lines_dy 및 실제 좌측 라벨 반영!)
    lx0 = pad_l
    lx1 = ox
    rx1 = tx(cell_w)
    ly_top = ty(cell_h)
    ly_bot = ty(0)
    left_header_elems = [
        f'<rect x="{lx0:.1f}" y="{ly_top:.1f}" width="{lx1 - lx0:.1f}" height="{ly_bot - ly_top:.1f}" fill="#111827" stroke="#22c55e" stroke-width="1.2"/>',
        f'<rect x="{lx1:.1f}" y="{ly_top:.1f}" width="{rx1 - lx1:.1f}" height="{ly_bot - ly_top:.1f}" fill="none" stroke="#a855f7" stroke-width="1.3"/>',
    ]

    h_lines_dy = meta.get("h_lines_dy", [])
    if not h_lines_dy:
        h_lines_dy = [cell_h * 0.91, cell_h * 0.20, cell_h * 0.13, cell_h * 0.065]
    for r_dy in h_lines_dy:
        if 20 < r_dy < cell_h - 20:
            ry = ty(r_dy)
            left_header_elems.append(f'<line x1="{lx0:.1f}" y1="{ry:.1f}" x2="{rx1:.1f}" y2="{ry:.1f}" stroke="#a855f7" stroke-width="0.9" stroke-opacity="0.7"/>')

    lh_cx = (lx0 + lx1) / 2
    actual_left_labels = meta.get("left_labels", [])
    if actual_left_labels:
        for lbl in actual_left_labels:
            l_dy = float(lbl["dy"])
            l_txt = lbl["text"]
            if 0 <= l_dy <= cell_h:
                l_col = "#4ade80"
                l_fs = "10.5"
                l_fw = "700"
                if re.search(r'상\s*부|TOP', l_txt, re.I):
                    l_col = "#fca5a5"
                elif re.search(r'하\s*부|BOT', l_txt, re.I):
                    l_col = "#93c5fd"
                elif re.search(r'늑\s*근|스터럽|STIRRUP', l_txt, re.I):
                    l_col = "#6ee7b7"
                elif re.search(r'SKIN|보\s*조|복\s*부', l_txt, re.I):
                    l_col = "#f472b6"
                elif re.search(r'^\(?\s*\d{2,4}\s*[xX×*]\s*\d{2,4}\s*\)?$', l_txt):
                    l_col = "#fcd34d"
                    l_fw = "800"
                elif l_dy >= cell_h * 0.80 and l_txt not in ["부 호", "부호"]:
                    # 좌측 헤더형 양식의 보 부호 (예: G2A, G3A, RG2A*)
                    l_col = "#38bdf8"
                    l_fs = "12.0"
                    l_fw = "800"
                left_header_elems.append(
                    f'<text x="{lh_cx:.1f}" y="{ty(l_dy + 15):.1f}" text-anchor="middle" fill="{l_col}" font-size="9.8" font-weight="{l_fw}" font-family="sans-serif">{l_txt}</text>'
                )
    else:
        default_labels = [
            (cell_h * 0.95, "부 호", "#94a3b8"),
            (cell_h * 0.56, "단면형태", "#94a3b8"),
            (cell_h * 0.49, "및 크기", "#94a3b8"),
            (cell_h * 0.16, "TOP BAR", "#fca5a5"),
            (cell_h * 0.095, "BOT BAR", "#93c5fd"),
            (cell_h * 0.032, "STIRRUP", "#6ee7b7"),
        ]
        for l_dy, l_txt, l_col in default_labels:
            left_header_elems.append(
                f'<text x="{lh_cx:.1f}" y="{ty(l_dy):.1f}" text-anchor="middle" fill="{l_col}" font-size="10.0" font-weight="700" font-family="sans-serif">{l_txt}</text>'
            )

    # 2. 현재 선택된 단면 구간(END / CENTER / BOTH / ALL / 전단면) 하이라이트 영역 표시
    sel_dx0, sel_dx1 = sec_info.get("col_dx_range", (0.0, cell_w))
    top_h_candidates = [d for d in h_lines_dy if d > cell_h * 0.82]
    header_Zone_bottom_dy = max(top_h_candidates) if top_h_candidates else cell_h
    hl_x = tx(sel_dx0)
    hl_w = max((sel_dx1 - sel_dx0) * scale, 10.0)
    hl_y = ty(header_Zone_bottom_dy)
    hl_h = ty(0.0) - hl_y
    highlight_elem = (
        f'<rect x="{hl_x:.1f}" y="{hl_y:.1f}" width="{hl_w:.1f}" height="{hl_h:.1f}" '
        f'fill="rgba(56, 189, 248, 0.08)" stroke="#38bdf8" stroke-width="1.8" stroke-dasharray="5,3"/>'
    )

    # 3. 실제 DXF 선분(테이블 격자, 수직 구분선, 콘크리트 단면 외곽선, 스터럽, 치수선) 렌더링
    inner_div_dx = meta.get("inner_dividers_dx", [])
    line_elems = []
    for dx1, dy1, dx2, dy2, skind in meta.get("cad_lines", []):
        sx1, sy1 = tx(dx1), ty(dy1)
        sx2, sy2 = tx(dx2), ty(dy2)
        is_true_col_wall = abs(dx1 - dx2) < 20 and any(abs(dx1 - dv) < 25 for dv in inner_div_dx)
        is_row_h_line = abs(dy1 - dy2) < 15 and any(abs((dy1 + dy2) / 2 - r_dy) < 18 for r_dy in h_lines_dy)
        if is_true_col_wall:
            line_elems.append(f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" stroke="#f59e0b" stroke-width="2.2"/>')
        elif is_row_h_line:
            line_elems.append(f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" stroke="#a855f7" stroke-width="0.9" stroke-opacity="0.7"/>')
        elif skind == "DIM":
            line_elems.append(f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" stroke="#cbd5e1" stroke-width="0.95"/>')
        elif abs(dx1 - dx2) < 15 and cell_h * 0.25 <= min(dy1, dy2) and max(dy1, dy2) <= cell_h * 0.96 and abs(dy2 - dy1) > 200:
            # 단면 내부 세로선(콘크리트 외곽선 또는 스터럽 세로선)
            line_elems.append(f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" stroke="#facc15" stroke-width="1.15"/>')
        else:
            stroke_c = "#a855f7" if (abs(dx1 - dx2) > cell_w * 0.6) else "#e2e8f0"
            stroke_w = "1.2" if stroke_c == "#e2e8f0" else "1.0"
            line_elems.append(f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" stroke="{stroke_c}" stroke-width="{stroke_w}"/>')

    # 4. 각 단면 컬럼의 CAD 단면 박스 내부에 상/하부 철근 점(Rebar Dot) 표시
    #    - DXF 원본에 CIRCLE 객체(cad_circles)가 있으면 원본 좌표를 그대로 투영하고, 없을 때만 추정 점을 생성
    dot_elems = []
    actual_cad_circles = meta.get("cad_circles", [])
    if actual_cad_circles:
        for cdx, cdy, cr in actual_cad_circles:
            r_svg = max(min(cr * scale * 1.15, 3.2), 1.8)
            dot_elems.append(f'<circle cx="{tx(cdx):.1f}" cy="{ty(cdy):.1f}" r="{r_svg:.1f}" fill="#facc15"/>')
    else:
        for s_key, s_val in sections_dict.items():
            c0, c1 = s_val.get("col_dx_range", (0.0, cell_w))
            col_h_segs = [
                (min(dx1, dx2), max(dx1, dx2), (dy1 + dy2) / 2)
                for dx1, dy1, dx2, dy2, sk in meta.get("cad_lines", [])
                if abs(dy1 - dy2) < 12 and 200 <= abs(dx2 - dx1) <= 1300
                and c0 + 80 <= min(dx1, dx2) and max(dx1, dx2) <= c1 - 80
                and cell_h * 0.26 <= (dy1 + dy2) / 2 <= cell_h * 0.84
            ]
            if col_h_segs:
                ys_sorted = sorted(col_h_segs, key=lambda item: item[2])
                bot_seg = ys_sorted[0]
                top_seg = ys_sorted[-1]
                bx0, bx1, by_cad = bot_seg[0] + 30, bot_seg[1] - 30, bot_seg[2] + 35
                tx0, tx1, ty_cad = top_seg[0] + 30, top_seg[1] - 30, top_seg[2] - 35
                t_cnt = min(int(s_val.get("top_count", 3)), 12)
                b_cnt = min(int(s_val.get("bot_count", 3)), 12)
                for idx_b in range(t_cnt):
                    px = tx0 + (tx1 - tx0) * idx_b / max(t_cnt - 1, 1) if t_cnt > 1 else (tx0 + tx1) / 2
                    dot_elems.append(f'<circle cx="{tx(px):.1f}" cy="{ty(ty_cad):.1f}" r="2.8" fill="#facc15"/>')
                for idx_b in range(b_cnt):
                    px = bx0 + (bx1 - bx0) * idx_b / max(b_cnt - 1, 1) if b_cnt > 1 else (bx0 + bx1) / 2
                    dot_elems.append(f'<circle cx="{tx(px):.1f}" cy="{ty(by_cad):.1f}" r="2.8" fill="#facc15"/>')

    # 5. 실제 DXF 텍스트 & 치수 숫자(DIMENSION)를 원본 CAD 비율 좌표 그대로 렌더링
    text_elems = []
    hdr_dy = float(meta.get("header_dy", cell_h * 0.93))
    max_row_line_dy = max([d for d in h_lines_dy if d < cell_h * 0.65], default=cell_h * 0.36)
    for item in meta.get("cad_texts", []):
        txt = item["text"]
        dx, dy = float(item["dx"]), float(item["dy"])
        kind = item["kind"]
        in_sel_col = (sel_dx0 - 20 <= dx <= sel_dx1 + 20)
        is_sec_zone_label = bool(re.search(r'(END|CENTER|BOTH|ALL|INT|EXT|전\s*단\s*면|단\s*부|중\s*앙)', txt, re.I))

        if is_sec_zone_label and dy >= cell_h * 0.55:
            # 단면 구간 헤더 (END(INT.), CENTER, END(EXT.), BOTH, 전단면 등)
            sx, sy = tx(dx + 15), ty(dy + 20)
            col = "#38bdf8" if in_sel_col else "#e879f9"
            fs, fw, anchor = 11.0, ("800" if in_sel_col else "700"), "start"
        elif abs(dy - hdr_dy) < 160 or dy >= cell_h * 0.90:
            # 보 부호 헤더 (예: 1TG1, (201동), -6~-4 G1)
            sx, sy = tx(dx + 220), ty(dy + 35)
            col, fs, fw, anchor = "#4ade80", 13.0, "800", "middle"
        elif kind == "DIM":
            # CAD 치수선 숫자 (예: 900, 1900)
            sx, sy = tx(dx), ty(dy + 25)
            col, fs, fw, anchor = "#fcd34d", 11.0, "800", "middle"
        elif dy > max_row_line_dy:
            # 단면도 영역 내 텍스트 (전단면, BOTH, CENTER, 주기사항 노트 등)
            if len(txt) > 10:
                # 주기사항 노트 (예: '1. 전구간 폐쇄형 스터럽 적용')
                sx, sy = tx(dx), ty(dy + 15)
                col, fs, fw, anchor = "#4ade80", 9.5, "600", "start"
            else:
                sx, sy = tx(dx + 160), ty(dy + 25)
                col = "#38bdf8" if in_sel_col else "#cbd5e1"
                fs, fw, anchor = 11.0, ("800" if in_sel_col else "600"), "middle"
        else:
            # 하단 배근 기입 행 (상부근, 하부근, 늑근/스터럽, SKIN BAR)
            sx, sy = tx(dx + 140), ty(dy + 15)
            if "@" in txt:
                col = "#6ee7b7" if in_sel_col else "#cbd5e1"
            elif dy >= max_row_line_dy * 0.72:
                col = "#fca5a5" if in_sel_col else "#e2e8f0"
            elif dy >= max_row_line_dy * 0.50:
                col = "#93c5fd" if in_sel_col else "#e2e8f0"
            else:
                col = "#f472b6" if in_sel_col else "#cbd5e1"
            fs, fw, anchor = 10.5, ("800" if in_sel_col else "600"), "middle"

        text_elems.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="{anchor}" fill="{col}" font-size="{fs}" font-weight="{fw}" font-family="\'Pretendard\', \'Noto Sans KR\', \'Malgun Gothic\', sans-serif">{txt}</text>'
        )

    svg_parts = [
        f'<div style="background:#090d16; padding:12px; border-radius:12px; border:1px solid #334155; box-shadow:0 8px 20px rgba(0,0,0,0.25);">',
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; padding:0 4px;">',
        f'<span style="color:#4ade80; font-size:12.5px; font-weight:700;">📐 DXF 도면 원본 셀 뷰어 — {beam_name} (선택 구간: {selected_section})</span>',
        f'<span style="color:#94a3b8; font-size:11px;">CAD 원본 X: {meta["start_x"]:.0f}~{meta["end_x"]:.0f} / Y: {meta["bottom_y"]:.0f}~{meta["top_y"]:.0f}</span>',
        f'</div>',
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border-radius:8px;">',
        "".join(left_header_elems),
        highlight_elem,
        "".join(line_elems),
        "".join(dot_elems),
        "".join(text_elems),
        f'</svg>',
        f'<div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:6px; padding:0 4px; font-size:11px; color:#cbd5e1;">',
        f'<span>🟦 <b>파란 점선박스:</b> 현재 선택된 검토 구간({selected_section})</span>',
        f'<span>🟧 <b>주황 실선:</b> 다구간(END/CENTER) 분리벽</span>',
        f'<span>🟨 <b>노란 치수/단면:</b> CAD 원본 치수 및 스터럽</span>',
        f'</div></div>',
    ]
    return "\n".join(svg_parts)


# =====================================================
# 2. 구조역학 계산 함수 및 단면 SVG 렌더링 엔진 (KDS 14 20 기준)
# =====================================================
REBAR_AREA = {10: 71.33, 13: 126.7, 16: 198.6, 19: 286.5, 22: 387.1, 25: 506.7, 29: 651.4, 32: 794.2}
ROUGHNESS_FACTOR = {
    "조면 확보 (μ=1.0, 표면 거칠기 6mm 이상)": 1.0,
    "조면 미확보 (μ=0.6, 일반 수직이어치기면)": 0.6,
    "일체 타설 콘크리트 (μ=1.4)": 1.4,
}
BAR_LIST = [10, 13, 16, 19, 22, 25, 29, 32]


def evaluate_beam_section(
    bw, H, cover, fck, fy, fyt,
    main_dia, top_bars, bot_bars,
    st_dia, st_legs, st_spacing,
    tension_zone, mu,
    calc_method, clear_span=8000.0, joint_x=2000.0, actual_vu=150.0, actual_mu=250.0
):
    bw = max(float(bw), 100.0)
    H = max(float(H), 150.0)
    cover = max(float(cover), 20.0)
    st_spacing = max(float(st_spacing), 10.0)
    st_legs = max(int(st_legs), 1)
    top_bars = max(int(top_bars), 1)
    bot_bars = max(int(bot_bars), 1)

    As_unit = REBAR_AREA.get(main_dia, 286.5)
    As_st_unit = REBAR_AREA.get(st_dia, 71.33)

    # 유효춤 d 산정
    d = max(H - cover - st_dia - main_dia / 2.0, 50.0)

    # 1. 배근 순간격 및 최대 1단 배근 가능 개수 검토 (KDS 14 20 50)
    usable_width = max(bw - 2 * cover - 2 * st_dia, 50.0)
    min_clear_spacing = max(float(main_dia), 25.0)
    max_bars_single_layer = max(int((usable_width + min_clear_spacing) // (main_dia + min_clear_spacing)), 2)

    def calc_clear_spacing(n_bars):
        n_layer1 = min(n_bars, max_bars_single_layer)
        if n_layer1 <= 1:
            return usable_width
        return (usable_width - n_layer1 * main_dia) / (n_layer1 - 1)

    clear_top = calc_clear_spacing(top_bars)
    clear_bot = calc_clear_spacing(bot_bars)
    spacing_ok = (clear_top >= min_clear_spacing - 0.1) and (clear_bot >= min_clear_spacing - 0.1)

    # 2. 휨강도 (Flexural Strength, KDS 14 20 20)
    beta1 = 0.85 if fck <= 28 else max(0.65, 0.85 - 0.007 * (fck - 28))
    As_top = top_bars * As_unit
    As_bot = bot_bars * As_unit
    As_tension = As_top if "상부" in tension_zone else As_bot
    tension_bars = top_bars if "상부" in tension_zone else bot_bars

    # 최소 철근량 및 철근비
    As_min_1 = (0.25 * math.sqrt(fck) / fy) * bw * d
    As_min_2 = (1.4 / fy) * bw * d
    As_min = max(As_min_1, As_min_2)
    rho = As_tension / (bw * d)
    rho_min = As_min / (bw * d)

    def calc_phi_Mn(As_val):
        a = (As_val * fy) / (0.85 * fck * bw)
        c = a / beta1 if beta1 > 0 else a / 0.85
        eps_t = 0.003 * (d - c) / max(c, 1e-6)
        eps_ty = fy / 200000.0
        if eps_t >= eps_ty + 0.003:
            phi_f = 0.85
        elif eps_t <= eps_ty:
            phi_f = 0.65
        else:
            phi_f = 0.65 + 0.20 * (eps_t - eps_ty) / 0.003
        Mn = As_val * fy * (d - a / 2.0) / 1e6  # kN·m
        return phi_f * Mn, Mn, phi_f, a, c, eps_t

    phiMn_top, Mn_top, phi_f_top, a_top, c_top, eps_t_top = calc_phi_Mn(As_top)
    phiMn_bot, Mn_bot, phi_f_bot, a_bot, c_bot, eps_t_bot = calc_phi_Mn(As_bot)
    phiMn_active = phiMn_top if "상부" in tension_zone else phiMn_bot
    eps_t_active = eps_t_top if "상부" in tension_zone else eps_t_bot
    phi_f_active = phi_f_top if "상부" in tension_zone else phi_f_bot
    a_active = a_top if "상부" in tension_zone else a_bot

    # 3. 전단강도 (Shear Strength, KDS 14 20 22)
    phi_v = 0.75
    Asv = As_st_unit * st_legs
    Vc = (1.0 / 6.0) * math.sqrt(fck) * bw * d / 1000.0  # kN
    Vs = Asv * fyt * d / st_spacing / 1000.0  # kN
    Vs_max = (2.0 / 3.0) * math.sqrt(fck) * bw * d / 1000.0  # kN
    phiVn = phi_v * (Vc + min(Vs, Vs_max))

    # 전단철근 최소면적 및 최대간격 체크
    Av_min = max(0.062 * math.sqrt(fck) * bw * st_spacing / fyt, 0.35 * bw * st_spacing / fyt)
    s_max = min(d / 2.0, 600.0) if Vs <= (1.0 / 3.0) * math.sqrt(fck) * bw * d / 1000.0 else min(d / 4.0, 300.0)
    stirrup_detail_ok = (Asv >= Av_min * 0.98) and (st_spacing <= s_max + 1.0)

    # 4. 작용 전단력 Vu 산정
    if ("위치 기반" in calc_method) or ("2차 본사" in calc_method):
        half_span = max(clear_span / 2.0, 1.0)
        reduction_factor = max(0.0, min(1.0, (half_span - joint_x) / half_span))
        Vu = phiVn * reduction_factor
    elif ("실데이터" in calc_method) or ("구조계산서 기반" in calc_method):
        reduction_factor = 1.0
        Vu = float(actual_vu)
    else:
        reduction_factor = 1.0
        Vu = phiVn

    # 5. 수직이어치기 전단마찰 검토 (Shear Friction)
    phi_sf = 0.75
    Avf = Vu * 1000.0 / (phi_sf * fy * mu)  # mm²
    # 전단마찰 상한강도 (KDS 14 20 22: Vn <= min(0.2*fck*Ac, (3.3 + 0.08*fck)*Ac, 11*Ac))
    Ac = bw * H
    Vn_sf_max = phi_sf * min(0.2 * fck * Ac, (3.3 + 0.08 * fck) * Ac, 11.0 * Ac) / 1000.0  # kN

    Ast = As_tension
    need_area = Avf - Ast
    if need_area > 0:
        sf_ok = False
        add_area = need_area
        add_ea = math.ceil(add_area / As_unit)
    else:
        sf_ok = True
        add_area = 0.0
        add_ea = 0

    dc_sf = Avf / max(Ast, 1.0)
    dc_shear = Vu / max(phiVn, 1.0)
    mu_for_req = float(actual_mu) if (("실데이터" in calc_method) or ("구조계산서 기반" in calc_method)) else (phiMn_active * 0.70)
    dc_flex = mu_for_req / max(phiMn_active, 1.0)

    # KDS 14 20 20 (4.2.2(3)) 최소철근량 예외규정: 배치 철근량 As >= (4/3) * 해석 소요철근량 As,req 이면 최소철근량 기준 만족
    rn_val = (mu_for_req * 1e6) / max(phi_f_active * bw * (d ** 2), 1.0)
    rad_term = max(0.0, 1.0 - (2.0 * rn_val) / max(0.85 * fck, 1.0))
    rho_req = (0.85 * fck / fy) * (1.0 - math.sqrt(rad_term))
    As_req = rho_req * bw * d
    As_min_4_3 = (4.0 / 3.0) * As_req
    As_req_allow_4_3 = 0.75 * Ast
    Mu_allow_4_3 = 0.75 * phiMn_active
    min_rebar_std_ok = (Ast >= As_min)
    min_rebar_4_3_ok = (Ast >= As_min_4_3)
    min_rebar_ok = min_rebar_std_ok or min_rebar_4_3_ok

    return {
        "bw": bw, "H": H, "d": d, "cover": cover,
        "As_unit": As_unit, "As_st_unit": As_st_unit,
        "As_top": As_top, "As_bot": As_bot, "Ast": Ast,
        "tension_bars": tension_bars,
        "As_min": As_min, "rho": rho, "rho_min": rho_min,
        "As_req": As_req, "As_min_4_3": As_min_4_3,
        "As_req_allow_4_3": As_req_allow_4_3, "Mu_allow_4_3": Mu_allow_4_3,
        "min_rebar_std_ok": min_rebar_std_ok, "min_rebar_4_3_ok": min_rebar_4_3_ok, "min_rebar_ok": min_rebar_ok,
        "phiMn_top": phiMn_top, "phiMn_bot": phiMn_bot, "phiMn_active": phiMn_active,
        "phi_f_active": phi_f_active, "a_active": a_active, "eps_t_active": eps_t_active,
        "Asv": Asv, "Av_min": Av_min, "Vc": Vc, "Vs": Vs, "Vs_max": Vs_max, "phiVn": phiVn,
        "s_max": s_max, "stirrup_detail_ok": stirrup_detail_ok,
        "Vu": Vu, "reduction_factor": reduction_factor,
        "Avf": Avf, "Vn_sf_max": Vn_sf_max,
        "sf_ok": sf_ok, "add_area": add_area, "add_ea": add_ea,
        "dc_sf": dc_sf, "dc_shear": dc_shear, "dc_flex": dc_flex,
        "clear_top": clear_top, "clear_bot": clear_bot,
        "min_clear_spacing": min_clear_spacing,
        "max_bars_single_layer": max_bars_single_layer,
        "spacing_ok": spacing_ok,
    }


def render_beam_svg(bw, H, cover, main_dia, top_bars, bot_bars, st_dia, st_legs, st_spacing, tension_zone, add_ea=0, top_layers=None, bot_layers=None):
    """고해상도 엔지니어링 스타일 보 단면도 SVG 생성 (DXF 원본 1열/2열 다단 배근 개수 1:1 동기화)"""
    svg_w, svg_h = 460, 440
    pad_x, pad_y = 75, 55
    draw_w = svg_w - 2 * pad_x
    draw_h = svg_h - 2 * pad_y

    scale = min(draw_w / max(bw, 200), draw_h / max(H, 200))
    rect_w = bw * scale
    rect_h = H * scale
    x0 = (svg_w - rect_w) / 2
    y0 = (svg_h - rect_h) / 2

    cov_px = max(cover * scale, 14)
    st_x0 = x0 + cov_px
    st_y0 = y0 + cov_px
    st_w = max(rect_w - 2 * cov_px, 40)
    st_h = max(rect_h - 2 * cov_px, 40)

    # CAD 표준 1단(1열) 최대 배근수 (중심간격 3.6*db 기준: 예 bw=1000, D16 -> 16가닥)
    w_ctc_mm = max(bw - 2 * cover - 2 * st_dia - main_dia, 40.0)
    s_ctc_mm = max(3.6 * float(main_dia), float(main_dia) + 25.0)
    max_single = max(int(w_ctc_mm // s_ctc_mm) + 1, 2)

    def _split_layers(n_bars, dxf_layer_list=None):
        n_bars = int(n_bars)
        if dxf_layer_list and sum(dxf_layer_list) == n_bars:
            return [int(x) for x in dxf_layer_list if int(x) > 0]
        l1_cap = max_single
        if dxf_layer_list and len(dxf_layer_list) >= 2 and int(dxf_layer_list[0]) >= 2:
            l1_cap = int(dxf_layer_list[0])
        if n_bars <= l1_cap:
            return [n_bars]
        if n_bars <= 2 * l1_cap:
            return [l1_cap, n_bars - l1_cap]
        l1 = l1_cap
        l2 = min(n_bars - l1, l1_cap)
        l3 = max(0, n_bars - l1 - l2)
        return [l1, l2, l3] if l3 > 0 else [l1, l2]

    resolved_top_layers = _split_layers(top_bars, top_layers)
    resolved_bot_layers = _split_layers(bot_bars, bot_layers)
    max_in_row = max([1] + resolved_top_layers + resolved_bot_layers)
    r_px_base = max(min(main_dia * scale * 0.45, 11.0), 5.5)
    r_px = min(r_px_base, max(2.8, (st_w - 14.0) / max(2.55 * max_in_row, 1.0)))

    def get_bar_coords(layers, is_top=True):
        coords = []
        y_base = (st_y0 + r_px + 4) if is_top else (st_y0 + st_h - r_px - 4)
        y_step = (2 * r_px + 5) if is_top else -(2 * r_px + 5)

        for l_idx, l_cnt in enumerate(layers):
            cy_l = y_base + l_idx * y_step
            for idx in range(l_cnt):
                if l_cnt == 1:
                    cx = st_x0 + st_w / 2
                else:
                    cx = st_x0 + r_px + 4 + idx * ((st_w - 2 * r_px - 8) / (l_cnt - 1))
                coords.append((cx, cy_l, l_idx + 1))
        return coords

    top_coords = get_bar_coords(resolved_top_layers, is_top=True)
    bot_coords = get_bar_coords(resolved_bot_layers, is_top=False)

    is_top_tension = "상부" in tension_zone
    top_color = "#ef4444" if is_top_tension else "#3b82f6"
    bot_color = "#ef4444" if not is_top_tension else "#3b82f6"

    # 내부 스터럽 다리(legs) 표현
    inner_legs_svg = ""
    if st_legs > 2:
        for leg_i in range(1, st_legs - 1):
            lx = st_x0 + leg_i * (st_w / (st_legs - 1))
            inner_legs_svg += f'<line x1="{lx:.1f}" y1="{st_y0:.1f}" x2="{lx:.1f}" y2="{st_y0+st_h:.1f}" stroke="#0284c7" stroke-width="2" stroke-dasharray="5,3"/>'

    bars_svg = ""
    for cx, cy, _ in top_coords:
        bars_svg += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_px:.1f}" fill="{top_color}" stroke="#0f172a" stroke-width="1.5"/>'
    for cx, cy, _ in bot_coords:
        bars_svg += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_px:.1f}" fill="{bot_color}" stroke="#0f172a" stroke-width="1.5"/>'

    # 추가 보강근(초록색 점선 원) 시각화
    if add_ea > 0:
        y_add = (st_y0 + r_px + 30) if is_top_tension else (st_y0 + st_h - r_px - 30)
        for idx in range(min(add_ea, 8)):
            cx = st_x0 + st_w * 0.2 + idx * (st_w * 0.6 / max(min(add_ea, 8) - 1, 1)) if add_ea > 1 else st_x0 + st_w / 2
            bars_svg += f'<circle cx="{cx:.1f}" cy="{y_add:.1f}" r="{r_px:.1f}" fill="#22c55e" stroke="#14532d" stroke-width="2" stroke-dasharray="2,2"/>'

    top_lyr_txt = f" [1열 {resolved_top_layers[0]}+2열 {resolved_top_layers[1]}]" if len(resolved_top_layers) == 2 else (
        f" [{'+'.join(str(x) for x in resolved_top_layers)}]" if len(resolved_top_layers) > 2 else ""
    )
    bot_lyr_txt = f" [1열 {resolved_bot_layers[0]}+2열 {resolved_bot_layers[1]}]" if len(resolved_bot_layers) == 2 else (
        f" [{'+'.join(str(x) for x in resolved_bot_layers)}]" if len(resolved_bot_layers) > 2 else ""
    )

    svg = (
        f'<div style="background:#0f172a; padding:10px; border-radius:12px; border:1px solid #334155;">'
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="380" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="1"/>'
        f'</pattern></defs>'
        f'<rect width="100%" height="100%" fill="url(#grid)" rx="8"/>'
        f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{rect_w:.1f}" height="{rect_h:.1f}" fill="#334155" stroke="#94a3b8" stroke-width="2.5" rx="3"/>'
        f'<rect x="{st_x0:.1f}" y="{st_y0:.1f}" width="{st_w:.1f}" height="{st_h:.1f}" fill="none" stroke="#38bdf8" stroke-width="2.5" rx="6"/>'
        f'{inner_legs_svg}'
        f'{bars_svg}'
        f'<line x1="{x0:.1f}" y1="{y0+rect_h+24:.1f}" x2="{x0+rect_w:.1f}" y2="{y0+rect_h+24:.1f}" stroke="#e2e8f0" stroke-width="1.5"/>'
        f'<line x1="{x0:.1f}" y1="{y0+rect_h+17:.1f}" x2="{x0:.1f}" y2="{y0+rect_h+31:.1f}" stroke="#e2e8f0" stroke-width="1.5"/>'
        f'<line x1="{x0+rect_w:.1f}" y1="{y0+rect_h+17:.1f}" x2="{x0+rect_w:.1f}" y2="{y0+rect_h+31:.1f}" stroke="#e2e8f0" stroke-width="1.5"/>'
        f'<text x="{svg_w/2:.1f}" y="{y0+rect_h+42:.1f}" fill="#f8fafc" font-size="13" font-family="sans-serif" font-weight="bold" text-anchor="middle">bw = {bw:.0f} mm</text>'
        f'<line x1="{x0-24:.1f}" y1="{y0:.1f}" x2="{x0-24:.1f}" y2="{y0+rect_h:.1f}" stroke="#e2e8f0" stroke-width="1.5"/>'
        f'<line x1="{x0-31:.1f}" y1="{y0:.1f}" x2="{x0-17:.1f}" y2="{y0:.1f}" stroke="#e2e8f0" stroke-width="1.5"/>'
        f'<line x1="{x0-31:.1f}" y1="{y0+rect_h:.1f}" x2="{x0-17:.1f}" y2="{y0+rect_h:.1f}" stroke="#e2e8f0" stroke-width="1.5"/>'
        f'<text x="{x0-36:.1f}" y="{svg_h/2:.1f}" fill="#f8fafc" font-size="13" font-family="sans-serif" font-weight="bold" text-anchor="middle" transform="rotate(-90, {x0-36:.1f}, {svg_h/2:.1f})">H = {H:.0f} mm</text>'
        f'<text x="{svg_w/2:.1f}" y="{y0-14:.1f}" fill="#fca5a5" font-size="12.0" font-family="sans-serif" font-weight="bold" text-anchor="middle">TOP: {top_bars}-D{main_dia}{top_lyr_txt} {"(인장측)" if is_top_tension else "(압축측)"}</text>'
        f'<text x="{svg_w/2:.1f}" y="{y0+rect_h-8:.1f}" fill="#93c5fd" font-size="11.5" font-family="sans-serif" font-weight="bold" text-anchor="middle">BOT: {bot_bars}-D{main_dia}{bot_lyr_txt} {"(인장측)" if not is_top_tension else "(압축측)"}</text>'
        f'<text x="{svg_w-14}" y="22" fill="#38bdf8" font-size="11.5" font-family="sans-serif" font-weight="bold" text-anchor="end">Stirrup: {st_legs}-D{st_dia}@{st_spacing:.0f}</text>'
        f'</svg></div>'
    )
    return svg


def evaluate_horizontal_joint(
    bw, H, cover, fck, fy, fyt,
    main_dia, top_bars, bot_bars,
    st_dia, st_legs, st_spacing,
    tension_zone, mu,
    P_perm=0.0,
    precision_mode=False,
    h_joint=None,
    use_actual_vu=False,
    actual_vu_kN=0.0,
    moment_mode=None,
):
    """KDS 기준 RC 보 수평 이어치기 전단마찰 검토 엔진
    - 일반 검토 모드: 최대 공칭전단강도 기반 균일 전단흐름 보수적 산정
    - 정밀 검토 모드: 모멘트 방향(+M 상부압축 / -M 하부압축 / 양방향 포락) 및 타설 높이(h_joint)에 따른 균열단면 전단흐름 저감계수(αq) 반영
    """
    bw = max(float(bw), 100.0)
    H = max(float(H), 150.0)
    cover = max(float(cover), 20.0)
    st_spacing = max(float(st_spacing), 10.0)
    st_legs = max(int(st_legs), 1)
    top_bars = max(int(top_bars), 1)
    bot_bars = max(int(bot_bars), 1)
    P_perm = max(float(P_perm), 0.0)
    if h_joint is None:
        h_joint = H * 0.5
    h_joint = max(0.0, min(H, float(h_joint)))

    # KDS 14 20 22 전단철근 및 전단마찰 보강근 설계기준항복강도 상한 제한 (최대 500 MPa)
    HJ_MAX_FY = 500.0
    fyt_raw = float(fyt)
    fy_raw = float(fy)
    fyt_eff = min(fyt_raw, HJ_MAX_FY)
    fy_vf_eff = min(fy_raw, HJ_MAX_FY)
    fyt_capped = fyt_raw > HJ_MAX_FY
    fy_vf_capped = fy_raw > HJ_MAX_FY

    As_unit = REBAR_AREA.get(main_dia, 286.5)
    As_st_unit = REBAR_AREA.get(st_dia, 71.33)
    d = max(H - cover - st_dia - main_dia / 2.0, 50.0)
    Asv = As_st_unit * st_legs

    # 1. 공칭전단강도 Vn (N) — KDS 14 20 22 (전단철근 강도 상한 500 MPa 적용)
    Vc_N = (1.0 / 6.0) * math.sqrt(fck) * bw * d
    Vs_N = (Asv * fyt_eff * d) / st_spacing
    Vn_N = Vc_N + Vs_N

    # [A] 일반 검토 모드 (표준 보수적 검토 — 전단 흐름 최대치 기준, αq = 1.0, 보강근 강도 상한 500 MPa 적용)
    Vnh_1m_std = Vn_N * (1000.0 / d)                       # N/m
    Avf_total_std = Vnh_1m_std / max(fy_vf_eff * mu, 1e-6) # mm²/m
    Asv_1m = Asv * (1000.0 / st_spacing)                   # mm²/m (기존 스터럽 보유량)
    Avf_P = (P_perm * 1000.0) / max(fy_vf_eff, 1e-6)       # mm²/m (영구 압축력 감소량)
    Avf_req_std = max(0.0, Avf_total_std - Asv_1m - Avf_P) # mm²/m

    # [B] 정밀 검토 모드 (모멘트 방향별 압축대 위치 + 타설 높이 h_joint 반영 전단 흐름 Q/I 정밀 검토)
    # 1) 균열 단면 탄성 중립축 깊이 c = k·d 산정 (정모멘트 +M 상부압축 / 부모멘트 -M 하부압축 각각 산정)
    Ec = 8500.0 * ((fck + 4.0) ** (1.0 / 3.0))
    n_mod = 200000.0 / max(Ec, 1.0)

    def _calc_cracked_c(n_tens_bars):
        as_t = max(int(n_tens_bars), 1) * As_unit
        rho_t = as_t / max(bw * d, 1.0)
        k_t = math.sqrt((rho_t * n_mod) ** 2 + 2.0 * rho_t * n_mod) - rho_t * n_mod
        c_t = min(max(k_t * d, 0.20 * d), 0.55 * d)
        return k_t, c_t

    def _calc_alpha_q(y_from_comp, c_val):
        if y_from_comp >= c_val:
            return 1.0, False
        aq = max(0.0, min(1.0, 1.0 - (1.0 - y_from_comp / max(c_val, 1e-6)) ** 2))
        return aq, True

    # +M (정모멘트: 하부 인장 / 상부 압축 -> 압축연단 = 상단, y_comp = H - h_joint)
    k_pos, c_pos = _calc_cracked_c(bot_bars)
    y_top = max(0.0, min(H, H - h_joint))
    alpha_q_pos, in_comp_pos = _calc_alpha_q(y_top, c_pos)

    # -M (부모멘트: 상부 인장 / 하부 압축 -> 압축연단 = 하단, y_comp = h_joint)
    k_neg, c_neg = _calc_cracked_c(top_bars)
    y_bot = max(0.0, min(H, h_joint))
    alpha_q_neg, in_comp_neg = _calc_alpha_q(y_bot, c_neg)

    # 모멘트 조건 해석 (미지정 시 tension_zone 자동 연동)
    mm_str = str(moment_mode or "").strip()
    if "포락" in mm_str or "ENVELOPE" in mm_str.upper():
        comp_face = "ENVELOPE"
        moment_mode_label = "양방향 포락 (+M / -M 모멘트 반전 고려)"
        if alpha_q_pos >= alpha_q_neg:
            alpha_q, in_comp_zone = alpha_q_pos, in_comp_pos
            k_cr, c_depth, y_comp, governing_face = k_pos, c_pos, y_top, "TOP"
        else:
            alpha_q, in_comp_zone = alpha_q_neg, in_comp_neg
            k_cr, c_depth, y_comp, governing_face = k_neg, c_neg, y_bot, "BOTTOM"
    elif ("하부 압축" in mm_str) or ("-M" in mm_str) or ("부모멘트" in mm_str) or (mm_str == "" and "상부" in str(tension_zone)):
        comp_face = "BOTTOM"
        governing_face = "BOTTOM"
        moment_mode_label = "부모멘트 -M (상부 인장 / 하부 압축)"
        alpha_q, in_comp_zone = alpha_q_neg, in_comp_neg
        k_cr, c_depth, y_comp = k_neg, c_neg, y_bot
    else:
        comp_face = "TOP"
        governing_face = "TOP"
        moment_mode_label = "정모멘트 +M (하부 인장 / 상부 압축)"
        alpha_q, in_comp_zone = alpha_q_pos, in_comp_pos
        k_cr, c_depth, y_comp = k_pos, c_pos, y_top

    # 3) 정밀 검토 기준 전단력 (실제 Vu 입력 시 Vu/φ, 미입력 시 공칭전단강도 Vn 적용)
    if use_actual_vu and actual_vu_kN > 0.0:
        Vn_eff_N = (float(actual_vu_kN) * 1000.0) / 0.75
        shear_basis_str = f"계수전단력 Vu/φ ({actual_vu_kN:.1f}/0.75 = {Vn_eff_N/1000.0:.1f} kN)"
    else:
        Vn_eff_N = Vn_N
        shear_basis_str = f"최대 공칭전단강도 Vn ({Vn_N/1000.0:.1f} kN)"

    Vnh_1m_prec_base = Vn_eff_N * (1000.0 / d)
    Vnh_1m_prec = alpha_q * Vnh_1m_prec_base
    Avf_total_prec = Vnh_1m_prec / max(fy_vf_eff * mu, 1e-6)
    Avf_req_prec = max(0.0, Avf_total_prec - Asv_1m - Avf_P)

    # 절감 효과 (일반 검토 대비 정밀 검토)
    delta_Avf_total = max(0.0, Avf_total_std - Avf_total_prec)
    saving_pct_total = (delta_Avf_total / Avf_total_std * 100.0) if Avf_total_std > 1e-6 else 0.0
    delta_Avf_req = max(0.0, Avf_req_std - Avf_req_prec)
    saving_pct_req = (delta_Avf_req / Avf_req_std * 100.0) if Avf_req_std > 1e-6 else (100.0 if (Avf_req_std == 0 and Avf_req_prec == 0) else 0.0)

    # 현재 활성 모드 결과 선택
    Vnh_1m = Vnh_1m_prec if precision_mode else Vnh_1m_std
    Avf_total = Avf_total_prec if precision_mode else Avf_total_std
    Avf_req = Avf_req_prec if precision_mode else Avf_req_std
    alpha_q_active = alpha_q if precision_mode else 1.0
    h_joint_active = h_joint if precision_mode else (H * 0.5)
    y_top_active = H - h_joint_active
    hj_ok = (Avf_req <= 1e-6)
    dc_hj = Avf_total / max(Asv_1m + Avf_P, 1.0)

    # 현장 조치 가이드: ① 스터럽 간격 축소안(s_req) & ② 추가 다우얼바(D10, D13, D16) 배근표
    Avf_need_for_st = max(0.0, Avf_total - Avf_P)
    s_req = (Asv * 1000.0) / Avf_need_for_st if Avf_need_for_st > 1e-6 else st_spacing
    s_req_practical = max(int(math.floor(s_req / 10.0) * 10), 10) if Avf_need_for_st > 1e-6 else int(st_spacing)

    dowel_options = []
    if Avf_req > 1e-6:
        for d_dia in [10, 13, 16]:
            ab_d = REBAR_AREA[d_dia]
            ea_1m = math.ceil(Avf_req / ab_d)
            sp_1leg = max(int(math.floor((1000.0 * ab_d / Avf_req) / 10.0) * 10), 20)
            sp_2leg = max(int(math.floor((2000.0 * ab_d / Avf_req) / 10.0) * 10), 20)
            dowel_options.append({
                "보강근 규격": f"D{d_dia}",
                "단면적 (mm²/본)": round(ab_d, 2),
                "1m당 최소 본수 (EA/m)": f"{ea_1m} EA/m",
                "1열(1가닥) 배근 간격": f"1-D{d_dia} @ {min(sp_1leg, 400)} mm",
                "2열(양측 2가닥) 배근 간격": f"2-D{d_dia} @ {min(sp_2leg, 400)} mm",
                "확보 보강 단면적 (mm²/m)": round(ea_1m * ab_d, 1),
            })

    return {
        "bw": bw, "H": H, "d": d, "cover": cover,
        "fyt_eff": fyt_eff, "fy_vf_eff": fy_vf_eff,
        "fyt_capped": fyt_capped, "fy_vf_capped": fy_vf_capped,
        "Asv": Asv, "Asv_1m": Asv_1m, "Avf_P": Avf_P,
        "Vc_kN": Vc_N / 1000.0, "Vs_kN": Vs_N / 1000.0, "Vn_kN": Vn_N / 1000.0,
        "Vn_eff_kN": (Vn_eff_N if precision_mode else Vn_N) / 1000.0,
        "shear_basis_str": shear_basis_str if precision_mode else f"최대 공칭전단강도 Vn ({Vn_N/1000.0:.1f} kN)",
        "c_depth": c_depth, "k_cr": k_cr,
        "c_pos": c_pos, "c_neg": c_neg,
        "alpha_q_pos": alpha_q_pos, "alpha_q_neg": alpha_q_neg,
        "comp_face": comp_face, "governing_face": governing_face,
        "moment_mode_label": moment_mode_label,
        "h_joint": h_joint_active, "y_top": y_top_active,
        "y_comp": y_comp if precision_mode else (H * 0.5),
        "in_comp_zone": in_comp_zone if precision_mode else False,
        "alpha_q": alpha_q_active, "alpha_q_prec": alpha_q,
        "Vnh_1m_kN": Vnh_1m / 1000.0, "Vnh_1m_std_kN": Vnh_1m_std / 1000.0, "Vnh_1m_prec_kN": Vnh_1m_prec / 1000.0,
        "Avf_total": Avf_total, "Avf_total_std": Avf_total_std, "Avf_total_prec": Avf_total_prec,
        "Avf_req": Avf_req, "Avf_req_std": Avf_req_std, "Avf_req_prec": Avf_req_prec,
        "delta_Avf_total": delta_Avf_total, "saving_pct_total": saving_pct_total,
        "delta_Avf_req": delta_Avf_req, "saving_pct_req": saving_pct_req,
        "hj_ok": hj_ok, "dc_hj": dc_hj,
        "s_req": s_req, "s_req_practical": s_req_practical,
        "dowel_options": dowel_options,
        "precision_mode": precision_mode,
    }


def render_horizontal_joint_svg(
    bw, H, cover, main_dia, top_bars, bot_bars,
    st_dia, st_legs, st_spacing, tension_zone,
    hj_res, top_layers=None, bot_layers=None
):
    """수평 이어치기 단면도 + 우측 전단흐름(Q/I) 분포도"""
    svg_w, svg_h = 560, 440
    pad_l, pad_r, pad_t, pad_b = 70, 175, 58, 56
    draw_w = svg_w - pad_l - pad_r
    draw_h = svg_h - pad_t - pad_b

    scale = min(draw_w / max(bw, 200), draw_h / max(H, 200))
    rect_w = bw * scale
    rect_h = H * scale
    x0 = pad_l + (draw_w - rect_w) / 2.0
    y0 = pad_t + (draw_h - rect_h) / 2.0

    cov_px = max(cover * scale, 13.0)
    st_x0 = x0 + cov_px
    st_y0 = y0 + cov_px
    st_w = max(rect_w - 2 * cov_px, 40.0)
    st_h = max(rect_h - 2 * cov_px, 40.0)

    w_ctc_mm = max(bw - 2 * cover - 2 * st_dia - main_dia, 40.0)
    s_ctc_mm = max(3.6 * float(main_dia), float(main_dia) + 25.0)
    max_single = max(int(w_ctc_mm // s_ctc_mm) + 1, 2)

    def _split_layers(n_bars, dxf_layer_list=None):
        n_bars = int(n_bars)
        if dxf_layer_list and sum(dxf_layer_list) == n_bars:
            return [int(x) for x in dxf_layer_list if int(x) > 0]
        l1_cap = max_single
        if dxf_layer_list and len(dxf_layer_list) >= 2 and int(dxf_layer_list[0]) >= 2:
            l1_cap = int(dxf_layer_list[0])
        if n_bars <= l1_cap:
            return [n_bars]
        if n_bars <= 2 * l1_cap:
            return [l1_cap, n_bars - l1_cap]
        l1 = l1_cap
        l2 = min(n_bars - l1, l1_cap)
        l3 = max(0, n_bars - l1 - l2)
        return [l1, l2, l3] if l3 > 0 else [l1, l2]

    resolved_top = _split_layers(top_bars, top_layers)
    resolved_bot = _split_layers(bot_bars, bot_layers)
    max_in_row = max([1] + resolved_top + resolved_bot)
    r_px_base = max(min(main_dia * scale * 0.42, 10.0), 4.8)
    r_px = min(r_px_base, max(2.6, (st_w - 14.0) / max(2.55 * max_in_row, 1.0)))

    def get_bar_coords(layers, is_top=True):
        coords = []
        y_base = (st_y0 + r_px + 4) if is_top else (st_y0 + st_h - r_px - 4)
        y_step = (2 * r_px + 4.5) if is_top else -(2 * r_px + 4.5)
        for l_idx, l_cnt in enumerate(layers):
            cy_l = y_base + l_idx * y_step
            for idx in range(l_cnt):
                cx = (st_x0 + st_w / 2) if l_cnt == 1 else (st_x0 + r_px + 4 + idx * ((st_w - 2 * r_px - 8) / (l_cnt - 1)))
                coords.append((cx, cy_l))
        return coords

    top_coords = get_bar_coords(resolved_top, True)
    bot_coords = get_bar_coords(resolved_bot, False)
    # 압축대(c) 음영 및 수평 이어치기 경계선(h_joint) 위치 계산
    c_depth = float(hj_res["c_depth"])
    c_pos = float(hj_res.get("c_pos", c_depth))
    c_neg = float(hj_res.get("c_neg", c_depth))
    h_joint = float(hj_res["h_joint"])
    y_comp = float(hj_res.get("y_comp", hj_res["y_top"]))
    alpha_q = float(hj_res["alpha_q"])
    is_prec = bool(hj_res["precision_mode"])
    comp_face = str(hj_res.get("comp_face", "TOP")) if is_prec else ("BOTTOM" if "상부" in tension_zone else "TOP")

    if comp_face == "ENVELOPE":
        top_color = "#f97316"
        bot_color = "#f97316"
    elif comp_face == "BOTTOM":
        top_color = "#ef4444"  # 상부 인장 (-M)
        bot_color = "#3b82f6"  # 하부 압축 (-M)
    else:
        top_color = "#3b82f6"  # 상부 압축 (+M)
        bot_color = "#ef4444"  # 하부 인장 (+M)

    # 내부 스터럽 다리
    inner_legs_svg = ""
    if st_legs > 2:
        for leg_i in range(1, st_legs - 1):
            lx = st_x0 + leg_i * (st_w / (st_legs - 1))
            inner_legs_svg += f'<line x1="{lx:.1f}" y1="{st_y0:.1f}" x2="{lx:.1f}" y2="{st_y0+st_h:.1f}" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="5,3"/>'

    bars_svg = ""
    for cx, cy in top_coords:
        bars_svg += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_px:.1f}" fill="{top_color}" stroke="#0f172a" stroke-width="1.2"/>'
    for cx, cy in bot_coords:
        bars_svg += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_px:.1f}" fill="{bot_color}" stroke="#0f172a" stroke-width="1.2"/>'

    c_px = min(c_depth * scale, rect_h)
    c_pos_px = min(c_pos * scale, rect_h)
    c_neg_px = min(c_neg * scale, rect_h)
    y_joint = y0 + rect_h - h_joint * scale
    y_joint = max(y0 + 2.0, min(y0 + rect_h - 2.0, y_joint))

    comp_zone_svg = ""
    if is_prec:
        if comp_face == "TOP":
            y_na = y0 + c_pos_px
            comp_zone_svg = (
                f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{rect_w:.1f}" height="{c_pos_px:.1f}" '
                f'fill="rgba(56, 189, 248, 0.20)" stroke="none"/>'
                f'<line x1="{x0-8:.1f}" y1="{y_na:.1f}" x2="{x0+rect_w+8:.1f}" y2="{y_na:.1f}" '
                f'stroke="#38bdf8" stroke-width="1.3" stroke-dasharray="4,3"/>'
                f'<text x="{x0+rect_w-6:.1f}" y="{y_na-5:.1f}" fill="#7dd3fc" font-size="9.2" font-weight="700" text-anchor="end">상부 압축대 c={c_pos:.0f}mm (+M)</text>'
            )
        elif comp_face == "BOTTOM":
            y_na = y0 + rect_h - c_neg_px
            comp_zone_svg = (
                f'<rect x="{x0:.1f}" y="{y_na:.1f}" width="{rect_w:.1f}" height="{c_neg_px:.1f}" '
                f'fill="rgba(56, 189, 248, 0.20)" stroke="none"/>'
                f'<line x1="{x0-8:.1f}" y1="{y_na:.1f}" x2="{x0+rect_w+8:.1f}" y2="{y_na:.1f}" '
                f'stroke="#38bdf8" stroke-width="1.3" stroke-dasharray="4,3"/>'
                f'<text x="{x0+rect_w-6:.1f}" y="{y_na+13:.1f}" fill="#7dd3fc" font-size="9.2" font-weight="700" text-anchor="end">하부 압축대 c={c_neg:.0f}mm (-M)</text>'
            )
        else:
            # 양방향 포락 (+M 상부압축 / -M 하부압축 동시 표시)
            y_na_top = y0 + c_pos_px
            y_na_bot = y0 + rect_h - c_neg_px
            comp_zone_svg = (
                f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{rect_w:.1f}" height="{c_pos_px:.1f}" fill="rgba(56, 189, 248, 0.12)" stroke="none"/>'
                f'<line x1="{x0-6:.1f}" y1="{y_na_top:.1f}" x2="{x0+rect_w+6:.1f}" y2="{y_na_top:.1f}" stroke="#38bdf8" stroke-width="1.1" stroke-dasharray="3,3"/>'
                f'<text x="{x0+rect_w-6:.1f}" y="{y_na_top-4:.1f}" fill="#7dd3fc" font-size="8.6" font-weight="700" text-anchor="end">+M c={c_pos:.0f}</text>'
                f'<rect x="{x0:.1f}" y="{y_na_bot:.1f}" width="{rect_w:.1f}" height="{c_neg_px:.1f}" fill="rgba(56, 189, 248, 0.12)" stroke="none"/>'
                f'<line x1="{x0-6:.1f}" y1="{y_na_bot:.1f}" x2="{x0+rect_w+6:.1f}" y2="{y_na_bot:.1f}" stroke="#38bdf8" stroke-width="1.1" stroke-dasharray="3,3"/>'
                f'<text x="{x0+rect_w-6:.1f}" y="{y_na_bot+12:.1f}" fill="#7dd3fc" font-size="8.6" font-weight="700" text-anchor="end">-M c={c_neg:.0f}</text>'
            )

    # 수평 이어치기 경계 가로 점선 (주황/초록 강조)
    joint_col = "#22c55e" if hj_res["hj_ok"] else "#f59e0b"
    lbl_y = (y_joint - 18.0) if (y_joint - y0 > 24.0) else (y_joint + 6.0)
    joint_svg = (
        f'<line x1="{x0-18:.1f}" y1="{y_joint:.1f}" x2="{x0+rect_w+18:.1f}" y2="{y_joint:.1f}" '
        f'stroke="{joint_col}" stroke-width="2.8" stroke-dasharray="7,4"/>'
        f'<circle cx="{x0-18:.1f}" cy="{y_joint:.1f}" r="3.2" fill="{joint_col}"/>'
        f'<circle cx="{x0+rect_w+18:.1f}" cy="{y_joint:.1f}" r="3.2" fill="{joint_col}"/>'
        f'<rect x="{x0+rect_w/2-74:.1f}" y="{lbl_y:.1f}" width="148" height="16" rx="4" fill="rgba(15,23,42,0.88)" stroke="{joint_col}" stroke-width="1"/>'
        f'<text x="{x0+rect_w/2:.1f}" y="{lbl_y+11.5:.1f}" fill="{joint_col}" font-size="9.8" font-weight="800" text-anchor="middle">'
        f'수평 이어치기 (h={h_joint:.0f}mm)</text>'
    )

    # 우측 전단흐름(Q/I) 분포도 패널
    qx0 = x0 + rect_w + 46.0
    qw = 88.0
    q_panel_svg = [
        f'<line x1="{qx0:.1f}" y1="{y0:.1f}" x2="{qx0:.1f}" y2="{y0+rect_h:.1f}" stroke="#64748b" stroke-width="1.2"/>',
        f'<text x="{qx0+qw/2:.1f}" y="{y0-14:.1f}" fill="#cbd5e1" font-size="10.5" font-weight="800" text-anchor="middle">전단흐름 분포 (q)</text>',
    ]
    if is_prec:
        steps = 28
        poly_pts = [f"{qx0:.1f},{y0:.1f}"]
        for i_s in range(0, steps + 1):
            frac_h = i_s / steps
            yy = y0 + frac_h * rect_h
            y_from_top_mm = frac_h * H
            y_from_bot_mm = H - y_from_top_mm
            aq_p = 1.0 if y_from_top_mm >= c_pos else max(0.0, min(1.0, 1.0 - (1.0 - y_from_top_mm / max(c_pos, 1e-6)) ** 2))
            aq_n = 1.0 if y_from_bot_mm >= c_neg else max(0.0, min(1.0, 1.0 - (1.0 - y_from_bot_mm / max(c_neg, 1e-6)) ** 2))
            if comp_face == "TOP":
                aq_s = aq_p
            elif comp_face == "BOTTOM":
                aq_s = aq_n
            else:
                aq_s = max(aq_p, aq_n)
            xx = qx0 + aq_s * qw
            poly_pts.append(f"{xx:.1f},{yy:.1f}")
        poly_pts.append(f"{qx0:.1f},{y0+rect_h:.1f}")
        q_panel_svg.append(
            f'<polygon points="{" ".join(poly_pts)}" fill="rgba(56,189,248,0.16)" stroke="#38bdf8" stroke-width="1.8"/>'
        )
        qx_j = qx0 + alpha_q * qw
        y_ref_txt = (
            f"상단 y={y_comp:.0f}mm (+M)" if comp_face == "TOP"
            else (f"하단 y={y_comp:.0f}mm (-M)" if comp_face == "BOTTOM" else "포락 max(+M,-M)")
        )
        q_panel_svg.append(
            f'<line x1="{qx0:.1f}" y1="{y_joint:.1f}" x2="{qx_j:.1f}" y2="{y_joint:.1f}" stroke="{joint_col}" stroke-width="2.4"/>'
            f'<circle cx="{qx_j:.1f}" cy="{y_joint:.1f}" r="4.0" fill="{joint_col}" stroke="#0f172a" stroke-width="1.2"/>'
            f'<text x="{qx0+qw/2:.1f}" y="{y0+rect_h+18:.1f}" fill="{joint_col}" font-size="11.0" font-weight="800" text-anchor="middle">αq = {alpha_q:.2f}</text>'
            f'<text x="{qx0+qw/2:.1f}" y="{y0+rect_h+33:.1f}" fill="#94a3b8" font-size="9.2" font-weight="600" text-anchor="middle">{y_ref_txt}</text>'
        )
    else:
        # 일반 모드: 복부 전체 균일 전단흐름 αq = 1.00
        q_panel_svg.append(
            f'<rect x="{qx0:.1f}" y="{y0:.1f}" width="{qw:.1f}" height="{rect_h:.1f}" fill="rgba(245,158,11,0.14)" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="4,2"/>'
            f'<line x1="{qx0:.1f}" y1="{y_joint:.1f}" x2="{qx0+qw:.1f}" y2="{y_joint:.1f}" stroke="{joint_col}" stroke-width="2.4"/>'
            f'<circle cx="{qx0+qw:.1f}" cy="{y_joint:.1f}" r="4.0" fill="{joint_col}" stroke="#0f172a" stroke-width="1.2"/>'
            f'<text x="{qx0+qw/2:.1f}" y="{y0+rect_h+18:.1f}" fill="#fbbf24" font-size="11.0" font-weight="800" text-anchor="middle">균일 αq = 1.00</text>'
            f'<text x="{qx0+qw/2:.1f}" y="{y0+rect_h+33:.1f}" fill="#94a3b8" font-size="9.5" font-weight="600" text-anchor="middle">(보수적 표준)</text>'
        )

    mode_badge_txt = (
        f"정밀 ({'+M 상부압축' if comp_face=='TOP' else ('-M 하부압축' if comp_face=='BOTTOM' else '±M 양방향 포락')})"
        if is_prec else "일반 검토 (표준)"
    )
    mode_badge_col = "#38bdf8" if is_prec else "#fbbf24"

    svg = (
        f'<div style="background:#0f172a; padding:10px; border-radius:12px; border:1px solid #334155;">'
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="380" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><pattern id="hgrid" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="1"/>'
        f'</pattern></defs>'
        f'<rect width="100%" height="100%" fill="url(#hgrid)" rx="8"/>'
        f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{rect_w:.1f}" height="{rect_h:.1f}" fill="#334155" stroke="#94a3b8" stroke-width="2.3" rx="3"/>'
        f'{comp_zone_svg}'
        f'<rect x="{st_x0:.1f}" y="{st_y0:.1f}" width="{st_w:.1f}" height="{st_h:.1f}" fill="none" stroke="#38bdf8" stroke-width="2.2" rx="5"/>'
        f'{inner_legs_svg}'
        f'{bars_svg}'
        f'{joint_svg}'
        f'{"".join(q_panel_svg)}'
        f'<line x1="{x0:.1f}" y1="{y0+rect_h+22:.1f}" x2="{x0+rect_w:.1f}" y2="{y0+rect_h+22:.1f}" stroke="#e2e8f0" stroke-width="1.4"/>'
        f'<line x1="{x0:.1f}" y1="{y0+rect_h+16:.1f}" x2="{x0:.1f}" y2="{y0+rect_h+28:.1f}" stroke="#e2e8f0" stroke-width="1.4"/>'
        f'<line x1="{x0+rect_w:.1f}" y1="{y0+rect_h+16:.1f}" x2="{x0+rect_w:.1f}" y2="{y0+rect_h+28:.1f}" stroke="#e2e8f0" stroke-width="1.4"/>'
        f'<text x="{x0+rect_w/2:.1f}" y="{y0+rect_h+40:.1f}" fill="#f8fafc" font-size="12.5" font-family="sans-serif" font-weight="bold" text-anchor="middle">bw = {bw:.0f} mm</text>'
        f'<line x1="{x0-26:.1f}" y1="{y0:.1f}" x2="{x0-26:.1f}" y2="{y0+rect_h:.1f}" stroke="#e2e8f0" stroke-width="1.4"/>'
        f'<line x1="{x0-32:.1f}" y1="{y0:.1f}" x2="{x0-20:.1f}" y2="{y0:.1f}" stroke="#e2e8f0" stroke-width="1.4"/>'
        f'<line x1="{x0-32:.1f}" y1="{y0+rect_h:.1f}" x2="{x0-20:.1f}" y2="{y0+rect_h:.1f}" stroke="#e2e8f0" stroke-width="1.4"/>'
        f'<text x="{x0-38:.1f}" y="{y0+rect_h/2:.1f}" fill="#f8fafc" font-size="12.5" font-family="sans-serif" font-weight="bold" text-anchor="middle" transform="rotate(-90, {x0-38:.1f}, {y0+rect_h/2:.1f})">H = {H:.0f} mm</text>'
        f'<text x="{x0+rect_w/2:.1f}" y="{y0-14:.1f}" fill="#e2e8f0" font-size="11.5" font-family="sans-serif" font-weight="bold" text-anchor="middle">Stirrup: {st_legs}-D{st_dia}@{st_spacing:.0f}</text>'
        f'<text x="16" y="22" fill="{mode_badge_col}" font-size="11.5" font-family="sans-serif" font-weight="800">● {mode_badge_txt}</text>'
        f'<text x="{svg_w-16}" y="22" fill="#94a3b8" font-size="10.5" font-family="sans-serif" font-weight="700" text-anchor="end">Vnh = {hj_res["Vnh_1m_kN"]:.1f} kN/m | Avf,req = {hj_res["Avf_req"]:.0f} mm²/m</text>'
        f'</svg></div>'
    )
    return svg


# =====================================================
# 3. 세션 상태 초기화
# =====================================================
if "extracted_beams" not in st.session_state:
    st.session_state.extracted_beams = {}
    st.session_state.dxf_filename = None
    st.session_state.entity_count = 0
    st.session_state.bw = 600.0
    st.session_state.beam_depth = 600.0
    st.session_state.main_bar = 19
    st.session_state.top_bars = 6
    st.session_state.bot_bars = 5
    st.session_state.top_layers = [6]
    st.session_state.bot_layers = [5]
    st.session_state.tension_zone = "상부 인장 (부모멘트 -M)"
    st.session_state.st_dia = 13
    st.session_state.st_spacing = 200.0
    st.session_state.st_legs = 3
    st.session_state.selected_beam_label = "직접 입력"
if "precision_unlocked" not in st.session_state:
    st.session_state.precision_unlocked = False

# 기존 세션의 구 명칭('상부 (단부)'/'하부 (중앙부)') 자동 마이그레이션
if st.session_state.get("tension_zone") == "상부 (단부)":
    st.session_state.tension_zone = "상부 인장 (부모멘트 -M)"
elif st.session_state.get("tension_zone") == "하부 (중앙부)":
    st.session_state.tension_zone = "하부 인장 (정모멘트 +M)"

# =====================================================
# 4. 상단 타이틀 & 사이드바 (DXF 업로드 및 재료 물성 설정)
# =====================================================
dxf_status_str = f"현재 도면: {st.session_state.dxf_filename}" if st.session_state.dxf_filename else "도면 미 업로드 (직접 입력 모드)"
st.markdown(
    f'<div class="dw-topbar">'
    f'<div><span class="dw-topbar-badge">KDS 구조기준 적용</span></div>'
    f'<div class="dw-topbar-right">'
    f'<span style="color:#617589; font-size:0.8rem;">{dxf_status_str}</span>'
    f'<span style="color:#cbd5e1;">|</span>'
    f'<span>대우건설 건축기술팀</span>'
    f'</div></div>'
    f'<div class="dw-page-header">'
    f'<div>'
    f'<h1>RC 보 이어치기 보강 검토 시스템</h1>'
    f'<p>CAD(DXF) 보 일람표 · KDS 기준 수직이어치기 전단마찰 보강 검토</p>'
    f'</div>'
    f'<div class="dw-member-pill">검토 대상 부재: <span style="color:#137fec; font-weight:900;">{st.session_state.selected_beam_label}</span></div>'
    f'</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        '<div class="dw-sidebar-brand">'
        '<div class="brand-title">DAEWOO E&C</div>'
        '<div class="brand-sub">RC부재 구조검토</div>'
        '</div>'
        '<div class="dw-sidebar-sec-title">1. 보 일람표(DXF) 도면 로드</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("캐드(DXF) 도면 파일 업로드", type=["dxf"], label_visibility="collapsed")

    if uploaded_file is not None:
        # 기존 세션이 구버전(schema_ver!=12)이면 자동 재파싱
        if st.session_state.dxf_filename != uploaded_file.name or st.session_state.get("schema_ver") != 12:
            with st.spinner(f"🛠️ '{uploaded_file.name}' 도면 층별 보 일람표 정밀 분석 중..."):
                try:
                    beams, ent_cnt = cached_parse_dxf(uploaded_file.getvalue(), uploaded_file.name, schema_ver=12)
                    st.session_state.extracted_beams = beams
                    st.session_state.dxf_filename = uploaded_file.name
                    st.session_state.entity_count = ent_cnt
                    st.session_state.schema_ver = 12
                    st.session_state.last_synced_beam_sec = None
                    st.toast(f"✅ '{uploaded_file.name}' 분석 완료! ({len(beams)}개 층별 보 추출)", icon="🏗️")
                except Exception as e:
                    st.error(f"DXF 분석 오류: {e}")
    elif st.session_state.extracted_beams or st.session_state.dxf_filename is not None:
        # 업로더 X 버튼으로 파일 삭제 시 즉시 미로드(직접 입력 모드)로 복귀
        st.session_state.extracted_beams = {}
        st.session_state.dxf_filename = None
        st.session_state.entity_count = 0
        st.session_state.last_synced_beam_sec = None
        st.session_state.selected_beam_label = "직접 입력"
        st.session_state.top_layers = [int(st.session_state.get("top_bars", 6))]
        st.session_state.bot_layers = [int(st.session_state.get("bot_bars", 5))]
        st.toast("↩️ 도면이 해제되어 직접 입력 모드로 전환되었습니다.", icon="✏️")
        st.rerun()

    if st.session_state.extracted_beams:
        floors_found = list(dict.fromkeys(split_floor_and_beam(k)[0] for k in st.session_state.extracted_beams.keys()))
        floors_str = ", ".join(floors_found)
        dxf_fn_disp = st.session_state.dxf_filename or ""
        st.markdown(
            f'<div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:9px; '
            f'padding:0.55rem 0.7rem; margin:0.25rem 0 0.65rem 0; color:#065f46; line-height:1.45;">'
            f'<div style="font-size:0.77rem; font-weight:800; color:#047857; margin-bottom:2px;">✅ 현재 로드된 도면</div>'
            f'<div title="{dxf_fn_disp}" style="font-size:0.68rem; color:#065f46; background:rgba(255,255,255,0.75); '
            f'border-radius:4px; padding:2px 6px; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
            f'{dxf_fn_disp}</div>'
            f'<div style="font-size:0.71rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
            f'• 층별 보 부재: <b>총 {len(st.session_state.extracted_beams)}개</b></div>'
            f'<div title="{floors_str}" style="font-size:0.71rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
            f'• 감지 층 구분: <b>{floors_str}</b></div>'
            f'<div style="font-size:0.71rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
            f'• 분석 객체 수: <b>{st.session_state.entity_count:,}개</b></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="dw-sidebar-sec-title">2. 재료 강도 및 기준 설정</div>', unsafe_allow_html=True)
    fck = st.selectbox("콘크리트 설계기준압축강도 fck (MPa)", [21, 24, 27, 30, 35, 40, 50], index=2)
    fy = st.selectbox("주철근 항복강도 fy (MPa)", [400, 500, 600], index=1)
    stirrup_fy = st.selectbox("전단철근(스터럽) 항복강도 fyt (MPa)", [400, 500, 600], index=1)
    cover = st.number_input("순피복두께 cc (mm)", min_value=20.0, max_value=120.0, value=50.0, step=5.0)
    surface_cond = st.selectbox("이어치기면 표면 상태 (마찰계수 μ)", list(ROUGHNESS_FACTOR.keys()), index=0)
    mu = ROUGHNESS_FACTOR[surface_cond]
    st.markdown('<div style="margin-top:0.8rem;"></div>', unsafe_allow_html=True)
    if st.button("🔒 로그아웃 (화면 잠금)", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown('<div class="dw-sidebar-footer">© (주)대우건설 건축기술팀</div>', unsafe_allow_html=True)

# =====================================================
# 5. DXF 보/단면 선택 영역 (로드된 경우)
# =====================================================
if st.session_state.extracted_beams:
    with st.container():
        st.markdown(
            '<div class="dw-section-card" style="margin-bottom:0.6rem;">'
            '<div class="dw-section-header">'
            '<div class="dw-section-title"><span class="dw-accent-bar"></span>보 부재 선택</div>'
            '<span class="dw-pill-blue">CAD 자동 파싱 연동</span>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        c_sel0, c_sel1, c_sel2, c_sel3 = st.columns([1.2, 1.8, 1.5, 1.6])

        all_beam_keys = list(st.session_state.extracted_beams.keys())
        floor_list = ["전체 층"] + list(dict.fromkeys(split_floor_and_beam(k)[0] for k in all_beam_keys))

        with c_sel0:
            selected_floor = st.selectbox("1️⃣ 층(Floor) 선택", floor_list)
            auto_sync = st.checkbox("🔄 선택 시 즉시 반영", value=True, help="부재 또는 단면 위치를 바꾸면 아래 구조검토 입력값에 즉시 자동 반영합니다.")

        if selected_floor == "전체 층":
            filtered_beam_list = all_beam_keys
        else:
            filtered_beam_list = [k for k in all_beam_keys if split_floor_and_beam(k)[0] == selected_floor]

        with c_sel1:
            selected_beam = st.selectbox("2️⃣ 층별 보 부호 (Floor + Mark)", filtered_beam_list)

        sections = st.session_state.extracted_beams[selected_beam]
        section_list = list(sections.keys())
        with c_sel2:
            selected_section = st.selectbox("3️⃣ 단면 위치 (Zone)", section_list)

        sec_data = sections[selected_section]
        extracted_main_dia = BAR_LIST[sec_data["main_bar_idx"]]
        fl_label, bm_only = split_floor_and_beam(selected_beam)

        def _apply_sec_to_state(b_label, s_label, s_dict):
            m_dia = BAR_LIST[s_dict["main_bar_idx"]]
            st.session_state.bw = min(max(float(s_dict["bw"]), 150.0), 5000.0)
            st.session_state.beam_depth = min(max(float(s_dict["depth"]), 200.0), 5000.0)
            if m_dia in BAR_LIST:
                st.session_state.main_bar = m_dia
            st.session_state.top_bars = min(max(int(s_dict["top_count"]), 1), 120)
            st.session_state.bot_bars = min(max(int(s_dict["bot_count"]), 1), 120)
            st.session_state.top_layers = s_dict.get("top_layers", [int(s_dict["top_count"])])
            st.session_state.bot_layers = s_dict.get("bot_layers", [int(s_dict["bot_count"])])
            if "CENTER" in s_label.upper() or "CEN" in s_label.upper():
                st.session_state.tension_zone = "하부 인장 (정모멘트 +M)"
            else:
                st.session_state.tension_zone = "상부 인장 (부모멘트 -M)"
            if int(s_dict["st_dia"]) in [10, 13, 16, 19]:
                st.session_state.st_dia = int(s_dict["st_dia"])
            st.session_state.st_spacing = min(max(float(s_dict["st_spacing"]), 50.0), 1000.0)
            st.session_state.st_legs = min(max(int(s_dict["st_legs"]), 1), 24)
            st.session_state.selected_beam_label = f"{b_label} ({s_label})"
            st.session_state.last_synced_beam_sec = (b_label, s_label)

        # 부재 또는 단면 드롭다운 변경 시 자동 동기화 (또는 이전 30가닥 제한/단수 미반영 시 즉시 복구)
        was_clamped_to_one = (
            (st.session_state.get("top_bars") == 1 and int(sec_data["top_count"]) > 1)
            or (st.session_state.get("bot_bars") == 1 and int(sec_data["bot_count"]) > 1)
            or st.session_state.get("top_layers") != sec_data.get("top_layers")
            or st.session_state.get("bot_layers") != sec_data.get("bot_layers")
        )
        if auto_sync and (st.session_state.get("last_synced_beam_sec") != (selected_beam, selected_section) or was_clamped_to_one):
            _apply_sec_to_state(selected_beam, selected_section, sec_data)

        with c_sel3:
            st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
            if st.button(
                "📥 제원표 강제 재반영",
                type="primary",
                use_container_width=True,
                help=f"'{selected_beam} [{selected_section}]' CAD 추출 제원을 아래 입력표에 다시 반영합니다.",
            ):
                _apply_sec_to_state(selected_beam, selected_section, sec_data)
                st.toast(f"'{selected_beam} - {selected_section}' 제원이 적용되었습니다!", icon="✅")
                st.rerun()

        # [핵심 추가] DXF 도면 원본 근거 화면 (기본 닫힘 상태, 클릭 시 펼쳐보기)
        with st.expander(f"🔎 [DXF 도면 원본 근거 화면] '{selected_beam} — {selected_section}' CAD 일람표 원본 도면 및 추출 근거 1:1 확인 (클릭하여 펼치기)", expanded=False):
            ev_col_cad, ev_col_tbl = st.columns([1.25, 1])
            with ev_col_cad:
                cad_cell_svg = render_dxf_cell_svg(selected_beam, selected_section, sections)
                st.markdown(cad_cell_svg, unsafe_allow_html=True)
            with ev_col_tbl:
                st.markdown(f"**📋 `{selected_beam} [{selected_section}]` DXF 원본 객체 ↔ 파싱 결과 1:1 대조표**")
                ev_rows = sec_data.get("evidence_rows", [])
                if ev_rows:
                    ev_df = pd.DataFrame(ev_rows)
                    st.dataframe(ev_df, use_container_width=True, hide_index=True, height=310)
                st.caption(
                    f"💡 **원본 검증 안내:** 좌측 화면은 업로드된 DXF 파일의 해당 보 셀 영역(CAD 좌표 "
                    f"`X={sec_data.get('cell_meta', {}).get('start_x', 0):.0f}~{sec_data.get('cell_meta', {}).get('end_x', 0):.0f}`, "
                    f"`Y={sec_data.get('cell_meta', {}).get('bottom_y', 0):.0f}~{sec_data.get('cell_meta', {}).get('top_y', 0):.0f}`)에 그려진 "
                    f"**실제 선분(LINE/LWPOLYLINE), 치수선(DIMENSION), 문자(TEXT)를 원본 좌표 그대로 투영한 화면**입니다."
                )

# =====================================================
# 6. 메인 탭 구성 (1단계: 수직 vs 수평 이어치기 기능 전환)
# =====================================================
tab_v, tab_h = st.tabs([
    "↔️ 수직 이어치기 검토",
    "↕️ 수평 이어치기 검토",
])

with tab_v:
    tab_detail, tab_schedule, tab_report = st.tabs([
        "1. 부재 별 검토",
        "2. 전체 보 일괄 구조검토표",
        "3. 구조검토 근거",
    ])

    # -----------------------------------------------------
    # [탭 1] 단면 상세 구조검토 & 시각화
    # -----------------------------------------------------
    with tab_detail:
        col_input, col_vis = st.columns([1.25, 1])

        with col_input:
            st.markdown(
                f'<div class="dw-section-card" style="margin-bottom:0.65rem;">'
                f'<div class="dw-section-header">'
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span>1. 단면 및 배근 제원 입력</div>'
                f'<span class="dw-pill-blue">현재 부재: {st.session_state.selected_beam_label}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                bw = st.number_input("보 폭 bw (mm)", min_value=150.0, max_value=5000.0, step=10.0, key="bw")
                beam_depth = st.number_input("보 춤 H (mm)", min_value=200.0, max_value=5000.0, step=10.0, key="beam_depth")
                tension_zone = st.selectbox("인장부 위치 (검토 기준)", ["상부 인장 (부모멘트 -M)", "하부 인장 (정모멘트 +M)"], key="tension_zone")
            with ic2:
                main_bar = st.selectbox("주근 직경 (mm)", BAR_LIST, key="main_bar")
                top_bars = st.number_input("상부 주근수 (TOP)", min_value=1, max_value=120, step=1, key="top_bars")
                bot_bars = st.number_input("하부 주근수 (BOT)", min_value=1, max_value=120, step=1, key="bot_bars")
            with ic3:
                stirrup_bar = st.selectbox("스터럽 직경 (mm)", [10, 13, 16, 19], key="st_dia")
                stirrup_legs = st.number_input("스터럽 가닥수 (Legs)", min_value=1, max_value=24, step=1, key="st_legs")
                stirrup_spacing = st.number_input("스터럽 간격 s (mm)", min_value=50.0, max_value=1000.0, step=10.0, key="st_spacing")

            st.markdown(
                '<div class="dw-section-card" style="margin-top:0.75rem; margin-bottom:0.5rem;">'
                '<div class="dw-section-header">'
                '<div class="dw-section-title"><span class="dw-accent-bar"></span>2. 하중 및 요구 전단력(Vu) / 휨모멘트(Mu) 산정 조건</div>'
                '<span class="dw-pill-blue">전단마찰 조건</span>'
                '</div></div>',
                unsafe_allow_html=True,
            )
            calc_method = st.radio(
                "전단력(Vu) 산정 방식 선택",
                [
                    "1차 현장 검토 (단면 설계전단강도를 작용 전단력으로 가정)",
                    "2차 본사 검토 (최적화, 보 순경간 및 단부 거리에 따른 전단력 감소 적용 등)",
                    "구조계산서 기반 검토 (구조계산서 계수하중 Vu, Mu 직접 입력)",
                ],
            )

            clear_span, joint_x, actual_vu, actual_mu = 8000.0, 2000.0, 150.0, 250.0
            if ("위치 기반" in calc_method) or ("2차 본사" in calc_method):
                lc1, lc2 = st.columns(2)
                with lc1:
                    clear_span = st.number_input("보 순경간 Ln (mm)", min_value=1000.0, max_value=30000.0, value=8000.0, step=100.0)
                with lc2:
                    joint_x = st.number_input("단부면에서 이어치기면까지 거리 x (mm)", min_value=0.0, max_value=15000.0, value=2000.0, step=100.0)
            elif ("실데이터" in calc_method) or ("구조계산서 기반" in calc_method):
                lc1, lc2 = st.columns(2)
                with lc1:
                    actual_vu = st.number_input("실제 계수전단력 Vu (kN)", min_value=0.0, max_value=10000.0, value=250.0, step=10.0)
                with lc2:
                    actual_mu = st.number_input("실제 계수휨모멘트 Mu (kN·m)", min_value=0.0, max_value=10000.0, value=300.0, step=10.0)

        # 구조검토 실행
        res = evaluate_beam_section(
            bw=bw, H=beam_depth, cover=cover, fck=fck, fy=fy, fyt=stirrup_fy,
            main_dia=main_bar, top_bars=top_bars, bot_bars=bot_bars,
            st_dia=stirrup_bar, st_legs=stirrup_legs, st_spacing=stirrup_spacing,
            tension_zone=tension_zone, mu=mu,
            calc_method=calc_method, clear_span=clear_span, joint_x=joint_x,
            actual_vu=actual_vu, actual_mu=actual_mu,
        )
        if ("실데이터" not in calc_method) and ("구조계산서 기반" not in calc_method):
            # 기본 휨모멘트 참조값은 0.75 * phiMn으로 표시
            actual_mu = round(res["phiMn_active"] * 0.7, 1)
            res["dc_flex"] = actual_mu / max(res["phiMn_active"], 1.0)

        with col_vis:
            st.markdown(
                '<div class="dw-section-card" style="margin-bottom:0.65rem;">'
                '<div class="dw-section-header">'
                '<div class="dw-section-title"><span class="dw-accent-bar"></span>실시간 보 단면 배근도 (CAD Cross-Section)</div>'
                '<span class="dw-pill-blue">단면 시각화</span>'
                '</div></div>',
                unsafe_allow_html=True,
            )
            svg_html = render_beam_svg(
                bw=bw, H=beam_depth, cover=cover, main_dia=main_bar,
                top_bars=top_bars, bot_bars=bot_bars,
                st_dia=stirrup_bar, st_legs=stirrup_legs, st_spacing=stirrup_spacing,
                tension_zone=tension_zone, add_ea=res["add_ea"],
                top_layers=st.session_state.get("top_layers"),
                bot_layers=st.session_state.get("bot_layers"),
            )
            st.markdown(svg_html, unsafe_allow_html=True)
            st.caption(
                f"🔴 빨간색: 인장측 주근({res['tension_bars']}-D{main_bar}) | "
                f"🔵 파란색: 압축측 주근 | "
                f"🟢 초록점선: 전단마찰 추가 보강근({res['add_ea']}EA)  \n"
                f"📏 1단 최대 배근 가능: {res['max_bars_single_layer']}EA (순간격 상부 {res['clear_top']:.1f}mm / 하부 {res['clear_bot']:.1f}mm)"
            )

        # =====================================================
        # 핵심 KPI 카드 & 4대 구조검토 결과 요약
        # =====================================================
        st.markdown(
            '<div class="dw-section-card" style="margin-top:1rem; margin-bottom:0.75rem;">'
            '<div class="dw-section-header">'
            '<div class="dw-section-title"><span class="dw-accent-bar"></span>3. 종합 구조검토 대시보드 (KDS 기준)</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        if res["min_rebar_std_ok"]:
            flex_kpi_delta = f"철근비 ρ={res['rho']*100:.2f}% ≥ 최소 {res['rho_min']*100:.2f}% (만족)"
            flex_foot_col = "#137fec"
        elif res["min_rebar_4_3_ok"]:
            flex_kpi_delta = f"ρ={res['rho']*100:.2f}% (4/3·As,req 예외규정 만족)"
            flex_foot_col = "#137fec"
        else:
            flex_kpi_delta = f"ρ={res['rho']*100:.2f}% < 최소 {res['rho_min']*100:.2f}% (4/3규정 미달)"
            flex_foot_col = "#dc2626"

        if ("보수적" in calc_method) or ("1차 현장" in calc_method):
            shear_kpi_delta = f"ΦVc {0.75*res['Vc']:.0f} + ΦVs {0.75*min(res['Vs'], res['Vs_max']):.0f} kN (이어치기 가정치로 적용)"
            shear_foot_col = "#137fec"
        elif ("위치 기반" in calc_method) or ("2차 본사" in calc_method):
            shear_kpi_delta = f"이어치기 가정 Vu={res['Vu']:.1f} kN (강도의 {res['reduction_factor']*100:.0f}% 적용)"
            shear_foot_col = "#137fec"
        else:
            shear_kpi_delta = f"계산서 Vu={res['Vu']:.1f} kN (전단 강도비 {res['dc_shear']*100:.0f}%)"
            shear_foot_col = "#137fec" if res["dc_shear"] <= 1.0 else "#dc2626"

        diff_area = res["Ast"] - res["Avf"]
        sf_foot_col = "#16a34a" if res["sf_ok"] else "#dc2626"
        sf_val_str = "보강 불필요" if res["sf_ok"] else f"+{res['add_ea']} EA (D{main_bar})"
        sf_delta_str = "전단마찰 안전 (OK)" if res["sf_ok"] else f"부족 철근량 {res['add_area']:.0f} mm²"

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                f'<div class="dw-kpi-card">'
                f'<div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">① 설계 휨강도 (ΦMn)</div>'
                f'<div class="dw-kpi-val">{res["phiMn_active"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN·m</span></div>'
                f'</div>'
                f'<div class="dw-kpi-foot" style="color:{flex_foot_col};"><span>{flex_kpi_delta}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f'<div class="dw-kpi-card">'
                f'<div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">② 설계 전단강도 (ΦVn)</div>'
                f'<div class="dw-kpi-val">{res["phiVn"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN</span></div>'
                f'</div>'
                f'<div class="dw-kpi-foot" style="color:{shear_foot_col};"><span>{shear_kpi_delta}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                f'<div class="dw-kpi-card">'
                f'<div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">③ 보유 vs 요구 전단마찰 철근량</div>'
                f'<div class="dw-kpi-val">{res["Ast"]:.0f} <span style="font-size:1.1rem; font-weight:700; color:#94a3b8;">/ {res["Avf"]:.0f} mm²</span></div>'
                f'</div>'
                f'<div class="dw-kpi-foot" style="color:{sf_foot_col};"><span>차이: {diff_area:+.0f} mm² (D/C {res["dc_sf"]:.2f})</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                f'<div class="dw-kpi-card">'
                f'<div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">④ 수직이어치기 추가 보강근</div>'
                f'<div class="dw-kpi-val" style="color:{sf_foot_col};">{sf_val_str}</div>'
                f'</div>'
                f'<div class="dw-kpi-foot" style="color:{sf_foot_col};"><span>{sf_delta_str}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 최종 결론 배너 (역기획: Step 4 Final Conclusion 스타일)
        if res["sf_ok"]:
            st.markdown(
                f'<div class="dw-conclusion-ok">'
                f'<div>'
                f'<div style="font-size:0.75rem; font-weight:800; color:#1e40af; text-transform:uppercase; letter-spacing:0.03em;">FINAL CONCLUSION · 수직이어치기 전단마찰 판정</div>'
                f'<div style="font-size:0.95rem; font-weight:800; color:#1e3a8a; margin-top:4px;">'
                f'현재 인장측 주근({res["tension_bars"]}-D{main_bar}, Ast={res["Ast"]:.0f} mm²)만으로 요구 전단마찰 철근량(Avf={res["Avf"]:.0f} mm²)을 만족하여 추가 보강근이 필요하지 않습니다.'
                f'</div></div>'
                f'<div class="dw-decision-pill-ok">보강 불필요 (OK)</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="dw-conclusion-ng">'
                f'<div>'
                f'<div style="font-size:0.75rem; font-weight:800; color:#991b1b; text-transform:uppercase; letter-spacing:0.03em;">FINAL CONCLUSION · 수직이어치기 전단마찰 판정 및 현장 조치</div>'
                f'<div style="font-size:0.95rem; font-weight:800; color:#b91c1c; margin-top:4px;">'
                f'요구 전단마찰 철근량(Avf={res["Avf"]:.0f} mm²) 대비 보유 주근량(Ast={res["Ast"]:.0f} mm²)이 {res["add_area"]:.0f} mm² 부족합니다. '
                f'이어치기면에 D{main_bar} 철근 최소 {res["add_ea"]}EA를 추가 배근하거나 구조 담당에게 문의하세요.'
                f'</div></div>'
                f'<div class="dw-decision-pill-ng">+{res["add_ea"]}-D{main_bar} 보강 필요</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 4개 세부 검토 카드
        rc1, rc2 = st.columns(2)
        with rc1:
            flex_ok = res["min_rebar_ok"] and res["eps_t_active"] >= 0.004
            if res["min_rebar_std_ok"] and res["eps_t_active"] >= 0.004:
                flex_badge_str = "OK (적정)"
            elif res["min_rebar_4_3_ok"] and res["eps_t_active"] >= 0.004:
                flex_badge_str = "OK (4/3·As,req 예외규정 만족)"
            else:
                flex_badge_str = "점검 필요"

            if res["min_rebar_std_ok"]:
                min_rebar_li = f'<li><b>최소철근량 일반식 (As,min):</b> {res["As_min"]:.0f} mm² vs 보유 {res["Ast"]:.0f} mm² (<b>만족</b>)</li>'
            else:
                min_rebar_li = (
                    f'<li><b>최소철근량 일반식 (As,min):</b> {res["As_min"]:.0f} mm² vs 보유 {res["Ast"]:.0f} mm² (대단면 예외규정 적용 대상)</li>'
                    f'<li><b>KDS 14 20 20 (4.2.2(3)) 예외규정 (As ≥ 4/3·As,req):</b> '
                    f'소요철근량({res["As_req"]:.0f} mm²)의 4/3배({res["As_min_4_3"]:.0f} mm²) 이상 배근 '
                    f'(<b>{"만족" if res["min_rebar_4_3_ok"] else "미달 NG"}</b> — 허용 최대 As,req ≤ {res["As_req_allow_4_3"]:.0f} mm² / Mu ≤ {res["Mu_allow_4_3"]:.1f} kN·m)</li>'
                )

            st.markdown(
                f'<div class="status-card">'
                f'<h4><span><span class="dw-accent-bar" style="height:15px; margin-right:8px; vertical-align:middle;"></span>1) 휨(Flexure) 및 철근비 검토</span><span class="{"badge-ok" if flex_ok else "badge-warn"}">{flex_badge_str}</span></h4>'
                f'<ul>'
                f'<li><b>유효춤 (d):</b> {res["d"]:.1f} mm (총춤 H={res["H"]:.0f}mm, 피복={res["cover"]:.0f}mm)</li>'
                f'<li><b>상부(단부) 설계휨강도 ΦMn(-):</b> {res["phiMn_top"]:.1f} kN·m ({top_bars}-D{main_bar}, As={res["As_top"]:.0f} mm²)</li>'
                f'<li><b>하부(중앙) 설계휨강도 ΦMn(+):</b> {res["phiMn_bot"]:.1f} kN·m ({bot_bars}-D{main_bar}, As={res["As_bot"]:.0f} mm²)</li>'
                f'{min_rebar_li}'
                f'<li><b>순인장변형률 (εt):</b> {res["eps_t_active"]:.5f} (강도감소계수 Φ={res["phi_f_active"]:.2f})</li>'
                f'</ul></div>',
                unsafe_allow_html=True,
            )

        with rc2:
            shear_ok = (res["Vu"] <= res["phiVn"] + 0.1) and res["stirrup_detail_ok"]
            if ("보수적" in calc_method) or ("1차 현장" in calc_method):
                shear_cap_li = (
                    f'<li><b>단면 설계전단강도 (ΦVn):</b> {res["phiVn"]:.1f} kN '
                    f'(보수적 가정: 설계전단강도를 작용전단력으로 적용)</li>'
                )
            elif ("위치 기반" in calc_method) or ("2차 본사" in calc_method):
                shear_cap_li = (
                    f'<li><b>단면 설계전단강도 (ΦVn):</b> {res["phiVn"]:.1f} kN '
                    f'(이어치기 위치 x={joint_x:.0f}mm 저감 반영 가정 전단력 Vu = {res["Vu"]:.1f} kN 적용, 강도의 {res["reduction_factor"]*100:.0f}%)</li>'
                )
            else:
                shear_cap_li = (
                    f'<li><b>단면 설계전단강도 (ΦVn):</b> {res["phiVn"]:.1f} kN vs 구조계산서 계수전단력 Vu = {res["Vu"]:.1f} kN '
                    f'(전단 강도비 Vu/ΦVn = {res["dc_shear"]:.2f})</li>'
                )

            st.markdown(
                f'<div class="status-card">'
                f'<h4><span><span class="dw-accent-bar" style="height:15px; margin-right:8px; vertical-align:middle;"></span>2) 전단(Shear) 및 스터럽 배근 검토</span><span class="{"badge-ok" if shear_ok else "badge-warn"}">{"OK (적정)" if shear_ok else "간격/철근량 확인"}</span></h4>'
                f'<ul>'
                f'<li><b>콘크리트 전단강도 (Vc):</b> {res["Vc"]:.1f} kN | <b>스터럽 전단강도 (Vs):</b> {res["Vs"]:.1f} kN</li>'
                f'{shear_cap_li}'
                f'<li><b>전단철근 단면적 (Asv):</b> {res["Asv"]:.1f} mm² (최소 요구 Av,min = {res["Av_min"]:.1f} mm²)</li>'
                f'<li><b>스터럽 간격 (s):</b> {stirrup_spacing:.0f} mm vs 최대허용간격 s_max = {res["s_max"]:.0f} mm ({"만족" if stirrup_spacing <= res["s_max"] else "간격 초과"})</li>'
                f'<li><b>주근 순간격:</b> 상부 {res["clear_top"]:.1f} mm / 하부 {res["clear_bot"]:.1f} mm (최소 {res["min_clear_spacing"]:.0f} mm {"만족" if res["spacing_ok"] else "2단 배근 적용"})</li>'
                f'</ul></div>',
                unsafe_allow_html=True,
            )

        # 경간 위치(x)에 따른 필요 보강근 시뮬레이션 차트 (기본 닫힘 상태, 클릭 시 펼쳐보기)
        with st.expander("📈 [최적화 시뮬레이션] 단부로부터의 이어치기 위치(x)별 작용 전단력(Vu) 및 필요 보강근 대수 분석 (클릭하여 펼치기)", expanded=False):
            sim_rows = []
            half_L = max(clear_span / 2.0, 1000.0)
            # 안전하게 무보강 이어치기가 가능한 최소 거리 x_safe 역산
            Vu_capacity = (res["Ast"] * 0.75 * fy * mu) / 1000.0  # kN
            if Vu_capacity >= res["phiVn"]:
                x_safe = 0.0
            else:
                x_safe = half_L * (1.0 - Vu_capacity / max(res["phiVn"], 1.0))

            st.info(
                f"💡 **무보강 수직이어치기 가능 위치 가이드:** 단부로부터 **$x \\ge {x_safe:.0f}\\text{{ mm}}$ ({x_safe/1000:.2f} m)** 이상 떨어진 지점에서 "
                f"수직이어치기를 시공하면 추가 보강근 없이 기존 주근({res['tension_bars']}-D{main_bar})만으로 전단마찰 안전성을 확보할 수 있습니다."
            )
            for ratio in [0.0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5]:
                x_pos = clear_span * ratio
                red = max(0.0, (half_L - x_pos) / half_L)
                vu_x = res["phiVn"] * red
                avf_x = vu_x * 1000.0 / (0.75 * fy * mu)
                need_x = max(0.0, avf_x - res["Ast"])
                ea_x = math.ceil(need_x / res["As_unit"]) if need_x > 0 else 0
                sim_rows.append({
                    "단부 거리 x (mm)": int(x_pos),
                    "경간비 (x/Ln)": f"{ratio:.2f}",
                    "감소계수": round(red, 2),
                    "작용전단력 Vu(x) [kN]": round(vu_x, 1),
                    "요구철근량 Avf [mm²]": round(avf_x, 0),
                    "보유철근량 Ast [mm²]": round(res["Ast"], 0),
                    "추가 보강근 (EA)": ea_x,
                    "판정": "✅ 무보강 OK" if ea_x == 0 else f"🚨 +{ea_x}-D{main_bar} 보강",
                })
            sim_df = pd.DataFrame(sim_rows)
            st.dataframe(sim_df, use_container_width=True, hide_index=True)

    # -----------------------------------------------------
    # [탭 2] DXF 전체 보 일람표 일괄 구조검토 (Batch Screening)
    # -----------------------------------------------------
    with tab_schedule:
        st.markdown(
            '<div class="dw-section-card" style="margin-bottom:0.75rem;">'
            '<div class="dw-section-header">'
            '<div class="dw-section-title"><span class="dw-accent-bar"></span>전체 부재 구조검토표</div>'
            '<span class="dw-pill-blue">전 부재 일괄 스크리닝</span>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        if not st.session_state.extracted_beams:
            st.warning("좌측 사이드바에서 DXF 파일을 업로드하거나 '폴더 내 지하주차장 보 일람표.dxf 즉시 로드' 버튼을 눌러주세요.")
        else:
            all_b_keys = list(st.session_state.extracted_beams.keys())
            floor_list_batch = []
            for bk in all_b_keys:
                fl_str, _ = split_floor_and_beam(bk)
                if fl_str not in floor_list_batch:
                    floor_list_batch.append(fl_str)

            bc1, bc2, bc3, bc4 = st.columns(4)
            with bc1:
                batch_floor = st.selectbox("층(Floor) 필터", ["전체 층 보기"] + floor_list_batch)
            with bc2:
                batch_mode = st.selectbox(
                    "일괄 검토 전단력 기준",
                    [
                        "보수적 스크리닝 (Vu = ΦVn, x=0 단부 최대전단 가정)",
                        "1/4 경간 위치 이어치기 (x = Ln/4, Vu = 0.5·ΦVn)",
                        "1/3 경간 위치 이어치기 (x = Ln/3, Vu = 0.33·ΦVn)",
                    ],
                    index=1,
                )
            with bc3:
                filter_status = st.selectbox("검토 결과 필터", ["전체 보기", "🚨 보강 필요(NG)만 보기", "✅ 안전(OK)만 보기"])
            with bc4:
                search_beam = st.text_input("보 부호 검색 (예: G1, B11, -3 G1)", "")

            batch_rows = []
            for b_name, secs in st.session_state.extracted_beams.items():
                fl_label, pure_mark = split_floor_and_beam(b_name)
                if batch_floor != "전체 층 보기" and fl_label != batch_floor:
                    continue
                if search_beam and search_beam.upper() not in b_name.upper():
                    continue
                for s_name, s_info in secs.items():
                    m_dia = BAR_LIST[s_info["main_bar_idx"]]
                    t_zone = "하부 인장 (정모멘트 +M)" if ("CENTER" in s_name.upper() or "CEN" in s_name.upper()) else "상부 인장 (부모멘트 -M)"
                    if "1/4" in batch_mode:
                        c_meth = "위치 기반"
                        j_x = 2000.0
                    elif "1/3" in batch_mode:
                        c_meth = "위치 기반"
                        j_x = 2667.0
                    else:
                        c_meth = "보수적"
                        j_x = 0.0

                    r_b = evaluate_beam_section(
                        bw=s_info["bw"], H=s_info["depth"], cover=cover,
                        fck=fck, fy=fy, fyt=stirrup_fy,
                        main_dia=m_dia, top_bars=s_info["top_count"], bot_bars=s_info["bot_count"],
                        st_dia=s_info["st_dia"], st_legs=s_info["st_legs"], st_spacing=s_info["st_spacing"],
                        tension_zone=t_zone, mu=mu,
                        calc_method=c_meth, clear_span=8000.0, joint_x=j_x,
                    )
                    status_str = "✅ 안전 (OK)" if r_b["sf_ok"] else f"🚨 보강 (+{r_b['add_ea']}-D{m_dia})"
                    if filter_status == "🚨 보강 필요(NG)만 보기" and r_b["sf_ok"]:
                        continue
                    if filter_status == "✅ 안전(OK)만 보기" and not r_b["sf_ok"]:
                        continue

                    batch_rows.append({
                        "층 표기": fl_label,
                        "보 부호": pure_mark,
                        "전체 부재명(층+부호)": b_name,
                        "단면 위치": s_name,
                        "단면 (bw×H)": f"{s_info['bw']:.0f}×{s_info['depth']:.0f}",
                        "주근 직경": f"D{m_dia}",
                        "상부근(TOP)": s_info["top_count"],
                        "하부근(BOT)": s_info["bot_count"],
                        "스터럽": f"{s_info['st_legs']}-D{s_info['st_dia']}@{s_info['st_spacing']:.0f}",
                        "인장기준": t_zone,
                        "설계휨강도 ΦMn (kN·m)": round(r_b["phiMn_active"], 1),
                        "설계전단강도 ΦVn (kN)": round(r_b["phiVn"], 1),
                        "작용전단력 Vu (kN)": round(r_b["Vu"], 1),
                        "보유철근 Ast (mm²)": round(r_b["Ast"], 0),
                        "요구철근 Avf (mm²)": round(r_b["Avf"], 0),
                        "D/C 비": round(r_b["dc_sf"], 2),
                        "검토 판정": status_str,
                    })

            batch_df = pd.DataFrame(batch_rows)
            total_cnt = len(batch_df)
            ok_cnt = sum(1 for r in batch_rows if "안전" in r["검토 판정"])
            ng_cnt = total_cnt - ok_cnt

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top"><div class="dw-kpi-label">검토 단면 총수</div>'
                    f'<div class="dw-kpi-val">{total_cnt} <span style="font-size:1rem; color:#64748b;">개소</span></div></div>'
                    f'<div class="dw-kpi-foot" style="color:#137fec;"><span>필터링된 전체 검토 대상</span></div></div>',
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top"><div class="dw-kpi-label">안전 (무보강 OK)</div>'
                    f'<div class="dw-kpi-val" style="color:#137fec;">{ok_cnt} <span style="font-size:1rem; color:#64748b;">개소</span></div></div>'
                    f'<div class="dw-kpi-foot" style="color:#137fec;"><span>비율: {(ok_cnt/max(total_cnt,1))*100:.1f}%</span></div></div>',
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top"><div class="dw-kpi-label">보강 필요 (NG)</div>'
                    f'<div class="dw-kpi-val" style="color:{"#dc2626" if ng_cnt > 0 else "#111418"};">{ng_cnt} <span style="font-size:1rem; color:#64748b;">개소</span></div></div>'
                    f'<div class="dw-kpi-foot" style="color:{"#dc2626" if ng_cnt > 0 else "#16a34a"};"><span>{"다우얼바 보강 또는 위치 조정 대상" if ng_cnt > 0 else "전 단면 안전"}</span></div></div>',
                    unsafe_allow_html=True,
                )

            st.dataframe(batch_df, use_container_width=True, hide_index=True, height=480)

            csv_bytes = batch_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 전체 보 구조검토 일람표 (CSV/엑셀 호환) 다운로드",
                data=csv_bytes,
                file_name=f"보_구조검토_일람표_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary",
            )

    # -----------------------------------------------------
    # [탭 3] 본사/감리 제출용 구조검토 보고서 출력
    # -----------------------------------------------------
    with tab_report:
        st.markdown(
            '<div class="dw-section-card" style="margin-bottom:0.75rem;">'
            '<div class="dw-section-header">'
            '<div class="dw-section-title"><span class="dw-accent-bar"></span>구조검토 계산 근거</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        beta1_val = 0.85 if fck <= 28 else max(0.65, 0.85 - 0.007 * (fck - 28))
        cmp_sym = r"\ge" if res["sf_ok"] else "<"
        judge_md_str = "✅ 안전 (보강 불필요)" if res["sf_ok"] else f"🚨 보강 필요 (D{main_bar} 철근 {res['add_ea']}EA 추가 배근)"
        judge_html_str = "안전 (무보강 OK)" if res["sf_ok"] else f"보강 필요 (+{res['add_ea']}-D{main_bar})"
        if res["min_rebar_std_ok"]:
            min_rebar_ok_str = "O.K (일반식 만족)"
            min_rebar_html_str = "OK (일반식 만족)"
            min_rebar_detail_md = f"- **최소철근량 ($A_{{s,\\min}}$):** $\\max\\left(\\frac{{0.25\\sqrt{{f_{{ck}}}}}}{{f_y}}b_w d,\\; \\frac{{1.4}}{{f_y}}b_w d\\right) = \\mathbf{{{res['As_min']:.1f}\\text{{ mm}}^2}} \\le A_s = {res['Ast']:.1f}\\text{{ mm}}^2$ **({min_rebar_ok_str})**"
        elif res["min_rebar_4_3_ok"]:
            min_rebar_ok_str = "O.K (KDS 14 20 20 4.2.2(3) 4/3·As,req 예외규정 만족)"
            min_rebar_html_str = "OK (4/3·As,req 예외규정 만족)"
            min_rebar_detail_md = (
                f"- **최소철근량 ($A_{{s,\\min}}$):** 일반식 ${res['As_min']:.1f}\\text{{ mm}}^2$ 대비 대단면 예외규정(KDS 14 20 20 4.2.2(3)) 적용 → "
                f"$\\frac{{4}}{{3}} A_{{s,\\text{{req}}}} = \\mathbf{{{res['As_min_4_3']:.1f}\\text{{ mm}}^2}} \\le A_s = {res['Ast']:.1f}\\text{{ mm}}^2$ **({min_rebar_ok_str})**"
            )
        else:
            min_rebar_ok_str = "N.G"
            min_rebar_html_str = "최소철근 확인"
            min_rebar_detail_md = f"- **최소철근량 ($A_{{s,\\min}}$):** ${res['As_min']:.1f}\\text{{ mm}}^2$ 및 $\\frac{{4}}{{3}} A_{{s,\\text{{req}}}} = {res['As_min_4_3']:.1f}\\text{{ mm}}^2 > A_s = {res['Ast']:.1f}\\text{{ mm}}^2$ **({min_rebar_ok_str})**"
        method_short = calc_method.split("(")[0].strip()

        report_md = f"""
### RC 보 부재 구조검토 및 수직이어치기 전단마찰 계산서

- **검토 대상 부재:** `{st.session_state.selected_beam_label}` (도면: `{st.session_state.dxf_filename or '수동 입력'}`)
- **적용 설계기준:** KDS 14 20 20 (콘크리트구조 휨 및 압축 설계기준), KDS 14 20 22 (콘크리트구조 전단 및 비틀림 설계기준)
- **검토 일시:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

#### 1. 단면 및 재료 제원
| 구분 | 항목 | 적용값 | 비고 |
|:---:|:---|:---:|:---|
| **단면 치수** | 보 폭 ($b_w$) × 보 춤 ($H$) | **{bw:.0f} × {beam_depth:.0f} mm** | 유효춤 $d = {res['d']:.1f}\\text{{ mm}}$ (피복 {cover:.0f} mm) |
| **재료 강도** | 콘크리트 ($f_{{ck}}$) / 주근 ($f_y$) / 스터럽 ($f_{{yt}}$) | **{fck} / {fy} / {stirrup_fy} MPa** | $\\beta_1 = {beta1_val:.3f}$ |
| **주근 배근** | 상부근 (TOP) / 하부근 (BOT) | **{top_bars}-D{main_bar} / {bot_bars}-D{main_bar}** | 단면적 1본당 $A_b = {res['As_unit']:.2f}\\text{{ mm}}^2$ |
| **전단철근** | 스터럽 배근 (Stirrup) | **{stirrup_legs}-D{stirrup_bar} @ {stirrup_spacing:.0f}** | $A_{{sv}} = {res['Asv']:.2f}\\text{{ mm}}^2$ |

---

#### 2. 휨강도 검토 (KDS 14 20 20)
- **인장측 검토 위치:** {tension_zone} ($A_s = {res['tension_bars']} \\times {res['As_unit']:.2f} = {res['Ast']:.1f}\\text{{ mm}}^2$)
{min_rebar_detail_md}
- **등가응력블록 깊이 ($a$):** $a = \\frac{{A_s f_y}}{{0.85 f_{{ck}} b_w}} = \\mathbf{{{res['a_active']:.1f}\\text{{ mm}}}}$
- **설계 휨강도 ($\\phi M_n$):** $\\phi A_s f_y \\left(d - \\frac{{a}}{{2}}\\right) = \\mathbf{{{res['phiMn_active']:.1f}\\text{{ kN·m}}}}$ (상부 $\\phi M_n = {res['phiMn_top']:.1f}\\text{{ kN·m}}$, 하부 $\\phi M_n = {res['phiMn_bot']:.1f}\\text{{ kN·m}}$)

---

#### 3. 전단강도 검토 (KDS 14 20 22)
- **콘크리트 전단강도 ($V_c$):** $\\frac{{1}}{{6}}\\sqrt{{f_{{ck}}}} b_w d = \\frac{{1}}{{6}}\\sqrt{{{fck}}} \\times {bw:.0f} \\times {res['d']:.1f} \\div 1000 = \\mathbf{{{res['Vc']:.1f}\\text{{ kN}}}}$
- **전단철근 전단강도 ($V_s$):** $\\frac{{A_{{sv}} f_{{yt}} d}}{{s}} = \\frac{{{res['Asv']:.1f} \\times {stirrup_fy} \\times {res['d']:.1f}}}{{{stirrup_spacing:.0f}}} \\div 1000 = \\mathbf{{{res['Vs']:.1f}\\text{{ kN}}}}$
- **설계 전단강도 ($\\phi V_n$):** $0.75 \\times ({res['Vc']:.1f} + {res['Vs']:.1f}) = \\mathbf{{{res['phiVn']:.1f}\\text{{ kN}}}}$

---

#### 4. 수직이어치기면 전단마찰 상세 검토 (KDS 14 20 22 - 4.5)
- **작용 계수전단력 ($V_u$):** $\\mathbf{{{res['Vu']:.1f}\\text{{ kN}}}}$ *(산정 기준: {method_short}, 감소계수 {res['reduction_factor']:.2f})*
- **이어치기면 마찰계수 ($\\mu$):** $\\mathbf{{{mu}}}$ *({surface_cond})*
- **요구 전단마찰 철근량 ($A_{{vf}}$):**
  $$A_{{vf}} = \\frac{{V_u}}{{\\phi f_y \\mu}} \\times 1000 = \\frac{{{res['Vu']:.1f}}}{{0.75 \\times {fy} \\times {mu}}} \\times 1000 = \\mathbf{{{res['Avf']:.1f}\\text{{ mm}}^2}}$$
- **보유 인장철근량 ($A_{{st}}$):** {res['tension_bars']} EA × {res['As_unit']:.2f} mm² = $\\mathbf{{{res['Ast']:.1f}\\text{{ mm}}^2}}$
- **검토 결과:** $A_{{st}} ({res['Ast']:.1f}\\text{{ mm}}^2) {cmp_sym} A_{{vf}} ({res['Avf']:.1f}\\text{{ mm}}^2)$ → **{judge_md_str}**
"""
        st.markdown(report_md)

        html_report = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>구조검토보고서 - {st.session_state.selected_beam_label}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>
body {{ font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', sans-serif; max-width: 900px; margin: 30px auto; color: #1e293b; line-height: 1.6; }}
h1 {{ border-bottom: 3px solid #1e3a8a; padding-bottom: 10px; color: #0f172a; }}
table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: 10px 12px; text-align: left; }}
th {{ background: #f1f5f9; font-weight: bold; }}
.box {{ background: #f8fafc; border-left: 5px solid #2563eb; padding: 14px 18px; margin: 16px 0; }}
</style>
</head>
<body>
<h1>RC 보 부재 구조검토 계산근거</h1>
<p><b>검토 부재:</b> {st.session_state.selected_beam_label} | <b>검토 일자:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<div style="text-align:center; margin: 20px 0;">{svg_html}</div>
<table>
<tr><th>항목</th><th>산정식 및 기준</th><th>결과값</th><th>판정</th></tr>
<tr><td>보 단면 / 유효춤</td><td>bw × H (d)</td><td>{bw:.0f} × {beam_depth:.0f} mm (d={res['d']:.1f} mm)</td><td>-</td></tr>
<tr><td>설계 휨강도 (ΦMn)</td><td>상부 {top_bars}-D{main_bar} / 하부 {bot_bars}-D{main_bar}</td><td>{res['phiMn_active']:.1f} kN·m</td><td>{min_rebar_html_str}</td></tr>
<tr><td>설계 전단강도 (ΦVn)</td><td>0.75 × (Vc={res['Vc']:.1f} + Vs={res['Vs']:.1f})</td><td>{res['phiVn']:.1f} kN</td><td>OK</td></tr>
<tr><td>전단마찰 검토 (Avf vs Ast)</td><td>Vu={res['Vu']:.1f} kN, μ={mu}</td><td>요구 {res['Avf']:.1f} mm² / 보유 {res['Ast']:.1f} mm²</td><td><b>{judge_html_str}</b></td></tr>
</table>
</body>
</html>"""

        st.download_button(
            label="🖨️ 인쇄/결재용 HTML 구조검토 계산근거 다운로드",
            data=html_report.encode("utf-8"),
            file_name=f"구조검토서_{st.session_state.selected_beam_label.replace(' ', '_')}.html",
            mime="text/html",
        )


# =====================================================
# [메인 탭 2] 수평 이어치기 검토 (Horizontal Joint)
# =====================================================
with tab_h:
    st.markdown(
        f'<div class="dw-section-card" style="margin-bottom:0.75rem;">'
        f'<div class="dw-section-header">'
        f'<div class="dw-section-title"><span class="dw-accent-bar"></span>RC 보 수평 이어치기 전단마찰 검토</div>'
        f'<span class="dw-pill-blue">현재 부재: {st.session_state.selected_beam_label}</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # 1. 검토 모드 선택 라디오 버튼 (일반 검토 vs 관리자 전용 정밀 검토)
    hj_mode_options = [
        "일반 검토 모드 (표준 보수적 검토 - 전단 흐름 최대치 기준)",
        "정밀 검토 모드 (타설 높이별 전단 흐름 Q/I 정밀 검토 - 관리자 전용)",
    ]
    hj_selected_mode = st.radio(
        "수평 이어치기 검토 모드 선택",
        hj_mode_options,
        index=0,
        horizontal=True,
        key="hj_mode_radio",
    )
    is_hj_precision_selected = ("정밀 검토 모드" in hj_selected_mode)

    # 2. 정밀 검토 모드 선택 시 전용 관리자 코드 인증 게이트
    hj_can_render = True
    if is_hj_precision_selected and not st.session_state.get("precision_unlocked", False):
        hj_can_render = False
        st.markdown(
            '<div style="background:#ffffff; border:1px solid #bfdbfe; border-left:5px solid #137fec; '
            'border-radius:12px; padding:1.25rem 1.5rem; margin:0.75rem 0 1rem 0; box-shadow:0 4px 14px rgba(19,127,236,0.08);">'
            '<div style="font-size:1.0rem; font-weight:800; color:#1e3a8a; margin-bottom:0.3rem;">🔒 관리자 전용 정밀 검토 모드 잠금</div>'
            '<div style="font-size:0.86rem; color:#475569; line-height:1.5;">'
            '타설 높이(<b>h_joint</b>)에 따른 균열단면 압축대(<b>c</b>) 내 포물선 전단흐름 저감계수(<b>αq</b>) 및 철근 절감 검토는 '
            '관리자 전용 정밀 검토 코드 인증 후 활성화됩니다.'
            '</div></div>',
            unsafe_allow_html=True,
        )
        col_lock_l, col_lock_c, col_lock_r = st.columns([1, 1.6, 1])
        with col_lock_c:
            with st.form("hj_precision_unlock_form", clear_on_submit=False):
                admin_input = st.text_input(
                    "정밀 검토 전용 관리자 코드 입력",
                    type="password",
                    placeholder="관리자 코드를 입력하세요",
                    key="hj_admin_code_input",
                )
                unlock_btn = st.form_submit_button("🔓 정밀 검토 모드 잠금 해제", type="primary", use_container_width=True)
                if unlock_btn:
                    if admin_input.strip() == ADMIN_PRECISION_CODE:
                        st.session_state["precision_unlocked"] = True
                        st.toast("정밀 검토 모드가 잠금 해제되었습니다!", icon="🔓")
                        st.rerun()
                    else:
                        st.error("정밀 검토 전용 코드가 일치하지 않습니다. 관리자에게 코드를 확인해 주세요.")

    if hj_can_render:
        # 현재 적용 중인 단면/재료 제원 (공통 사이드바 + 상단 DXF/수직탭 제원 연동)
        hj_bw = float(st.session_state.get("bw", 600.0))
        hj_H = float(st.session_state.get("beam_depth", 600.0))
        hj_main_dia = int(st.session_state.get("main_bar", 19))
        hj_top_bars = int(st.session_state.get("top_bars", 6))
        hj_bot_bars = int(st.session_state.get("bot_bars", 5))
        hj_st_dia = int(st.session_state.get("st_dia", 13))
        hj_st_legs = int(st.session_state.get("st_legs", 3))
        hj_st_spacing = float(st.session_state.get("st_spacing", 200.0))
        hj_tension_zone = str(st.session_state.get("tension_zone", "상부 인장 (부모멘트 -M)"))

        # 정밀 모드 잠금 해제 상태 배너 + 재잠금 버튼
        if is_hj_precision_selected:
            ul_c1, ul_c2 = st.columns([4.5, 1.2])
            with ul_c1:
                st.success("🔓 **정밀 검토 모드 활성화됨** — 타설 높이(h_joint)에 따른 균열단면 압축대(c) 내 포물선 전단흐름(Q/I) 저감 검토가 적용됩니다.")
            with ul_c2:
                if st.button("🔒 정밀 모드 잠금", key="hj_relock_btn", use_container_width=True):
                    st.session_state["precision_unlocked"] = False
                    st.rerun()

        # 3. 입력 조건 및 전용 SVG 단면도 (좌: 조건 입력 & 제원 요약 / 우: 수평 이어치기 SVG)
        hj_col_in, hj_col_vis = st.columns([1.15, 1.1])

        with hj_col_in:
            st.markdown(
                f'<div class="dw-section-card" style="margin-bottom:0.65rem;">'
                f'<div class="dw-section-header">'
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span>1. 수평 이어치기 검토 조건</div>'
                f'<span class="dw-pill-blue">{"정밀 모드 (Q/I)" if is_hj_precision_selected else "일반 모드 (표준)"}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            # 연동된 단면 제원 요약 표시 (KDS 14 20 전단철근 및 보강근 설계강도 상한 500 MPa 제한 안내)
            hj_fy_eff_disp = min(float(fy), 500.0)
            hj_fyt_eff_disp = min(float(stirrup_fy), 500.0)
            hj_fy_cap_txt = f"{hj_fy_eff_disp:.0f} MPa (입력 {fy}→상한 500 적용)" if float(fy) > 500.0 else f"{hj_fy_eff_disp:.0f} MPa"
            hj_fyt_cap_txt = f"{hj_fyt_eff_disp:.0f} MPa (입력 {stirrup_fy}→상한 500 적용)" if float(stirrup_fy) > 500.0 else f"{hj_fyt_eff_disp:.0f} MPa"
            st.info(
                f"📌 **연동된 검토 단면:** `{st.session_state.selected_beam_label}`  \n"
                f"• 단면: **{hj_bw:.0f} × {hj_H:.0f} mm** | 주근: 상부 **{hj_top_bars}-D{hj_main_dia}** / 하부 **{hj_bot_bars}-D{hj_main_dia}**  \n"
                f"• 기존 스터럽: **{hj_st_legs}-D{hj_st_dia} @ {hj_st_spacing:.0f}** | 마찰계수 **μ={mu}**  \n"
                f"• 설계 적용 강도 (≤500 MPa 제한): **fck={fck} MPa** / **보강근 fy={hj_fy_cap_txt}** / **전단철근 fyt={hj_fyt_cap_txt}**"
            )
            if float(fy) > 500.0 or float(stirrup_fy) > 500.0:
                st.warning(
                    "⚠️ **KDS 14 20 설계기준 항복강도 상한 적용:** 수평 이어치기 검토에서 전단철근(fyt) 및 전단마찰 보강근(fy)의 설계강도는 최대 **500 MPa**로 자동 제한되어 계산됩니다."
                )

            # 공통 추가 입력: 영구 압축력 P (kN/m)
            hj_p_perm = st.number_input(
                "영구 압축력 P (kN/m) — 이어치기면에 수직으로 작용하는 영구 순압축력",
                min_value=0.0, max_value=5000.0, value=0.0, step=10.0,
                key="hj_p_perm_input",
                help="보 상부 벽체 자중 등으로 이어치기면에 영구 압축력이 작용하는 경우 입력합니다. (기본값 0.0 kN/m)",
            )

            hj_h_joint = hj_H * 0.5
            hj_use_actual_vu = False
            hj_actual_vu_val = 0.0
            hj_moment_mode = None

            if is_hj_precision_selected:
                st.markdown("---")
                st.markdown("**🎯 정밀 검토 추가 입력 (압축·인장면 / 타설 높이 / 작용 전단력)**")
                hj_mm_options = [
                    "부모멘트 -M (상부 인장 / 하부 압축 — 보 단부 기준)",
                    "정모멘트 +M (하부 인장 / 상부 압축 — 보 중앙부 기준)",
                    "양방향 포락 (+M / -M 모멘트 반전 고려 — 보수적)",
                ]
                default_mm = hj_mm_options[0] if "상부" in hj_tension_zone else hj_mm_options[1]
                # 선택 부재/단면(인장부 위치)이 바뀌었을 때만 모멘트 조건 기본값을 자동 동기화
                if (
                    "hj_moment_mode_sel" not in st.session_state
                    or st.session_state.get("hj_last_tension_zone") != hj_tension_zone
                ):
                    st.session_state["hj_moment_mode_sel"] = default_mm
                    st.session_state["hj_last_tension_zone"] = hj_tension_zone

                hj_moment_mode = st.selectbox(
                    "모멘트 방향 및 압축/인장면 조건 (전단흐름 Q/I 압축대 기준)",
                    hj_mm_options,
                    key="hj_moment_mode_sel",
                    help="부모멘트(-M, 단부)는 보 하부가 압축대이므로 상부 타설면에서는 저감 불가(αq=1.0)입니다. 정모멘트(+M, 중앙부)는 보 상부가 압축대입니다.",
                )

                # 부재 변경으로 H가 바뀌었거나 초기 실행일 때 h_joint 기본값을 0.5H로 안전 클램핑
                if "hj_h_joint_slider" not in st.session_state or st.session_state.get("hj_last_H") != hj_H:
                    st.session_state["hj_h_joint_slider"] = float(round(hj_H * 0.5, 0))
                    st.session_state["hj_last_H"] = hj_H
                else:
                    st.session_state["hj_h_joint_slider"] = float(
                        min(max(float(st.session_state["hj_h_joint_slider"]), 0.0), float(hj_H))
                    )

                hj_h_joint = st.slider(
                    "보 하단으로부터의 수평 이어치기 높이 h_joint (mm)",
                    min_value=0.0,
                    max_value=float(hj_H),
                    step=10.0,
                    key="hj_h_joint_slider",
                    help="보 하단면에서 수평 타설 경계면까지의 높이입니다. 압축대 내부(정모멘트 상부 / 부모멘트 하부)에 위치할 때만 αq가 저감됩니다.",
                )
                if "하부 압축" in hj_moment_mode:
                    y_ref_caption = f"하단 압축연단으로부터 깊이 **$y_{{comp}} = h_{{joint}} = {hj_h_joint:.0f}\\text{{ mm}}$**"
                elif "상부 압축" in hj_moment_mode:
                    y_ref_caption = f"상단 압축연단으로부터 깊이 **$y_{{comp}} = H - h_{{joint}} = {hj_H - hj_h_joint:.0f}\\text{{ mm}}$**"
                else:
                    y_ref_caption = f"상단 깊이 **{hj_H - hj_h_joint:.0f} mm** / 하단 높이 **{hj_h_joint:.0f} mm** (양방향 포락 max 적용)"
                st.caption(
                    f"📏 현재 타설 높이: 하단에서 **{hj_h_joint:.0f} mm** (`{hj_h_joint/max(hj_H,1)*100:.1f}% H`) · {y_ref_caption}"
                )

                hj_use_actual_vu = st.checkbox(
                    "실제 계수전단력 Vu (kN) 직접 입력 적용 (미체크 시 공칭전단강도 Vn 기준 보수적 적용)",
                    value=False,
                    key="hj_use_actual_vu_chk",
                )
                if hj_use_actual_vu:
                    hj_actual_vu_val = st.number_input(
                        "실제 계수전단력 Vu (kN) — 내부 계산 시 Vu / φ (φ=0.75) 적용",
                        min_value=0.0, max_value=20000.0, value=250.0, step=10.0,
                        key="hj_actual_vu_input",
                    )

        # 수평 이어치기 역학 계산 실행
        hj_res = evaluate_horizontal_joint(
            bw=hj_bw, H=hj_H, cover=cover, fck=fck, fy=fy, fyt=stirrup_fy,
            main_dia=hj_main_dia, top_bars=hj_top_bars, bot_bars=hj_bot_bars,
            st_dia=hj_st_dia, st_legs=hj_st_legs, st_spacing=hj_st_spacing,
            tension_zone=hj_tension_zone, mu=mu,
            P_perm=hj_p_perm,
            precision_mode=is_hj_precision_selected,
            h_joint=hj_h_joint,
            use_actual_vu=hj_use_actual_vu,
            actual_vu_kN=hj_actual_vu_val,
            moment_mode=hj_moment_mode,
        )

        with hj_col_vis:
            st.markdown(
                f'<div class="dw-section-card" style="margin-bottom:0.65rem;">'
                f'<div class="dw-section-header">'
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span>수평 이어치기 단면도 & 전단흐름(Q/I) 분포</div>'
                f'<span class="dw-pill-blue">αq = {hj_res["alpha_q"]:.2f}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            hj_svg_html = render_horizontal_joint_svg(
                bw=hj_bw, H=hj_H, cover=cover, main_dia=hj_main_dia,
                top_bars=hj_top_bars, bot_bars=hj_bot_bars,
                st_dia=hj_st_dia, st_legs=hj_st_legs, st_spacing=hj_st_spacing,
                tension_zone=hj_tension_zone, hj_res=hj_res,
                top_layers=st.session_state.get("top_layers"),
                bot_layers=st.session_state.get("bot_layers"),
            )
            st.markdown(hj_svg_html, unsafe_allow_html=True)
            if is_hj_precision_selected:
                if hj_res["comp_face"] == "ENVELOPE":
                    zone_txt = (
                        f"양방향 포락 (αq,+M={hj_res['alpha_q_pos']:.2f}, αq,-M={hj_res['alpha_q_neg']:.2f} 중 지배값)"
                    )
                    st.caption(
                        f"🔷 **{hj_res['moment_mode_label']}** | "
                        f"c(+M)={hj_res['c_pos']:.0f}mm / c(-M)={hj_res['c_neg']:.0f}mm | "
                        f"**{zone_txt}** → **αq = {hj_res['alpha_q']:.3f}**"
                    )
                else:
                    comp_lbl = "상부 압축대 (+M)" if hj_res["comp_face"] == "TOP" else "하부 압축대 (-M)"
                    zone_txt = f"{comp_lbl} 내부 (포물선 저감 적용)" if hj_res["in_comp_zone"] else "인장 균열구간 (저감 불가 αq=1.00)"
                    st.caption(
                        f"🔷 **{comp_lbl} 중립축 c = {hj_res['c_depth']:.1f} mm** (k={hj_res['k_cr']:.3f}, y_comp={hj_res['y_comp']:.0f} mm) | "
                        f"위치: **{zone_txt}** | **αq = {hj_res['alpha_q']:.3f}**"
                    )
            else:
                st.caption(
                    "🟧 **일반 검토 모드:** 타설 높이와 무관하게 복부 중앙(0.5H) 기준 최대 균일 전단흐름(q = Vn/d, αq = 1.00)을 적용합니다."
                )

        # 4. 상단 요약 메트릭 카드 (4열 KPI)
        st.markdown(
            f'<div class="dw-section-card" style="margin-top:0.85rem; margin-bottom:0.75rem;">'
            f'<div class="dw-section-header">'
            f'<div class="dw-section-title"><span class="dw-accent-bar"></span>2. 수평 이어치기 구조검토 결과 대시보드 (KDS 14 20)</div>'
            f'<span class="dw-pill-blue">{"정밀 검토 모드 (Q/I)" if is_hj_precision_selected else "일반 검토 모드 (표준 보수적)"}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        hj_status_col = "#16a34a" if hj_res["hj_ok"] else "#dc2626"
        hj_judge_label = "보강 불필요 (OK)" if hj_res["hj_ok"] else f"+{hj_res['Avf_req']:.0f} mm²/m"
        hj_judge_sub = "기존 스터럽으로 수평전단 안전" if hj_res["hj_ok"] else f"추가 보강 필요 (D/C {hj_res['dc_hj']:.2f})"

        hk1, hk2, hk3, hk4 = st.columns(4)
        with hk1:
            st.markdown(
                f'<div class="dw-kpi-card"><div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">① 공칭전단강도 (Vn)</div>'
                f'<div class="dw-kpi-val">{hj_res["Vn_eff_kN"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN</span></div>'
                f'</div><div class="dw-kpi-foot" style="color:#137fec;"><span>Vc {hj_res["Vc_kN"]:.1f} + Vs {hj_res["Vs_kN"]:.1f} kN</span></div></div>',
                unsafe_allow_html=True,
            )
        with hk2:
            st.markdown(
                f'<div class="dw-kpi-card"><div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">② 1m당 작용 수평전단력 (Vnh,1m)</div>'
                f'<div class="dw-kpi-val">{hj_res["Vnh_1m_kN"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN/m</span></div>'
                f'</div><div class="dw-kpi-foot" style="color:#137fec;"><span>전단흐름 저감계수 αq = {hj_res["alpha_q"]:.3f}</span></div></div>',
                unsafe_allow_html=True,
            )
        with hk3:
            st.markdown(
                f'<div class="dw-kpi-card"><div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">③ 기존 스터럽 보유 vs 총 필요량</div>'
                f'<div class="dw-kpi-val">{hj_res["Asv_1m"]:.0f} <span style="font-size:1.05rem; font-weight:700; color:#94a3b8;">/ {hj_res["Avf_total"]:.0f} mm²/m</span></div>'
                f'</div><div class="dw-kpi-foot" style="color:{hj_status_col};"><span>영구압축 감소 Avf,P = {hj_res["Avf_P"]:.0f} mm²/m</span></div></div>',
                unsafe_allow_html=True,
            )
        with hk4:
            st.markdown(
                f'<div class="dw-kpi-card"><div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">④ 추가 보강근 소요량 (Avf,req)</div>'
                f'<div class="dw-kpi-val" style="color:{hj_status_col};">{hj_judge_label}</div>'
                f'</div><div class="dw-kpi-foot" style="color:{hj_status_col};"><span>{hj_judge_sub}</span></div></div>',
                unsafe_allow_html=True,
            )

        # 정밀 검토 모드: 일반 검토 대비 철근량 절감 효과 표시 배너
        if is_hj_precision_selected:
            st.markdown(
                f'<div style="background:#f0f9ff; border:1px solid #bae6fd; border-left:5px solid #0284c7; '
                f'border-radius:12px; padding:0.95rem 1.25rem; margin:0.65rem 0;">'
                f'<div style="font-size:0.8rem; font-weight:800; color:#0369a1; margin-bottom:4px;">💡 일반 검토 대비 정밀 검토(Q/I) 철근량 절감 효과</div>'
                f'<div style="font-size:0.9rem; font-weight:700; color:#0c4a6e;">'
                f'• 1m당 총 필요 전단마찰철근량: <b>{hj_res["Avf_total_std"]:.0f}</b> → <b>{hj_res["Avf_total_prec"]:.0f} mm²/m</b> '
                f'(절감량 <b>ΔAvf = {hj_res["delta_Avf_total"]:.0f} mm²/m</b>, 절감률 <b>{hj_res["saving_pct_total"]:.1f}%</b>)<br/>'
                f'• 1m당 추가 보강근 소요량: <b>{hj_res["Avf_req_std"]:.0f}</b> → <b>{hj_res["Avf_req_prec"]:.0f} mm²/m</b> '
                f'(절감량 <b>ΔAvf,req = {hj_res["delta_Avf_req"]:.0f} mm²/m</b>, 절감률 <b>{hj_res["saving_pct_req"]:.1f}%</b>)'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        # 최종 결론 배너
        if hj_res["hj_ok"]:
            st.markdown(
                f'<div class="dw-conclusion-ok">'
                f'<div>'
                f'<div style="font-size:0.75rem; font-weight:800; color:#1e40af; text-transform:uppercase;">FINAL CONCLUSION · 수평 이어치기 전단마찰 판정</div>'
                f'<div style="font-size:0.95rem; font-weight:800; color:#1e3a8a; margin-top:4px;">'
                f'기존 스터럽({hj_st_legs}-D{hj_st_dia}@{hj_st_spacing:.0f}, Asv,1m={hj_res["Asv_1m"]:.0f} mm²/m)만으로 '
                f'1m당 필요 수평전단마찰 철근량(Avf,total={hj_res["Avf_total"]:.0f} mm²/m)을 만족하여 추가 보강근이 불필요합니다.'
                f'</div></div>'
                f'<div class="dw-decision-pill-ok">보강 불필요 (OK)</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="dw-conclusion-ng">'
                f'<div>'
                f'<div style="font-size:0.75rem; font-weight:800; color:#991b1b; text-transform:uppercase;">FINAL CONCLUSION · 수평 이어치기 전단마찰 판정 및 현장 조치</div>'
                f'<div style="font-size:0.95rem; font-weight:800; color:#b91c1c; margin-top:4px;">'
                f'기존 스터럽 보유량({hj_res["Asv_1m"]:.0f} mm²/m) 대비 1m당 <b>{hj_res["Avf_req"]:.0f} mm²/m</b>가 부족합니다. '
                f'아래 가이드에 따라 스터럽 간격을 축소하거나 추가 다우얼바를 수평 이어치기면에 수직 정착하세요.'
                f'</div></div>'
                f'<div class="dw-decision-pill-ng">+{hj_res["Avf_req"]:.0f} mm²/m 보강 필요</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # 5. 현장 조치 가이드 (보강 필요 시 자동 출력)
            st.markdown(
                '<div class="dw-section-card" style="margin-top:0.85rem; margin-bottom:0.65rem;">'
                '<div class="dw-section-header">'
                '<div class="dw-section-title"><span class="dw-accent-bar"></span>3. 수평 이어치기 현장 조치 가이드 (보강 대안)</div>'
                '<span class="dw-pill-blue">시공 대안 자동 산출</span>'
                '</div></div>',
                unsafe_allow_html=True,
            )
            fg1, fg2 = st.columns([1, 1.85])
            with fg1:
                st_warn = " *(※ 50mm 미만 과밀 배근 우려 → 스터럽 가닥수 증대 또는 대안 ② 다우얼바 보강 권장)*" if hj_res["s_req_practical"] < 50 else ""
                st.markdown(
                    f'<div class="status-card">'
                    f'<h4><span>① 스터럽 간격 축소안</span><span class="badge-warn">s ≤ {hj_res["s_req_practical"]} mm</span></h4>'
                    f'<ul>'
                    f'<li><b>현재 스터럽:</b> {hj_st_legs}-D{hj_st_dia} @ {hj_st_spacing:.0f} mm (보유 {hj_res["Asv_1m"]:.0f} mm²/m)</li>'
                    f'<li><b>이론 필요 간격 (s_req):</b> <b>{hj_res["s_req"]:.1f} mm</b></li>'
                    f'<li><b>시공 권장 간격:</b> <b>{hj_st_legs}-D{hj_st_dia} @ {hj_res["s_req_practical"]} mm 이하</b>{st_warn}</li>'
                    f'</ul></div>',
                    unsafe_allow_html=True,
                )
            with fg2:
                st.markdown("**② 추가 다우얼바 (D10, D13, D16) 1m당 배근 본수 및 간격표**")
                if hj_res["dowel_options"]:
                    st.dataframe(pd.DataFrame(hj_res["dowel_options"]), use_container_width=True, hide_index=True)

        # 산정 근거 상세 수식 Expander (기본 닫힘)
        with st.expander("📐 [계산 근거 확인] 수평 이어치기 KDS 14 20 상세 산정식 보기 (클릭하여 펼치기)", expanded=False):
            hj_prec_note = (
                f"\n> **압축·인장면 적용 ({hj_res['moment_mode_label']}):** "
                f"압축연단 깊이 $y_{{\\text{{comp}}}} = {hj_res['y_comp']:.0f}\\text{{ mm}}$, "
                f"중립축 깊이 $c = {hj_res['c_depth']:.1f}\\text{{ mm}}$ → 전단흐름 저감계수 $\\alpha_q = \\mathbf{{{hj_res['alpha_q']:.3f}}}$"
                if is_hj_precision_selected
                else ""
            )
            hj_formula_md = f"""
> **KDS 14 20 22 설계강도 상한 적용:** 전단철근 $f_{{ys}} = \\min({stirrup_fy},\\,500) = \\mathbf{{{hj_res['fyt_eff']:.0f}\\text{{ MPa}}}}$, 전단마찰 보강근 $f_{{y,\\text{{vf}}}} = \\min({fy},\\,500) = \\mathbf{{{hj_res['fy_vf_eff']:.0f}\\text{{ MPa}}}}${hj_prec_note}

1. **공칭전단강도 ($V_n$):**
   $$V_n = \\frac{{1}}{{6}}\\sqrt{{{fck}}}\\cdot {hj_bw:.0f}\\cdot {hj_res['d']:.1f} + \\frac{{{hj_res['Asv']:.1f}\\cdot {hj_res['fyt_eff']:.0f}\\cdot {hj_res['d']:.1f}}}{{{hj_st_spacing:.0f}}} = \\mathbf{{{hj_res['Vn_kN']:.1f}\\text{{ kN}}}}$$
   *(적용 전단력 기준: {hj_res['shear_basis_str']})*
2. **1m당 작용 수평전단력 ($V_{{nh,1\\text{{m}}}}$):**
   $$V_{{nh,1\\text{{m}}}} = \\alpha_q \\times V_{{n,\\text{{eff}}}} \\times \\frac{{1000}}{{d}} = {hj_res['alpha_q']:.3f} \\times {hj_res['Vn_eff_kN']:.1f} \\times \\frac{{1000}}{{{hj_res['d']:.1f}}} = \\mathbf{{{hj_res['Vnh_1m_kN']:.1f}\\text{{ kN/m}}}}$$
3. **1m당 총 필요 전단마찰철근량 ($A_{{vf,\\text{{total}}}}$):**
   $$A_{{vf,\\text{{total}}}} = \\frac{{V_{{nh,1\\text{{m}}}} \\times 1000}}{{f_{{y,\\text{{vf}}}} \\times \\mu}} = \\frac{{{hj_res['Vnh_1m_kN']*1000:.0f}}}{{{hj_res['fy_vf_eff']:.0f} \\times {mu}}} = \\mathbf{{{hj_res['Avf_total']:.1f}\\text{{ mm}}^2/\\text{{m}}}}$$
4. **기존 스터럽 보유량 ($A_{{sv,1\\text{{m}}}}$) 및 영구 압축력 감소량 ($A_{{vf,P}}$):**
   $$A_{{sv,1\\text{{m}}}} = {hj_res['Asv']:.1f} \\times \\frac{{1000}}{{{hj_st_spacing:.0f}}} = \\mathbf{{{hj_res['Asv_1m']:.1f}\\text{{ mm}}^2/\\text{{m}}}}, \\quad A_{{vf,P}} = \\frac{{{hj_p_perm:.1f} \\times 1000}}{{{hj_res['fy_vf_eff']:.0f}}} = \\mathbf{{{hj_res['Avf_P']:.1f}\\text{{ mm}}^2/\\text{{m}}}}$$
5. **최종 추가 보강근 소요량 ($A_{{vf,\\text{{req}}}}$):**
   $$A_{{vf,\\text{{req}}}} = \\max\\left(0,\\; {hj_res['Avf_total']:.1f} - {hj_res['Asv_1m']:.1f} - {hj_res['Avf_P']:.1f}\\right) = \\mathbf{{{hj_res['Avf_req']:.1f}\\text{{ mm}}^2/\\text{{m}}}}$$
"""
            st.markdown(hj_formula_md)

        # 6. 수평 이어치기 HTML 보고서 다운로드 (단일 부재)
        hj_mode_title = "정밀 검토 모드 (타설 높이 Q/I 반영)" if is_hj_precision_selected else "일반 검토 모드 (표준 보수적)"
        hj_dowel_html_rows = "".join(
            f"<tr><td>{opt['보강근 규격']}</td><td>{opt['1m당 최소 본수 (EA/m)']}</td><td>{opt['1열(1가닥) 배근 간격']}</td><td>{opt['2열(양측 2가닥) 배근 간격']}</td></tr>"
            for opt in hj_res["dowel_options"]
        ) if hj_res["dowel_options"] else "<tr><td colspan='4'>기존 스터럽으로 안전 (추가 보강 불필요)</td></tr>"

        hj_judge_html_str = (
            "OK - 보강 불필요"
            if hj_res["hj_ok"]
            else f"NG - 보강 필요, s_req={hj_res['s_req_practical']}mm"
        )
        hj_mat_html_str = (
            f"fck={fck} / 보강근 fy={hj_res['fy_vf_eff']:.0f} MPa"
            + (f" (입력 {fy}→500 제한)" if hj_res["fy_vf_capped"] else "")
            + f" / 전단철근 fyt={hj_res['fyt_eff']:.0f} MPa"
            + (f" (입력 {stirrup_fy}→500 제한)" if hj_res["fyt_capped"] else "")
            + f" / μ = {mu}"
        )
        hj_html_report = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>수평 이어치기 구조검토서 - {st.session_state.selected_beam_label}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>
body {{ font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', sans-serif; max-width: 920px; margin: 30px auto; color: #1e293b; line-height: 1.6; }}
h1 {{ border-bottom: 3px solid #137fec; padding-bottom: 10px; color: #0f172a; }}
table {{ width: 100%; border-collapse: collapse; margin: 14px 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: 9px 12px; text-align: left; }}
th {{ background: #f1f5f9; font-weight: bold; }}
.badge {{ display:inline-block; background:#eff6ff; color:#1d4ed8; padding:4px 10px; border-radius:999px; font-weight:bold; font-size:13px; }}
</style>
</head>
<body>
<h1>🏗️ RC 보 수평 이어치기 전단마찰 구조검토서</h1>
<p><b>검토 부재:</b> {st.session_state.selected_beam_label} | <span class="badge">{hj_mode_title}</span> | <b>검토 일시:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<div style="text-align:center; margin: 18px 0;">{hj_svg_html}</div>
<table>
<tr><th>구분</th><th>산정 조건 / 기준</th><th>검토 결과</th></tr>
<tr><td>보 단면 / 유효춤</td><td>bw × H (d)</td><td>{hj_bw:.0f} × {hj_H:.0f} mm (d = {hj_res['d']:.1f} mm)</td></tr>
<tr><td>재료 및 마찰계수</td><td>fck / fy,vf / fyt (≤500 MPa 제한) / μ</td><td>{hj_mat_html_str}</td></tr>
<tr><td>기존 스터럽 배근</td><td>Asv,1m = Asv × 1000 / s</td><td>{hj_st_legs}-D{hj_st_dia} @ {hj_st_spacing:.0f} ({hj_res['Asv_1m']:.1f} mm²/m)</td></tr>
<tr><td>공칭전단강도 (Vn)</td><td>{hj_res['shear_basis_str']}</td><td>{hj_res['Vn_eff_kN']:.1f} kN (Vc={hj_res['Vc_kN']:.1f} + Vs={hj_res['Vs_kN']:.1f})</td></tr>
<tr><td>타설 높이 & 저감계수</td><td>{hj_res['moment_mode_label']} | h_joint={hj_res['h_joint']:.0f}mm (y_comp={hj_res['y_comp']:.0f}mm, c={hj_res['c_depth']:.1f}mm)</td><td>αq = {hj_res['alpha_q']:.3f}</td></tr>
<tr><td>1m당 작용 수평전단력</td><td>Vnh,1m = αq × Vn × 1000 / d</td><td>{hj_res['Vnh_1m_kN']:.1f} kN/m</td></tr>
<tr><td>총 필요 전단마찰철근량</td><td>Avf,total = Vnh,1m / (fy × μ)</td><td>{hj_res['Avf_total']:.1f} mm²/m</td></tr>
<tr><td><b>최종 추가 보강 소요량</b></td><td><b>Avf,req = max(0, Avf,total - Asv,1m - Avf,P)</b></td><td><b>{hj_res['Avf_req']:.1f} mm²/m ({hj_judge_html_str})</b></td></tr>
</table>
<h3>현장 보강 대안 (추가 다우얼바 배근표)</h3>
<table>
<tr><th>규격</th><th>1m당 최소 본수</th><th>1열(1가닥) 간격</th><th>2열(양측 2가닥) 간격</th></tr>
{hj_dowel_html_rows}
</table>
</body>
</html>"""

        st.download_button(
            label="🖨️ 수평 이어치기 구조검토 계산근거 다운로드",
            data=hj_html_report.encode("utf-8"),
            file_name=f"수평이어치기_검토서_{st.session_state.selected_beam_label.replace(' ', '_')}.html",
            mime="text/html",
            key="hj_html_dl_btn",
        )

        # 7. 전체 보 일괄 검토 (Horizontal Joint Batch Screening) & CSV 다운로드
        st.markdown(
            '<div class="dw-section-card" style="margin-top:1.1rem; margin-bottom:0.65rem;">'
            '<div class="dw-section-header">'
            '<div class="dw-section-title"><span class="dw-accent-bar"></span>4. 전체 보 일람표 수평 이어치기 일괄 검토</div>'
            '<span class="dw-pill-blue">전 부재 일괄 스크리닝</span>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        if not st.session_state.extracted_beams:
            st.info("좌측 사이드바에서 DXF 도면 파일을 업로드하면 전체 보 부재에 대한 수평 이어치기 일괄 검토가 자동으로 수행됩니다.")
        else:
            all_hb_keys = list(st.session_state.extracted_beams.keys())
            hb_floors = []
            for bk in all_hb_keys:
                fl_s, _ = split_floor_and_beam(bk)
                if fl_s not in hb_floors:
                    hb_floors.append(fl_s)

            if is_hj_precision_selected:
                hb1, hb2, hb2b, hb3, hb4 = st.columns([1.0, 1.5, 1.5, 1.1, 1.0])
                with hb1:
                    hj_batch_floor = st.selectbox("층(Floor) 필터", ["전체 층 보기"] + hb_floors, key="hj_batch_floor")
                with hb2:
                    hj_batch_depth_mode = st.selectbox(
                        "일괄 타설 위치 기준 (정밀)",
                        [
                            "상부 슬래브 하단 기준 (y_top = 180 mm)",
                            "상부 슬래브 하단 기준 (y_top = 200 mm)",
                            "상부 슬래브 하단 기준 (y_top = 150 mm)",
                            "보 중앙 타설 기준 (h_joint = 0.5H)",
                        ],
                        key="hj_batch_depth_mode",
                    )
                with hb2b:
                    hj_batch_mm_mode = st.selectbox(
                        "압축/인장면 기준 (모멘트)",
                        [
                            "단면 자동 (단부 -M / 중앙 +M)",
                            "양방향 포락 (+M/-M 보수적)",
                            "전 단면 부모멘트 (-M 하부압축)",
                            "전 단면 정모멘트 (+M 상부압축)",
                        ],
                        key="hj_batch_mm_mode",
                    )
                with hb3:
                    hj_batch_filter = st.selectbox("검토 결과 필터", ["전체 보기", "🚨 보강 필요(NG)만 보기", "✅ 안전(OK)만 보기"], key="hj_batch_filter")
                with hb4:
                    hj_batch_search = st.text_input("보 부호 검색", "", placeholder="예: G1, B2, -1RG", key="hj_batch_search")
            else:
                hb1, hb2, hb3 = st.columns(3)
                with hb1:
                    hj_batch_floor = st.selectbox("층(Floor) 필터", ["전체 층 보기"] + hb_floors, key="hj_batch_floor_std")
                with hb2:
                    hj_batch_filter = st.selectbox("검토 결과 필터", ["전체 보기", "🚨 보강 필요(NG)만 보기", "✅ 안전(OK)만 보기"], key="hj_batch_filter_std")
                with hb3:
                    hj_batch_search = st.text_input("보 부호 검색", "", placeholder="예: G1, B2, -1RG", key="hj_batch_search_std")
                hj_batch_depth_mode = "보 중앙 타설 기준 (h_joint = 0.5H)"
                hj_batch_mm_mode = "단면 자동 (단부 -M / 중앙 +M)"

            hj_batch_rows = []
            for b_name, secs in st.session_state.extracted_beams.items():
                fl_lbl, pure_mk = split_floor_and_beam(b_name)
                if hj_batch_floor != "전체 층 보기" and fl_lbl != hj_batch_floor:
                    continue
                if hj_batch_search and hj_batch_search.upper() not in b_name.upper():
                    continue
                for s_name, s_info in secs.items():
                    m_dia_b = BAR_LIST[s_info["main_bar_idx"]]
                    t_zone_b = "하부 인장 (정모멘트 +M)" if ("CENTER" in s_name.upper() or "CEN" in s_name.upper()) else "상부 인장 (부모멘트 -M)"
                    H_b = float(s_info["depth"])
                    if is_hj_precision_selected:
                        if "150" in hj_batch_depth_mode:
                            h_j_b = max(0.0, H_b - 150.0)
                        elif "180" in hj_batch_depth_mode:
                            h_j_b = max(0.0, H_b - 180.0)
                        elif "200" in hj_batch_depth_mode:
                            h_j_b = max(0.0, H_b - 200.0)
                        else:
                            h_j_b = H_b * 0.5
                        if "포락" in hj_batch_mm_mode:
                            mm_b = "양방향 포락"
                        elif "부모멘트" in hj_batch_mm_mode:
                            mm_b = "부모멘트 -M"
                        elif "정모멘트" in hj_batch_mm_mode:
                            mm_b = "정모멘트 +M"
                        else:
                            mm_b = None
                    else:
                        h_j_b = H_b * 0.5
                        mm_b = None

                    r_hb = evaluate_horizontal_joint(
                        bw=s_info["bw"], H=H_b, cover=cover,
                        fck=fck, fy=fy, fyt=stirrup_fy,
                        main_dia=m_dia_b, top_bars=s_info["top_count"], bot_bars=s_info["bot_count"],
                        st_dia=s_info["st_dia"], st_legs=s_info["st_legs"], st_spacing=s_info["st_spacing"],
                        tension_zone=t_zone_b, mu=mu,
                        P_perm=hj_p_perm,
                        precision_mode=is_hj_precision_selected,
                        h_joint=h_j_b,
                        moment_mode=mm_b,
                    )
                    if hj_batch_filter == "🚨 보강 필요(NG)만 보기" and r_hb["hj_ok"]:
                        continue
                    if hj_batch_filter == "✅ 안전(OK)만 보기" and not r_hb["hj_ok"]:
                        continue

                    d13_ea = math.ceil(r_hb["Avf_req"] / REBAR_AREA[13]) if r_hb["Avf_req"] > 1e-6 else 0
                    hj_status_str = "✅ 안전 (OK)" if r_hb["hj_ok"] else f"🚨 보강 (+{r_hb['Avf_req']:.0f} mm²/m, D13 {d13_ea}EA/m)"
                    row_dict = {
                        "층 표기": fl_lbl,
                        "보 부호": pure_mk,
                        "단면 위치": s_name,
                        "단면 (bw×H)": f"{s_info['bw']:.0f}×{H_b:.0f}",
                        "기존 스터럽": f"{s_info['st_legs']}-D{s_info['st_dia']}@{s_info['st_spacing']:.0f}",
                        "공칭전단 Vn (kN)": round(r_hb["Vn_kN"], 1),
                        "저감계수 αq": round(r_hb["alpha_q"], 3),
                        "수평전단 Vnh,1m (kN/m)": round(r_hb["Vnh_1m_kN"], 1),
                        "총 필요 Avf (mm²/m)": round(r_hb["Avf_total"], 0),
                        "스터럽 보유 Asv,1m (mm²/m)": round(r_hb["Asv_1m"], 0),
                        "추가 소요 Avf,req (mm²/m)": round(r_hb["Avf_req"], 0),
                        "스터럽 권장간격 s_req (mm)": "-" if r_hb["hj_ok"] else r_hb["s_req_practical"],
                        "검토 판정": hj_status_str,
                    }
                    if is_hj_precision_selected:
                        cf_lbl = "상부압축(+M)" if r_hb["comp_face"] == "TOP" else ("하부압축(-M)" if r_hb["comp_face"] == "BOTTOM" else "포락(±M)")
                        row_dict["압축면 기준"] = cf_lbl
                        row_dict["절감률 (%)"] = round(r_hb["saving_pct_total"], 1)
                    hj_batch_rows.append(row_dict)

            hj_batch_df = pd.DataFrame(hj_batch_rows)
            hb_tot = len(hj_batch_df)
            hb_ok = sum(1 for r in hj_batch_rows if "안전" in r["검토 판정"])
            hb_ng = hb_tot - hb_ok

            hm1, hm2, hm3 = st.columns(3)
            with hm1:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top"><div class="dw-kpi-label">수평 이어치기 검토 총수</div>'
                    f'<div class="dw-kpi-val">{hb_tot} <span style="font-size:1rem; color:#64748b;">개소</span></div></div>'
                    f'<div class="dw-kpi-foot" style="color:#137fec;"><span>적용 모드: {"정밀(Q/I)" if is_hj_precision_selected else "일반(표준)"}</span></div></div>',
                    unsafe_allow_html=True,
                )
            with hm2:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top"><div class="dw-kpi-label">안전 (무보강 OK)</div>'
                    f'<div class="dw-kpi-val" style="color:#137fec;">{hb_ok} <span style="font-size:1rem; color:#64748b;">개소</span></div></div>'
                    f'<div class="dw-kpi-foot" style="color:#137fec;"><span>비율: {(hb_ok/max(hb_tot,1))*100:.1f}%</span></div></div>',
                    unsafe_allow_html=True,
                )
            with hm3:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top"><div class="dw-kpi-label">보강 필요 (NG)</div>'
                    f'<div class="dw-kpi-val" style="color:{"#dc2626" if hb_ng > 0 else "#111418"};">{hb_ng} <span style="font-size:1rem; color:#64748b;">개소</span></div></div>'
                    f'<div class="dw-kpi-foot" style="color:{"#dc2626" if hb_ng > 0 else "#16a34a"};"><span>{"스터럽 간격 축소 또는 다우얼바 보강 대상" if hb_ng > 0 else "전 단면 안전"}</span></div></div>',
                    unsafe_allow_html=True,
                )

            st.dataframe(hj_batch_df, use_container_width=True, hide_index=True, height=440)

            hj_csv_bytes = hj_batch_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 전체 보 수평 이어치기 검토 일람표 (CSV/엑셀 호환) 다운로드",
                data=hj_csv_bytes,
                file_name=f"수평이어치기_일괄검토_{'정밀' if is_hj_precision_selected else '일반'}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary",
                key="hj_batch_csv_dl_btn",
            )

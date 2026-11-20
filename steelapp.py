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
    .dw-step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #eff6ff;
        color: #137fec;
        border: 1px solid #bfdbfe;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        padding: 2px 8px;
        border-radius: 999px;
        line-height: 1.25;
        flex-shrink: 0;
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

    # AutoCAD 비출력(plot=0, DEFPOINT/DEFPOINTS/NOPLOT)·꺼짐(OFF)·동결(FROZEN) 레이어 자동 식별
    # (도면 작성용 보조 중심선·검토 메모·수정 구름 등 실제 출력되지 않는 가이드 요소 제외)
    off_frozen_layers = set()
    excluded_layers = {'DEFPOINT', 'DEFPOINTS'}
    try:
        for lyr in doc.layers:
            lname_up = lyr.dxf.name.upper()
            if lyr.is_off() or lyr.is_frozen():
                off_frozen_layers.add(lname_up)
                excluded_layers.add(lname_up)
            elif getattr(lyr.dxf, 'plot', 1) == 0:
                excluded_layers.add(lname_up)
    except Exception:
        pass
    
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
        ent_layer_up = str(getattr(e.dxf, 'layer', '') or '').upper()
        if t == 'INSERT':
            if ent_layer_up in off_frozen_layers:
                return
            try:
                bname_up = (e.dxf.name if e.dxf.hasattr('name') else '').upper()
                if 'BARDOT' in bname_up:
                    if ent_layer_up not in excluded_layers:
                        cad_circles.append((float(e.dxf.insert.x), float(e.dxf.insert.y), 18.0))
                else:
                    for sub_e in e.virtual_entities():
                        if getattr(sub_e.dxf, 'invisible', 0):
                            continue
                        sub_t = sub_e.dxftype()
                        if sub_t != 'INSERT': 
                            process_entity(sub_e)
                        else:
                            sub_lyr_up = str(getattr(sub_e.dxf, 'layer', '') or '').upper()
                            sub_bname = (sub_e.dxf.name if sub_e.dxf.hasattr('name') else '').upper()
                            if 'BARDOT' in sub_bname and sub_lyr_up not in excluded_layers:
                                cad_circles.append((float(sub_e.dxf.insert.x), float(sub_e.dxf.insert.y), 18.0))
            except Exception:
                pass
            return
        # 비출력(DEFPOINT/NOPLOT 등)·꺼짐·동결 레이어 위의 보조선/메모/구름마크 객체 제외
        if ent_layer_up in excluded_layers:
            return
        if t == 'CIRCLE':
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
            if bottom_y + (top_y - bottom_y) * 0.25 <= ry <= sec_hdr_upper_y:
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
                    # 인쇄된 수직 구분선이 없는 표(보조선 DEFPOINT만 있는 경우 등):
                    # 좌측정렬 TEXT 좌표(insert.x) 대신 각 단면 상단의 수평 치수선(H-DIM) 중앙 좌표를 기준으로 정확히 분할
                    h_dim_xs = sorted(
                        float(r['x']) for _, r in beam_df[(beam_df['kind'] == 'DIM') & (beam_df['orient'] == 'H')].iterrows()
                        if bottom_y + (top_y - bottom_y) * 0.35 <= float(r['y']) <= top_y - 30
                    )
                    # 인접 H-DIM 중 각 구간 헤더(lx, rx)에 가장 가까운 빔 중심 좌표 매칭
                    lx_dim = min(h_dim_xs, key=lambda xh: abs(xh - (lx + 260.0))) if h_dim_xs else None
                    rx_dim = min(h_dim_xs, key=lambda xh: abs(xh - (rx + 260.0))) if h_dim_xs else None
                    if lx_dim is not None and rx_dim is not None and rx_dim - lx_dim > 400.0 and lx < (lx_dim + rx_dim) / 2.0 < rx:
                        inner_dividers.append(round((lx_dim + rx_dim) / 2.0, 1))
                    else:
                        inner_dividers.append(round((lx + rx) / 2.0, 1))
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
                if bottom_y + (top_y - bottom_y) * 0.25 <= ry <= sec_hdr_upper_y:
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
REBAR_DB = {10: 9.53, 13: 12.7, 16: 15.9, 19: 19.1, 22: 22.2, 25: 25.4, 29: 28.6, 32: 31.8}
ROUGHNESS_FACTOR = {
    "조면 확보 (μ=1.0, 표면 거칠기 6mm 이상)": 1.0,
    "조면 미확보 (μ=0.6, 일반 수직이어치기면)": 0.6,
    "일체 타설 콘크리트 (μ=1.4)": 1.4,
}
BAR_LIST = [10, 13, 16, 19, 22, 25, 29, 32]


def _resolve_beam_layers(bw, cover, main_dia, st_dia, n_bars, dxf_layer_list=None, G_max=25.0):
    """보 주근 다단(1열/2열/3열...) 분할 공통 함수.
    - DXF 원본 단수 합계가 현재 주근수와 일치하면 DXF 원본 구성을 그대로 유지
    - 수동 입력/개수 변경 시 KDS 14 20 50 4.3.2 최소 순간격(s_min) 기준 1열 최대 수용 개수로 상·하부 동일 분할
    """
    n_bars = max(int(n_bars), 1)
    if (
        dxf_layer_list
        and isinstance(dxf_layer_list, (list, tuple))
        and len(dxf_layer_list) >= 1
        and sum(int(x) for x in dxf_layer_list) == n_bars
        and int(dxf_layer_list[0]) >= 1
    ):
        return [int(x) for x in dxf_layer_list if int(x) > 0]

    W_usable = float(bw) - 2.0 * float(cover) - 2.0 * float(st_dia)
    db = float(main_dia)
    s_min = max(25.0, db, (4.0 / 3.0) * max(float(G_max), 0.0))
    l1_cap = max(int((max(W_usable, 0.0) + s_min) // (db + s_min)), 1)

    if n_bars <= l1_cap:
        return [n_bars]
    out = []
    rem = n_bars
    while rem > 0:
        cnt = min(rem, l1_cap)
        out.append(cnt)
        rem -= cnt
    return out


def _calc_row_open_cap(n_exist, W_usable, main_dia, s_min, ref_row_cap=None):
    """기존 열(n_exist 가닥 고정)의 빈 공간에 최소 순간격 s_min 이상을 유지하며 삽입 가능한 최대 추가 보강근 수"""
    n_exist = int(n_exist)
    db = float(main_dia)
    max_by_smin = max(int((max(W_usable, 0.0) + s_min) // (db + s_min)), 1)
    row_cap = min(max_by_smin, int(ref_row_cap)) if (ref_row_cap is not None and int(ref_row_cap) >= 2) else max_by_smin
    if n_exist <= 0:
        return max_by_smin
    if n_exist == 1:
        return max(row_cap - 1, 0)
    s_row_curr = (W_usable - n_exist * db) / (n_exist - 1)
    per_gap_cap = max(int((s_row_curr - s_min) // (db + s_min)), 0)
    if per_gap_cap <= 0:
        return 0
    return min((n_exist - 1) * per_gap_cap, max(row_cap - n_exist, 0))


def _plan_add_bars(active_layers, W_usable, main_dia, s_min, add_ea):
    """기존 배근(1열→2열→... 순서)의 빈 공간에 최소 순간격(s_min)을 만족하는 만큼 우선 삽입하고,
    초과분만 기존 주근 안쪽 다음 열(2열, 3열...)로 자동 분배하는 통합 배근 계획.
    Returns: (add_on_exist_rows: list[int], add_new_rows: list[int], l1_open_cap: int)
    """
    add_ea = max(int(add_ea), 0)
    n_exist_lyrs = len(active_layers)
    add_on_exist = [0] * n_exist_lyrs
    if n_exist_lyrs == 0:
        return [], [], 0

    l1_open_cap = _calc_row_open_cap(active_layers[0], W_usable, main_dia, s_min, ref_row_cap=None)
    if add_ea == 0:
        return add_on_exist, [], l1_open_cap

    rem = add_ea
    for idx, n_ex in enumerate(active_layers):
        ref_cap = None if idx == 0 else active_layers[0]
        cap_i = l1_open_cap if idx == 0 else _calc_row_open_cap(n_ex, W_usable, main_dia, s_min, ref_row_cap=ref_cap)
        take = min(rem, cap_i)
        add_on_exist[idx] = take
        rem -= take
        if rem <= 0:
            break

    add_new = []
    if rem > 0:
        db = float(main_dia)
        new_row_cap = max(int((max(W_usable, 0.0) + s_min) // (db + s_min)), 2)
        while rem > 0:
            c = min(rem, new_row_cap)
            add_new.append(c)
            rem -= c

    return add_on_exist, add_new, l1_open_cap


def evaluate_beam_section(
    bw, H, cover, fck, fy, fyt,
    main_dia, top_bars, bot_bars,
    st_dia, st_legs, st_spacing,
    tension_zone, mu,
    calc_method, clear_span=8000.0, joint_x=2000.0, actual_vu=150.0,
    top_layers=None, bot_layers=None, G_max=25.0,
):
    bw = max(float(bw), 100.0)
    H = max(float(H), 150.0)
    cover = max(float(cover), 20.0)
    st_spacing = max(float(st_spacing), 10.0)
    st_legs = max(int(st_legs), 1)
    top_bars = max(int(top_bars), 1)
    bot_bars = max(int(bot_bars), 1)
    G_max = max(float(G_max), 0.0)

    As_unit = REBAR_AREA.get(main_dia, 286.5)
    As_st_unit = REBAR_AREA.get(st_dia, 71.33)

    # 유효춤 d 산정
    d = max(H - cover - st_dia - main_dia / 2.0, 50.0)

    # 1. 주근 순간격 기준 및 실제 1열 순간격 기초 산정 (KDS 14 20 50 4.3.2)
    W_usable = bw - 2.0 * cover - 2.0 * float(st_dia)
    s_min = max(25.0, float(main_dia), (4.0 / 3.0) * G_max)
    max_bars_single_layer = max(int((max(W_usable, 0.0) + s_min) // (float(main_dia) + s_min)), 1)

    def calc_clear_spacing(n_layer1):
        if n_layer1 <= 1:
            return W_usable
        return (W_usable - n_layer1 * float(main_dia)) / (n_layer1 - 1)

    resolved_top_lyrs = _resolve_beam_layers(bw, cover, main_dia, st_dia, top_bars, top_layers, G_max=G_max)
    resolved_bot_lyrs = _resolve_beam_layers(bw, cover, main_dia, st_dia, bot_bars, bot_layers, G_max=G_max)
    n1_top = resolved_top_lyrs[0]
    n1_bot = resolved_bot_lyrs[0]
    active_tension_layers = resolved_top_lyrs if "상부" in tension_zone else resolved_bot_lyrs
    n1_tension = active_tension_layers[0]
    clear_top = calc_clear_spacing(n1_top)
    clear_bot = calc_clear_spacing(n1_bot)
    s_curr = calc_clear_spacing(n1_tension)

    # 보유 주근 단면적
    As_top = top_bars * As_unit
    As_bot = bot_bars * As_unit
    As_tension = As_top if "상부" in tension_zone else As_bot
    tension_bars = top_bars if "상부" in tension_zone else bot_bars

    # 2. 전단강도 (Shear Strength, KDS 14 20 22)
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

    # 3. 작용 전단력 Vu 산정
    half_span = max(float(clear_span) / 2.0, 1.0)
    if ("위치 기반" in calc_method) or ("2차 본사" in calc_method):
        reduction_factor = max(0.0, min(1.0, (half_span - float(joint_x)) / half_span))
        Vu = phiVn * reduction_factor
    elif ("실데이터" in calc_method) or ("구조계산서 기반" in calc_method):
        reduction_factor = 1.0
        Vu = float(actual_vu)
    else:
        reduction_factor = 1.0
        Vu = phiVn

    # 4. 수직이어치기 전단마찰 검토 (Shear Friction, KDS 14 20 22 - 4.5)
    phi_sf = 0.75
    Avf = Vu * 1000.0 / (phi_sf * fy * mu)  # mm²
    # 전단마찰 상한강도 (KDS 14 20 22: Vn <= min(0.2*fck*Ac, (3.3 + 0.08*fck)*Ac, 11*Ac))
    Ac = bw * H
    Vn_sf_max = phi_sf * min(0.2 * fck * Ac, (3.3 + 0.08 * fck) * Ac, 11.0 * Ac) / 1000.0  # kN
    sf_max_ok = (Vu <= Vn_sf_max + 1e-6)

    Ast = As_tension
    Vu_cap = (Ast * phi_sf * fy * mu) / 1000.0  # 보유 인장주근의 전단마찰 내력 (kN)
    if Vu_cap >= phiVn:
        x_safe = 0.0
    else:
        x_safe = half_span * (1.0 - Vu_cap / max(phiVn, 1e-6))

    need_area = Avf - Ast
    if need_area > 0:
        sf_ok = False
        add_area = need_area
        add_ea = math.ceil(add_area / As_unit)
    else:
        sf_ok = True
        add_area = 0.0
        add_ea = 0

    # 5. 전단마찰 보강근 기존 1열 사이 고정 삽입 시 주근 순간격 검토 (KDS 14 20 50 4.3.2)
    n_total_layer1 = n1_tension + add_ea
    if add_ea == 0:
        m_max_per_gap = 0
        s_after = s_curr
    elif n1_tension >= 2:
        # 기존 1열 주근 간격(s_curr)을 고정한 채 (n1-1)개 빈 공간에 add_ea를 균등 삽입 시 최대 삽입 개수
        m_max_per_gap = math.ceil(add_ea / (n1_tension - 1))
        s_after = (s_curr - m_max_per_gap * float(main_dia)) / (m_max_per_gap + 1)
    else:
        # 기존 1열 주근 1가닥(중앙 고정) 시 좌우 공간 배치 기준 순간격
        m_max_per_gap = add_ea
        s_after = (W_usable - n_total_layer1 * float(main_dia)) / max(add_ea, 1)

    curr_spacing_ok = (s_curr >= s_min - 1e-6)
    after_spacing_ok = (s_after >= s_min - 1e-6)
    spacing_ok = after_spacing_ok if add_ea > 0 else curr_spacing_ok

    # 보강근 통합 배근 계획 (1열→2열→... 기존 열 여유 공간 우선 삽입 + 초과분만 안쪽 새 열 배치)
    add_on_exist_rows, add_new_rows, l1_open_cap = _plan_add_bars(
        active_tension_layers, W_usable, main_dia, s_min, add_ea
    )
    l1_add_cnt = add_on_exist_rows[0] if add_on_exist_rows else 0

    if add_ea == 0:
        if curr_spacing_ok:
            spacing_summary_txt = f"현재 1열 순간격 {s_curr:.1f} mm (최소 기준 {s_min:.1f} mm 이상 OK)"
        elif s_curr < 0.0:
            spacing_summary_txt = f"현재 1열 순간격 0 mm 미만({s_curr:.1f} mm, 최소 기준 {s_min:.1f} mm 미만 — 2단 배근 확인)"
        else:
            spacing_summary_txt = f"현재 1열 순간격 {s_curr:.1f} mm (최소 기준 {s_min:.1f} mm 미만 — 2단 배근 확인)"
    else:
        if after_spacing_ok:
            spacing_summary_txt = (
                f"보강근(+{add_ea} EA) 기존열 사이 삽입 시 순간격 {s_after:.1f} mm ≥ 최소 {s_min:.1f} mm (1열 추가 배근 가능)"
            )
        elif l1_add_cnt > 0:
            if n1_tension >= 2:
                m_l1_fit = math.ceil(l1_add_cnt / (n1_tension - 1))
                s_l1_fit = (s_curr - m_l1_fit * float(main_dia)) / (m_l1_fit + 1)
            else:
                s_l1_fit = (W_usable - (n1_tension + l1_add_cnt) * float(main_dia)) / max(l1_add_cnt, 1)
            rem_after_l1 = add_ea - l1_add_cnt
            spacing_summary_txt = (
                f"보강근(+{add_ea} EA) 중 1열 최대 {l1_add_cnt}EA 삽입 가능·순간격 {s_l1_fit:.1f} mm ≥ {s_min:.1f} mm "
                f"(초과 {rem_after_l1}EA → 분산 배근 필요)"
            )
        elif s_after < 0.0:
            spacing_summary_txt = (
                f"보강근(+{add_ea} EA) 기존 1열 사이 삽입 시 순간격 0 mm 미만({s_after:.1f} mm) < 최소 {s_min:.1f} mm "
                f"(과밀 → 분산 배근 필요)"
            )
        else:
            spacing_summary_txt = (
                f"보강근(+{add_ea} EA) 기존 1열 사이 삽입 시 순간격 {s_after:.1f} mm < 최소 {s_min:.1f} mm "
                f"(과밀 → 분산 배근 필요)"
            )

    # 보강근 단면 예시도 배치 위치 안내 텍스트 (render_beam_svg와 1:1 동일)
    if add_ea == 0:
        add_placement_desc = ""
    elif after_spacing_ok:
        add_placement_desc = "(1열 기존 주근 사이 삽입)"
    else:
        placed_parts = []
        for r_idx, c_val in enumerate(add_on_exist_rows):
            if c_val > 0:
                placed_parts.append(f"{r_idx + 1}열 {c_val}EA")
        for n_idx, c_val in enumerate(add_new_rows):
            if c_val > 0:
                placed_parts.append(f"{len(active_tension_layers) + n_idx + 1}열 {c_val}EA")
        if len(placed_parts) == 1 and sum(add_on_exist_rows) == 0:
            add_placement_desc = f"(기존 주근 안쪽 {len(active_tension_layers) + 1}열 배치 — 예시)"
        elif len(placed_parts) == 1 and len(add_new_rows) == 0:
            target_row = next(i + 1 for i, c in enumerate(add_on_exist_rows) if c > 0)
            add_placement_desc = f"(기존 {target_row}열 남는 공간 배치 — 예시)"
        else:
            add_placement_desc = f"({' + '.join(placed_parts)} 배치 — 예시)"

    dc_sf = Avf / max(Ast, 1.0)
    dc_shear = Vu / max(phiVn, 1.0)

    return {
        "bw": bw, "H": H, "d": d, "cover": cover,
        "As_unit": As_unit, "As_st_unit": As_st_unit,
        "As_top": As_top, "As_bot": As_bot, "Ast": Ast,
        "tension_bars": tension_bars,
        "Asv": Asv, "Av_min": Av_min, "Vc": Vc, "Vs": Vs, "Vs_max": Vs_max, "phiVn": phiVn,
        "s_max": s_max, "stirrup_detail_ok": stirrup_detail_ok,
        "Vu": Vu, "reduction_factor": reduction_factor,
        "Avf": Avf, "Vn_sf_max": Vn_sf_max, "sf_max_ok": sf_max_ok,
        "Vu_cap": Vu_cap, "x_safe": x_safe,
        "sf_ok": sf_ok, "add_area": add_area, "add_ea": add_ea,
        "dc_sf": dc_sf, "dc_shear": dc_shear,
        "G_max": G_max, "W_usable": W_usable,
        "n1_top": n1_top, "n1_bot": n1_bot,
        "active_tension_layers": active_tension_layers,
        "add_on_exist_rows": add_on_exist_rows,
        "add_new_rows": add_new_rows,
        "l1_open_cap": l1_open_cap,
        "add_placement_desc": add_placement_desc,
        "n1_tension": n1_tension, "n_total_layer1": n_total_layer1,
        "m_max_per_gap": m_max_per_gap,
        "s_min": s_min, "s_curr": s_curr, "s_after": s_after,
        "curr_spacing_ok": curr_spacing_ok, "after_spacing_ok": after_spacing_ok,
        "spacing_summary_txt": spacing_summary_txt,
        "clear_top": clear_top, "clear_bot": clear_bot,
        "min_clear_spacing": s_min,
        "max_bars_single_layer": max_bars_single_layer,
        "spacing_ok": spacing_ok,
    }


def get_vertical_joint_recommendation(H, clear_span, x_safe, joint_x):
    """사내 추천 수직 이어치기 구간 (D ~ D + 1,000 mm, 여기서 D는 총 보 춤 H) 및 x_safe 연동 산정"""
    H_val = float(H)
    Ln = max(float(clear_span), 1.0)
    half_span = Ln / 2.0
    x_s = float(x_safe)
    x_cur = float(joint_x)

    rec_start = H_val
    rec_end = min(H_val + 1000.0, half_span)

    if H_val >= half_span:
        return {
            "case": "deep_or_short",
            "rec_start": half_span,
            "rec_end": half_span,
            "in_rec": None,
            "status_label": "별도 검토",
            "headline": (
                f"추천 이어치기 구간 (D ~ D+1,000mm 기준): 보 춤(D={H_val:,.0f} mm) ≥ Ln/2({half_span:,.0f} mm) — "
                f"경간 중앙부(Ln/2 = {half_span:,.0f} mm, 0.50 Ln) 기준 별도 검토 필요"
            ),
        }

    if x_s <= rec_end + 1e-6:
        eff_start = max(x_s, rec_start)
        eff_end = rec_end
        in_rec = (eff_start - 1e-6 <= x_cur <= eff_end + 1e-6)
        return {
            "case": "normal",
            "rec_start": eff_start,
            "rec_end": eff_end,
            "in_rec": in_rec,
            "status_label": "추천 구간 내" if in_rec else "추천 구간 외",
            "headline": (
                f"추천 이어치기 구간 (D ~ D+1,000mm 기준): "
                f"{eff_start:,.0f} ~ {eff_end:,.0f} mm ({eff_start / Ln:.2f} ~ {eff_end / Ln:.2f} Ln)"
            ),
        }

    if x_s < half_span - 1e-6:
        eff_start = x_s
        eff_end = half_span
        in_rec = (eff_start - 1e-6 <= x_cur <= eff_end + 1e-6)
        return {
            "case": "need_rebar_in_base",
            "rec_start": eff_start,
            "rec_end": eff_end,
            "in_rec": in_rec,
            "status_label": "추천 구간 내" if in_rec else "추천 구간 외",
            "headline": (
                f"추천 이어치기 구간 (무보강 시공): "
                f"{eff_start:,.0f} ~ {eff_end:,.0f} mm ({eff_start / Ln:.2f} ~ 0.50 Ln) · "
                f"기본 추천 구간({rec_start:,.0f} ~ {rec_end:,.0f} mm) 배치 시 보강근 필요"
            ),
        }

    # x_safe >= clear_span / 2.0
    in_rec = (rec_start - 1e-6 <= x_cur <= rec_end + 1e-6)
    return {
        "case": "all_rebar",
        "rec_start": rec_start,
        "rec_end": rec_end,
        "in_rec": in_rec,
        "status_label": "추천 구간 내" if in_rec else "추천 구간 외",
        "headline": (
            f"추천 이어치기 구간 (D ~ D+1,000mm 기준): "
            f"{rec_start:,.0f} ~ {rec_end:,.0f} mm ({rec_start / Ln:.2f} ~ {rec_end / Ln:.2f} Ln) — "
            f"전 구간 보강 필요(해당 구간 배치 후 보강근 적용 권장)"
        ),
    }


def render_beam_svg(
    bw, H, cover, main_dia, top_bars, bot_bars,
    st_dia, st_legs, st_spacing, tension_zone,
    add_ea=0, top_layers=None, bot_layers=None, can_fit_layer1=False,
):
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

    # KDS 14 20 50 4.3.2 최소 순간격(s_min) 기준 1열 최대 배근수 (상·하부 및 단면 검토 공통 기준)
    W_usable_kds = float(bw) - 2.0 * float(cover) - 2.0 * float(st_dia)
    s_min_kds = max(25.0, float(main_dia), (4.0 / 3.0) * 25.0)
    max_single = max(int((max(W_usable_kds, 0.0) + s_min_kds) // (float(main_dia) + s_min_kds)), 2)

    resolved_top_layers = _resolve_beam_layers(bw, cover, main_dia, st_dia, top_bars, top_layers)
    resolved_bot_layers = _resolve_beam_layers(bw, cover, main_dia, st_dia, bot_bars, bot_layers)
    is_top_tension = "상부" in tension_zone
    add_ea = max(int(add_ea), 0)
    active_layers = resolved_top_layers if is_top_tension else resolved_bot_layers
    opp_layers = resolved_bot_layers if is_top_tension else resolved_top_layers

    # 기존 주근 반지름 및 좌표는 원설계 배근 기준으로 완전 고정 (미배근 ↔ 배근 후 토글 시 기존 주근 위치·크기 불변)
    max_in_row_orig = max([1] + resolved_top_layers + resolved_bot_layers)
    r_px_base = max(min(main_dia * scale * 0.45, 11.0), 5.5)
    r_px = min(r_px_base, max(2.8, (st_w - 14.0) / max(2.55 * max_in_row_orig, 1.0)))
    row_gap = 5.0

    def _row_x_positions(n_cnt, rad=None):
        rr = r_px if rad is None else rad
        if n_cnt <= 1:
            return [st_x0 + st_w / 2.0]
        return [st_x0 + rr + 4.0 + idx * ((st_w - 2.0 * rr - 8.0) / (n_cnt - 1)) for idx in range(n_cnt)]

    def get_bar_coords(layers, is_top=True):
        coords = []
        y_base = (st_y0 + r_px + 4.0) if is_top else (st_y0 + st_h - r_px - 4.0)
        y_step = (2.0 * r_px + row_gap) if is_top else -(2.0 * r_px + row_gap)

        for l_idx, l_cnt in enumerate(layers):
            cy_l = y_base + l_idx * y_step
            for cx in _row_x_positions(l_cnt):
                coords.append((cx, cy_l, l_idx + 1))
        return coords

    top_coords = get_bar_coords(resolved_top_layers, is_top=True)
    bot_coords = get_bar_coords(resolved_bot_layers, is_top=False)

    def _pick_symmetric_indices(total_slots, k):
        """0 .. total_slots-1 중 k개 인덱스를 좌우 대칭·균등 선택"""
        if k <= 0 or total_slots <= 0:
            return []
        if k >= total_slots:
            return list(range(total_slots))
        if k == 1:
            return [(total_slots - 1) // 2]
        chosen = set()
        for j in range(k // 2):
            off = int((j + 0.5) * (total_slots - 1) / k)
            chosen.add(off)
            chosen.add(total_slots - 1 - off)
        if k % 2 == 1:
            chosen.add((total_slots - 1) // 2)
        return sorted(chosen)

    # 추가 보강근 통합 배치 계산 (1열→2열→... 기존 열 여유 공간 우선 삽입 후, 초과분만 안쪽 새 열 배치; 기존 주근 위치·크기 완전 고정)
    add_coords = []
    r_add = r_px

    if add_ea > 0:
        y_base_act = (st_y0 + r_px + 4.0) if is_top_tension else (st_y0 + st_h - r_px - 4.0)
        y_step_act = (2.0 * r_px + row_gap) if is_top_tension else -(2.0 * r_px + row_gap)
        y_base_opp = (st_y0 + st_h - r_px - 4.0) if is_top_tension else (st_y0 + r_px + 4.0)
        y_step_opp = -(2.0 * r_px + row_gap) if is_top_tension else (2.0 * r_px + row_gap)

        act_inner_y = y_base_act + (len(active_layers) - 1) * y_step_act
        opp_inner_y = y_base_opp + (len(opp_layers) - 1) * y_step_opp

        add_on_exist, add_new_rows, _ = _plan_add_bars(
            active_layers, W_usable_kds, main_dia, s_min_kds, add_ea
        )

        # Step A: 기존 열(1열→2열→...) 여유 공간에 기존 주근 이동 없이 대칭 삽입
        for row_idx, take_cnt in enumerate(add_on_exist):
            if take_cnt <= 0:
                continue
            y_row = y_base_act + row_idx * y_step_act
            n_ex = active_layers[row_idx]
            exist_xs = _row_x_positions(n_ex)
            if n_ex == 1:
                x_center = exist_xs[0]
                ref_cols = max(active_layers[0] if row_idx > 0 else max_single, 2)
                grid_xs = _row_x_positions(ref_cols)
                avail_cols = [gx for gx in grid_xs if abs(gx - x_center) >= 2.0 * r_px + 1.5]
                if len(avail_cols) >= take_cnt:
                    picked = []
                    lo, hi = 0, len(avail_cols) - 1
                    while len(picked) < take_cnt and lo <= hi:
                        picked.append(avail_cols[lo])
                        if len(picked) < take_cnt and hi != lo:
                            picked.append(avail_cols[hi])
                        lo += 1
                        hi -= 1
                    for gx in sorted(picked):
                        add_coords.append((gx, y_row))
                else:
                    x_left_edge = st_x0 + r_px + 4.0
                    x_right_edge = st_x0 + st_w - r_px - 4.0
                    n_left = take_cnt // 2
                    n_right = take_cnt - n_left
                    min_sub_step = None
                    for side_n, xa, xb in ((n_left, x_left_edge, x_center), (n_right, x_center, x_right_edge)):
                        if side_n <= 0:
                            continue
                        step = (xb - xa) / (side_n + 1)
                        if min_sub_step is None or step < min_sub_step:
                            min_sub_step = step
                        for t in range(side_n):
                            add_coords.append((xa + (t + 1) * step, y_row))
                    if min_sub_step is not None and min_sub_step < r_px + r_add + 0.6:
                        r_add = max(2.2, min(r_add, min_sub_step - r_px - 0.6, (min_sub_step - 0.6) / 2.0))
            else:
                n_gaps = n_ex - 1
                base_per_gap, extra_bars = divmod(take_cnt, n_gaps)
                extra_gaps = set(_pick_symmetric_indices(n_gaps, extra_bars))
                min_sub_step = None
                for g_idx in range(n_gaps):
                    k_in_gap = base_per_gap + (1 if g_idx in extra_gaps else 0)
                    if k_in_gap <= 0:
                        continue
                    x_l, x_r = exist_xs[g_idx], exist_xs[g_idx + 1]
                    sub_step = (x_r - x_l) / (k_in_gap + 1)
                    if min_sub_step is None or sub_step < min_sub_step:
                        min_sub_step = sub_step
                    for t in range(k_in_gap):
                        add_coords.append((x_l + (t + 1) * sub_step, y_row))
                if min_sub_step is not None and min_sub_step < r_px + r_add + 0.6:
                    r_add = max(2.2, min(r_add, min_sub_step - r_px - 0.6, (min_sub_step - 0.6) / 2.0))

        # Step B: 기존 열에 넣고 남은 초과 보강근만 기존 주근 안쪽 다음 단부터 자동 줄바꿈 배치
        if add_new_rows:
            r_add = min(r_add, max(2.2, (st_w - 14.0) / max(2.55 * max(add_new_rows), 1.0)))

            avail_web_h = abs(opp_inner_y - act_inner_y) - 2.0 * r_px
            num_add_rows = len(add_new_rows)
            add_gap = row_gap
            needed_h = num_add_rows * (2.0 * r_add) + (num_add_rows + 1) * add_gap
            if avail_web_h > 0 and needed_h > avail_web_h:
                add_gap = max(1.5, min(row_gap, avail_web_h / max(num_add_rows * 4.0, 1.0)))
                r_add = min(r_add, max(2.2, (avail_web_h - (num_add_rows + 1) * add_gap) / max(2.0 * num_add_rows, 1.0)))

            dir_sign = 1.0 if is_top_tension else -1.0
            y_add_start = act_inner_y + dir_sign * (r_px + r_add + add_gap)
            y_safe_limit = opp_inner_y - dir_sign * (r_px + r_add + add_gap)
            eff_add_step = dir_sign * (2.0 * r_add + add_gap)
            if num_add_rows > 1:
                y_add_end = y_add_start + (num_add_rows - 1) * eff_add_step
                if (is_top_tension and y_add_end > y_safe_limit) or ((not is_top_tension) and y_add_end < y_safe_limit):
                    eff_add_step = (y_safe_limit - y_add_start) / (num_add_rows - 1)

            for r_i, cnt_row in enumerate(add_new_rows):
                cy_add = y_add_start + r_i * eff_add_step
                if is_top_tension:
                    cy_add = min(cy_add, y_safe_limit)
                else:
                    cy_add = max(cy_add, y_safe_limit)
                for cx_add in _row_x_positions(cnt_row, rad=r_add):
                    add_coords.append((cx_add, cy_add))

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
    for cx, cy in add_coords:
        bars_svg += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_add:.1f}" fill="#22c55e" stroke="#14532d" stroke-width="2" stroke-dasharray="2,2"/>'

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


def render_vertical_joint_elevation_svg(
    clear_span, joint_x, phiVn, Vu, Vu_cap, x_safe,
    reduction_factor, sf_ok, add_ea, main_dia, tension_zone,
    bw=600.0, H=600.0
):
    """2차 본사 검토(위치 기반 전단력 감소)용 보 종단면(입면도) + 전단력 분포도(SFD) 1:1 수직 정렬 SVG"""
    Ln = max(float(clear_span), 1000.0)
    half_L = Ln / 2.0
    jx = max(0.0, min(half_L, float(joint_x)))
    xs = max(0.0, min(half_L, float(x_safe)))
    phiVn_v = max(float(phiVn), 1.0)
    Vu_v = max(0.0, float(Vu))
    Vcap_v = max(0.0, float(Vu_cap))

    svg_w, svg_h = 980, 442
    col_w = 46.0
    x_s0 = 92.0
    x_s1 = 888.0
    span_w = x_s1 - x_s0
    x_mid = (x_s0 + x_s1) / 2.0

    def x_px(x_mm):
        return x_s0 + (max(0.0, min(Ln, float(x_mm))) / Ln) * span_w

    # ── 상단: 보 종단면 입면도 좌표 ──
    y_col_t, y_col_b = 58.0, 190.0
    y_b0, y_b1 = 86.0, 160.0
    beam_h_px = y_b1 - y_b0
    is_top_tension = "상부" in str(tension_zone)
    top_bar_col = "#ef4444" if is_top_tension else "#3b82f6"
    bot_bar_col = "#3b82f6" if is_top_tension else "#ef4444"

    x_safe_l = x_px(xs)
    x_safe_r = x_px(Ln - xs)
    x_j = x_px(jx)
    joint_col = "#22c55e" if sf_ok else "#f97316"

    # 사내 추천 이어치기 구간 (D ~ D+1,000mm + x_safe 연동)
    vj_rec = get_vertical_joint_recommendation(H=H, clear_span=Ln, x_safe=xs, joint_x=jx)

    # 무보강 가능 구간 음영 (상단 입면도)
    safe_w_px = max(0.0, x_safe_r - x_safe_l)
    safe_zone_label = (
        "전 구간 무보강 이어치기 가능 (x_safe = 0 mm)"
        if xs <= 1e-6
        else f"무보강 이어치기 가능 구간 (x ≥ {xs:.0f} mm, {xs/Ln:.2f}Ln)"
    )
    elev_safe_svg = (
        f'<rect x="{x_safe_l:.1f}" y="{y_b0:.1f}" width="{safe_w_px:.1f}" height="{beam_h_px:.1f}" '
        f'fill="rgba(34, 197, 94, 0.16)" stroke="none"/>'
    )
    if xs > 1e-6:
        elev_safe_svg += (
            f'<line x1="{x_safe_l:.1f}" y1="{y_b0-6:.1f}" x2="{x_safe_l:.1f}" y2="{y_b1+6:.1f}" stroke="#22c55e" stroke-width="1.3" stroke-dasharray="4,3"/>'
            f'<line x1="{x_safe_r:.1f}" y1="{y_b0-6:.1f}" x2="{x_safe_r:.1f}" y2="{y_b1+6:.1f}" stroke="#22c55e" stroke-width="1.3" stroke-dasharray="4,3"/>'
        )

    # ── 하단: 전단력 분포도(SFD) 좌표 (동일 X축 x_s0 ~ x_s1 1:1 정렬) ──
    y_vtop = 248.0
    y_v0 = 384.0
    sfd_h = y_v0 - y_vtop

    # 사내 추천 이어치기 구간 시각화 (상단 입면도 + 하단 SFD 1:1 수직 정렬)
    elev_rec_svg = ""
    sfd_rec_svg = ""
    if vj_rec["case"] == "deep_or_short":
        rec_pill_w = 196.0
        rec_pill_x = x_mid - rec_pill_w / 2.0
        elev_rec_svg = (
            f'<line x1="{x_mid:.1f}" y1="{y_b0-7:.1f}" x2="{x_mid:.1f}" y2="{y_b1+4:.1f}" '
            f'stroke="#facc15" stroke-width="2.0" stroke-dasharray="4,3"/>'
            f'<rect x="{rec_pill_x:.1f}" y="58" width="{rec_pill_w:.1f}" height="18" rx="4" '
            f'fill="rgba(15,23,42,0.94)" stroke="#facc15" stroke-width="1.1"/>'
            f'<text x="{x_mid:.1f}" y="70.5" fill="#fde047" font-size="9.8" font-weight="800" text-anchor="middle">'
            f'★ 추천: 중앙부(Ln/2) 별도 검토</text>'
        )
        sfd_rec_svg = (
            f'<line x1="{x_mid:.1f}" y1="{y_vtop:.1f}" x2="{x_mid:.1f}" y2="{y_v0:.1f}" '
            f'stroke="#facc15" stroke-width="1.4" stroke-dasharray="3,3" stroke-opacity="0.75"/>'
        )
    elif vj_rec["rec_end"] > vj_rec["rec_start"] + 1e-6:
        rec_s = vj_rec["rec_start"]
        rec_e = vj_rec["rec_end"]
        x_rl0 = x_px(rec_s)
        x_rl1 = x_px(rec_e)
        rec_w = max(2.0, x_rl1 - x_rl0)
        x_rl_mid = (x_rl0 + x_rl1) / 2.0

        # 우측 대칭 추천 구간 (Ln - rec_end ~ Ln - rec_start)
        x_rr0 = x_px(Ln - rec_e)
        x_rr1 = x_px(Ln - rec_s)
        rec_rw = max(0.0, x_rr1 - x_rr0)

        rec_tag_prefix = "★ 추천 구간" if vj_rec["case"] != "all_rebar" else "★ 추천(보강)"
        rec_pill_txt = f"{rec_tag_prefix} {rec_s:,.0f}~{rec_e:,.0f}mm ({rec_s/Ln:.2f}~{rec_e/Ln:.2f}Ln)"
        rec_pill_w = max(210.0, min(286.0, len(rec_pill_txt) * 7.2 + 18.0))
        rec_pill_x = max(x_s0, min(x_s1 - rec_pill_w, x_rl_mid - rec_pill_w / 2.0))

        # 상단 입면도 좌측 추천 구간 하이라이트 + 상부 브래킷 & 배지
        elev_rec_svg = (
            f'<rect x="{x_rl0:.1f}" y="{y_b0+1:.1f}" width="{rec_w:.1f}" height="{beam_h_px-2:.1f}" '
            f'fill="rgba(250, 204, 21, 0.24)" stroke="#facc15" stroke-width="1.6" stroke-dasharray="4,2"/>'
            f'<line x1="{x_rl0:.1f}" y1="{y_b0-6:.1f}" x2="{x_rl1:.1f}" y2="{y_b0-6:.1f}" stroke="#facc15" stroke-width="1.8"/>'
            f'<line x1="{x_rl0:.1f}" y1="{y_b0-9:.1f}" x2="{x_rl0:.1f}" y2="{y_b0-2:.1f}" stroke="#facc15" stroke-width="1.6"/>'
            f'<line x1="{x_rl1:.1f}" y1="{y_b0-9:.1f}" x2="{x_rl1:.1f}" y2="{y_b0-2:.1f}" stroke="#facc15" stroke-width="1.6"/>'
            f'<rect x="{rec_pill_x:.1f}" y="58" width="{rec_pill_w:.1f}" height="18" rx="4" '
            f'fill="rgba(15,23,42,0.94)" stroke="#facc15" stroke-width="1.1"/>'
            f'<text x="{rec_pill_x + rec_pill_w/2:.1f}" y="70.5" fill="#fde047" font-size="9.7" font-weight="800" text-anchor="middle">'
            f'{rec_pill_txt}</text>'
        )
        # 우측 대칭 구간(좌측과 겹치지 않는 경우 연하게 보조 표시)
        if rec_rw >= 2.0 and x_rr0 >= x_rl1 - 1.0:
            elev_rec_svg += (
                f'<rect x="{x_rr0:.1f}" y="{y_b0+1:.1f}" width="{rec_rw:.1f}" height="{beam_h_px-2:.1f}" '
                f'fill="rgba(250, 204, 21, 0.11)" stroke="#facc15" stroke-opacity="0.55" stroke-width="1.1" stroke-dasharray="4,3"/>'
            )

        # 하단 SFD 좌측 추천 구간 수직 밴드 + 바닥 강조 바 (1:1 정렬)
        sfd_rec_svg = (
            f'<rect x="{x_rl0:.1f}" y="{y_vtop:.1f}" width="{rec_w:.1f}" height="{sfd_h:.1f}" '
            f'fill="rgba(250, 204, 21, 0.11)" stroke="none"/>'
            f'<line x1="{x_rl0:.1f}" y1="{y_vtop:.1f}" x2="{x_rl0:.1f}" y2="{y_v0:.1f}" '
            f'stroke="#facc15" stroke-width="1.2" stroke-dasharray="3,3" stroke-opacity="0.7"/>'
            f'<line x1="{x_rl1:.1f}" y1="{y_vtop:.1f}" x2="{x_rl1:.1f}" y2="{y_v0:.1f}" '
            f'stroke="#facc15" stroke-width="1.2" stroke-dasharray="3,3" stroke-opacity="0.7"/>'
            f'<rect x="{x_rl0:.1f}" y="{y_v0-4.0:.1f}" width="{rec_w:.1f}" height="4.0" fill="#facc15" rx="1"/>'
        )
        if rec_rw >= 2.0 and x_rr0 >= x_rl1 - 1.0:
            sfd_rec_svg += (
                f'<rect x="{x_rr0:.1f}" y="{y_vtop:.1f}" width="{rec_rw:.1f}" height="{sfd_h:.1f}" '
                f'fill="rgba(250, 204, 21, 0.05)" stroke="none"/>'
                f'<rect x="{x_rr0:.1f}" y="{y_v0-3.0:.1f}" width="{rec_rw:.1f}" height="3.0" fill="#facc15" fill-opacity="0.45" rx="1"/>'
            )

    if safe_w_px >= 140:
        elev_safe_svg += (
            f'<text x="{x_mid:.1f}" y="{(y_b0+y_b1)/2+4:.1f}" fill="#86efac" font-size="11.0" font-weight="800" text-anchor="middle">{safe_zone_label}</text>'
        )

    # Vcap >= phiVn 인 예외 케이스에서도 그래프 상단을 벗어나지 않도록 안전 스케일링
    v_cap_visual = min(Vcap_v, phiVn_v * 1.12)
    v_max_plot = max(phiVn_v, v_cap_visual, 1.0) * 1.08

    def y_v(v_val):
        frac = max(0.0, min(1.0, float(v_val) / v_max_plot))
        return y_v0 - frac * sfd_h

    y_phivn = y_v(phiVn_v)
    y_cap = y_v(v_cap_visual)
    y_vu = y_v(min(Vu_v, v_max_plot))

    # SFD 폴리곤: 좌/우 위험(보강 필요) 날개 + 중앙 무보강 가능 구간 분리 음영
    sfd_polys = []
    if xs > 1e-6:
        # 좌측 보강 필요 구간 (0 ~ x_safe)
        sfd_polys.append(
            f'<polygon points="{x_s0:.1f},{y_v0:.1f} {x_s0:.1f},{y_phivn:.1f} {x_safe_l:.1f},{y_cap:.1f} {x_safe_l:.1f},{y_v0:.1f}" '
            f'fill="rgba(239, 68, 68, 0.18)" stroke="none"/>'
        )
        # 우측 보강 필요 구간 (Ln - x_safe ~ Ln)
        sfd_polys.append(
            f'<polygon points="{x_safe_r:.1f},{y_v0:.1f} {x_safe_r:.1f},{y_cap:.1f} {x_s1:.1f},{y_phivn:.1f} {x_s1:.1f},{y_v0:.1f}" '
            f'fill="rgba(239, 68, 68, 0.18)" stroke="none"/>'
        )
        # 중앙 무보강 가능 구간 (x_safe ~ Ln/2 ~ Ln - x_safe)
        sfd_polys.append(
            f'<polygon points="{x_safe_l:.1f},{y_v0:.1f} {x_safe_l:.1f},{y_cap:.1f} {x_mid:.1f},{y_v0:.1f} {x_safe_r:.1f},{y_cap:.1f} {x_safe_r:.1f},{y_v0:.1f}" '
            f'fill="rgba(56, 189, 248, 0.20)" stroke="none"/>'
        )
    else:
        # 전 구간 무보강 가능 (x_safe = 0)
        sfd_polys.append(
            f'<polygon points="{x_s0:.1f},{y_v0:.1f} {x_s0:.1f},{y_phivn:.1f} {x_mid:.1f},{y_v0:.1f} {x_s1:.1f},{y_phivn:.1f} {x_s1:.1f},{y_v0:.1f}" '
            f'fill="rgba(34, 197, 94, 0.20)" stroke="none"/>'
        )

    # SFD 대칭 선형 분포선 (ΦVn -> 0 -> ΦVn)
    sfd_outline = (
        f'<polyline points="{x_s0:.1f},{y_phivn:.1f} {x_mid:.1f},{y_v0:.1f} {x_s1:.1f},{y_phivn:.1f}" '
        f'fill="none" stroke="#38bdf8" stroke-width="2.4"/>'
    )

    # 전단마찰 내력 수평선 Vcap 및 교점(x_safe) 마커
    vcap_lbl = (
        f"전단마찰 내력 Vcap = {Vcap_v:.1f} kN ≥ ΦVn (전 구간 OK)"
        if Vcap_v >= phiVn_v
        else f"전단마찰 내력 Vcap = {Vcap_v:.1f} kN (φ·Ast·fy·μ)"
    )
    cap_line_svg = (
        f'<line x1="{x_s0:.1f}" y1="{y_cap:.1f}" x2="{x_s1:.1f}" y2="{y_cap:.1f}" '
        f'stroke="#22c55e" stroke-width="1.8" stroke-dasharray="6,4"/>'
        f'<rect x="{x_s1-265:.1f}" y="{max(y_vtop-16, y_cap-21):.1f}" width="260" height="17" rx="4" fill="rgba(15,23,42,0.90)" stroke="#22c55e" stroke-width="0.9"/>'
        f'<text x="{x_s1-135:.1f}" y="{max(y_vtop-16, y_cap-21)+12.0:.1f}" fill="#4ade80" font-size="9.8" font-weight="800" text-anchor="middle">{vcap_lbl}</text>'
    )
    if 1e-6 < xs < half_L - 1e-6:
        cap_line_svg += (
            f'<circle cx="{x_safe_l:.1f}" cy="{y_cap:.1f}" r="4.5" fill="#0f172a" stroke="#22c55e" stroke-width="2.2"/>'
            f'<line x1="{x_safe_l:.1f}" y1="{y_cap:.1f}" x2="{x_safe_l:.1f}" y2="{y_v0:.1f}" stroke="#22c55e" stroke-width="1.2" stroke-dasharray="3,3"/>'
            f'<text x="{x_safe_l:.1f}" y="{y_v0+15:.1f}" fill="#4ade80" font-size="9.5" font-weight="800" text-anchor="middle">x_safe={xs:.0f}</text>'
            f'<circle cx="{x_safe_r:.1f}" cy="{y_cap:.1f}" r="4.0" fill="#0f172a" stroke="#22c55e" stroke-width="1.8"/>'
        )

    # 현재 이어치기 위치(joint_x) 수직 연결선 + 상단/하단 콜아웃 배지 (좌우 잘림 방지 클램핑)
    status_pill_txt = "OK 무보강" if sf_ok else f"NG +{add_ea}-D{main_dia}"
    top_pill_w = 248.0
    top_pill_x = max(x_s0, min(x_s1 - top_pill_w, x_j - top_pill_w / 2.0))
    vu_pill_w = 198.0
    vu_pill_x = max(x_s0 + 4.0, min(x_s1 - vu_pill_w - 4.0, x_j + 10.0))
    vu_pill_y = max(y_vtop + 2.0, min(y_v0 - 24.0, y_vu - 22.0))

    joint_link_svg = (
        # 상단 입면도 -> 하단 SFD 1:1 수직 연결 점선
        f'<line x1="{x_j:.1f}" y1="{y_b0-10:.1f}" x2="{x_j:.1f}" y2="{y_v0:.1f}" '
        f'stroke="{joint_col}" stroke-width="2.2" stroke-dasharray="6,4"/>'
        # 상단 입면도 내 굵은 수직 이어치기선
        f'<line x1="{x_j:.1f}" y1="{y_b0-4:.1f}" x2="{x_j:.1f}" y2="{y_b1+4:.1f}" '
        f'stroke="{joint_col}" stroke-width="3.4"/>'
        f'<circle cx="{x_j:.1f}" cy="{y_b0-4:.1f}" r="3.4" fill="{joint_col}"/>'
        f'<circle cx="{x_j:.1f}" cy="{y_b1+4:.1f}" r="3.4" fill="{joint_col}"/>'
        # 상단 이어치기 콜아웃 배지
        f'<rect x="{top_pill_x:.1f}" y="{y_b1+12:.1f}" width="{top_pill_w:.1f}" height="20" rx="5" fill="rgba(15,23,42,0.92)" stroke="{joint_col}" stroke-width="1.2"/>'
        f'<text x="{top_pill_x+top_pill_w/2:.1f}" y="{y_b1+25.5:.1f}" fill="{joint_col}" font-size="10.2" font-weight="800" text-anchor="middle">'
        f'이어치기 x={jx:.0f}mm ({jx/Ln:.2f}Ln) · {status_pill_txt}</text>'
        # 하단 SFD 현재 작용 전단력 포인트 (joint_x, Vu)
        f'<circle cx="{x_j:.1f}" cy="{y_vu:.1f}" r="5.5" fill="{joint_col}" stroke="#0f172a" stroke-width="1.8"/>'
        f'<rect x="{vu_pill_x:.1f}" y="{vu_pill_y:.1f}" width="{vu_pill_w:.1f}" height="19" rx="4" fill="rgba(15,23,42,0.92)" stroke="{joint_col}" stroke-width="1.1"/>'
        f'<text x="{vu_pill_x+vu_pill_w/2:.1f}" y="{vu_pill_y+13.0:.1f}" fill="{joint_col}" font-size="10.0" font-weight="800" text-anchor="middle">'
        f'Vu(x) = {Vu_v:.1f} kN (감소 {reduction_factor:.2f})</text>'
    )

    # X축 눈금 (0, Ln/4, Ln/2, 3Ln/4, Ln)
    ticks_svg = ""
    for frac, t_lbl in [(0.0, "0 (단부)"), (0.25, f"Ln/4 ({Ln*0.25:.0f})"), (0.5, f"Ln/2 ({Ln*0.5:.0f}, 중앙)"), (0.75, f"3Ln/4 ({Ln*0.75:.0f})"), (1.0, f"Ln ({Ln:.0f})")]:
        tx = x_s0 + frac * span_w
        ticks_svg += (
            f'<line x1="{tx:.1f}" y1="{y_v0:.1f}" x2="{tx:.1f}" y2="{y_v0+5:.1f}" stroke="#64748b" stroke-width="1.2"/>'
            f'<text x="{tx:.1f}" y="{y_v0+30:.1f}" fill="#94a3b8" font-size="9.8" font-weight="700" text-anchor="middle">{t_lbl}</text>'
        )

    svg = (
        f'<div style="background:#0f172a; padding:12px; border-radius:12px; border:1px solid #334155;">'
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><pattern id="vgrid" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<path d="M 24 0 L 0 0 0 24" fill="none" stroke="#1e293b" stroke-width="1"/></pattern></defs>'
        f'<rect width="100%" height="100%" fill="url(#vgrid)" rx="8"/>'
        # 헤더 타이틀
        f'<text x="20" y="24" fill="#38bdf8" font-size="12.0" font-weight="800">● 상단: 보 종단면 입면도 (순경간 Ln = {Ln:.0f} mm · 단면 {bw:.0f}×{H:.0f})</text>'
        f'<text x="{svg_w-20}" y="24" fill="#94a3b8" font-size="10.8" font-weight="700" text-anchor="end">ΦVn = {phiVn_v:.1f} kN | Vcap = {Vcap_v:.1f} kN | x_safe = {xs:.0f} mm</text>'
        # 순경간 Ln 치수선
        f'<line x1="{x_s0:.1f}" y1="44" x2="{x_s1:.1f}" y2="44" stroke="#cbd5e1" stroke-width="1.3"/>'
        f'<line x1="{x_s0:.1f}" y1="38" x2="{x_s0:.1f}" y2="50" stroke="#cbd5e1" stroke-width="1.3"/>'
        f'<line x1="{x_s1:.1f}" y1="38" x2="{x_s1:.1f}" y2="50" stroke="#cbd5e1" stroke-width="1.3"/>'
        f'<rect x="{x_mid-72:.1f}" y="34" width="144" height="18" rx="4" fill="#0f172a"/>'
        f'<text x="{x_mid:.1f}" y="47" fill="#f8fafc" font-size="11.0" font-weight="800" text-anchor="middle">순경간 Ln = {Ln:.0f} mm</text>'
        # 양단 지점 기둥
        f'<rect x="{x_s0-col_w:.1f}" y="{y_col_t:.1f}" width="{col_w:.1f}" height="{y_col_b-y_col_t:.1f}" fill="#334155" stroke="#64748b" stroke-width="2" rx="2"/>'
        f'<text x="{x_s0-col_w/2:.1f}" y="{(y_col_t+y_col_b)/2+4:.1f}" fill="#cbd5e1" font-size="10.0" font-weight="800" text-anchor="middle">기둥</text>'
        f'<rect x="{x_s1:.1f}" y="{y_col_t:.1f}" width="{col_w:.1f}" height="{y_col_b-y_col_t:.1f}" fill="#334155" stroke="#64748b" stroke-width="2" rx="2"/>'
        f'<text x="{x_s1+col_w/2:.1f}" y="{(y_col_t+y_col_b)/2+4:.1f}" fill="#cbd5e1" font-size="10.0" font-weight="800" text-anchor="middle">기둥</text>'
        # 보 본체 외곽 + 무보강 음영 + 추천 이어치기 구간 + 상하부 주근
        f'<rect x="{x_s0:.1f}" y="{y_b0:.1f}" width="{span_w:.1f}" height="{beam_h_px:.1f}" fill="#1e293b" stroke="#94a3b8" stroke-width="2.2"/>'
        f'{elev_safe_svg}'
        f'{elev_rec_svg}'
        f'<line x1="{x_s0-18:.1f}" y1="{y_b0+11:.1f}" x2="{x_s1+18:.1f}" y2="{y_b0+11:.1f}" stroke="{top_bar_col}" stroke-width="2.8"/>'
        f'<line x1="{x_s0-18:.1f}" y1="{y_b1-11:.1f}" x2="{x_s1+18:.1f}" y2="{y_b1-11:.1f}" stroke="{bot_bar_col}" stroke-width="2.8"/>'
        # 패널 구분선 & 하단 SFD 헤더
        f'<line x1="20" y1="210" x2="{svg_w-20}" y2="210" stroke="#334155" stroke-width="1" stroke-dasharray="4,4"/>'
        f'<text x="20" y="232" fill="#38bdf8" font-size="12.0" font-weight="800">● 하단: 전단력 분포도 SFD (|V(x)| = ΦVn · |1 - 2x/Ln|)</text>'
        # SFD 축 & 단부 ΦVn 라벨
        f'<line x1="{x_s0:.1f}" y1="{y_vtop-6:.1f}" x2="{x_s0:.1f}" y2="{y_v0:.1f}" stroke="#64748b" stroke-width="1.3"/>'
        f'<line x1="{x_s0:.1f}" y1="{y_v0:.1f}" x2="{x_s1:.1f}" y2="{y_v0:.1f}" stroke="#94a3b8" stroke-width="1.5"/>'
        f'<text x="{x_s0-8:.1f}" y="{y_phivn+4:.1f}" fill="#7dd3fc" font-size="10.0" font-weight="800" text-anchor="end">ΦVn {phiVn_v:.0f}</text>'
        f'<text x="{x_s0-8:.1f}" y="{y_v0+4:.1f}" fill="#94a3b8" font-size="9.5" font-weight="700" text-anchor="end">0 kN</text>'
        f'<text x="{x_s1+8:.1f}" y="{y_phivn+4:.1f}" fill="#7dd3fc" font-size="10.0" font-weight="800" text-anchor="start">ΦVn {phiVn_v:.0f}</text>'
        # SFD 영역, 추천 구간 밴드, 외곽선, 내력선, 1:1 수직 연결 이어치기선 & 포인트, X축 눈금
        f'{"".join(sfd_polys)}'
        f'{sfd_rec_svg}'
        f'{sfd_outline}'
        f'{cap_line_svg}'
        f'{joint_link_svg}'
        f'{ticks_svg}'
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

    # 현장 조치 가이드: 스터럽 간격 축소안(s_req) & 추가 다우얼바(D10~D25) 배근표
    Avf_need_for_st = max(0.0, Avf_total - Avf_P)
    s_req = (Asv * 1000.0) / Avf_need_for_st if Avf_need_for_st > 1e-6 else st_spacing
    s_req_practical = max(int(math.floor(s_req / 10.0) * 10), 10) if Avf_need_for_st > 1e-6 else int(st_spacing)

    dowel_options = []
    if Avf_req > 1e-6:
        for d_dia in [10, 13, 16, 19, 22, 25]:
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


def evaluate_horizontal_joint_anchorage(
    bar_dia, fck, fy, H, h_joint, cover,
    use_cover_07=True,
    use_excess_reduction=True,
    Avf_req=0.0,
    Avf_prov=0.0,
    s_prov=None,
    n_prov=None,
):
    """KDS 14 20 52 기준 보 수평이어치기 전단마찰보강근 정착길이 산정, 감소계수(피복 0.7·초과철근 저감) 적용 및 부족 시 추가 배근량 역산
    - KDS 14 20 52 4.1.1(3): sqrt(fck) 상한 8.4 MPa 적용
    - KDS 14 20 52 4.1.2(2) 표 4.1-1 ('기타의 경우', α=1.0): D19 이하 0.72 / D22 이상 0.90, 초과철근 저감 후 최소 300 mm
    - KDS 14 20 52 4.1.5: 90° 표준갈고리 단일화 (구부린 끝 12db 이상), D35 이하 피복 보정계수 0.7 기본 적용(가용 깊이 h-max(c,50)), 최소 max(8db, 150 mm)
    - KDS 14 20 52 4.1.2(5), 4.1.5(3)③: 초과철근 저감계수(min(1.0, Avf,req/Avf,prov)) 적용 및 NG 시 추가 필요 배근량·간격/가닥수 역산
    - KDS 14 20 52 4.4.4(2): D16 이하 스터럽(90°/135° 갈고리, 6db 이상 연장) 간이 정착 기준 안내
    """
    bar_dia_int = int(bar_dia)
    db = float(REBAR_DB.get(bar_dia_int, float(bar_dia_int)))
    ab = float(REBAR_AREA.get(bar_dia_int, math.pi * (db ** 2) / 4.0))
    fck_val = max(float(fck), 1.0)
    fy_eff = min(float(fy), 500.0)
    H_val = max(float(H), 100.0)
    h_bot = max(0.0, min(H_val, float(h_joint)))
    h_top = max(0.0, H_val - h_bot)
    cover_val = max(float(cover), 0.0)

    # 1. sqrt(fck) 상한 8.4 MPa (KDS 14 20 52 4.1.1(3))
    sqrt_fck_raw = math.sqrt(fck_val)
    sqrt_fck = min(sqrt_fck_raw, 8.4)
    sqrt_fck_capped = sqrt_fck_raw > 8.4

    # 2. 초과철근 저감계수 (KDS 14 20 52 4.1.2(5), 4.1.5(3)③)
    Avf_req_val = max(float(Avf_req), 0.0)
    Avf_prov_val = max(float(Avf_prov), 0.0)
    if bool(use_excess_reduction) and Avf_req_val > 0.0 and Avf_prov_val > 0.0:
        excess_factor = min(1.0, Avf_req_val / Avf_prov_val)
        excess_applied = True
    else:
        excess_factor = 1.0
        excess_applied = False

    # 3. 일자(직선) 인장정착길이 ld (KDS 14 20 52 4.1.2(2) 표 4.1-1 '기타의 경우', α=1.0, 최소 300 mm)
    ld_coeff = 0.72 if bar_dia_int <= 19 else 0.90
    ld_min = 300.0
    ld_base = (ld_coeff * fy_eff / sqrt_fck) * db
    ld_after_excess = ld_base * excess_factor
    ld = max(ld_after_excess, ld_min)
    ld_min_applied = ld_after_excess < ld_min
    ld_cover_eff = cover_val
    req_h_straight = ld + ld_cover_eff

    # 4. 90° 표준갈고리 인장정착길이 ldh (KDS 14 20 52 4.1.5, 피복 보정 0.7 기본 적용, 최소 max(8db, 150 mm))
    cover_07_eligible = bar_dia_int <= 35
    cover_07_applied = bool(use_cover_07) and cover_07_eligible
    cover_07_factor = 0.7 if cover_07_applied else 1.0
    ldh_min = max(8.0 * db, 150.0)
    ldh_basic = (0.24 * fy_eff / sqrt_fck) * db
    ldh_base = ldh_basic * cover_07_factor
    ldh_after_excess = ldh_base * excess_factor
    ldh = max(ldh_after_excess, ldh_min)
    ldh_min_applied = ldh_after_excess < ldh_min
    ldh_cover_eff = max(cover_val, 50.0) if cover_07_applied else cover_val
    req_h_hook = ldh + ldh_cover_eff

    # 90° 표준갈고리 및 D16 이하 스터럽 갈고리 상세 연장길이
    hook_90_ext = 12.0 * db
    stirrup_eligible = bar_dia_int <= 16
    stirrup_hook_ext = 6.0 * db

    def _eval_method(h_zone, l_base, l_applied, l_min, c_eff):
        h_avail = h_zone - c_eff
        req_h = l_applied + c_eff
        margin = h_avail - l_applied
        if h_avail >= l_applied:
            return {
                "h_avail": h_avail,
                "c_eff": c_eff,
                "l_base": l_base,
                "l_applied": l_applied,
                "l_min": l_min,
                "req_h": req_h,
                "margin": margin,
                "ok": True,
                "status_code": "OK",
                "status_label": "OK",
                "can_solve_by_excess": True,
                "Avf_need": Avf_req_val,
                "delta_Avf": 0.0,
                "ratio_vs_req": 1.0,
                "ratio_vs_prov": 1.0,
                "add_pct_vs_req": 0.0,
                "add_pct_vs_prov": 0.0,
                "s_need": int(s_prov) if (s_prov is not None and s_prov > 0) else None,
                "n_need": int(n_prov) if (n_prov is not None and n_prov > 0) else None,
                "n_add": 0,
                "excess_msg": f"정착 가능 (여유 +{margin:.1f} mm)",
            }

        # Case A: 가용 정착 깊이가 최소 하한(l_min) 미만 -> 초과철근으로도 해결 불가
        if h_avail < l_min:
            return {
                "h_avail": h_avail,
                "c_eff": c_eff,
                "l_base": l_base,
                "l_applied": l_applied,
                "l_min": l_min,
                "req_h": req_h,
                "margin": margin,
                "ok": False,
                "status_code": "NG_BELOW_MIN",
                "status_label": "NG (하한 미만)",
                "can_solve_by_excess": False,
                "Avf_need": None,
                "delta_Avf": None,
                "ratio_vs_req": None,
                "ratio_vs_prov": None,
                "add_pct_vs_req": None,
                "add_pct_vs_prov": None,
                "s_need": None,
                "n_need": None,
                "n_add": None,
                "excess_msg": f"최소 정착길이 하한({l_min:.0f} mm) 미만 — 초과철근 추가 배근으로도 해결 불가",
            }

        # Case B: l_min <= h_avail < l_applied -> 초과철근 저감 역산 가능
        ratio_vs_req = l_base / max(h_avail, 1e-6)
        add_pct_vs_req = max(0.0, (ratio_vs_req - 1.0) * 100.0)
        if Avf_req_val > 0.0:
            Avf_need = Avf_req_val * ratio_vs_req
            Avf_ref_prov = Avf_prov_val if Avf_prov_val > 0.0 else Avf_req_val
            delta_Avf = max(0.0, Avf_need - Avf_ref_prov)
            ratio_vs_prov = Avf_need / max(Avf_ref_prov, 1e-6)
            add_pct_vs_prov = max(0.0, (ratio_vs_prov - 1.0) * 100.0)
        else:
            Avf_need = 0.0
            delta_Avf = 0.0
            ratio_vs_prov = ratio_vs_req
            add_pct_vs_prov = add_pct_vs_req

        # 간격(s_need) 및 가닥수(n_need, n_add) 환산
        s_need = None
        if s_prov is not None and float(s_prov) > 0.0:
            s_need = max(int(math.floor(float(s_prov) / max(ratio_vs_prov, 1e-6))), 10)
        n_need = None
        n_add = None
        if n_prov is not None and int(n_prov) > 0:
            n_need = int(math.ceil(float(n_prov) * ratio_vs_prov))
            n_add = max(0, n_need - int(n_prov))
        elif Avf_need > 0.0:
            n_base = int(math.ceil(Avf_prov_val / ab)) if Avf_prov_val > 0.0 else int(math.ceil(Avf_req_val / ab))
            n_need = int(math.ceil(Avf_need / ab))
            n_add = max(0, n_need - n_base)

        parts = [f"소요 대비 {ratio_vs_req:.2f}배(+{add_pct_vs_req:.1f}%)"]
        if Avf_need > 0.0:
            parts.append(f"필요 {Avf_need:.0f} mm²/m (추가 ΔAvf={delta_Avf:.0f} mm²/m, 현 배근 대비 {ratio_vs_prov:.2f}배/+{add_pct_vs_prov:.1f}%)")
        if s_need is not None and s_prov is not None:
            parts.append(f"간격 @{float(s_prov):.0f}→@{s_need} 이하")
        if n_need is not None:
            parts.append(f"최소 {n_need}EA/m (+{n_add}EA/m)")
        if not bool(use_excess_reduction):
            parts.append("[※ 초과철근 저감 옵션 해제 상태]")

        return {
            "h_avail": h_avail,
            "c_eff": c_eff,
            "l_base": l_base,
            "l_applied": l_applied,
            "l_min": l_min,
            "req_h": req_h,
            "margin": margin,
            "ok": False,
            "status_code": "NG_EXCESS_SOLVABLE",
            "status_label": "NG (초과배근 가능)",
            "can_solve_by_excess": True,
            "Avf_need": Avf_need,
            "delta_Avf": delta_Avf,
            "ratio_vs_req": ratio_vs_req,
            "ratio_vs_prov": ratio_vs_prov,
            "add_pct_vs_req": add_pct_vs_req,
            "add_pct_vs_prov": add_pct_vs_prov,
            "s_need": s_need,
            "n_need": n_need,
            "n_add": n_add,
            "excess_msg": " · ".join(parts),
        }

    def _judge_zone(zone_name, h_zone):
        st_m = _eval_method(h_zone, ld_base, ld, ld_min, ld_cover_eff)
        hk_m = _eval_method(h_zone, ldh_base, ldh, ldh_min, ldh_cover_eff)
        if st_m["ok"]:
            status_code = "STRAIGHT_OK"
            status_label = "일자 배근 가능"
            badge_cls = "badge-ok"
            guidance = (
                f"{zone_name} 일자 가용 깊이({st_m['h_avail']:.1f} mm) ≥ ld({ld:.1f} mm) — "
                f"일자(직선) 정착 및 90° 표준갈고리 정착 모두 가능합니다."
            )
        elif hk_m["ok"]:
            status_code = "HOOK_REQUIRED"
            status_label = "90° 표준갈고리 필요 (일자 불가)"
            badge_cls = "badge-warn"
            guidance = (
                f"{zone_name} 일자 배근은 {abs(st_m['margin']):.1f} mm 부족하나, 90° 표준갈고리 가용 깊이({hk_m['h_avail']:.1f} mm) ≥ ldh({ldh:.1f} mm)로 "
                f"90° 표준갈고리(구부린 끝 12db={hook_90_ext:.0f}mm 이상 연장) 정착이 가능합니다."
            )
        else:
            status_code = "INSUFFICIENT"
            status_label = "정착 깊이 부족 (90° 갈고리도 NG)"
            badge_cls = "badge-ng"
            if hk_m["can_solve_by_excess"]:
                guidance = (
                    f"{zone_name} 90° 표준갈고리 정착이 {abs(hk_m['margin']):.1f} mm 부족합니다. "
                    f"초과철근 저감 적용 시 [{hk_m['excess_msg']}]로 해결하거나, D16 이하 스터럽 정착·이어치기 위치 조정을 검토하세요."
                )
            else:
                guidance = (
                    f"{zone_name} 90° 갈고리 가용 깊이({hk_m['h_avail']:.1f} mm)가 {hk_m['excess_msg']}. "
                    f"별도 상세 검토 필요"
                )
        return {
            "zone_name": zone_name,
            "h_zone": h_zone,
            "straight": st_m,
            "hook90": hk_m,
            "status_code": status_code,
            "status_label": status_label,
            "badge_cls": badge_cls,
            "guidance": guidance,
        }

    return {
        "bar_dia": bar_dia_int,
        "db": db,
        "ab": ab,
        "fck": fck_val,
        "fy_eff": fy_eff,
        "sqrt_fck_raw": sqrt_fck_raw,
        "sqrt_fck": sqrt_fck,
        "sqrt_fck_capped": sqrt_fck_capped,
        "use_cover_07": cover_07_applied,
        "cover_07_factor": cover_07_factor,
        "use_excess_reduction": bool(use_excess_reduction),
        "excess_applied": excess_applied,
        "excess_factor": excess_factor,
        "Avf_req": Avf_req_val,
        "Avf_prov": Avf_prov_val,
        "s_prov": float(s_prov) if (s_prov is not None and float(s_prov) > 0) else None,
        "n_prov": int(n_prov) if (n_prov is not None and int(n_prov) > 0) else None,
        "ld_coeff": ld_coeff,
        "ld_base": ld_base,
        "ld": ld,
        "ld_min": ld_min,
        "ld_min_applied": ld_min_applied,
        "ld_cover_eff": ld_cover_eff,
        "req_h_straight": req_h_straight,
        "ldh_basic": ldh_basic,
        "ldh_base": ldh_base,
        "ldh": ldh,
        "ldh_min": ldh_min,
        "ldh_min_applied": ldh_min_applied,
        "ldh_cover_eff": ldh_cover_eff,
        "req_h_hook": req_h_hook,
        "hook_90_ext": hook_90_ext,
        "stirrup_eligible": stirrup_eligible,
        "stirrup_hook_ext": stirrup_hook_ext,
        "H": H_val,
        "h_top": h_top,
        "h_bot": h_bot,
        "cover": cover_val,
        "top": _judge_zone("상부 구간", h_top),
        "bot": _judge_zone("하부 구간", h_bot),
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

    resolved_top = _resolve_beam_layers(bw, cover, main_dia, st_dia, top_bars, top_layers)
    resolved_bot = _resolve_beam_layers(bw, cover, main_dia, st_dia, bot_bars, bot_layers)
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
    f'<p>CAD(DXF) 보 일람표 · KDS 기준 이어치기 전단마찰 보강 검토</p>'
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
        '<div class="dw-sidebar-sec-title">보 일람표(DXF) 도면 로드</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("캐드(DXF) 도면 파일 업로드", type=["dxf"], label_visibility="collapsed")

    if uploaded_file is not None:
        # 기존 세션이 구버전(schema_ver!=13)이면 자동 재파싱
        if st.session_state.dxf_filename != uploaded_file.name or st.session_state.get("schema_ver") != 13:
            with st.spinner(f"🛠️ '{uploaded_file.name}' 도면 층별 보 일람표 정밀 분석 중..."):
                try:
                    beams, ent_cnt = cached_parse_dxf(uploaded_file.getvalue(), uploaded_file.name, schema_ver=13)
                    st.session_state.extracted_beams = beams
                    st.session_state.dxf_filename = uploaded_file.name
                    st.session_state.entity_count = ent_cnt
                    st.session_state.schema_ver = 13
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

    st.markdown('<div class="dw-sidebar-sec-title">재료 강도 및 기준 설정</div>', unsafe_allow_html=True)
    fck = st.selectbox("콘크리트 설계기준압축강도 fck (MPa)", [21, 24, 27, 30, 35, 40, 50, 60, 70, 80], index=2)
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
            '</div></div>',
            unsafe_allow_html=True,
        )
        c_sel0, c_sel1, c_sel2, c_sel3 = st.columns([1.2, 1.8, 1.5, 1.6])

        all_beam_keys = list(st.session_state.extracted_beams.keys())
        floor_list = ["전체 층"] + list(dict.fromkeys(split_floor_and_beam(k)[0] for k in all_beam_keys))

        with c_sel0:
            selected_floor = st.selectbox("▶ 층(Floor) 선택", floor_list)
            auto_sync = st.checkbox("선택 시 즉시 반영", value=True, help="부재 또는 단면 위치를 바꾸면 아래 구조검토 입력값에 즉시 자동 반영합니다.")

        if selected_floor == "전체 층":
            filtered_beam_list = all_beam_keys
        else:
            filtered_beam_list = [k for k in all_beam_keys if split_floor_and_beam(k)[0] == selected_floor]

        with c_sel1:
            selected_beam = st.selectbox("▶ 층별 보 부호 (Floor + Mark)", filtered_beam_list)

        sections = st.session_state.extracted_beams[selected_beam]
        section_list = list(sections.keys())
        with c_sel2:
            selected_section = st.selectbox("▶ 단면 위치 (Zone)", section_list)

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
            if any(k in s_label.upper() for k in ("CENTER", "CEN", "MID")) or ("중앙" in s_label):
                st.session_state.tension_zone = "하부 인장 (정모멘트 +M)"
            else:
                st.session_state.tension_zone = "상부 인장 (부모멘트 -M)"
            if int(s_dict["st_dia"]) in [10, 13, 16, 19]:
                st.session_state.st_dia = int(s_dict["st_dia"])
            st.session_state.st_spacing = min(max(float(s_dict["st_spacing"]), 50.0), 1000.0)
            st.session_state.st_legs = min(max(int(s_dict["st_legs"]), 1), 24)
            st.session_state.selected_beam_label = f"{b_label} ({s_label})"
            st.session_state.last_synced_beam_sec = (b_label, s_label)
            for _sk in ("bw", "beam_depth", "tension_zone", "main_bar", "top_bars", "bot_bars", "st_dia", "st_legs", "st_spacing"):
                st.session_state[f"hj_{_sk}"] = st.session_state[_sk]

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
        with st.expander(f"[원본 근거 화면] '{selected_beam} — {selected_section}' (클릭하여 펼치기)", expanded=False):
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
_BEAM_SYNC_KEYS = ("bw", "beam_depth", "tension_zone", "main_bar", "top_bars", "bot_bars", "st_dia", "st_legs", "st_spacing")
for _sk in _BEAM_SYNC_KEYS:
    if f"hj_{_sk}" not in st.session_state:
        st.session_state[f"hj_{_sk}"] = st.session_state[_sk]

def _sync_vj_to_hj(k):
    st.session_state[f"hj_{k}"] = st.session_state[k]

def _sync_hj_to_vj(k):
    st.session_state[k] = st.session_state[f"hj_{k}"]

tab_v, tab_h = st.tabs([
    "↔️ 수직 이어치기 검토",
    "↕️ 수평 이어치기 검토",
])

with tab_v:
    tab_detail, tab_schedule, tab_report = st.tabs([
        "부재별 검토",
        "전체 보 일괄 구조검토표",
        "구조검토 근거",
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
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span><span class="dw-step-badge">STEP 1</span>단면 및 배근 제원 입력</div>'
                f'<span class="dw-pill-blue">현재 부재: {st.session_state.selected_beam_label}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                bw = st.number_input("보 폭 bw (mm)", min_value=150.0, max_value=5000.0, step=10.0, key="bw", on_change=_sync_vj_to_hj, args=("bw",))
                beam_depth = st.number_input("보 춤 H (mm)", min_value=200.0, max_value=5000.0, step=10.0, key="beam_depth", on_change=_sync_vj_to_hj, args=("beam_depth",))
                tension_zone = st.selectbox("인장부 위치 (검토 기준)", ["상부 인장 (부모멘트 -M)", "하부 인장 (정모멘트 +M)"], key="tension_zone", on_change=_sync_vj_to_hj, args=("tension_zone",))
            with ic2:
                main_bar = st.selectbox("주근 직경 (mm)", BAR_LIST, key="main_bar", on_change=_sync_vj_to_hj, args=("main_bar",))
                top_bars = st.number_input("상부 주근수 (TOP)", min_value=1, max_value=120, step=1, key="top_bars", on_change=_sync_vj_to_hj, args=("top_bars",))
                bot_bars = st.number_input("하부 주근수 (BOT)", min_value=1, max_value=120, step=1, key="bot_bars", on_change=_sync_vj_to_hj, args=("bot_bars",))
            with ic3:
                stirrup_bar = st.selectbox("스터럽 직경 (mm)", [10, 13, 16, 19], key="st_dia", on_change=_sync_vj_to_hj, args=("st_dia",))
                stirrup_legs = st.number_input("스터럽 가닥수 (Legs)", min_value=1, max_value=24, step=1, key="st_legs", on_change=_sync_vj_to_hj, args=("st_legs",))
                stirrup_spacing = st.number_input("스터럽 간격 s (mm)", min_value=50.0, max_value=1000.0, step=10.0, key="st_spacing", on_change=_sync_vj_to_hj, args=("st_spacing",))

            st.markdown(
                '<div class="dw-section-card" style="margin-top:0.75rem; margin-bottom:0.5rem;">'
                '<div class="dw-section-header">'
                '<div class="dw-section-title"><span class="dw-accent-bar"></span><span class="dw-step-badge">STEP 2</span>하중 및 요구 전단력(Vu) 산정 조건</div>'
                '<span class="dw-pill-blue">전단마찰 조건</span>'
                '</div></div>',
                unsafe_allow_html=True,
            )
            calc_method = st.radio(
                "전단력(Vu) 산정 방식 선택",
                [
                    "1차 현장 검토 (단면 설계전단강도를 작용 전단력으로 가정)",
                    "2차 본사 검토 (최적화, 보 순경간 및 단부 거리에 따른 전단력 감소 적용 등)",
                    "구조계산서 기반 검토 (구조계산서 계수전단력 Vu 직접 입력)",
                ],
                key="vj_calc_method_radio",
            )

            is_vj_pos_mode = ("위치 기반" in calc_method) or ("2차 본사" in calc_method)
            is_vj_vu_mode = ("실데이터" in calc_method) or ("구조계산서 기반" in calc_method)
            clear_span, joint_x, actual_vu = 8000.0, 2000.0, 250.0
            if is_vj_pos_mode:
                clear_span = st.number_input(
                    "보 순경간 Ln (mm)",
                    min_value=1000.0, max_value=30000.0, value=8000.0, step=100.0,
                    key="vj_clear_span_input",
                )
                max_jx = float(round(clear_span / 2.0, 0))
                if "vj_joint_x_slider" not in st.session_state:
                    st.session_state["vj_joint_x_slider"] = min(2000.0, max_jx)
                else:
                    st.session_state["vj_joint_x_slider"] = float(
                        min(max(float(st.session_state["vj_joint_x_slider"]), 0.0), max_jx)
                    )
                joint_x = st.slider(
                    "단부면에서 이어치기면까지 거리 x (mm)",
                    min_value=0.0,
                    max_value=max_jx,
                    step=100.0,
                    key="vj_joint_x_slider",
                    help="0(단부면) ~ Ln/2(보 중앙) 범위에서 수직 이어치기 위치를 조절하면 아래 보 종단면과 전단력 분포도(SFD)가 실시간 연동됩니다.",
                )
                span_ratio = joint_x / max(clear_span, 1.0)
                red_disp = max(0.0, min(1.0, 1.0 - 2.0 * span_ratio))
                st.caption(
                    f"📏 현재 경간비 **x / Ln = {span_ratio:.3f}** (`{span_ratio*100:.1f}%`) · "
                    f"전단력 감소계수 **(1 - 2x/Ln) = {red_disp:.3f}** (`{red_disp*100:.1f}%`)"
                )
            elif is_vj_vu_mode:
                actual_vu = st.number_input(
                    "실제 계수전단력 Vu (kN)",
                    min_value=0.0, max_value=10000.0, value=250.0, step=10.0,
                    key="vj_actual_vu_input",
                )

        # 구조검토 실행
        res = evaluate_beam_section(
            bw=bw, H=beam_depth, cover=cover, fck=fck, fy=fy, fyt=stirrup_fy,
            main_dia=main_bar, top_bars=top_bars, bot_bars=bot_bars,
            st_dia=stirrup_bar, st_legs=stirrup_legs, st_spacing=stirrup_spacing,
            tension_zone=tension_zone, mu=mu,
            calc_method=calc_method, clear_span=clear_span, joint_x=joint_x,
            actual_vu=actual_vu,
            top_layers=st.session_state.get("top_layers"),
            bot_layers=st.session_state.get("bot_layers"),
        )

        with col_vis:
            cur_svg_mode = st.session_state.get("vj_svg_view_mode", "원설계 배근 (미배근)")
            if res["add_ea"] == 0:
                vis_pill_html = '<span class="dw-pill-blue">원설계 단면 (보강 불필요)</span>'
            elif cur_svg_mode == "보강근 반영 (배근 후)":
                vis_pill_html = (
                    f'<span class="dw-pill-blue" style="background:#dcfce7; color:#15803d; border-color:#86efac;">'
                    f'보강근 반영 (+{res["add_ea"]}-D{main_bar})</span>'
                )
            else:
                vis_pill_html = (
                    f'<span class="dw-pill-blue">원설계 배근 (미배근 · 보강 +{res["add_ea"]}EA 대기)</span>'
                )

            st.markdown(
                f'<div class="dw-section-card" style="margin-bottom:0.45rem;">'
                f'<div class="dw-section-header">'
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span>실시간 보 단면 배근 예시도</div>'
                f'{vis_pill_html}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            svg_view_mode = st.radio(
                "단면도 표시 모드",
                ["원설계 배근 (미배근)", "보강근 반영 (배근 후)"],
                index=0,
                horizontal=True,
                label_visibility="collapsed",
                key="vj_svg_view_mode",
            )
            show_add_in_svg = (svg_view_mode == "보강근 반영 (배근 후)") and (res["add_ea"] > 0)
            svg_html = render_beam_svg(
                bw=bw, H=beam_depth, cover=cover, main_dia=main_bar,
                top_bars=top_bars, bot_bars=bot_bars,
                st_dia=stirrup_bar, st_legs=stirrup_legs, st_spacing=stirrup_spacing,
                tension_zone=tension_zone,
                add_ea=(res["add_ea"] if show_add_in_svg else 0),
                top_layers=st.session_state.get("top_layers"),
                bot_layers=st.session_state.get("bot_layers"),
                can_fit_layer1=res["after_spacing_ok"],
            )
            st.markdown(svg_html, unsafe_allow_html=True)
            spacing_cap_tail = (
                f"인장측 1열 {res['n1_tension']}EA 기준 (Gmax={res['G_max']:.0f}mm)"
                if res["add_ea"] == 0
                else f"현재 1열 {res['s_curr']:.1f} mm ({res['n1_tension']}EA)"
            )
            if res["add_ea"] == 0:
                add_legend_txt = "🟢 초록색: 전단마찰 추가 보강근 불필요(0EA)"
            elif not show_add_in_svg:
                add_legend_txt = (
                    f"⚪ 원설계(미배근) 표시 중 — 상단에서 '보강근 반영(배근 후)' 선택 시 "
                    f"+{res['add_ea']}-D{main_bar} 표시"
                )
            else:
                add_legend_txt = f"🟢 초록색: 전단마찰 추가 보강근 {res['add_ea']}EA {res['add_placement_desc']}"
            spacing_cap_line = res["spacing_summary_txt"]
            split_idx = spacing_cap_line.rfind(" (")
            if split_idx != -1:
                spacing_cap_line = f"{spacing_cap_line[:split_idx]}  \n{spacing_cap_line[split_idx + 1:]}"
            st.caption(
                f"🔴 빨간색: 인장측 주근({res['tension_bars']}-D{main_bar}) | "
                f"🔵 파란색: 압축측 주근  \n"
                f"{add_legend_txt}  \n"
                f"📏 {spacing_cap_line} · {spacing_cap_tail}"
            )

        # 2차 본사 검토(위치 기반 전단력 감소) 전용: 가로 전체 폭 보 종단면(입면도) + 전단력 분포도(SFD)
        elev_svg_html = ""
        if is_vj_pos_mode:
            st.markdown(
                f'<div class="dw-section-card" style="margin-top:0.85rem; margin-bottom:0.65rem;">'
                f'<div class="dw-section-header">'
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span>보 종단면(입면도) & 전단력 분포도(SFD) — 수직 이어치기 위치 연동</div>'
                f'<span class="dw-pill-blue">Ln={clear_span:.0f}mm · x={joint_x:.0f}mm ({joint_x/max(clear_span,1)*100:.1f}%)</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            elev_svg_html = render_vertical_joint_elevation_svg(
                clear_span=clear_span, joint_x=joint_x,
                phiVn=res["phiVn"], Vu=res["Vu"], Vu_cap=res["Vu_cap"],
                x_safe=res["x_safe"], reduction_factor=res["reduction_factor"],
                sf_ok=res["sf_ok"], add_ea=res["add_ea"], main_dia=main_bar,
                tension_zone=tension_zone, bw=bw, H=beam_depth,
            )
            st.markdown(elev_svg_html, unsafe_allow_html=True)
            vj_rec = get_vertical_joint_recommendation(
                H=beam_depth, clear_span=clear_span, x_safe=res["x_safe"], joint_x=joint_x,
            )
            rec_cap_txt = (
                f"🟡 노란 점선: 추천 중앙부($L_n/2$) 별도 검토"
                if vj_rec["case"] == "deep_or_short"
                else f"🟡 노란 음영: 추천 이어치기 구간 ({vj_rec['rec_start']:,.0f}~{vj_rec['rec_end']:,.0f} mm)"
            )
            st.caption(
                f"🟢 초록 음영: 무보강 이어치기 가능 구간 ($x \\ge {res['x_safe']:.0f}$ mm, $V_{{\\text{{cap}}}} = {res['Vu_cap']:.1f}$ kN) | "
                f"🔴 붉은 음영: 추가 보강 필요 구간 ($x < {res['x_safe']:.0f}$ mm)  \n"
                f"{rec_cap_txt} | 현재 위치 $x = {joint_x:.0f}$ mm → $V_u(x) = {res['Vu']:.1f}$ kN"
            )
            if vj_rec["in_rec"] is True:
                rec_badge_bg, rec_badge_fg = "#dcfce7", "#15803d"
            elif vj_rec["in_rec"] is False:
                rec_badge_bg, rec_badge_fg = "#fef3c7", "#b45309"
            else:
                rec_badge_bg, rec_badge_fg = "#e2e8f0", "#334155"
            st.markdown(
                f'<div style="background:#f0f9ff; border:1px solid #bae6fd; border-left:5px solid #0284c7; '
                f'border-radius:12px; padding:0.85rem 1.15rem; margin:0.45rem 0 0.75rem 0;">'
                f'<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-bottom:4px;">'
                f'<div style="font-size:0.88rem; font-weight:800; color:#0c4a6e;">📍 {vj_rec["headline"]}</div>'
                f'<span style="background:{rec_badge_bg}; color:{rec_badge_fg}; font-size:0.78rem; font-weight:800; '
                f'padding:2px 10px; border-radius:999px; white-space:nowrap;">{vj_rec["status_label"]}</span>'
                f'</div>'
                f'<div style="font-size:0.83rem; font-weight:500; color:#1e3a5f; line-height:1.45;">'
                f'단부 전단위험단면·부모멘트(-M)·지진 등 횡력 집중 구간(보춤 D 이내)을 회피하고, 휨모멘트 변곡점 부근에서 안정적으로 시공하기 위한 권장 위치입니다.'
                f'</div>'
                f'<div style="font-size:0.78rem; color:#475569; margin-top:3px;">'
                f'※ 작은보 교차부(집중하중)나 횡력 지배 부재는 \'구조계산서 기반 검토\'로 실제 Vu를 확인하세요.'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        # =====================================================
        # 핵심 KPI 카드 & 구조검토 결과 요약 (4열: 설계전단강도 / 적용전단력 / 전단마찰 철근량 / 추가 보강근)
        # =====================================================
        st.markdown(
            '<div class="dw-section-card" style="margin-top:1rem; margin-bottom:0.75rem;">'
            '<div class="dw-section-header">'
            '<div class="dw-section-title"><span class="dw-accent-bar"></span><span class="dw-step-badge">STEP 3</span>구조검토 결과요약</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        phivc_val = 0.75 * res["Vc"]
        phivs_val = 0.75 * min(res["Vs"], res["Vs_max"])
        if ("보수적" in calc_method) or ("1차 현장" in calc_method):
            vu_kpi_delta = "1차 현장 검토: 단면 ΦVn 100% 가정 적용"
            vu_foot_col = "#137fec"
        elif is_vj_pos_mode:
            vu_kpi_delta = f"2차 본사 검토: x={joint_x:.0f}mm (감소계수 {res['reduction_factor']:.2f}, ΦVn의 {res['reduction_factor']*100:.0f}%)"
            vu_foot_col = "#137fec"
        else:
            vu_kpi_delta = f"계산서 입력 Vu (전단 강도비 Vu/ΦVn = {res['dc_shear']*100:.0f}%)"
            vu_foot_col = "#137fec" if res["dc_shear"] <= 1.0 else "#dc2626"

        diff_area = res["Ast"] - res["Avf"]
        sf_foot_col = "#16a34a" if res["sf_ok"] else "#dc2626"
        sf_val_str = "보강 불필요" if res["sf_ok"] else f"+{res['add_ea']} EA (D{main_bar})"
        sf_delta_str = "전단마찰 안전 (OK)" if res["sf_ok"] else f"부족 철근량 {res['add_area']:.0f} mm²"

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                f'<div class="dw-kpi-card">'
                f'<div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">설계 전단강도 (ΦVn)</div>'
                f'<div class="dw-kpi-val">{res["phiVn"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN</span></div>'
                f'</div>'
                f'<div class="dw-kpi-foot" style="color:#137fec;"><span>ΦVc {phivc_val:.1f} + ΦVs {phivs_val:.1f} kN</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f'<div class="dw-kpi-card">'
                f'<div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">적용 전단력 (Vu)</div>'
                f'<div class="dw-kpi-val">{res["Vu"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN</span></div>'
                f'</div>'
                f'<div class="dw-kpi-foot" style="color:{vu_foot_col};"><span>{vu_kpi_delta}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                f'<div class="dw-kpi-card">'
                f'<div class="dw-kpi-top">'
                f'<div class="dw-kpi-label">보유 vs 요구 전단마찰 철근량</div>'
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
                f'<div class="dw-kpi-label">수직이어치기 추가 보강근</div>'
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
                f'<div style="font-size:0.78rem; font-weight:800; color:#1e40af; letter-spacing:0.02em;">검토결과</div>'
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
                f'<div style="font-size:0.78rem; font-weight:800; color:#991b1b; letter-spacing:0.02em;">검토결과</div>'
                f'<div style="font-size:0.95rem; font-weight:800; color:#b91c1c; margin-top:4px;">'
                f'요구 전단마찰 철근량(Avf={res["Avf"]:.0f} mm²) 대비 보유 주근량(Ast={res["Ast"]:.0f} mm²)이 {res["add_area"]:.0f} mm² 부족합니다. '
                f'이어치기면에 D{main_bar} 철근 최소 {res["add_ea"]}EA를 추가 배근하거나 구조 담당에게 문의하세요.'
                f'</div></div>'
                f'<div class="dw-decision-pill-ng">+{res["add_ea"]}-D{main_bar} 보강 필요</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 하단 상세 검토 2열 카드 (좌: 단면 전단강도 및 배근 검토 / 우: 수직이어치기 전단마찰 및 무보강 위치 검토)
        rc1, rc2 = st.columns(2)
        with rc1:
            shear_ok = (res["Vu"] <= res["phiVn"] + 0.1) and res["stirrup_detail_ok"]
            spacing_li_body = (
                res["spacing_summary_txt"]
                if res["add_ea"] == 0
                else f'현재 {res["s_curr"]:.1f} mm<br/>→ {res["spacing_summary_txt"]}'
            )
            st.markdown(
                f'<div class="status-card">'
                f'<h4><span><span class="dw-accent-bar" style="height:15px; margin-right:8px; vertical-align:middle;"></span>단면 전단강도 및 배근 검토</span><span class="{"badge-ok" if shear_ok else "badge-warn"}">{"OK (적정)" if shear_ok else "간격/철근량 확인"}</span></h4>'
                f'<ul>'
                f'<li><b>콘크리트 / 스터럽 전단강도:</b> Vc = {res["Vc"]:.1f} kN | Vs = {res["Vs"]:.1f} kN (유효춤 d={res["d"]:.1f} mm)</li>'
                f'<li><b>단면 설계 전단강도 (ΦVn):</b> <b>{res["phiVn"]:.1f} kN</b> (ΦVc {phivc_val:.1f} + ΦVs {phivs_val:.1f} kN)</li>'
                f'<li><b>전단철근 단면적 (Asv):</b> {res["Asv"]:.1f} mm² vs 최소 요구 Av,min = {res["Av_min"]:.1f} mm² ({"만족" if res["Asv"] >= res["Av_min"]*0.98 else "미달"})</li>'
                f'<li><b>스터럽 간격 (s):</b> {stirrup_spacing:.0f} mm vs 최대허용간격 s_max = {res["s_max"]:.0f} mm ({"만족" if stirrup_spacing <= res["s_max"] else "간격 초과"})</li>'
                f'<li><b>주근 순간격 (인장측 1열 {res["n1_tension"]}EA):</b> {spacing_li_body}</li>'
                f'</ul></div>',
                unsafe_allow_html=True,
            )

        with rc2:
            sf_card_ok = res["sf_ok"] and res["sf_max_ok"]
            sf_badge_cls = "badge-ok" if sf_card_ok else "badge-ng"
            sf_badge_txt = "OK (안전)" if sf_card_ok else ("상한강도 초과" if not res["sf_max_ok"] else f"+{res['add_ea']}-D{main_bar} 보강")
            sf_max_txt = "만족 (OK)" if res["sf_max_ok"] else "초과 (NG — 단면 검토 필요)"
            x_safe_txt = (
                f"x_safe = 0 mm (전 구간 무보강 가능, 보유 내력 Vcap={res['Vu_cap']:.1f} kN ≥ ΦVn)"
                if res["x_safe"] <= 1e-6
                else f"단부로부터 x ≥ <b>{res['x_safe']:.0f} mm</b> ({res['x_safe']/1000:.2f} m, Ln={clear_span:.0f}mm 기준, Vcap={res['Vu_cap']:.1f} kN)"
            )
            add_req_li_txt = (
                f"추가 보강 불필요 (여유 {diff_area:+.0f} mm²)"
                if res["sf_ok"]
                else f"<b>+{res['add_ea']}-D{main_bar}</b> (부족 {res['add_area']:.0f} mm²)"
            )
            st.markdown(
                f'<div class="status-card">'
                f'<h4><span><span class="dw-accent-bar" style="height:15px; margin-right:8px; vertical-align:middle;"></span>수직이어치기 전단마찰 및 무보강 위치 검토</span><span class="{sf_badge_cls}">{sf_badge_txt}</span></h4>'
                f'<ul>'
                f'<li><b>적용 전단력 (Vu):</b> <b>{res["Vu"]:.1f} kN</b> (감소계수 {res["reduction_factor"]:.2f}) | <b>마찰계수 μ = {mu}</b></li>'
                f'<li><b>요구 vs 보유 철근량:</b> 요구 Avf = <b>{res["Avf"]:.0f} mm²</b> vs 보유 Ast = <b>{res["Ast"]:.0f} mm²</b> ({res["tension_bars"]}-D{main_bar}, D/C {res["dc_sf"]:.2f})</li>'
                f'<li><b>전단마찰 상한강도 검토 (Vu ≤ ΦVn,sf,max):</b> {res["Vu"]:.1f} kN ≤ {res["Vn_sf_max"]:.1f} kN (<b>{sf_max_txt}</b>)</li>'
                f'<li><b>무보강 가능 최소 거리 (x_safe):</b> {x_safe_txt}</li>'
                f'<li><b>추가 보강 소요량:</b> {add_req_li_txt}</li>'
                f'</ul></div>',
                unsafe_allow_html=True,
            )

        # 경간 위치(x)에 따른 필요 보강근 시뮬레이션 차트 (기본 닫힘 상태, 클릭 시 펼쳐보기)
        with st.expander("[최적화 시뮬레이션] 단부 이어치기 위치(x)별 전단력 및 필요 보강근 분석 (클릭하여 펼치기)", expanded=False):
            sim_rows = []
            half_L = max(clear_span / 2.0, 1000.0)
            x_safe = res["x_safe"]

            st.info(
                f"💡 **수직이어치기 위치 가이드:** 단부로부터 **$x \\ge {x_safe:.0f}\\text{{ mm}}$ ({x_safe/1000:.2f} m)** 이상 떨어진 지점에서 "
                f"수직이어치기 시공시 추가 보강근 없이 기존 주근({res['tension_bars']}-D{main_bar})만으로 전단마찰 안전성 확보가능"
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
                    t_zone = "하부 인장 (정모멘트 +M)" if (any(k in s_name.upper() for k in ("CENTER", "CEN", "MID")) or ("중앙" in s_name)) else "상부 인장 (부모멘트 -M)"
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
                        top_layers=s_info.get("top_layers"),
                        bot_layers=s_info.get("bot_layers"),
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
        cmp_sym = r"\ge" if res["sf_ok"] else "<"
        judge_md_str = "✅ 안전 (보강 불필요)" if res["sf_ok"] else f"🚨 보강 필요 (D{main_bar} 철근 {res['add_ea']}EA 추가 배근)"
        judge_html_str = "안전 (무보강 OK)" if res["sf_ok"] else f"보강 필요 (+{res['add_ea']}-D{main_bar})"
        sf_max_html_str = "OK" if res["sf_max_ok"] else "NG (상한 초과)"
        method_short = calc_method.split("(")[0].strip()
        pos_detail_md = (
            f"\n- **이어치기 위치 조건 (2차 본사 검토):** 순경간 $L_n = {clear_span:.0f}\\text{{ mm}}$, 단부 거리 $x = {joint_x:.0f}\\text{{ mm}}$ (`x/Ln = {joint_x/max(clear_span,1):.3f}`), 감소계수 $\\mathbf{{{res['reduction_factor']:.3f}}}$"
            if is_vj_pos_mode
            else ""
        )

        report_md = f"""
### RC 보 부재 수직이어치기 전단마찰 구조검토 계산서

- **검토 대상 부재:** `{st.session_state.selected_beam_label}` (도면: `{st.session_state.dxf_filename or '수동 입력'}`)
- **적용 설계기준:** KDS 14 20 22 (콘크리트구조 전단 및 비틀림 설계기준)
- **검토 일시:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

#### 1. 단면 및 재료 제원
| 구분 | 항목 | 적용값 | 비고 |
|:---:|:---|:---:|:---|
| **단면 치수** | 보 폭 ($b_w$) × 보 춤 ($H$) | **{bw:.0f} × {beam_depth:.0f} mm** | 유효춤 $d = {res['d']:.1f}\\text{{ mm}}$ (피복 {cover:.0f} mm) |
| **재료 강도** | 콘크리트 ($f_{{ck}}$) / 주근 ($f_y$) / 스터럽 ($f_{{yt}}$) | **{fck} / {fy} / {stirrup_fy} MPa** | 전단강도 감소계수 $\\phi = 0.75$ |
| **주근 배근** | 상부근 (TOP) / 하부근 (BOT) | **{top_bars}-D{main_bar} / {bot_bars}-D{main_bar}** | 단면적 1본당 $A_b = {res['As_unit']:.2f}\\text{{ mm}}^2$ |
| **전단철근** | 스터럽 배근 (Stirrup) | **{stirrup_legs}-D{stirrup_bar} @ {stirrup_spacing:.0f}** | $A_{{sv}} = {res['Asv']:.2f}\\text{{ mm}}^2$ |

---

#### 2. 전단강도 검토 (KDS 14 20 22)
- **콘크리트 전단강도 ($V_c$):** $\\frac{{1}}{{6}}\\sqrt{{f_{{ck}}}} b_w d = \\frac{{1}}{{6}}\\sqrt{{{fck}}} \\times {bw:.0f} \\times {res['d']:.1f} \\div 1000 = \\mathbf{{{res['Vc']:.1f}\\text{{ kN}}}}$
- **전단철근 전단강도 ($V_s$):** $\\frac{{A_{{sv}} f_{{yt}} d}}{{s}} = \\frac{{{res['Asv']:.1f} \\times {stirrup_fy} \\times {res['d']:.1f}}}{{{stirrup_spacing:.0f}}} \\div 1000 = \\mathbf{{{res['Vs']:.1f}\\text{{ kN}}}}$
- **설계 전단강도 ($\\phi V_n$):** $0.75 \\times ({res['Vc']:.1f} + {min(res['Vs'], res['Vs_max']):.1f}) = \\mathbf{{{res['phiVn']:.1f}\\text{{ kN}}}}$
- **스터럽 상세 검토:** $A_{{sv}} = {res['Asv']:.1f}\\text{{ mm}}^2$ vs $A_{{v,\\min}} = {res['Av_min']:.1f}\\text{{ mm}}^2$, 간격 $s = {stirrup_spacing:.0f}\\text{{ mm}}$ vs $s_{{\\max}} = {res['s_max']:.0f}\\text{{ mm}}$

---

#### 3. 수직이어치기면 전단마찰 상세 검토 (KDS 14 20 22 - 4.5)
- **작용 계수전단력 ($V_u$):** $\\mathbf{{{res['Vu']:.1f}\\text{{ kN}}}}$ *(산정 기준: {method_short}, 감소계수 {res['reduction_factor']:.2f})*{pos_detail_md}
- **이어치기면 마찰계수 ($\\mu$):** $\\mathbf{{{mu}}}$ *({surface_cond})*
- **전단마찰 상한강도 검토:** $V_u ({res['Vu']:.1f}\\text{{ kN}}) \\le \\phi V_{{n,\\text{{sf,max}}}} ({res['Vn_sf_max']:.1f}\\text{{ kN}})$ → **{sf_max_html_str}**
- **요구 전단마찰 철근량 ($A_{{vf}}$):**
  $$A_{{vf}} = \\frac{{V_u}}{{\\phi f_y \\mu}} \\times 1000 = \\frac{{{res['Vu']:.1f}}}{{0.75 \\times {fy} \\times {mu}}} \\times 1000 = \\mathbf{{{res['Avf']:.1f}\\text{{ mm}}^2}}$$
- **보유 인장철근량 ($A_{{st}}$):** {res['tension_bars']} EA × {res['As_unit']:.2f} mm² = $\\mathbf{{{res['Ast']:.1f}\\text{{ mm}}^2}}$ *(전단마찰 내력 $V_{{\\text{{cap}}}} = {res['Vu_cap']:.1f}\\text{{ kN}}$, 무보강 최소 거리 $x_{{\\text{{safe}}}} = {res['x_safe']:.0f}\\text{{ mm}}$)*
- **검토 결과:** $A_{{st}} ({res['Ast']:.1f}\\text{{ mm}}^2) {cmp_sym} A_{{vf}} ({res['Avf']:.1f}\\text{{ mm}}^2)$ → **{judge_md_str}**
"""
        st.markdown(report_md)

        elev_html_block = (
            f'<h3>보 종단면(입면도) 및 전단력 분포도(SFD) — 2차 본사 검토</h3>'
            f'<div style="text-align:center; margin: 16px 0;">{elev_svg_html}</div>'
            if (is_vj_pos_mode and elev_svg_html)
            else ""
        )

        html_report = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>구조검토보고서 - {st.session_state.selected_beam_label}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>
body {{ font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', sans-serif; max-width: 920px; margin: 30px auto; color: #1e293b; line-height: 1.6; }}
h1 {{ border-bottom: 3px solid #1e3a8a; padding-bottom: 10px; color: #0f172a; }}
table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: 10px 12px; text-align: left; }}
th {{ background: #f1f5f9; font-weight: bold; }}
.box {{ background: #f8fafc; border-left: 5px solid #2563eb; padding: 14px 18px; margin: 16px 0; }}
</style>
</head>
<body>
<h1>RC 보 부재 수직이어치기 구조검토 계산근거</h1>
<p><b>검토 부재:</b> {st.session_state.selected_beam_label} | <b>검토 방식:</b> {method_short} | <b>검토 일자:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<div style="text-align:center; margin: 20px 0;">{svg_html}</div>
{elev_html_block}
<table>
<tr><th>항목</th><th>산정식 및 기준</th><th>결과값</th><th>판정</th></tr>
<tr><td>보 단면 / 유효춤</td><td>bw × H (d)</td><td>{bw:.0f} × {beam_depth:.0f} mm (d={res['d']:.1f} mm)</td><td>-</td></tr>
<tr><td>설계 전단강도 (ΦVn)</td><td>0.75 × (Vc={res['Vc']:.1f} + Vs={min(res['Vs'], res['Vs_max']):.1f})</td><td>{res['phiVn']:.1f} kN</td><td>{"OK" if res["stirrup_detail_ok"] else "배근 확인"}</td></tr>
<tr><td>적용 전단력 (Vu)</td><td>{method_short} (감소계수 {res['reduction_factor']:.2f})</td><td>{res['Vu']:.1f} kN</td><td>{"OK" if res["Vu"] <= res["phiVn"] + 0.1 else "초과"}</td></tr>
<tr><td>전단마찰 상한강도</td><td>Vu ≤ ΦVn,sf,max ({res['Vn_sf_max']:.1f} kN)</td><td>{res['Vu']:.1f} / {res['Vn_sf_max']:.1f} kN</td><td>{sf_max_html_str}</td></tr>
<tr><td>전단마찰 검토 (Avf vs Ast)</td><td>Vu={res['Vu']:.1f} kN, μ={mu}, x_safe={res['x_safe']:.0f}mm</td><td>요구 {res['Avf']:.1f} mm² / 보유 {res['Ast']:.1f} mm²</td><td><b>{judge_html_str}</b></td></tr>
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
    tab_h_detail, tab_h_schedule, tab_h_report = st.tabs([
        "부재별 검토",
        "전체 보 일괄 구조검토표",
        "구조검토 근거",
    ])

    hj_can_render = True
    is_hj_precision_selected = False
    hj_p_perm = 0.0

    with tab_h_detail:
        # STEP 1 (단면 제원) & STEP 2 (검토 모드/조건) — 수직 이어치기와 동일한 좌(1.25):우(1) 구성
        hj_col_in, hj_col_vis = st.columns([1.25, 1])

        with hj_col_in:
            st.markdown(
                f'<div class="dw-section-card" style="margin-bottom:0.65rem;">'
                f'<div class="dw-section-header">'
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span><span class="dw-step-badge">STEP 1</span>단면 및 배근 제원 입력</div>'
                f'<span class="dw-pill-blue">현재 부재: {st.session_state.selected_beam_label}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            hic1, hic2, hic3 = st.columns(3)
            with hic1:
                hj_bw = st.number_input("보 폭 bw (mm)", min_value=150.0, max_value=5000.0, step=10.0, key="hj_bw", on_change=_sync_hj_to_vj, args=("bw",))
                hj_H = st.number_input("보 춤 H (mm)", min_value=200.0, max_value=5000.0, step=10.0, key="hj_beam_depth", on_change=_sync_hj_to_vj, args=("beam_depth",))
                hj_tension_zone = st.selectbox("인장부 위치 (검토 기준)", ["상부 인장 (부모멘트 -M)", "하부 인장 (정모멘트 +M)"], key="hj_tension_zone", on_change=_sync_hj_to_vj, args=("tension_zone",))
            with hic2:
                hj_main_dia = st.selectbox("주근 직경 (mm)", BAR_LIST, key="hj_main_bar", on_change=_sync_hj_to_vj, args=("main_bar",))
                hj_top_bars = st.number_input("상부 주근수 (TOP)", min_value=1, max_value=120, step=1, key="hj_top_bars", on_change=_sync_hj_to_vj, args=("top_bars",))
                hj_bot_bars = st.number_input("하부 주근수 (BOT)", min_value=1, max_value=120, step=1, key="hj_bot_bars", on_change=_sync_hj_to_vj, args=("bot_bars",))
            with hic3:
                hj_st_dia = st.selectbox("스터럽 직경 (mm)", [10, 13, 16, 19], key="hj_st_dia", on_change=_sync_hj_to_vj, args=("st_dia",))
                hj_st_legs = st.number_input("스터럽 가닥수 (Legs)", min_value=1, max_value=24, step=1, key="hj_st_legs", on_change=_sync_hj_to_vj, args=("st_legs",))
                hj_st_spacing = st.number_input("스터럽 간격 s (mm)", min_value=50.0, max_value=1000.0, step=10.0, key="hj_st_spacing", on_change=_sync_hj_to_vj, args=("st_spacing",))

            hj_mode_options = [
                "일반 검토 모드 (표준 보수적 검토 — 전단 흐름 최대치 기준)",
                "정밀 검토 모드 (타설 높이별 전단 흐름 Q/I 정밀 검토 — 관리자 전용)",
            ]
            cur_hj_mode_preview = st.session_state.get("hj_mode_radio", hj_mode_options[0])
            is_hj_prec_pill = ("정밀 검토 모드" in cur_hj_mode_preview)
            st.markdown(
                f'<div class="dw-section-card" style="margin-top:0.75rem; margin-bottom:0.5rem;">'
                f'<div class="dw-section-header">'
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span><span class="dw-step-badge">STEP 2</span>수평 이어치기 검토 모드 및 조건</div>'
                f'<span class="dw-pill-blue">{"정밀 모드 (Q/I)" if is_hj_prec_pill else "일반 모드 (표준)"}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            hj_selected_mode = st.radio(
                "수평 이어치기 검토 모드 선택",
                hj_mode_options,
                index=0,
                key="hj_mode_radio",
            )
            is_hj_precision_selected = ("정밀 검토 모드" in hj_selected_mode)
            hj_can_render = (not is_hj_precision_selected) or bool(st.session_state.get("precision_unlocked", False))

            if float(fy) > 500.0 or float(stirrup_fy) > 500.0:
                st.warning(
                    "⚠️ **KDS 14 20 강도 상한 적용:** 수평 이어치기 검토에서 전단철근 및 전단마찰 보강근 설계강도 최대 **500 MPa**로 제한적용"
                )

            hj_p_perm = 0.0
            hj_h_joint = hj_H * 0.5
            hj_use_actual_vu = False
            hj_actual_vu_val = 0.0
            hj_moment_mode = None

            if is_hj_precision_selected and not hj_can_render:
                st.markdown(
                    '<div style="background:#ffffff; border:1px solid #bfdbfe; border-left:5px solid #137fec; '
                    'border-radius:12px; padding:1.0rem 1.25rem; margin:0.6rem 0 0.75rem 0; box-shadow:0 4px 14px rgba(19,127,236,0.08);">'
                    '<div style="font-size:0.95rem; font-weight:800; color:#1e3a8a; margin-bottom:0.25rem;">🔒 관리자 전용 정밀 검토 모드 잠금</div>'
                    '<div style="font-size:0.84rem; color:#475569; line-height:1.5;">'
                    '타설 높이(<b>h_joint</b>)별 균열단면 압축대(<b>c</b>) 전단흐름 저감(<b>αq</b>) 및 영구 압축력 반영 검토는 '
                    '관리자 코드 인증 후 활성화됩니다.'
                    '</div></div>',
                    unsafe_allow_html=True,
                )
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

            elif is_hj_precision_selected and hj_can_render:
                ul_c1, ul_c2 = st.columns([3.5, 1.3])
                with ul_c1:
                    st.success("🔓 **정밀 검토 모드 활성화됨** — 타설 높이(h_joint)별 전단흐름(Q/I) 저감이 적용됩니다.")
                with ul_c2:
                    if st.button("🔒 잠금", key="hj_relock_btn", use_container_width=True):
                        st.session_state["precision_unlocked"] = False
                        st.rerun()

                hj_mm_options = [
                    "부모멘트 -M (상부 인장 / 하부 압축 — 보 단부 기준)",
                    "정모멘트 +M (하부 인장 / 상부 압축 — 보 중앙부 기준)",
                    "양방향 포락 (+M / -M 모멘트 반전 고려 — 보수적)",
                ]
                default_mm = hj_mm_options[0] if "상부" in hj_tension_zone else hj_mm_options[1]
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

                # 정밀 검토 모드 전용: 영구 압축력 P (kN/m)
                hj_p_perm = st.number_input(
                    "영구 압축력 P (kN/m) — 이어치기면에 수직으로 작용하는 영구 순압축력",
                    min_value=0.0, max_value=5000.0, value=0.0, step=10.0,
                    key="hj_p_perm_input",
                    help="보 상부 벽체 자중 등으로 이어치기면에 영구 압축력이 작용하는 경우 입력합니다. (기본값 0.0 kN/m)",
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

        if hj_can_render:
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
                    f'<div class="dw-section-title"><span class="dw-accent-bar"></span>수평 이어치기 단면도 & 전단흐름 분포</div>'
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
                f'<div class="dw-section-title"><span class="dw-accent-bar"></span><span class="dw-step-badge">STEP 3</span>수평 이어치기 구조검토 결과요약</div>'
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
                    f'<div class="dw-kpi-label">공칭전단강도 (Vn)</div>'
                    f'<div class="dw-kpi-val">{hj_res["Vn_eff_kN"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN</span></div>'
                    f'</div><div class="dw-kpi-foot" style="color:#137fec;"><span>Vc {hj_res["Vc_kN"]:.1f} + Vs {hj_res["Vs_kN"]:.1f} kN</span></div></div>',
                    unsafe_allow_html=True,
                )
            with hk2:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top">'
                    f'<div class="dw-kpi-label">1m당 작용 수평전단력 (Vnh,1m)</div>'
                    f'<div class="dw-kpi-val">{hj_res["Vnh_1m_kN"]:.1f} <span style="font-size:1rem; font-weight:700; color:#64748b;">kN/m</span></div>'
                    f'</div><div class="dw-kpi-foot" style="color:#137fec;"><span>전단흐름 저감계수 αq = {hj_res["alpha_q"]:.3f}</span></div></div>',
                    unsafe_allow_html=True,
                )
            with hk3:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top">'
                    f'<div class="dw-kpi-label">기존 스터럽 보유 vs 총 필요량</div>'
                    f'<div class="dw-kpi-val">{hj_res["Asv_1m"]:.0f} <span style="font-size:1.05rem; font-weight:700; color:#94a3b8;">/ {hj_res["Avf_total"]:.0f} mm²/m</span></div>'
                    f'</div><div class="dw-kpi-foot" style="color:{hj_status_col};"><span>영구압축 감소 Avf,P = {hj_res["Avf_P"]:.0f} mm²/m</span></div></div>',
                    unsafe_allow_html=True,
                )
            with hk4:
                st.markdown(
                    f'<div class="dw-kpi-card"><div class="dw-kpi-top">'
                    f'<div class="dw-kpi-label">추가 보강근 소요량 (Avf,req)</div>'
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
                    f'<div style="font-size:0.78rem; font-weight:800; color:#1e40af; letter-spacing:0.02em;">검토결과</div>'
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
                    f'<div style="font-size:0.78rem; font-weight:800; color:#991b1b; letter-spacing:0.02em;">검토결과</div>'
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
                    '<div class="dw-section-title"><span class="dw-accent-bar"></span>수평 이어치기 현장 조치 가이드</div>'
                    '</div></div>',
                    unsafe_allow_html=True,
                )
                st_warn = (
                    '<br/><span style="color:#b45309; font-size:0.82rem; font-weight:600;">'
                    '※ 50mm 미만 과밀 배근 우려 → 스터럽 가닥수 증대 또는 추가 다우얼바 보강 권장</span>'
                    if hj_res["s_req_practical"] < 50
                    else ""
                )
                cur_anch_dia = int(st.session_state.get("hj_anch_bar_dia", 13))
                dowel_trs = ""
                for opt in hj_res["dowel_options"]:
                    is_sel_row = (opt["보강근 규격"] == f"D{cur_anch_dia}")
                    row_bg = "background:#eff6ff;" if is_sel_row else ""
                    spec_col = "color:#1d4ed8; font-weight:800;" if is_sel_row else "color:#1e293b; font-weight:700;"
                    dowel_trs += (
                        f'<tr style="{row_bg} border-bottom:1px solid #f1f5f9;">'
                        f'<td style="padding:7px 10px; {spec_col}">{opt["보강근 규격"]}</td>'
                        f'<td style="padding:7px 10px; text-align:right; color:#475569;">{opt["단면적 (mm²/본)"]:.2f}</td>'
                        f'<td style="padding:7px 10px; text-align:center; font-weight:700; color:#1e293b;">{opt["1m당 최소 본수 (EA/m)"]}</td>'
                        f'<td style="padding:7px 10px; text-align:center; color:#334155;">{opt["1열(1가닥) 배근 간격"]}</td>'
                        f'<td style="padding:7px 10px; text-align:center; color:#334155;">{opt["2열(양측 2가닥) 배근 간격"]}</td>'
                        f'<td style="padding:7px 10px; text-align:right; font-weight:700; color:#0f172a;">{opt["확보 보강 단면적 (mm²/m)"]:.1f}</td>'
                        f'</tr>'
                    )
                st.markdown(
                    f'<div style="display:grid; grid-template-columns:1fr 1.85fr; gap:1rem; align-items:stretch; margin-bottom:0.5rem;">'
                    f'<div class="status-card" style="height:100%; display:flex; flex-direction:column; margin-bottom:0;">'
                    f'<h4><span><span class="dw-accent-bar" style="height:15px; margin-right:8px; vertical-align:middle;"></span>스터럽 간격 축소안</span>'
                    f'<span class="badge-warn">s ≤ {hj_res["s_req_practical"]} mm</span></h4>'
                    f'<ul style="flex:1;">'
                    f'<li><b>현재 스터럽:</b> {hj_st_legs}-D{hj_st_dia} @ {hj_st_spacing:.0f} mm (보유 {hj_res["Asv_1m"]:.0f} mm²/m)</li>'
                    f'<li><b>이론 필요 간격 (s_req):</b> <b>{hj_res["s_req"]:.1f} mm</b></li>'
                    f'<li><b>시공 권장 간격:</b> <b>{hj_st_legs}-D{hj_st_dia} @ {hj_res["s_req_practical"]} mm 이하</b>{st_warn}</li>'
                    f'<li><b>추가 소요 철근량 (Avf,req):</b> <b>{hj_res["Avf_req"]:.0f} mm²/m</b></li>'
                    f'</ul></div>'
                    f'<div class="status-card" style="height:100%; display:flex; flex-direction:column; margin-bottom:0;">'
                    f'<h4><span><span class="dw-accent-bar" style="height:15px; margin-right:8px; vertical-align:middle;"></span>추가 다우얼바 1m당 배근 본수 및 간격표</span></h4>'
                    f'<div style="overflow-x:auto; flex:1;">'
                    f'<table style="width:100%; border-collapse:collapse; font-size:0.84rem; margin-top:4px;">'
                    f'<thead>'
                    f'<tr style="background:#f8fafc; border-top:1px solid #e2e8f0; border-bottom:1.5px solid #e2e8f0; color:#475569; font-size:0.78rem;">'
                    f'<th style="padding:7px 10px; text-align:left; font-weight:700;">규격</th>'
                    f'<th style="padding:7px 10px; text-align:right; font-weight:700;">단면적<br/>(mm²/본)</th>'
                    f'<th style="padding:7px 10px; text-align:center; font-weight:700;">최소 본수<br/>(EA/m)</th>'
                    f'<th style="padding:7px 10px; text-align:center; font-weight:700;">1열(1가닥)<br/>배근 간격</th>'
                    f'<th style="padding:7px 10px; text-align:center; font-weight:700;">2열(양측 2가닥)<br/>배근 간격</th>'
                    f'<th style="padding:7px 10px; text-align:right; font-weight:700;">확보 단면적<br/>(mm²/m)</th>'
                    f'</tr>'
                    f'</thead>'
                    f'<tbody>{dowel_trs}</tbody>'
                    f'</table></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

            # 5.5 전단마찰보강근 정착길이 산정, 감소계수(피복 0.7·초과철근) 및 상·하부 개별 정착 검토 (KDS 14 20 52)
            st.markdown(
                '<div class="dw-section-card" style="margin-top:0.9rem; margin-bottom:0.65rem;">'
                '<div class="dw-section-header">'
                '<div class="dw-section-title"><span class="dw-accent-bar"></span><span class="dw-step-badge">STEP 4</span>전단마찰보강근 정착길이 및 상·하부 정착 제한 검토</div>'
                '</div></div>',
                unsafe_allow_html=True,
            )

            hj_need_dowel = (hj_res["Avf_req"] > 1e-6)
            if hj_need_dowel:
                ac_sel1, ac_sel2, ac_sel3, ac_sel4 = st.columns([1.15, 1.15, 1.15, 1.15])
            else:
                ac_sel1, ac_sel3, ac_sel4 = st.columns([1.2, 1.4, 1.4])
                ac_sel2 = None

            with ac_sel1:
                hj_anch_dia = st.selectbox(
                    "전단마찰보강근 규격",
                    [10, 13, 16, 19, 22, 25],
                    index=1,
                    format_func=lambda x: f"D{x} (db={REBAR_DB[x]:.2f} mm)",
                    key="hj_anch_bar_dia",
                    help="D19 이하 일자정착 계수 0.72 / D22 이상 계수 0.90 적용 (KDS 14 20 52 표 4.1-1 '기타의 경우')",
                )

            ab_anch = REBAR_AREA[hj_anch_dia]
            min_ea_req = max(int(math.ceil(hj_res["Avf_req"] / ab_anch)), 1) if hj_need_dowel else 1

            if hj_need_dowel and ac_sel2 is not None:
                anch_sync_sig = (int(hj_anch_dia), round(float(hj_res["Avf_req"]), 1))
                if (
                    "hj_anch_n_prov" not in st.session_state
                    or st.session_state.get("hj_anch_last_sig") != anch_sync_sig
                ):
                    st.session_state["hj_anch_n_prov"] = min_ea_req
                    st.session_state["hj_anch_last_sig"] = anch_sync_sig
                elif int(st.session_state["hj_anch_n_prov"]) < min_ea_req:
                    st.session_state["hj_anch_n_prov"] = min_ea_req

                with ac_sel2:
                    hj_anch_n_prov_input = st.number_input(
                        f"시공 배근 본수 (EA/m · 최소 {min_ea_req})",
                        min_value=min_ea_req,
                        max_value=200,
                        step=1,
                        key="hj_anch_n_prov",
                        help="다우얼바 1m당 시공 본수를 늘리면 초과철근 저감계수(Avf,req / Avf,prov)에 따라 정착길이 감소 효과를 실시간으로 확인할 수 있습니다.",
                    )

            with ac_sel3:
                st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                hj_anch_use_07 = st.checkbox(
                    "90° 갈고리 피복 보정계수 0.7 적용 (D35 이하)",
                    value=True,
                    key="hj_anch_use_07",
                    help="측면 피복 ≥65mm 및 단부 피복 ≥50mm 확보 조건 시 0.7 저감 적용 (가용 깊이 h - max(c, 50))",
                )
            with ac_sel4:
                st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                hj_anch_use_excess = st.checkbox(
                    "초과철근 저감계수 (Avf,req / Avf,prov) 적용",
                    value=True,
                    key="hj_anch_use_excess",
                    help="KDS 14 20 52 4.1.2(5), 4.1.5(3)③ 초과철근 저감 적용 (지진하중 등 fy 완전 발휘 필수 구간 제외)",
                )

            # 전단마찰 검토 결과와 연동된 소요/보유 배근량·간격·가닥수 산정
            if hj_need_dowel:
                anch_Avf_req = hj_res["Avf_req"]
                anch_n_prov = max(int(hj_anch_n_prov_input), min_ea_req)
                anch_Avf_prov = anch_n_prov * ab_anch
                anch_s_prov = round(1000.0 / anch_n_prov, 1)
                anch_s_2leg = round(2000.0 / anch_n_prov, 1)
                anch_basis_lbl = f"추가 다웰근 D{hj_anch_dia} 기준 (소요 {anch_Avf_req:.0f} / 시공 {anch_Avf_prov:.0f} mm²/m, {anch_n_prov}EA/m · @{anch_s_prov:.0f})"
            else:
                anch_Avf_req = max(0.0, hj_res["Avf_total"] - hj_res["Avf_P"])
                anch_Avf_prov = max(hj_res["Asv_1m"], 1.0)
                anch_s_prov = float(hj_st_spacing)
                anch_n_prov = max(int(round(hj_st_legs * (1000.0 / max(hj_st_spacing, 1.0)))), 1)
                anch_basis_lbl = f"기존 스터럽 기준 (소요 {anch_Avf_req:.0f} / 보유 {anch_Avf_prov:.0f} mm²/m, @{anch_s_prov:.0f})"

            anch_res = evaluate_horizontal_joint_anchorage(
                bar_dia=hj_anch_dia,
                fck=fck,
                fy=fy,
                H=hj_H,
                h_joint=hj_res["h_joint"],
                cover=cover,
                use_cover_07=hj_anch_use_07,
                use_excess_reduction=hj_anch_use_excess,
                Avf_req=anch_Avf_req,
                Avf_prov=anch_Avf_prov,
                s_prov=anch_s_prov,
                n_prov=anch_n_prov,
            )

            if hj_need_dowel:
                extra_ea_cnt = anch_n_prov - min_ea_req
                prov_ratio_pct = (anch_Avf_prov / max(anch_Avf_req, 1e-6)) * 100.0
                if extra_ea_cnt > 0 and hj_anch_use_excess:
                    extra_eff_txt = (
                        f" · ✅ **초과배근 +{extra_ea_cnt}EA/m 반영** "
                        f"(ψ_excess = **{anch_res['excess_factor']:.3f}**, 일자 ld `{anch_res['ld_base']:.0f} → {anch_res['ld']:.0f} mm`)"
                    )
                elif extra_ea_cnt > 0 and not hj_anch_use_excess:
                    extra_eff_txt = " · 💡 우측 **'초과철근 저감계수 적용'** 체크 시 정착길이 감소 효과가 반영됩니다."
                else:
                    extra_eff_txt = f" · 최소 본수 기준 (ψ_excess = {anch_res['excess_factor']:.3f})"
                st.caption(
                    f"📐 **시공 배근량 (D{hj_anch_dia}):** 소요 **{anch_Avf_req:.0f}** vs 시공 **{anch_Avf_prov:.0f} mm²/m** "
                    f"({anch_n_prov}EA/m, 소요 대비 {prov_ratio_pct:.0f}% · 1열 @{anch_s_prov:.0f}mm / 2열 @{anch_s_2leg:.0f}mm){extra_eff_txt}"
                )

            sqrt_cap_badge = (
                f" | ⚠️ **sqrt(fck) 상한 8.4 MPa 적용** (원래 √{fck:.0f}={anch_res['sqrt_fck_raw']:.2f}, KDS 14 20 52 4.1.1(3))"
                if anch_res["sqrt_fck_capped"]
                else f" | √fck = {anch_res['sqrt_fck']:.2f} MPa (상한 8.4 이하)"
            )
            excess_badge = (
                f" | 초과철근 저감 ψ_excess = **{anch_res['excess_factor']:.3f}**"
                if anch_res["excess_applied"]
                else " | 초과철근 저감 미적용 (1.000)"
            )

            if anch_res["sqrt_fck_capped"]:
                st.warning(
                    f"⚠️ **KDS 14 20 52 4.1.1(3) sqrt(fck) 상한 8.4 MPa 적용:** 입력된 콘크리트 강도 `fck = {fck} MPa` (> 70.56 MPa)에 대해 "
                    f"정착길이(ld, ldh) 산정 시 √fck 값을 최대 **8.4 MPa**로 제한하여 보수적으로 계산했습니다."
                )

            # 배근 방식별 요구 정착길이 & 피복두께 포함 제한 높이 요약 (3열 동일 고정 높이 정렬)
            ak1, ak2, ak3 = st.columns(3)
            with ak1:
                ld_min_note = " (최소 300mm 하한)" if anch_res["ld_min_applied"] else f" (계수 {anch_res['ld_coeff']:.2f}, α=1.0)"
                st.markdown(
                    f'<div class="dw-kpi-card" style="min-height:132px; height:132px;"><div class="dw-kpi-top">'
                    f'<div class="dw-kpi-label">일자(직선) 인장정착길이 (ld)</div>'
                    f'<div class="dw-kpi-val">{anch_res["ld"]:.0f} <span style="font-size:0.95rem; font-weight:700; color:#64748b;">mm</span></div>'
                    f'</div><div class="dw-kpi-foot" style="color:#137fec;">'
                    f'<span>필요높이 ld+c = <b>{anch_res["req_h_straight"]:.0f} mm</b>{ld_min_note}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
            with ak2:
                cov_07_lbl = f"0.7 적용, 피복 max(c,50)={anch_res['ldh_cover_eff']:.0f}mm" if anch_res["use_cover_07"] else f"0.7 미적용, 피복 c={anch_res['ldh_cover_eff']:.0f}mm"
                st.markdown(
                    f'<div class="dw-kpi-card" style="min-height:132px; height:132px;"><div class="dw-kpi-top">'
                    f'<div class="dw-kpi-label">90° 표준갈고리 정착길이 (ldh)</div>'
                    f'<div class="dw-kpi-val">{anch_res["ldh"]:.0f} <span style="font-size:0.95rem; font-weight:700; color:#64748b;">mm</span></div>'
                    f'</div><div class="dw-kpi-foot" style="color:#0284c7;">'
                    f'<span>필요높이 ldh+{anch_res["ldh_cover_eff"]:.0f} = <b>{anch_res["req_h_hook"]:.0f} mm</b> ({cov_07_lbl})</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
            with ak3:
                st.markdown(
                    f'<div class="dw-kpi-card" style="min-height:132px; height:132px;"><div class="dw-kpi-top">'
                    f'<div class="dw-kpi-label">90° 표준갈고리 상세 & 감소계수</div>'
                    f'<div class="dw-kpi-val" style="font-size:0.95rem; line-height:1.38;">'
                    f'90° 끝단 연장: ≥ {anch_res["hook_90_ext"]:.0f} mm <span style="font-size:0.78rem; color:#64748b;">(12db)</span><br/>'
                    f'초과저감 ψ_excess = {anch_res["excess_factor"]:.3f} <span style="font-size:0.78rem; color:#64748b;">(피복 {anch_res["cover_07_factor"]:.1f})</span>'
                    f'</div></div><div class="dw-kpi-foot" style="color:#475569;">'
                    f'<span>하한: 일자 ≥300mm / 90° ≥max(8db,150)={anch_res["ldh_min"]:.0f}mm</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

            # 현장 시공 주의 문구 (90° 갈고리 0.7 저감 조건 & 초과철근 저감 주의)
            st.caption(
                f"※ **90° 갈고리 0.7 저감 적용 조건:** 측면 피복 65mm 이상(스터럽에서 안쪽 이격) 및 단부 피복 50mm 이상 확보, "
                f"90° 구부림 끝단(12 db = {anch_res['hook_90_ext']:.0f}mm)은 보 길이 방향(종방향)으로 배근"
            )
            if anch_res["use_excess_reduction"]:
                st.caption(
                    "※ **초과철근 저감 주의:** 지진하중 저항 등 철근 항복강도(fy)의 완전 발휘가 필수인 구간에는 초과철근 저감 적용 불가"
                )

            # 상부 구간 / 하부 구간 개별 정착 판별 2열 카드 (CSS Grid 동일 높이 + 하단 종합 판정 박스 정렬)
            anch_zone_cards = []
            for z_data, z_title in [
                (anch_res["top"], f"상부 타설 구간 (h_상 = {anch_res['h_top']:.0f} mm)"),
                (anch_res["bot"], f"하부 타설 구간 (h_하 = {anch_res['h_bot']:.0f} mm)"),
            ]:
                st_m = z_data["straight"]
                hk_m = z_data["hook90"]
                st_margin_txt = f"OK (여유 +{st_m['margin']:.1f} mm)" if st_m["ok"] else f"NG (부족 {st_m['margin']:.1f} mm)"
                hk_margin_txt = f"OK (여유 +{hk_m['margin']:.1f} mm)" if hk_m["ok"] else f"NG (부족 {hk_m['margin']:.1f} mm)"
                st_excess_li = f"<br/><span style='color:#475569; font-size:0.83rem;'>↳ 초과배근 검토: {st_m['excess_msg']}</span>" if not st_m["ok"] else ""
                hk_excess_li = f"<br/><span style='color:#475569; font-size:0.83rem;'>↳ 초과배근 검토: {hk_m['excess_msg']}</span>" if not hk_m["ok"] else ""
                hk_cov_formula = f"h - max(c,50) = {z_data['h_zone']:.0f} - {hk_m['c_eff']:.0f}" if anch_res["use_cover_07"] else f"h - c = {z_data['h_zone']:.0f} - {hk_m['c_eff']:.0f}"
                if z_data["badge_cls"] == "badge-ok":
                    concl_bg, concl_bd, concl_fg = "#eff6ff", "#137fec", "#1e3a8a"
                elif z_data["badge_cls"] == "badge-warn":
                    concl_bg, concl_bd, concl_fg = "#f0f9ff", "#0284c7", "#0c4a6e"
                else:
                    concl_bg, concl_bd, concl_fg = "#fef2f2", "#dc2626", "#991b1b"
                anch_zone_cards.append(
                    f'<div class="status-card" style="height:100%; display:flex; flex-direction:column; margin-bottom:0;">'
                    f'<h4><span><span class="dw-accent-bar" style="height:15px; margin-right:8px; vertical-align:middle;"></span>{z_title}</span>'
                    f'<span class="{z_data["badge_cls"]}">{z_data["status_label"]}</span></h4>'
                    f'<ul style="flex:1; margin-bottom:0.65rem;">'
                    f'<li><b>일자(직선) 배근 (ld={anch_res["ld"]:.0f} mm):</b> '
                    f'가용 h-c = <b>{st_m["h_avail"]:.1f} mm</b> / 필요높이 <b>{st_m["req_h"]:.0f} mm</b> → <b>{st_margin_txt}</b>{st_excess_li}</li>'
                    f'<li><b>90° 표준갈고리 (ldh={anch_res["ldh"]:.0f} mm):</b> '
                    f'가용 {hk_cov_formula} = <b>{hk_m["h_avail"]:.1f} mm</b> / 필요높이 <b>{hk_m["req_h"]:.0f} mm</b> → <b>{hk_margin_txt}</b>{hk_excess_li}</li>'
                    f'</ul>'
                    f'<div style="background:{concl_bg}; border-left:4px solid {concl_bd}; border-radius:8px; '
                    f'padding:0.65rem 0.85rem; margin-top:auto; color:{concl_fg}; font-size:0.86rem; line-height:1.5; font-weight:700;">'
                    f'종합 판정 및 조치: {z_data["guidance"]}'
                    f'</div></div>'
                )
            st.markdown(
                f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; align-items:stretch; margin-bottom:0.75rem;">'
                f'{"".join(anch_zone_cards)}</div>',
                unsafe_allow_html=True,
            )

            # 규격별(D10~D25) 상·하부 정착 판정 일괄 비교표
            anch_cmp_rows = []
            for cmp_d in [10, 13, 16, 19, 22, 25]:
                ab_c = REBAR_AREA[cmp_d]
                if hj_res["Avf_req"] > 1e-6:
                    n_c = max(int(math.ceil(hj_res["Avf_req"] / ab_c)), 1)
                    avf_p_c = n_c * ab_c
                    s_c = round(1000.0 / n_c, 1)
                else:
                    n_c = anch_n_prov
                    avf_p_c = anch_Avf_prov
                    s_c = anch_s_prov
                r_c = evaluate_horizontal_joint_anchorage(
                    cmp_d, fck, fy, hj_H, hj_res["h_joint"], cover,
                    use_cover_07=hj_anch_use_07,
                    use_excess_reduction=hj_anch_use_excess,
                    Avf_req=anch_Avf_req, Avf_prov=avf_p_c, s_prov=s_c, n_prov=n_c,
                )
                anch_cmp_rows.append({
                    "규격": f"D{cmp_d}",
                    "일자 계수": f"{r_c['ld_coeff']:.2f}",
                    "일자 ld / 필요높이": f"{r_c['ld']:.0f} / {r_c['req_h_straight']:.0f} mm",
                    "90° ldh / 필요높이": f"{r_c['ldh']:.0f} / {r_c['req_h_hook']:.0f} mm",
                    "상부 일자 / 90°": f"{r_c['top']['straight']['status_label']} / {r_c['top']['hook90']['status_label']}",
                    "하부 일자 / 90°": f"{r_c['bot']['straight']['status_label']} / {r_c['bot']['hook90']['status_label']}",
                    "스터럽(≤D16) 정착": "가능 (90°/135°, 6db)" if r_c["stirrup_eligible"] else "불가 (ld/ldh 확보)",
                })
            with st.expander("📋 규격별(D10~D25) 정착길이 및 상·하부 정착 가능 여부 비교표 보기", expanded=False):
                st.dataframe(pd.DataFrame(anch_cmp_rows), use_container_width=True, hide_index=True)
        else:
            with hj_col_vis:
                st.markdown(
                    '<div class="dw-section-card" style="margin-bottom:0.65rem;">'
                    '<div class="dw-section-header">'
                    '<div class="dw-section-title"><span class="dw-accent-bar"></span>수평 이어치기 단면도 & 전단흐름(Q/I) 분포</div>'
                    '<span class="dw-pill-blue">관리자 인증 대기</span>'
                    '</div></div>',
                    unsafe_allow_html=True,
                )
                st.info("🔒 좌측 STEP 2에서 관리자 코드를 인증하면 정밀 검토 단면도 및 결과가 표시됩니다.")

    with tab_h_schedule:
        if not hj_can_render:
            st.info("🔒 관리자 전용 정밀 검토 모드가 잠겨 있습니다. '부재별 검토' 탭에서 관리자 코드를 입력하거나 '일반 검토 모드'로 전환해 주세요.")
        else:
            # 7. 전체 보 일괄 검토 (Horizontal Joint Batch Screening) & CSV 다운로드
            st.markdown(
                '<div class="dw-section-card" style="margin-top:1.1rem; margin-bottom:0.65rem;">'
                '<div class="dw-section-header">'
                '<div class="dw-section-title"><span class="dw-accent-bar"></span>전체 보 일람표 수평 이어치기 일괄 검토</div>'
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

    with tab_h_report:
        if not hj_can_render:
            st.info("🔒 관리자 전용 정밀 검토 모드가 잠겨 있습니다. '부재별 검토' 탭에서 관리자 코드를 입력하거나 '일반 검토 모드'로 전환해 주세요.")
        else:
            # 산정 근거 상세 수식 Expander (기본 닫힘)
            st.markdown(
                '<div class="dw-section-card" style="margin-bottom:0.75rem;">'
                '<div class="dw-section-header">'
                '<div class="dw-section-title"><span class="dw-accent-bar"></span>수평 이어치기 구조검토 계산근거</div>'
                '<span class="dw-pill-blue">KDS 14 20 22 · 14 20 52</span>'
                '</div></div>',
                unsafe_allow_html=True,
            )
            hj_prec_note = (
                f"\n> **압축·인장면 적용 ({hj_res['moment_mode_label']}):** "
                f"압축연단 깊이 $y_{{\\text{{comp}}}} = {hj_res['y_comp']:.0f}\\text{{ mm}}$, "
                f"중립축 깊이 $c = {hj_res['c_depth']:.1f}\\text{{ mm}}$ → 전단흐름 저감계수 $\\alpha_q = \\mathbf{{{hj_res['alpha_q']:.3f}}}$"
                if is_hj_precision_selected
                else ""
            )
            anch_sqrt_note = (
                f" (sqrt(fck) 상한 8.4 MPa 적용, 원래 √{fck}={anch_res['sqrt_fck_raw']:.2f})"
                if anch_res["sqrt_fck_capped"]
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
6. **전단마찰보강근 정착길이 산정 (KDS 14 20 52, D{anch_res['bar_dia']}, $d_b={anch_res['db']:.2f}$ mm, $\\sqrt{{f_{{ck}}}}={anch_res['sqrt_fck']:.2f}$ MPa{anch_sqrt_note}, $\\psi_{{\\text{{excess}}}}={anch_res['excess_factor']:.3f}$):**
   - **일자(직선) 인장정착길이 ($l_d$, 표 4.1-1 '기타의 경우', $\\alpha=1.0$, {'D19 이하 0.72' if anch_res['bar_dia'] <= 19 else 'D22 이상 0.90'}):**
     $$l_d = \\max\\left(\\frac{{{anch_res['ld_coeff']:.2f} \\times {anch_res['fy_eff']:.0f}}}{{{anch_res['sqrt_fck']:.2f}}} \\times {anch_res['db']:.2f} \\times {anch_res['excess_factor']:.3f},\\; 300\\right) = \\mathbf{{{anch_res['ld']:.1f}\\text{{ mm}}}} \\quad (l_d+c = \\mathbf{{{anch_res['req_h_straight']:.1f}\\text{{ mm}}}})$$
   - **90° 표준갈고리 정착길이 ($l_{{dh}}$, 4.1.5, 피복 보정 {anch_res['cover_07_factor']:.1f}, 구부린 끝 $12d_b={anch_res['hook_90_ext']:.0f}$ mm 이상):**
     $$l_{{dh}} = \\max\\left(\\frac{{0.24 \\times {anch_res['fy_eff']:.0f}}}{{{anch_res['sqrt_fck']:.2f}}} \\times {anch_res['db']:.2f} \\times {anch_res['cover_07_factor']:.1f} \\times {anch_res['excess_factor']:.3f},\\; 8d_b,\\; 150\\right) = \\mathbf{{{anch_res['ldh']:.1f}\\text{{ mm}}}} \\quad (l_{{dh}}+{anch_res['ldh_cover_eff']:.0f} = \\mathbf{{{anch_res['req_h_hook']:.1f}\\text{{ mm}}}})$$
   - **상·하부 개별 가용 깊이 & 판정:** 상부(일자 {anch_res['top']['straight']['h_avail']:.0f}mm / 90° {anch_res['top']['hook90']['h_avail']:.0f}mm → {anch_res['top']['status_label']}) · 하부(일자 {anch_res['bot']['straight']['h_avail']:.0f}mm / 90° {anch_res['bot']['hook90']['h_avail']:.0f}mm → {anch_res['bot']['status_label']})
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
            anch_sqrt_html = (
                f"sqrt(fck) 상한 8.4 MPa 적용 (입력 fck={fck} MPa)"
                if anch_res["sqrt_fck_capped"]
                else f"√fck = {anch_res['sqrt_fck']:.2f} MPa"
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
<h3>전단마찰보강근 정착길이 및 상·하부 개별 정착 제한 검토 (KDS 14 20 52)</h3>
<p><b>검토 규격:</b> D{anch_res['bar_dia']} (db={anch_res['db']:.2f} mm, fy={anch_res['fy_eff']:.0f} MPa, {anch_sqrt_html}, 순피복 c={anch_res['cover']:.0f} mm, 피복보정={anch_res['cover_07_factor']:.1f}, 초과저감 ψ_excess={anch_res['excess_factor']:.3f})</p>
<table>
<tr><th>구분 / 검토 구간</th><th>일자(직선) 배근 (ld={anch_res['ld']:.0f}mm, 필요 {anch_res['req_h_straight']:.0f}mm)</th><th>90° 표준갈고리 (ldh={anch_res['ldh']:.0f}mm, 필요 {anch_res['req_h_hook']:.0f}mm, 12db={anch_res['hook_90_ext']:.0f}mm)</th></tr>
<tr><td>상부 구간 (h_상 = {anch_res['h_top']:.0f} mm)</td><td>가용 {anch_res['top']['straight']['h_avail']:.1f}mm → <b>{anch_res['top']['straight']['status_label']}</b> ({anch_res['top']['straight']['excess_msg']})</td><td>가용 {anch_res['top']['hook90']['h_avail']:.1f}mm → <b>{anch_res['top']['hook90']['status_label']}</b> ({anch_res['top']['hook90']['excess_msg']})</td></tr>
<tr><td>하부 구간 (h_하 = {anch_res['h_bot']:.0f} mm)</td><td>가용 {anch_res['bot']['straight']['h_avail']:.1f}mm → <b>{anch_res['bot']['straight']['status_label']}</b> ({anch_res['bot']['straight']['excess_msg']})</td><td>가용 {anch_res['bot']['hook90']['h_avail']:.1f}mm → <b>{anch_res['bot']['hook90']['status_label']}</b> ({anch_res['bot']['hook90']['excess_msg']})</td></tr>
<tr><td>시공 주의 및 D16 이하 스터럽 안내</td><td colspan="2">※ 90° 갈고리 0.7 저감 적용 조건: 측면 피복 65mm 이상(스터럽에서 안쪽 이격) 및 단부 피복 50mm 이상 확보, 90° 구부림 끝단(12db)은 보 길이 방향(종방향)으로 배근. 지진하중 저항 등 철근 항복강도(fy)의 완전 발휘가 필수인 구간에는 초과철근 저감 적용 불가.<br/>※ D16 이하 스터럽(KDS 14 20 52 4.4.4(2)): 상·하부 종방향 주철근을 둘러싸는 90°/135° 스터럽 갈고리(연장 6db 이상)로 단부 정착 가능. D19 이상 철근 또는 단독 다웰근은 간이 정착 적용 불가(상·하부 각각 정착길이 확보 또는 기계적 정착 등 별도 검토 필요).</td></tr>
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


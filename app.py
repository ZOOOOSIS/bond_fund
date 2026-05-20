import streamlit as st
import pandas as pd
import plotly.express as px
from sheets_client import read_sheet, append_row
from nav_engine import update_nav, get_nav_df

st.set_page_config(page_title="Bond Fund Dashboard", layout="wide")

# ── 상단 펀드 전환 버튼 ──────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 6])
with col1:
    if st.button("🇰🇷 한국 펀드", use_container_width=True):
        st.session_state["market"] = "KR"
with col2:
    if st.button("🇺🇸 미국 펀드", use_container_width=True):
        st.session_state["market"] = "US"

if "market" not in st.session_state:
    st.session_state["market"] = "KR"

market = st.session_state["market"]

# ── 타이틀 ───────────────────────────────────────────────────────
st.title("🇰🇷 한국 채권 펀드" if market == "KR" else "🇺🇸 미국 채권 펀드")
st.divider()

# ── NAV 업데이트 버튼 ─────────────────────────────────────────────
if st.button("📈 오늘 NAV 업데이트"):
    update_nav(market)
    st.success("NAV 업데이트 완료!")
    st.rerun()

if st.button("🔄 전체 NAV 재계산"):
    from nav_engine import recalculate_all_nav
    recalculate_all_nav(market)
    st.success("전체 NAV 재계산 완료!")
    st.rerun()

# ── NAV 차트 ─────────────────────────────────────────────────────
st.subheader("누적 수익률 추이")
df = get_nav_df(market)

if df.empty:
    st.info("아직 NAV 데이터가 없어요. 초기 포지션을 설정하고 NAV를 업데이트해주세요.")
else:
    # 수익률로 변환 (NAV 100 기준)
    nav_cols = [c for c in df.columns if c != "날짜"]
    for col in nav_cols:
        df[col] = df[col].astype(float)
        df[col] = (df[col] - 100)  # 100 기준 수익률 (%)
    df["날짜"] = pd.to_datetime(df["날짜"]).dt.date

    fig = px.line(
        df, x="날짜", y=nav_cols,
        labels={"value": "수익률 (%)", "날짜": "날짜", "variable": "구분"},
        color_discrete_map={
            "펀드NAV":     "#1f77b4",
            "BM1_3Y100":  "#aec7e8",
            "BM2_10Y100": "#ffbb78",
            "BM3_5050":   "#98df8a",
            "BM1_2Y100":  "#aec7e8",
        }
    )
    fig.update_layout(hovermode="x unified", legend_title="구분")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 현재 포지션 ───────────────────────────────────────────────────
st.subheader("현재 포지션")
pos_tab = "KR_포지션" if market == "KR" else "US_포지션"
pos_data = read_sheet(pos_tab)

if pos_data:
    latest = pos_data[-1]
    if market == "KR":
        c1, c2, c3 = st.columns(3)
        c1.metric("설정일", latest["날짜"])
        c2.metric("KR 3년물", f"{float(latest['KR3Y_비중'])*100:.0f}%")
        c3.metric("KR 10년물", f"{float(latest['KR10Y_비중'])*100:.0f}%")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("설정일", latest["날짜"])
        c2.metric("US 2년물", f"{float(latest['US2Y_비중'])*100:.0f}%")
        c3.metric("US 10년물", f"{float(latest['US10Y_비중'])*100:.0f}%")
else:
    st.info("포지션 데이터가 없어요.")

st.divider()

# ── 리밸런싱 패널 ─────────────────────────────────────────────────
st.subheader("포지션 조정")

if market == "KR":
    default_3y = int(float(pos_data[-1]["KR3Y_비중"]) * 100) if pos_data else 50
    kr3y = st.slider("KR 3년물 비중 (%)", 0, 100, default_3y, step=5)
    kr10y = 100 - kr3y
    st.write(f"KR 10년물 비중: **{kr10y}%** (자동)")

    if st.button("💾 포지션 저장"):
        today = pd.Timestamp.today().strftime("%Y-%m-%d")
        append_row("KR_포지션", [today, kr3y / 100, kr10y / 100])
        st.success(f"저장 완료! KR3Y {kr3y}% / KR10Y {kr10y}%")
        st.rerun()
else:
    default_2y = int(float(pos_data[-1]["US2Y_비중"]) * 100) if pos_data else 50
    us2y = st.slider("US 2년물 비중 (%)", 0, 100, default_2y, step=5)
    us10y = 100 - us2y
    st.write(f"US 10년물 비중: **{us10y}%** (자동)")

    if st.button("💾 포지션 저장"):
        today = pd.Timestamp.today().strftime("%Y-%m-%d")
        append_row("US_포지션", [today, us2y / 100, us10y / 100])
        st.success(f"저장 완료! US2Y {us2y}% / US10Y {us10y}%")
        st.rerun()

st.divider()

# ── 성과 요약 ─────────────────────────────────────────────────────
st.subheader("성과 요약")

if not df.empty:
    summary = {}
    for col in nav_cols:
        summary[col] = f"{df[col].iloc[-1]:.2f}%"
    st.table(pd.DataFrame(summary, index=["누적수익률"]))
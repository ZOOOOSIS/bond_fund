import pandas as pd
from sheets_client import read_sheet, append_row, overwrite_sheet

# 듀레이션 고정값
DURATION = {
    "KR3Y": 2.8,
    "KR10Y": 8.5,
    "US2Y": 1.9,
    "US10Y": 8.5,
}

# BM 구성
KR_BM = {
    "BM1_3Y100":  {"KR3Y": 1.0, "KR10Y": 0.0},
    "BM2_10Y100": {"KR3Y": 0.0, "KR10Y": 1.0},
    "BM3_5050":   {"KR3Y": 0.5, "KR10Y": 0.5},
}

US_BM = {
    "BM1_2Y100":  {"US2Y": 1.0, "US10Y": 0.0},
    "BM2_10Y100": {"US2Y": 0.0, "US10Y": 1.0},
    "BM3_5050":   {"US2Y": 0.5, "US10Y": 0.5},
}


def calc_return(weights: dict, prev_rates: dict, curr_rates: dict) -> float:
    """듀레이션 근사로 수익률 계산 (단위: %)"""
    total = 0.0
    for ticker, weight in weights.items():
        delta = curr_rates[ticker] - prev_rates[ticker]
        price_change = -DURATION[ticker] * (delta / 100)
        total += weight * price_change
    return total


def update_nav(market: str):
    """금리데이터 마지막 2행을 읽어서 오늘 NAV 계산 후 저장"""
    if market == "KR":
        rates_data = read_sheet("KR_금리")
    else:
        rates_data = read_sheet("US_금리")
    
    if len(rates_data) < 2:
        print("금리 데이터가 2일치 이상 필요해요.")
        return

    prev = rates_data[-2]
    curr = rates_data[-1]
    today = curr["날짜"]

    if market == "KR":
        nav_tab = "KR_NAV"
        pos_tab = "KR_포지션"
        bm_dict = KR_BM
        tickers = ["KR3Y", "KR10Y"]
        bm_cols = ["BM1_3Y100", "BM2_10Y100", "BM3_5050"]
        header = ["날짜", "펀드NAV", "BM1_3Y100", "BM2_10Y100", "BM3_5050"]
    else:
        nav_tab = "US_NAV"
        pos_tab = "US_포지션"
        bm_dict = US_BM
        tickers = ["US2Y", "US10Y"]
        bm_cols = ["BM1_2Y100", "BM2_10Y100", "BM3_5050"]
        header = ["날짜", "펀드NAV", "BM1_2Y100", "BM2_10Y100", "BM3_5050"]

    pos_data = read_sheet(pos_tab)
    if not pos_data:
        print(f"{pos_tab}에 포지션 데이터가 없어요.")
        return

    latest_pos = pos_data[-1]
    if market == "KR":
        weights = {
            "KR3Y":  float(latest_pos["KR3Y_비중"]),
            "KR10Y": float(latest_pos["KR10Y_비중"]),
        }
    else:
        weights = {
            "US2Y":  float(latest_pos["US2Y_비중"]),
            "US10Y": float(latest_pos["US10Y_비중"]),
        }

    prev_rates = {t: float(prev[t]) for t in tickers}
    curr_rates = {t: float(curr[t]) for t in tickers}

    fund_ret = calc_return(weights, prev_rates, curr_rates)
    bm_rets = {bm: calc_return(w, prev_rates, curr_rates) for bm, w in bm_dict.items()}

    nav_data = read_sheet(nav_tab)

    if not nav_data:
        prev_fund_nav = 100.0
        prev_bm_navs = {bm: 100.0 for bm in bm_dict}
    else:
        last = nav_data[-1]
        prev_fund_nav = float(last["펀드NAV"])
        prev_bm_navs = {bm: float(last[bm]) for bm in bm_cols}

    new_fund_nav = round(prev_fund_nav * (1 + fund_ret / 100), 4)
    new_bm_navs = {
        bm: round(prev_bm_navs[bm] * (1 + bm_rets[bm] / 100), 4)
        for bm in bm_dict
    }

    new_row = [today, new_fund_nav] + [new_bm_navs[bm] for bm in bm_dict]
    append_row(nav_tab, new_row)
    print(f"{market} NAV 업데이트 완료: {today} / 펀드={new_fund_nav}")


def get_nav_df(market: str) -> pd.DataFrame:
    """Streamlit 차트용 NAV 데이터프레임 반환"""
    tab = "KR_NAV" if market == "KR" else "US_NAV"
    data = read_sheet(tab)
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["날짜"] = pd.to_datetime(df["날짜"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values("날짜").reset_index(drop=True)
    return df

def recalculate_all_nav(market: str):
    """금리 데이터 전체를 읽어서 NAV를 처음부터 재계산"""
    if market == "KR":
        rates_data = read_sheet("KR_금리")
        nav_tab = "KR_NAV"
        pos_tab = "KR_포지션"
        bm_dict = KR_BM
        tickers = ["KR3Y", "KR10Y"]
        bm_cols = ["BM1_3Y100", "BM2_10Y100", "BM3_5050"]
        header = ["날짜", "펀드NAV", "BM1_3Y100", "BM2_10Y100", "BM3_5050"]
    else:
        rates_data = read_sheet("US_금리")
        nav_tab = "US_NAV"
        pos_tab = "US_포지션"
        bm_dict = US_BM
        tickers = ["US2Y", "US10Y"]
        bm_cols = ["BM1_2Y100", "BM2_10Y100", "BM3_5050"]
        header = ["날짜", "펀드NAV", "BM1_2Y100", "BM2_10Y100", "BM3_5050"]

    if len(rates_data) < 2:
        print("금리 데이터가 2일치 이상 필요해요.")
        return

    # 날짜순 정렬
    df_rates = pd.DataFrame(rates_data)
    df_rates = df_rates.sort_values("날짜").reset_index(drop=True)

    # 포지션 읽기
    pos_data = read_sheet(pos_tab)
    if not pos_data:
        print(f"{pos_tab}에 포지션 데이터가 없어요.")
        return

    # NAV 초기값
    fund_nav = 100.0
    bm_navs = {bm: 100.0 for bm in bm_dict}
    new_rows = []

    for i in range(1, len(df_rates)):
        prev = df_rates.iloc[i-1]
        curr = df_rates.iloc[i]
        today = curr["날짜"]

        # 해당 날짜 이전 가장 최근 포지션 찾기
        pos_df = pd.DataFrame(pos_data)
        pos_df = pos_df.sort_values("날짜")
        valid_pos = pos_df[pos_df["날짜"] <= today]
        if valid_pos.empty:
            latest_pos = pos_df.iloc[0]
        else:
            latest_pos = valid_pos.iloc[-1]

        if market == "KR":
            weights = {
                "KR3Y":  float(latest_pos["KR3Y_비중"]),
                "KR10Y": float(latest_pos["KR10Y_비중"]),
            }
        else:
            weights = {
                "US2Y":  float(latest_pos["US2Y_비중"]),
                "US10Y": float(latest_pos["US10Y_비중"]),
            }

        prev_rates = {t: float(prev[t]) for t in tickers}
        curr_rates = {t: float(curr[t]) for t in tickers}

        fund_ret = calc_return(weights, prev_rates, curr_rates)
        bm_rets = {bm: calc_return(w, prev_rates, curr_rates) for bm, w in bm_dict.items()}

        fund_nav = round(fund_nav * (1 + fund_ret / 100), 4)
        bm_navs = {bm: round(bm_navs[bm] * (1 + bm_rets[bm] / 100), 4) for bm in bm_dict}

        new_rows.append([today, fund_nav] + [bm_navs[bm] for bm in bm_dict])

    # 시트 덮어쓰기
    overwrite_sheet(nav_tab, new_rows, header)
    print(f"{market} 전체 NAV 재계산 완료: {len(new_rows)}일치")
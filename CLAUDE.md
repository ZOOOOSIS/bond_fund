# Bond Fund Project

## 프로젝트 개요
채권 모의투자 대시보드. 한국/미국 채권 펀드 NAV를 추적하고 벤치마크 대비 성과를 측정.

## 기술 스택
- Python, Streamlit, Google Sheets (gspread), Telegram Bot
- 패키지 실행: `python -m streamlit run app.py`, `python -m pip install`

## 파일 구조
- `app.py` — Streamlit 대시보드 메인
- `bond_bot.py` — 텔레그램 봇 (일간 금리 파싱)
- `nav_engine.py` — NAV 계산 엔진 (듀레이션 근사)
- `sheets_client.py` — Google Sheets 연동
- `.env` — 환경변수 (SPREADSHEET_ID, SERVICE_ACCOUNT_PATH, BOT_TOKEN)
- `service_account.json` — Google 서비스 계정 키

## Google Sheets 구조 (Spreadsheet ID: 1t2Hr-S-WriuQA0kfvwcT_OI0i1P_sOq-i9VGR658yHw)
- `KR_금리` — 일간 KR 금리 (날짜, KR3Y, KR10Y)
- `US_금리` — 일간 US 금리 (날짜, US2Y, US10Y)
- `KR_포지션` — KR 비중 이력 (날짜, KR3Y_비중, KR10Y_비중)
- `US_포지션` — US 비중 이력 (날짜, US2Y_비중, US10Y_비중)
- `KR_NAV` — KR 펀드 NAV + BM3개
- `US_NAV` — US 펀드 NAV + BM3개

## 듀레이션 고정값
- KR3Y: 2.8, KR10Y: 8.5, US2Y: 1.9, US10Y: 8.5

## 응답 언어
한국어로 응답해줘.
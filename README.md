# 채권 모의투자 대시보드 (bond_fund)

듀레이션 근사 기반으로 한국/미국 채권 펀드 NAV를 매일 계산하고
벤치마크 3개와 성과를 비교하는 모의투자 대시보드.

## 주요 기능
- 한국 / 미국 펀드 탭 분리 UI
- 듀레이션 근사로 일간 수익률 계산
- NAV 누적 추이 차트
- 벤치마크 3개 동시 추적 (단기 100%, 장기 100%, 혼합 50:50)
- 포지션 슬라이더로 비중 조절 및 이력 저장
- 텔레그램 봇으로 일간 금리 자동 파싱

## 기술 스택
- Python, Streamlit
- Google Sheets (gspread)
- Telegram Bot API

## 실행 방법
python -m pip install -r requirements.txt
python -m streamlit run app.py

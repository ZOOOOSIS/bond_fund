import re
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
from sheets_client import read_sheet, append_row

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_date(text: str) -> str | None:
    match = re.search(r'\((\d{1,2})/(\d{1,2})\)', text)
    if match:
        mm, dd = match.groups()
        return f"2026-{mm.zfill(2)}-{dd.zfill(2)}"
    return None


def prev_business_day(date_str: str) -> str:
    """주어진 날짜의 전 영업일 반환 (토→금, 일→금, 월→금)"""
    d = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)
    while d.weekday() >= 5:  # 5=토, 6=일
        d -= timedelta(days=1)
    return d.strftime("%Y-%m-%d")


def parse_kr_rates(text: str) -> dict | None:
    patterns = {
        "KR3Y":  r'국고채\s*3년물\s*([\d.]+)',
        "KR10Y": r'국고채\s*10년물\s*([\d.]+)',
    }
    rates = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            rates[key] = float(match.group(1))
        else:
            return None
    return rates


def parse_us_rates(text: str) -> dict | None:
    patterns = {
        "US2Y":  r'미\s*국채\s*2년물\s*([\d.]+)',
        "US10Y": r'미\s*국채\s*10년물\s*([\d.]+)',
    }
    rates = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            rates[key] = float(match.group(1))
        else:
            return None
    return rates


def is_duplicate(date_str: str, tab_name: str) -> bool:
    data = read_sheet(tab_name)
    existing_dates = [row["날짜"] for row in data]
    return date_str in existing_dates


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.channel_post
    if not message:
        return

    text = message.text or message.caption or ""
    if not text:
        return

    logger.info(f"메시지 수신: {text[:80]}")

    date_str = parse_date(text)
    if not date_str:
        logger.info("날짜 파싱 실패 — 스킵")
        return

    # KR 시도
    kr_rates = parse_kr_rates(text)
    if kr_rates:
        if is_duplicate(date_str, "KR_금리"):
            logger.info(f"KR 중복 스킵: {date_str}")
            await message.reply_text(f"⚠️ {date_str} KR 데이터는 이미 저장되어 있어요.")
            return
        append_row("KR_금리", [date_str, kr_rates["KR3Y"], kr_rates["KR10Y"]])
        logger.info(f"KR 저장 완료: {date_str} {kr_rates}")
        await message.reply_text(f"✅ KR 금리 저장 완료!\n날짜: {date_str}\n3년물: {kr_rates['KR3Y']}%\n10년물: {kr_rates['KR10Y']}%")
        return

    # US 시도
    us_rates = parse_us_rates(text)
    if us_rates:
        us_date_str = prev_business_day(date_str)  # 전 영업일로 변환
        if is_duplicate(us_date_str, "US_금리"):
            logger.info(f"US 중복 스킵: {us_date_str}")
            await message.reply_text(f"⚠️ {us_date_str} US 데이터는 이미 저장되어 있어요.")
            return
        append_row("US_금리", [us_date_str, us_rates["US2Y"], us_rates["US10Y"]])
        logger.info(f"US 저장 완료: {us_date_str} {us_rates}")
        await message.reply_text(f"✅ US 금리 저장 완료!\n날짜: {us_date_str}\n2년물: {us_rates['US2Y']}%\n10년물: {us_rates['US10Y']}%")
        return

    logger.info("KR/US 모두 파싱 실패 — 스킵")


def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    logger.info("bond_bot 시작!")
    app.run_polling()


if __name__ == "__main__":
    main()
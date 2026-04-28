import asyncio
import schedule
import time
from telegram import Bot

from core.database import cursor, conn
from core.llm import ask_llm

BOT_TOKEN = "8516024664:AAGYqNyyFnSkUixfSlyG-QBMSCebK9jCLQg"
CHAT_ID = 6644308148

bot = Bot(token=BOT_TOKEN)


async def send_daily_summary():
    cursor.execute("SELECT id, content FROM topics WHERE used=0 LIMIT 1")
    row = cursor.fetchone()

    if not row:
        await bot.send_message(chat_id=CHAT_ID, text="No topics left")
        return

    topic_id, content = row

    summary = ask_llm(content, "Give a short easy summary")

    cursor.execute("UPDATE topics SET used=1 WHERE id=?", (topic_id,))
    conn.commit()

    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"Daily Topic:\n\n{summary}"
    )


def run_async_job():
    asyncio.run(send_daily_summary())


# ⏰ schedule
#schedule.every(20).seconds.do(run_async_job)   # 🔥 for testing
schedule.every().day.at("09:00").do(run_async_job)  # real use


if __name__ == "__main__":
    print("Telegram scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(1)
import os
from dotenv import load_dotenv
from core.database import cursor, conn
from core.llm import ask_llm

load_dotenv()

async def send_daily(context):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    cursor.execute("SELECT id, content FROM topics WHERE used=0 LIMIT 1")
    row = cursor.fetchone()

    if not row:
        await context.bot.send_message(chat_id=chat_id, text="No topics left")
        return

    topic_id, content = row

    summary = ask_llm(content, "Give short summary")

    cursor.execute("UPDATE topics SET used=1 WHERE id=?", (topic_id,))
    conn.commit()

    await context.bot.send_message(chat_id=chat_id, text=summary)
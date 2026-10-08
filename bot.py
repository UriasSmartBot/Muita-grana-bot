
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OTCHARTS_API_KEY = os.getenv("OTCHARTS_API_KEY")
DISPLAY_TZ = os.getenv("DISPLAY_TZ", "America/Sao_Paulo")

def validar_configuracao():
    faltando = [
        nome for nome, valor in {
            "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
            "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
            "OTCHARTS_API_KEY": OTCHARTS_API_KEY,
        }.items()
        if not valor
    ]
    if faltando:
        logging.error("Configure no Render: %s", ", ".join(faltando))
        return False
    return True

def horario_local():
    return datetime.now(ZoneInfo(DISPLAY_TZ)).strftime("%d/%m/%Y %H:%M:%S")

async def main():
    if not validar_configuracao():
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"🤖 Bot iniciado. Horário local: {horario_local()}"
    )
    logging.info("Mensagem de teste enviada ao Telegram.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

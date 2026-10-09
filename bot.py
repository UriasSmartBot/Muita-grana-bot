
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OTCHARTS_API_KEY = os.getenv("OTCHARTS_API_KEY")
DISPLAY_TZ = os.getenv("DISPLAY_TZ", "America/Sao_Paulo")


def validar_configuracao():
    obrigatorias = {
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "OTCHARTS_API_KEY": OTCHARTS_API_KEY,
    }

    faltando = [
        nome for nome, valor in obrigatorias.items()
        if not valor
    ]

    if faltando:
        logging.error(
            "Variáveis ausentes no Render: %s",
            ", ".join(faltando),
        )
        return False

    return True


async def main():
    if not validar_configuracao():
        return

    agora = datetime.now(
        ZoneInfo(DISPLAY_TZ)
    ).strftime("%d/%m/%Y %H:%M:%S")

    bot = Bot(token=TELEGRAM_TOKEN)

    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=(
            "🤖 Muita-grana-bot iniciado!\n\n"
            f"Horário de Brasília: {agora}\n"
            "Configuração inicial verificada.\n"
            "Modo: teste, sem operações automáticas.\n"
            "Dados ao vivo: ainda não conectados."
        ),
    )

    logging.info("Mensagem de teste enviada ao Telegram.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

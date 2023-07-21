import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def bemvindo(message: types.Message):
    print(message.from_id)
    await bot.send_message(
        chat_id=message.from_id,
        text=(
            "Olá!\n"
            "Seja bem-vindo!\n\n"
            "Sou um bot que raspa a página de documentação técnica do "
            "eSocial a procura de novos documentos '.pdf', e notifica "
            "os interessados.\n\n"
            "/entrar para ser notificado.\n"
            "/sair para não ser mais notificado.\n"
        ),
        disable_web_page_preview=False,
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
from datetime import datetime, timedelta
import logging
import os
from typing import List, Optional

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from db import Arquivo, Inscrito
from utils import formatar_mensagem

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)

emoji_sucesso = '\U0001f44d'
emoji_erro = '\U000026d4'
emoji_direcao = '\U0001F502'

comandos = {
    'entrar': 'para se inscrever.',
    'recentes': 'para listar arquivos recentes.',
    'sair': 'para cancelar a inscrição.',
}

async def enviar_mensagem(
        chat_id: int,
        titulo: str,
        emoji: Optional[str]=None,
        texto: Optional[str]=None,
        opcoes: Optional[List[str]]=None
        ) -> types.Message:
    msg = ""
    # Sucesso
    if emoji is not None:
        msg += emoji + " "
    msg += f"{titulo}\n\n"
    # Texto
    if texto is not None:
        msg += texto + '\n\n'
    # Oções
    if opcoes is not None:
        for o in opcoes:
            msg += f"/{o} {comandos[o]}\n"
    # Mensagem
    return await bot.send_message(
        chat_id=chat_id,
        text=msg,
        disable_web_page_preview=False,
    )


@dp.message_handler(commands=['entrar'])
async def entrar(message: types.Message):
    chat = message.chat
    inscrito, _ = Inscrito.get_or_create(
        id=chat.id,
        nome=chat.first_name,
    )
    if inscrito.ativo:
        await enviar_mensagem(
            chat_id=chat.id,
            emoji=emoji_erro,
            titulo="Você já é inscrito!",
        )
    else:
        inscrito.ativo = True
        inscrito.save()
        await enviar_mensagem(
            chat_id=chat.id,
            emoji=emoji_sucesso,
            titulo="Incrição efetuada!",
            texto="Quando houver novidade você será notificado.",
        )

@dp.message_handler(commands=['sair'])
async def sair(message: types.Message):
    chat = message.chat
    inscrito: Inscrito = Inscrito.get_or_none(chat.id)
    if inscrito is None or not inscrito.ativo:
        await enviar_mensagem(
            chat_id=chat.id,
            emoji=emoji_erro,
            titulo="Você não está inscrito!",
        )
    else:
        inscrito.ativo = False
        inscrito.save()
        await enviar_mensagem(
            chat_id=chat.id,
            emoji=emoji_sucesso,
            titulo="Incrição cancelada!",
        )

@dp.message_handler(commands=['recentes'])
async def recentes(message: types.Message):
    dt = datetime.now() - timedelta(days=60)
    arquivos = Arquivo.filter(Arquivo.data>=dt)
    if arquivos:
        emoji=emoji_direcao
        titulo="Aqui está os arquivos encontrados nos últimos 60 dias:"
        msg = formatar_mensagem(arquivos=arquivos)
    else:
        emoji=emoji_erro
        titulo="Não foram encontrados arquivos novos nos últimos 60 dias."
        msg = None
    await enviar_mensagem(
        chat_id=message.from_id,
        emoji=emoji,
        titulo=titulo,
        texto=msg,
    )

@dp.message_handler(commands=['start', 'ajuda'])
async def saudacao(message: types.Message):
    await enviar_mensagem(
        chat_id=message.from_id,
        titulo="Olá!\nSeja bem-vindo!",
        texto=(
            "Sou um bot que raspa a página de documentação técnica do "
            "eSocial a procura de novos documentos '.pdf', e notifica "
            "os interessados."
        ),
        opcoes=['entrar', 'recentes', 'sair']
    )

if __name__ == '__main__':
    import signal
    def sair_com_seguranca(*args, **kwargs):
        raise(SystemExit)
    
    signal.signal(signal.SIGTERM, sair_com_seguranca)
    executor.start_polling(dp, skip_updates=True)
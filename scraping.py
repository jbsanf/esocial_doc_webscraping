import asyncio
from collections import defaultdict
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from bot import bot
from db import pg_db, Arquivo, Inscrito, Notificar
from utils import formatar_mensagem

async def enviar_notificacao(inscrito: Inscrito, arquivos: List[Arquivo]) -> None:
    msg = f'{inscrito.nome}, aqui está a lista de novos arquivos que encontrei:\n\n'
    msg += formatar_mensagem(arquivos=[arq.arquivo for arq in arquivos])
    await bot.send_message(
        chat_id=inscrito.id,
        text=msg,
        disable_web_page_preview=False,
    )
    Notificar.delete().where(Notificar.inscrito==inscrito).execute()

async def preparar_notificacao() -> None:
    notificar = defaultdict(list)
    for nt in Notificar.filter():
        notificar[nt.inscrito].append(nt)
    
    with pg_db.atomic():
        for insc, arquivos in notificar.items():
            msg = f'{insc.nome} aqui está a lista de novos arquivo que encontrei:\n\n'
            for arq in arquivos:
                msg += f'- {arq.arquivo.nome}\n'
            await asyncio.gather(enviar_notificacao(inscrito=insc, arquivos=arquivos))
    
    await (await bot.get_session()).close()

def obter_lista() -> List[dict]:
    response = requests.get('https://www.gov.br/esocial/pt-br/documentacao-tecnica')
    soup = BeautifulSoup(response.content, features="html.parser")
    dt_hoje = datetime.now()
    for item in soup.find_all('a'):
        if item['href'].endswith('.pdf'):
            nome = item.text.strip()
            link = item['href']
            if nome.startswith('-'):
                nome = nome[1:].strip()
            arquivo = link.split('/')[-1]
            yield dict(
                nome=nome,
                link=item['href'],
                data=dt_hoje,
                arquivo=arquivo,
            )
    return []


if __name__ == '__main__':
    logger.info(f"Iniciando busca por novos arquivos.")
    inscritos: List[Inscrito] = Inscrito.todos_ativos()

    # Buscar novidades e gerar notificação
    with pg_db.atomic():
        for arq in obter_lista():
            arquivo, criado = Arquivo.get_or_create(
                arquivo=arq.pop('arquivo'),
                defaults=arq,
            )
            if criado:
                for inscrito in inscritos:
                    Notificar.create(
                        arquivo=arquivo,
                        inscrito=inscrito,
                    )
    
    # Notificar os inscritos
    asyncio.run(preparar_notificacao())
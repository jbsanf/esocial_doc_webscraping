from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

from db import Arquivo

def obter_lista() -> List[dict]:
    response = requests.get('https://www.gov.br/esocial/pt-br/documentacao-tecnica')
    soup = BeautifulSoup(response.content, features="html.parser")
    dt_hoje = datetime.now()
    for item in soup.find_all('a'):
        if item['href'].endswith('.pdf'):
            nome = item.text
            link = item['href']
            if nome.startswith('-'):
                nome = nome[1:]
            nome = nome.strip()
            arquivo = link.split('/')[-1]
            yield dict(
                nome=item.text,
                link=item['href'],
                data=dt_hoje,
                arquivo=arquivo,
            )
    return []


if __name__ == '__main__':
    for arq in obter_lista():
        arquivo, criado = Arquivo.get_or_create(
            arquivo=arq.pop('arquivo'),
            defaults=arq,
        )
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB, where
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

db = TinyDB("./db.json", storage=serialization)
tbl_arquivos = db.table('arquivos')


@dataclass
class Arquivo:
    nome: str
    link: str
    data: datetime
    arquivo: str = field(init=False)

    def __post_init__(self):
        if self.nome.startswith('-'):
            self.nome = self.nome[1:]
        self.nome = self.nome.strip()
        self.arquivo = self.link.split('/')[-1]
    
    def existe(self) -> bool:
        return bool(tbl_arquivos.search(where('arquivo')==self.arquivo))

    def gravar(self) -> None:
        tbl_arquivos.insert(self.__dict__)

    @classmethod
    def obter_lista(cls) -> List['Arquivo']:
        response = requests.get('https://www.gov.br/esocial/pt-br/documentacao-tecnica')
        soup = BeautifulSoup(response.content, features="html.parser")
        dt_hoje = datetime.now()
        for item in soup.find_all('a'):
            if item['href'].endswith('.pdf'):
                yield cls(
                    nome=item.text,
                    link=item['href'],
                    data=dt_hoje,
                )


if __name__ == '__main__':
    for arq in Arquivo.obter_lista():
        if not arq.existe():
            arq.gravar()
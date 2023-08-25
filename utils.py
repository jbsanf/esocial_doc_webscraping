from typing import List

from db import Arquivo


def formatar_mensagem(arquivos: List[Arquivo]) -> str:
    msg = ''
    for arq in arquivos:
        msg += (
            f'{(arq.nome or arq.arquivo).upper()}\n'
            f'{arq.link}'
            '\n\n'
        )
    return msg
"""
Q1-b: destino = saída padrão (System.out).

    python -m demos_streams.q1b_stdout                 -> mostra os bytes em hexadecimal
    python -m demos_streams.q1b_stdout | python -m demos_streams.q2b_stdin
                                                       -> envia bytes REAIS para a entrada padrão do outro programa
"""

import sys

from models.exemplo import criar_loja_exemplo
from streams.loja_output_stream import LojaOutputStream


class DestinoHexa:
    """Destino auxiliar: imprime os bytes em hexadecimal (só para ler no terminal)."""

    def write(self, dados):
        sys.stdout.write(dados.hex(" ") + "\n")
        return len(dados)

    def flush(self):
        sys.stdout.flush()


def main():
    pecas = criar_loja_exemplo().pecas

    if sys.stdout.isatty():
        destino = DestinoHexa()       
    else:
        destino = sys.stdout.buffer    

    with LojaOutputStream(destino, pecas, len(pecas)) as saida:
        saida.enviar()


if __name__ == "__main__":
    main()
"""
Q2-c: origem = arquivo (FileInputStream).

    python -m demos_streams.q2c_arquivo        (rode antes q1c_arquivo)
"""

import os

from streams.loja_input_stream import LojaInputStream

ARQUIVO = os.path.join("dados", "pecas.bin")


def main():
    if not os.path.exists(ARQUIVO):
        print(f"Arquivo {ARQUIVO} não existe. Rode antes: python -m demos_streams.q1c_arquivo")
        return

    with open(ARQUIVO, "rb") as arquivo:                
        with LojaInputStream(arquivo) as entrada:
            pecas = entrada.ler_pecas()

    print(f"Li {len(pecas)} peças de {ARQUIVO}:")
    for peca in pecas:
        print("  ", peca)


if __name__ == "__main__":
    main()
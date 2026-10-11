"""
Q2-b: origem = entrada padrão (System.in).

    python -m demos_streams.q1b_stdout | python -m demos_streams.q2b_stdin
    python -m demos_streams.q2b_stdin < dados/pecas.bin
"""

import sys

from streams.loja_input_stream import LojaInputStream


def main():
    with LojaInputStream(sys.stdin.buffer) as entrada:
        pecas = entrada.ler_pecas()

    print(f"Recebi {len(pecas)} peças pela entrada padrão:")
    for peca in pecas:
        print("  ", peca)


if __name__ == "__main__":
    main()
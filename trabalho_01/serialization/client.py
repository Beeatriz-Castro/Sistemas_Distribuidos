"""
QUESTÃO 3 - Cliente da Loja (TCP).

Para cada operação o cliente:
  1. EMPACOTA o request  (dict -> bytes JSON) e envia
  2. recebe os bytes do reply e DESEMPACOTA (bytes -> dict)
  3. reconstrói os objetos (PecaDeRoupa / Venda) a partir do resultado

Executar:
  python -m questao3_serializacao.cliente            (menu interativo)
  python -m questao3_serializacao.cliente --demo     (demonstração automática)
"""

import argparse
import socket

from models.peca_de_roupa import TIPOS_DE_PECA, Camiseta, criar_peca, peca_de_dict
from models.venda import Venda
from serialization.protocolo import desempacotar, empacotar, enviar, receber


class ErroRemoto(Exception):
    """O servidor respondeu com status erro."""


class ClienteLoja:

    def __init__(self, host, porta, verboso=True):
        self.verboso = verboso
        self._socket = socket.create_connection((host, porta))

    def fechar(self):
        self._socket.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.fechar()

    def _chamar(self, operacao, argumentos=None):
        requisicao = {"operacao": operacao, "argumentos": argumentos or {}}
        if self.verboso:
            print(f"  >> Empacotado ({len(empacotar(requisicao))} bytes): "
                  f"{empacotar(requisicao).decode('utf-8')}")

        enviar(self._socket, requisicao)       
        resposta = receber(self._socket)      
        if resposta is None:
            raise ConnectionError("O servidor encerrou a conexão")

        if self.verboso:
            print(f" Desempacotado: {resposta}")
        if resposta["status"] != "OK":
            raise ErroRemoto(resposta["mensagem"])
        return resposta["resultado"]


    def listar_pecas(self):
        resultado = self._chamar("LISTAR_PECAS")
        return [peca_de_dict(item) for item in resultado]

    def adicionar_peca(self, peca):
        resultado = self._chamar("ADICIONAR_PECA", {"peca": peca.para_dict()})
        return peca_de_dict(resultado)

    def vender_peca(self, codigo, quantidade):
        resultado = self._chamar("VENDER_PECA", {"codigo": codigo, "quantidade": quantidade})
        return Venda.de_dict(resultado)

    def total_vendas(self):
        return self._chamar("TOTAL_VENDAS")


def demonstracao(cliente):
    print("\n=== 1) Listando as peças da loja ===")
    for peca in cliente.listar_pecas():
        print("  ", peca)

    print("\n=== 2) Enviando um OBJETO Camiseta serializado para o servidor ===")
    nova = Camiseta(6, "Camiseta Polo", "Lacoste", "G", "verde", 189.90, 8, "curta")
    print("   Adicionada:", cliente.adicionar_peca(nova))

    print("\n=== 3) Vendendo 2 unidades da peça 6 ===")
    print("  ", cliente.vender_peca(6, 2))

    print("\n=== 4) Tentando vender mais do que existe em estoque (erro esperado) ===")
    try:
        cliente.vender_peca(4, 99)
    except ErroRemoto as erro:
        print("   Erro recebido do servidor:", erro)

    print("\n=== 5) Total vendido ===")
    print("  ", cliente.total_vendas())


def _ler_nova_peca():
    tipos = list(TIPOS_DE_PECA)
    for i, nome in enumerate(tipos, start=1):
        print(f"  {i}) {nome}")
    tipo = tipos[int(input("Tipo da peça: ")) - 1]
    rotulo = TIPOS_DE_PECA[tipo].ROTULO_DETALHE
    return criar_peca(
        tipo,
        int(input("Código: ")), input("Nome: "), input("Marca: "),
        input("Tamanho: "), input("Cor: "),
        float(input("Preço: ")), int(input("Quantidade em estoque: ")),
        input(f"{rotulo.capitalize()}: "),
    )


def menu(cliente):
    while True:
        print("\n--- LOJA DE ROUPAS ---")
        print("1) Listar peças  2) Adicionar peça  3) Vender peça  4) Total de vendas  0) Sair")
        opcao = input("Opção: ").strip()
        try:
            if opcao == "1":
                for peca in cliente.listar_pecas():
                    print("  ", peca)
            elif opcao == "2":
                print("   Adicionada:", cliente.adicionar_peca(_ler_nova_peca()))
            elif opcao == "3":
                codigo = int(input("Código da peça: "))
                quantidade = int(input("Quantidade: "))
                print("  ", cliente.vender_peca(codigo, quantidade))
            elif opcao == "4":
                print("  ", cliente.total_vendas())
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
        except ErroRemoto as erro:
            print("Erro do servidor:", erro)
        except (ValueError, IndexError):
            print("Entrada inválida.")


def main():
    parser = argparse.ArgumentParser(description="Cliente da loja de roupas (Questão 3)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--porta", type=int, default=5050)
    parser.add_argument("--demo", action="store_true", help="executa uma demonstração automática")
    args = parser.parse_args()

    with ClienteLoja(args.host, args.porta) as cliente:
        if args.demo:
            demonstracao(cliente)
        else:
            menu(cliente)


if __name__ == "__main__":
    main()
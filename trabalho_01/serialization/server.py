"""
QUESTÃO 3 - Servidor da Loja (TCP).

Fluxo de cada requisição:
  1. receber()      -> lê bytes e DESEMPACOTA o request (bytes -> dict)
  2. processar()    -> usa EstoqueService / VendasService (reconstrói objetos)
  3. enviar()       -> EMPACOTA o reply (dict -> bytes) e envia ao cliente

Executar:  python -m questao3_serializacao.servidor [--host H] [--porta P]
"""

import argparse
import socket
import threading

from models.exemplo import criar_loja_exemplo
from models.peca_de_roupa import peca_de_dict
from serialization.protocolo import enviar, receber
from services.estoque_service import EstoqueService
from services.vendas_service import VendasService


class ServidorLoja:

    def __init__(self, host, porta, loja, verboso=True):
        self.estoque = EstoqueService(loja)
        self.vendas = VendasService(self.estoque)
        self.verboso = verboso
        self._trava = threading.Lock()  # um cliente por vez mexe nos dados

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host, porta))
        self._socket.listen()
        self.porta = self._socket.getsockname()[1]  # útil quando porta=0

    def _log(self, *args):
        if self.verboso:
            print(*args, flush=True)

    # ---------- laço principal: uma thread por cliente ----------
    def servir(self):
        self._log(f"Servidor da loja aguardando na porta {self.porta}...")
        while True:
            try:
                conexao, endereco = self._socket.accept()
            except OSError:  # socket fechado por parar()
                break
            threading.Thread(target=self._atender_cliente,
                             args=(conexao, endereco), daemon=True).start()

    def parar(self):
        self._socket.close()

    def _atender_cliente(self, conexao, endereco):
        self._log(f"[+] Cliente conectado: {endereco}")
        with conexao:
            try:
                while True:
                    requisicao = receber(conexao)          # desempacota o request
                    if requisicao is None:
                        break
                    self._log(f"    REQUEST  de {endereco}: {requisicao}")
                    resposta = self.processar(requisicao)
                    self._log(f"    REPLY    para {endereco}: {resposta}")
                    enviar(conexao, resposta)              # empacota o reply
            except (ConnectionError, ValueError) as erro:
                self._log(f"    Conexão com {endereco} encerrada com erro: {erro}")
        self._log(f"[-] Cliente desconectado: {endereco}")

    # ---------- lógica da aplicação ----------
    def processar(self, requisicao):
        """Recebe o request já desempacotado e devolve o reply (ainda como dict)."""
        try:
            operacao = requisicao["operacao"]
            argumentos = requisicao.get("argumentos", {})
            with self._trava:
                resultado = self._executar(operacao, argumentos)
            return {"status": "OK", "resultado": resultado}
        except KeyError as erro:
            return {"status": "ERRO", "mensagem": f"Campo ausente na mensagem: {erro}"}
        except (ValueError, TypeError) as erro:
            return {"status": "ERRO", "mensagem": str(erro)}

    def _executar(self, operacao, args):
        if operacao == "LISTAR_PECAS":
            return [peca.para_dict() for peca in self.estoque.listar_pecas()]

        if operacao == "ADICIONAR_PECA":
            peca = peca_de_dict(args["peca"])          # dict -> objeto da subclasse certa
            self.estoque.adicionar_peca(peca)
            return peca.para_dict()

        if operacao == "VENDER_PECA":
            venda = self.vendas.vender(int(args["codigo"]), int(args["quantidade"]))
            return venda.para_dict()

        if operacao == "TOTAL_VENDAS":
            return {"quantidade_vendas": len(self.vendas.listar_vendas()),
                    "total": self.vendas.total_vendido()}

        raise ValueError(f"Operação desconhecida: {operacao}")


def main():
    parser = argparse.ArgumentParser(description="Servidor da loja de roupas (Questão 3)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--porta", type=int, default=5050)
    args = parser.parse_args()

    servidor = ServidorLoja(args.host, args.porta, criar_loja_exemplo())
    try:
        servidor.servir()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        servidor.parar()


if __name__ == "__main__":
    main()
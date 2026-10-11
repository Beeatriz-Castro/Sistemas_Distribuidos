"""
Em Java seria:  class LojaOutputStream extends OutputStream
Em Python:      class LojaOutputStream(io.RawIOBase)   (stream binário de saída)

Envia, byte a byte, os dados de um conjunto (array/lista) de PecaDeRoupa
para um destino qualquer: System.out, arquivo ou conexão TCP.

FORMATO BINÁRIO (big-endian, igual ao DataOutputStream do Java):
    int32   quantidade de peças que vêm a seguir
    Para cada peça:
        string  tipo        (ex.: "Camiseta")
        int32   codigo
        string  nome
        string  marca
        string  tamanho
        string  cor
        double  preco       (8 bytes, IEEE 754)
        int32   quantidade  (estoque)
        string  detalhe     (atributo específico da subclasse)
    onde "string" = 2 bytes com o tamanho + os bytes UTF-8 do texto
    (o mesmo que writeUTF do Java).
"""

import io
import struct

class LojaOutputStream(io.RawIOBase):

    def __init__(self, destino, pecas, quantidade):
        """
        destino    : onde os bytes serão escritos (qualquer objeto com write(bytes))
        pecas      : lista de objetos PecaDeRoupa
        quantidade : quantos objetos da lista serão enviados
        """
        super().__init__()
        self.destino = destino
        if quantidade < 0 or quantidade > len(pecas):
            self.destino = None  # nada a descarregar quando o objeto for finalizado
            raise ValueError(f"quantidade ({quantidade}) deve estar entre 0 e {len(pecas)}")
        self.pecas = pecas
        self.quantidade = quantidade

    def writable(self):
        return True

    def write(self, dados):
        self.destino.write(dados)
        return len(dados)

    def flush(self):
        if not self.closed and self.destino is not None and hasattr(self.destino, "flush"):
            self.destino.flush()

    def close(self):
        if not self.closed:
            try:
                self.flush()
            except ValueError: 
                pass
            super().close()

    def enviar(self):
        self.write(struct.pack(">i", self.quantidade))
        for peca in self.pecas[:self.quantidade]:
            self.write(self._empacotar_peca(peca))
        self.flush()

    @staticmethod
    def _texto(texto):
        dados = texto.encode("utf-8")
        return struct.pack(">H", len(dados)) + dados

    def _empacotar_peca(self, peca):
        return (
            self._texto(peca.tipo)
            + struct.pack(">i", peca.codigo)
            + self._texto(peca.nome)
            + self._texto(peca.marca)
            + self._texto(peca.tamanho)
            + self._texto(peca.cor)
            + struct.pack(">d", peca.preco)
            + struct.pack(">i", peca.quantidade)
            + self._texto(peca.detalhe)
        )
# Sistema de Gestão de Loja de Roupas — Trabalho 1 de Sistemas Distribuídos

## 1. Objetivo do projeto

O serviço remoto escolhido é um sistema simples de gestão de uma loja de roupas. O projeto demonstra dois modos diferentes de transportar dados:

- **Itens 1 e 2 — Streams:** escrever e ler uma sequência binária de peças usando destinos/origens diferentes: saída/entrada padrão, arquivo e TCP.
- **Item 3 — Serialização:** um cliente envia pedidos de operações para um servidor TCP. As mensagens são codificadas em JSON, processadas pelo servidor e respondidas ao cliente.

Esses dois caminhos são relacionados, mas não são o mesmo protocolo. Por isso existem a pasta `demos_stream/` e a pasta `serialization/`.

> **Fora do escopo deste repositório:** o item 4 (multicast) e a questão extra de votação descritos no enunciado.

## 2. Preparação

Execute os comandos a partir da raiz do projeto, isto é, da pasta `trabalho_01/`. Use `python3 -m pacote.modulo`, sem escrever `.py` no fim.

```bash
cd caminho/para/trabalho_01
python3 --version
```

O projeto utiliza apenas módulos da biblioteca padrão do Python. Não é necessário instalar dependências externas.

## 3. Estrutura do projeto

```text
trabalho_01/
├── README.md
├── models/
│   ├── peca_de_roupa.py       # PecaDeRoupa, subclasses e conversões
│   ├── loja.py                # estado da loja: coleção de peças
│   ├── venda.py               # objeto que representa uma venda
│   └── exemplo.py             # dados de exemplo
├── services/
│   ├── erros.py               # erros de negócio
│   ├── estoque_service.py     # operações de estoque
│   ├── vendas.py              # interface/abstração de vendas
│   └── vendas_service.py      # operações de venda
├── streams/
│   ├── loja_output_stream.py  # escrita do formato binário (item 1)
│   └── loja_input_stream.py   # leitura do formato binário (item 2)
├── demos_stream/
│   ├── q1b.py                 # item 1-b: saída padrão
│   ├── q1c.py                 # item 1-c: arquivo
│   ├── q1d.py                 # item 1-d: cliente que envia por TCP
│   ├── q2b.py                 # item 2-b: entrada padrão
│   ├── q2c.py                 # item 2-c: leitura de arquivo
│   └── q2d.py                 # item 2-d: servidor que recebe por TCP
└── serialization/
    ├── protocolo.py           # JSON, enquadramento e envio/recebimento
    ├── client.py              # cliente da questão 3
    └── server.py              # servidor da questão 3
```

## 4. Conceitos fundamentais do Capítulo 4

### 4.1 Processos, mensagens e comunicação

Um **processo** é um programa em execução. Neste projeto, o cliente e o servidor são processos diferentes. Eles precisam combinar como estabelecer a comunicação e como interpretar os bytes que trocam.

O capítulo apresenta duas operações básicas: **send** (enviar) e **receive** (receber). Em Python, neste projeto, funções como `sendall()` e `recv()` executam parte desse papel.

### 4.2 Socket, IP e porta

Um **socket** é uma ponta (*endpoint*) de comunicação entre processos. O destino de uma conexão é identificado por um endereço IP e uma porta. O IP identifica a máquina/interface de rede; a porta identifica o processo/serviço que recebe naquela máquina.

- **Servidor:** cria um socket, associa-o a um endereço/porta (`bind`) e aguarda conexões (`listen` e `accept`).
- **Cliente:** solicita uma conexão ao endereço/porta do servidor (`socket.create_connection`).
- **TCP:** oferece um fluxo confiável e ordenado de bytes entre as pontas conectadas.

O TCP não preserva fronteiras de mensagens da aplicação. Uma chamada de `recv(n)` pode devolver menos de `n` bytes. Por isso, a aplicação precisa definir um formato que permita saber quanto deve ler.

### 4.3 Stream (fluxo de bytes)

Um **stream** representa uma sequência de bytes que pode ser lida ou escrita. A mesma implementação de saída deve poder escrever para diferentes destinos, desde que eles ofereçam a interface de escrita:

- saída padrão: `sys.stdout.buffer`;
- arquivo: `open(..., "wb")`;
- conexão TCP: fluxo binário criado a partir do socket com `makefile("wb")`.

Analogamente, uma implementação de entrada pode ler de:

- entrada padrão: `sys.stdin.buffer`;
- arquivo: `open(..., "rb")`;
- conexão TCP: `makefile("rb")`.

O enunciado usa os nomes `OutputStream` e `InputStream`, comuns em Java. Como o projeto está em Python, `LojaOutputStream` e `LojaInputStream` adaptam o conceito usando as interfaces de fluxo binário do Python (`io.RawIOBase` e os métodos correspondentes). Não são subclasses das classes Java.

### 4.4 Serialização, empacotamento e desempacotamento

Os objetos do programa contêm atributos e comportamentos; a rede transporta bytes. **Serializar** é transformar a representação de dados em uma forma que possa ser armazenada ou transmitida. **Empacotar (marshalling)** é organizar os dados no formato externo da mensagem; **desempacotar (unmarshalling)** é interpretar a mensagem recebida e recuperar os dados estruturados.

Neste projeto há duas conversões conceitualmente distintas:

1. **Objeto Python → dicionário:** por exemplo, `peca.para_dict()`.
2. **Dicionário → bytes JSON UTF-8:** `empacotar()` em `serialization/protocolo.py`.

No recebimento, o caminho é inverso. Depois de obter o dicionário, `peca_de_dict()` ou `Venda.de_dict()` reconstrói o objeto correspondente.

O JSON foi escolhido como formato externo porque é textual, legível e amplamente suportado. Isso combina com a ideia do capítulo de um formato externo acordado previamente entre remetente e destinatário. O JSON é diferente da serialização binária nativa de objetos Java apresentada nos slides, mas atende à exigência do trabalho, que permite uma representação externa de dados.

### 4.5 Por que o protocolo de TCP inclui o tamanho da mensagem?

TCP fornece um fluxo de bytes, não uma mensagem completa por chamada. Em `serialization/protocolo.py`, cada mensagem tem:

```text
+----------------------+----------------------+
| tamanho: 4 bytes     | corpo: JSON em UTF-8  |
+----------------------+----------------------+
```

O tamanho é codificado em quatro bytes. O receptor lê primeiro esse cabeçalho e depois lê exatamente o número de bytes indicado. `_receber_exato()` repete `recv()` enquanto faltarem bytes. Isso evita assumir que uma única leitura receberá a mensagem inteira.

O protocolo de streams dos itens 1 e 2 possui **seu próprio formato binário**, diferente do formato JSON do item 3. Um receptor tem que usar o mesmo protocolo que o remetente usou.

## 5. Modelos e serviços: o que cada pasta faz?

### `models/` — objetos de dados

- `PecaDeRoupa` representa os dados comuns de uma peça.
- `Camiseta`, `Calca`, `Vestido`, `Jaqueta` e `Acessorio` especializam a peça e acrescentam seu detalhe específico.
- `Loja` mantém a coleção de peças.
- `Venda` representa o registro de uma venda.
- `exemplo.py` cria dados iniciais usados nas demonstrações.

O enunciado pede pelo menos duas classes de dados do serviço escolhido. Essas classes são os objetos que o serviço manipula e transmite.

### `services/` — operações e regras de negócio

- `EstoqueService` concentra operações sobre as peças e o estoque.
- `VendasService` realiza vendas e calcula os totais.
- `vendas.py` define a abstração/interface de vendas.
- `erros.py` contém erros usados para representar situações inválidas do domínio.

Separar modelos e serviços evita misturar os dados de uma peça com regras como verificar estoque suficiente ou registrar uma venda.

## 6. Itens 1 e 2 — Streams

### 6.1 `streams/loja_output_stream.py`

`LojaOutputStream` codifica um conjunto de peças no formato binário definido pelo projeto e escreve os bytes no destino recebido pelo construtor. O construtor recebe:

1. o stream de destino;
2. a sequência de peças;
3. a quantidade de peças a enviar.

O método `enviar()` escreve o cabeçalho com a quantidade e os campos de cada peça. Os campos de texto são codificados em UTF-8 e precedidos pelo tamanho em bytes; os campos numéricos têm representação binária definida pelo protocolo.

### 6.2 `streams/loja_input_stream.py`

`LojaInputStream` lê o formato binário produzido pelo `LojaOutputStream`. Ele lê a quantidade de peças, lê os campos de cada uma na mesma ordem e reconstrói a subclasse correta. O método `_ler_exato(n)` continua lendo até obter `n` bytes; se a origem terminar antes, sinaliza fim inesperado do fluxo.

**Regra essencial:** a ordem e o formato de leitura têm que corresponder exatamente à ordem e ao formato de escrita.

### 6.3 Por que existem seis arquivos em `demos_stream/`?

Esses arquivos são **programas de demonstração**, não seis implementações diferentes do stream. Cada um conecta a implementação comum a uma origem ou destino específico, como exige o enunciado.

| Arquivo | Requisito | Função |
|---|---|---|
| `q1b.py` | 1-b | escreve as peças na saída padrão; no terminal, exibe os bytes em hexadecimal para que sejam legíveis |
| `q1c.py` | 1-c | escreve as peças em `dados/pecas.bin` |
| `q1d.py` | 1-d | conecta-se ao servidor TCP e envia as peças |
| `q2b.py` | 2-b | lê peças da entrada padrão |
| `q2c.py` | 2-c | lê as peças de `dados/pecas.bin` |
| `q2d.py` | 2-d | atua como servidor TCP e lê as peças enviadas pelo cliente |

Os sufixos `b`, `c` e `d` correspondem às alíneas do enunciado. Os programas de demonstração tornam possível testar a mesma lógica com diferentes fontes e destinos sem alterar as classes de stream.

### 6.4 Testes dos itens 1 e 2

Execute a partir da raiz do projeto.

**Teste 1-b — enviar para a saída padrão:**

```bash
python3 -m demos_stream.q1b
```

No terminal, os bytes são apresentados em hexadecimal para facilitar a inspeção. Quando a saída é redirecionada para outro programa, o script escreve bytes reais.

**Teste combinado 1-b + 2-b — conectar saída padrão à entrada padrão por um pipe:**

```bash
python3 -m demos_stream.q1b | python3 -m demos_stream.q2b
```

O resultado esperado é a reconstrução e exibição das cinco peças de exemplo.

**Teste 1-c — gravar arquivo:**

```bash
python3 -m demos_stream.q1c
```

Esse comando cria `dados/pecas.bin`.

**Teste 2-c — ler o arquivo:**

```bash
python3 -m demos_stream.q2c
```

Execute `q1c` antes de `q2c`.

**Variação do item 2-b — redirecionar o arquivo para a entrada padrão:**

```bash
python3 -m demos_stream.q2b < dados/pecas.bin
```

**Teste 1-d + 2-d — TCP, em dois terminais:**

Terminal 1, servidor que recebe:

```bash
python3 -m demos_stream.q2d
```

Terminal 2, cliente que envia:

```bash
python3 -m demos_stream.q1d
```

O servidor deve mostrar as cinco peças recebidas. Por padrão, esse par usa a porta `5051`. O servidor de streams espera o formato binário de `LojaOutputStream`; ele **não** interpreta as mensagens JSON da questão 3.

## 7. Item 3 — Cliente-servidor com serialização

### 7.1 Por que `serialization/` é separado de `demos_stream/`?

O item 3 pede outra interação. Nos itens 1 e 2, o objetivo é demonstrar leitura e escrita de um conjunto de objetos num fluxo. No item 3, o cliente envia uma **requisição de operação**, o servidor executa a operação da loja e retorna uma **resposta**.

Por isso, a pasta `serialization/` possui um protocolo próprio, um cliente e um servidor próprios:

- `client.py`: monta e envia requisições; recebe respostas e transforma resultados em objetos.
- `server.py`: recebe requisições, chama os serviços da loja e devolve respostas.
- `protocolo.py`: define como transformar mensagens em bytes e como transmiti-las por TCP.

A pasta `services/` não é um segundo servidor de rede. Ela contém a lógica de negócio usada pelo servidor de serialização. O arquivo `serialization/server.py` é que aceita conexões TCP e chama esses serviços.

### 7.2 Formato das mensagens

Uma requisição tem uma operação e seus argumentos:

```json
{
  "operacao": "VENDER_PECA",
  "argumentos": {
    "codigo": 6,
    "quantidade": 2
  }
}
```

Uma resposta de sucesso usa `status` e `resultado`:

```json
{
  "status": "OK",
  "resultado": {
    "codigo": 1,
    "codigo_peca": 6,
    "quantidade": 2
  }
}
```

Uma resposta de erro usa `status` e `mensagem`:

```json
{
  "status": "ERRO",
  "mensagem": "Estoque insuficiente"
}
```

Os exemplos acima são ilustrativos; os campos exatos de `resultado` dependem do objeto devolvido pela operação.

### 7.3 Caminho completo de uma chamada

1. O cliente cria um dicionário com `operacao` e `argumentos`.
2. `empacotar()` transforma o dicionário em JSON codificado como bytes UTF-8.
3. `enviar()` acrescenta o cabeçalho de tamanho e transmite os bytes por TCP.
4. O servidor usa `receber()` para ler uma mensagem completa e desempacotá-la.
5. O servidor chama `EstoqueService` ou `VendasService` para executar a operação.
6. O servidor empacota a resposta e a envia.
7. O cliente recebe e desempacota a resposta e, quando necessário, reconstrói um objeto `PecaDeRoupa` ou `Venda`.

Essa sequência atende às quatro responsabilidades de empacotamento/desempacotamento exigidas na alínea 3-a: request do cliente, request no servidor, reply do servidor e reply no cliente.

### 7.4 Operações disponíveis

| Operação | O que faz |
|---|---|
| `LISTAR_PECAS` | retorna as peças cadastradas |
| `ADICIONAR_PECA` | envia uma peça serializada e adiciona-a ao estoque |
| `VENDER_PECA` | tenta vender a quantidade solicitada |
| `TOTAL_VENDAS` | retorna a quantidade de vendas e o total vendido |

### 7.5 Como testar o item 3

Abra dois terminais na raiz do projeto.

**Terminal 1 — iniciar o servidor de serialização (porta padrão `5050`):**

```bash
python3 -m serialization.server
```

**Terminal 2 — demonstração automática:**

```bash
python3 -m serialization.client --demo
```

O modo `--demo` lista peças, adiciona uma camiseta, tenta vender unidades, demonstra uma venda inválida por falta de estoque e consulta o total de vendas.

Para abrir o menu interativo:

```bash
python3 -m serialization.client
```

O servidor de serialização usa a porta `5050` por padrão; o servidor das demonstrações de streams usa `5051`. São servidores distintos, pois recebem protocolos diferentes.

O servidor de serialização atende clientes em threads separadas. Uma trava (`threading.Lock`) protege operações que modificam o estoque, evitando que duas requisições concorrentes alterem esse estado ao mesmo tempo.

## 8. Problemas comuns

| Sintoma | Possível causa e solução |
|---|---|
| `ModuleNotFoundError` | Confira se está na raiz `trabalho_01/` e use os nomes reais dos pacotes. |
| `python -m demos_stream.q1b.py` falha | Com `-m`, não se usa `.py`: execute `python3 -m demos_stream.q1b`. |
| `ConnectionRefusedError` | O servidor correspondente não está rodando ou o endereço/porta não corresponde. |
| `Address already in use` | Já existe um processo usando a porta; encerre-o ou escolha outra porta. |
| `Falha ao receber: O fluxo terminou antes de chegarem todos os bytes esperados` | O receptor pode estar lendo um protocolo diferente do enviado, ou a conexão foi fechada antes do envio completo. Use `q1d` com `q2d` para o protocolo binário de streams; use `serialization.client` com `serialization.server` para o protocolo JSON. |
| `q2b` parece ficar parado | Está aguardando bytes na entrada padrão; use o pipe ou o redirecionamento de arquivo. |
| `dados/pecas.bin` não existe | Execute primeiro `python3 -m demos_stream.q1c`. |
| A demonstração de serialização acusa código duplicado | O servidor mantém o estado em memória durante sua execução. Reinicie o servidor para voltar aos dados iniciais. |

## 9. Roteiro de demonstração

1. Mostre `models/peca_de_roupa.py` e `models/venda.py`: os objetos de domínio.
2. Mostre `streams/loja_output_stream.py` e `streams/loja_input_stream.py`: como os bytes são escritos e lidos.
3. Execute `q1b | q2b`: demonstração de saída padrão ligada à entrada padrão.
4. Execute `q1c` e `q2c`: demonstração com arquivo.
5. Execute `q2d` e `q1d` em dois terminais: demonstração dos streams por TCP.
6. Execute `serialization.server` e `serialization.client --demo`: mostre request, reply, JSON e reconstrução de objetos.
7. Explique que são protocolos separados e que o servidor correto precisa corresponder ao cliente usado.

## 10. Relação com o enunciado e limites

| Requisito do documento | Onde demonstrar |
|---|---|
| Pelo menos duas classes de dados e duas classes de serviço | `models/` e `services/` |
| Item 1-a: destino, conjunto e quantidade no construtor do stream de saída | `streams/loja_output_stream.py` |
| Item 1-b: saída padrão | `demos_stream/q1b.py` |
| Item 1-c: arquivo | `demos_stream/q1c.py` |
| Item 1-d: servidor remoto TCP | `demos_stream/q1d.py` com `demos_stream/q2d.py` |
| Item 2-a: origem no construtor do stream de entrada | `streams/loja_input_stream.py` |
| Item 2-b: entrada padrão | `demos_stream/q2b.py` |
| Item 2-c: arquivo | `demos_stream/q2c.py` |
| Item 2-d: cliente remoto TCP | `demos_stream/q2d.py` com `demos_stream/q1d.py` |
| Item 3: serialização e comunicação cliente-servidor por sockets | `serialization/client.py`, `serialization/server.py`, `serialization/protocolo.py` |
| Item 3-a: request/reply empacotados e desempacotados nos dois lados | `serialization/protocolo.py`, `client.py` e `server.py` |

A documentação e os comandos descrevem como executar os testes manuais; para confirmar o funcionamento no ambiente de entrega, execute cada teste e registre as saídas observadas. Este repositório não implementa o item 4 de multicast nem a questão extra de votação.

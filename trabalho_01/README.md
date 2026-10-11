# Sistema de Gestão de Loja de Roupas — Trabalho 1 de Sistemas Distribuídos

## 1. Objetivo do projeto

O serviço remoto escolhido é um sistema simples de gestão de uma loja de roupas. O projeto demonstra os mecanismos de comunicação entre processos do Capítulo 4:

- **Itens 1 e 2 — Streams:** escrever e ler uma sequência binária de peças usando destinos/origens diferentes: saída/entrada padrão, arquivo e TCP.
- **Item 3 — Serialização:** um cliente envia pedidos de operações para um servidor TCP. As mensagens são codificadas em JSON, processadas pelo servidor e respondidas ao cliente.
- **Item 4 — Multicast:** clientes se autenticam por TCP e passam a receber, por UDP multicast (grupo `230.0.0.1`), notificações, alertas e atualizações de estoque da loja em tempo real.
- **Questão extra — Votação:** sistema de votação distribuído com prazo, eleitores e administradores; login, candidatos e votos por TCP, notas informativas por multicast.

Cada item tem sua pasta (`demos_stream/`, `serialization/`, `multicast/`, `votacao/`) porque usa um protocolo próprio. Há também uma suíte de testes automatizados em `tests/`.

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
│   ├── erros.py               # LojaError: erros de negócio
│   ├── estoque_service.py     # operações de estoque
│   ├── vendas.py              # interface/abstração de vendas
│   └── vendas_service.py      # operações de venda
├── streams/
│   ├── loja_output_stream.py  # escrita do formato binário (item 1)
│   └── loja_input_stream.py   # leitura do formato binário (item 2)
├── demos_stream/
│   ├── q1b.py / q1c.py / q1d.py   # item 1: saída padrão, arquivo, TCP
│   └── q2b.py / q2c.py / q2d.py   # item 2: entrada padrão, arquivo, TCP
├── serialization/
│   ├── protocolo.py           # JSON, enquadramento e envio/recebimento
│   ├── servidor_base.py       # servidor request/reply multithread (itens 3, 4 e extra)
│   ├── cliente_base.py        # cliente request/reply (itens 3, 4 e extra)
│   ├── client.py              # cliente da questão 3
│   └── server.py              # servidor da questão 3
├── multicast/                 # item 4
│   ├── grupo.py               # joinGroup / leaveGroup / sockets multicast
│   ├── mensagens.py           # formato JSON: tipo, mensagem, timestamp, seq
│   ├── servidor.py            # autenticação TCP + envio multicast concorrente
│   ├── cliente.py             # thread de escuta + thread de interação
│   └── demo.py                # demonstração automática com 3 clientes
├── votacao/                   # questão extra
│   ├── modelo.py              # Candidato, Urna (prazo, votos, apuração)
│   ├── servidor.py            # servidor TCP multithread + notas por multicast
│   ├── cliente.py             # cliente eleitor/administrador
│   └── demo.py                # demonstração automática
└── tests/                     # testes automatizados (unittest)
```

## 4. Conceitos fundamentais do Capítulo 4

### 4.1 Processos, mensagens e comunicação

Um **processo** é um programa em execução. Neste projeto, os clientes e os servidores são processos diferentes. Eles precisam combinar como estabelecer a comunicação e como interpretar os bytes que trocam.

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

O laço "aceitar conexão → uma thread por cliente → receber request → executar → enviar reply" está em `serialization/servidor_base.py` (classe `ServidorTCP`), e o lado cliente em `serialization/cliente_base.py` (classe `ClienteTCP`). Os servidores dos itens 3, 4 e da questão extra herdam dessas classes e implementam apenas as suas operações.

## 8. Item 4 — Multicast

### 8.1 Arquitetura

```text
                 (1) AUTENTICAR usuario/senha  ── TCP unicast, porta 5060 ──►
  Cliente  ◄── (2) token + grupo 230.0.0.1 + porta 5007 ──────────────────────  Servidor
     │
     │ (3) joinGroup(230.0.0.1)
     ▼
  ◄════ (4) NOTIFICACAO / ALERTA / ATUALIZACAO ══ UDP multicast 230.0.0.1:5007 ═══ Servidor
```

- O **TCP** (unicast) é usado só para a autenticação: o servidor confere usuário e senha e só então informa o grupo e a porta multicast. A troca usa o mesmo protocolo request/reply do item 3.
- O **UDP multicast** entrega cada datagrama, de uma vez, a todos os processos que entraram no grupo. O endereço `230.0.0.1` é de classe D (224.0.0.0 a 239.255.255.255) e a porta `5007` é fixa. O TTL padrão é 1, ou seja, os datagramas não saem da rede local.
- **joinGroup / leaveGroup:** em Python são as opções de socket `IP_ADD_MEMBERSHIP` e `IP_DROP_MEMBERSHIP` (`multicast/grupo.py`). Depois de `leaveGroup`, o cliente deixa de receber as mensagens, mesmo que outros clientes da mesma máquina continuem no grupo.

### 8.2 Formato das mensagens (JSON, um datagrama por mensagem)

```json
{
  "tipo": "ALERTA",
  "mensagem": "Estoque baixo de 'Jaqueta de Couro': 2 unidade(s)",
  "timestamp": 1791744000,
  "seq": 7
}
```

`tipo` é `NOTIFICACAO`, `ALERTA` ou `ATUALIZACAO`. O campo `seq` foi acrescentado ao formato sugerido para mostrar a ordem de envio. Como o envio é concorrente, os números podem chegar fora de ordem, e o UDP não garante entrega. Diferentemente do TCP, não é preciso cabeçalho de tamanho: cada `recvfrom()` devolve exatamente um datagrama.

### 8.3 Threads

| Lado | Thread | Função |
|---|---|---|
| Servidor | `accept` + uma por conexão | autenticação TCP |
| Servidor | `simulacao-loja` | simula vendas e reposições usando `EstoqueService`/`VendasService` e publica `ATUALIZACAO` e `ALERTA` (estoque baixo/esgotado) |
| Servidor | pool `envio_0..3` | publicações assíncronas (`publicar_async`) e rajadas concorrentes (`rajada N`) |
| Servidor | principal | console do administrador: publica mensagens digitadas |
| Cliente | `escuta-multicast` | bloqueia em `recvfrom()` e exibe cada mensagem assim que chega |
| Cliente | `interacao-usuario` | lê comandos: `sair` (leaveGroup), `entrar` (joinGroup), `historico`, `status`, `fim` |

Várias threads do servidor chamam `publicar()` ao mesmo tempo; o contador de sequência é protegido por uma trava.

### 8.4 Como testar

**Demonstração automática** (servidor + 3 clientes simultâneos, leave/join e rajada concorrente):

```bash
python3 -m multicast.demo
```

**Manual, em vários terminais:**

```bash
# Terminal 1 — servidor (console do administrador + simulação da loja a cada 5 s)
python3 -m multicast.servidor

# Terminais 2, 3, 4... — um cliente por terminal
python3 -m multicast.cliente --usuario ana --senha 123
python3 -m multicast.cliente --usuario bruno --senha 123
python3 -m multicast.cliente --usuario carla --senha 123 --auto 60   # só escuta por 60 s
```

Usuários: `ana`, `bruno`, `carla`, `davi` (senha `123`) e `admin` (senha `admin`).

No console do servidor: `n <texto>` (NOTIFICACAO), `a <texto>` (ALERTA), `u <texto>` (ATUALIZACAO), `rajada 10` (10 mensagens concorrentes), `clientes`, `sair`. Para desligar a simulação automática, use `--intervalo 0`.

**Em máquinas diferentes da mesma rede:** rode o cliente com `--host IP_DO_SERVIDOR`. Se a máquina tiver várias interfaces, informe a interface com `--interface IP_LOCAL` no cliente e no servidor.

## 9. Questão extra — Sistema de votação

### 9.1 Funcionamento

- O servidor (`votacao/servidor.py`) abre a votação com um **prazo** (`--duracao`, em segundos). Um `threading.Timer` encerra a urna no fim do prazo; depois disso o servidor recusa votos e alterações de candidatos e calcula **total de votos, percentuais e vencedor** (ou empate).
- O **eleitor** faz login e recebe, na resposta, a lista de candidatos, o tempo restante e o grupo multicast. Cada eleitor vota uma única vez. O resultado só fica disponível para ele depois do prazo.
- O **administrador** adiciona e remove candidatos, envia **notas informativas** e pode consultar a apuração parcial. Se um candidato é removido, os votos dele são anulados e esses eleitores podem votar de novo.
- **Comunicação:** login, lista de candidatos, votos e demais operações vão por **TCP unicast** (porta `6000`), com servidor **multithread** (uma thread por cliente) e uma trava na urna. O **UDP multicast** (`230.0.0.2:6001`) é usado **exclusivamente** para as notas dos administradores.
- **Representação externa de dados:** JSON com cabeçalho de tamanho (o mesmo `protocolo.py` do item 3). O enunciado sugere protocol buffers, mas aceita JSON. Com JSON o projeto continua usando só a biblioteca padrão.

| Operação | Quem | Argumentos |
|---|---|---|
| `LOGIN` | todos | `usuario`, `senha` |
| `LISTAR_CANDIDATOS`, `STATUS`, `LOGOUT` | todos | `token` |
| `VOTAR` | eleitor | `token`, `numero` |
| `RESULTADO` | eleitor (após o prazo) / admin (parcial a qualquer momento) | `token` |
| `ADICIONAR_CANDIDATO` | admin | `token`, `nome`, `partido`, `numero` (opcional) |
| `REMOVER_CANDIDATO` | admin | `token`, `numero` |
| `ENVIAR_NOTA` | admin | `token`, `texto` → enviada por multicast |

Cada cliente tem uma thread `escuta-notas` (multicast) e uma thread `interacao-usuario` (menu).

### 9.2 Como testar

**Demonstração automática** (prazo de 4 s, 5 eleitores votando em paralelo, erros esperados e resultado final):

```bash
python3 -m votacao.demo
```

**Manual:**

```bash
# Terminal 1 — servidor com 2 minutos de votação
python3 -m votacao.servidor --duracao 120

# Terminal 2 — administrador
python3 -m votacao.cliente --usuario admin --senha admin

# Terminais 3, 4... — eleitores (eleitor1 até eleitor10, senha 123)
python3 -m votacao.cliente --usuario eleitor1 --senha 123
```

Use `--verboso` no cliente para ver as mensagens empacotadas e desempacotadas.

## 10. Testes automatizados

```bash
python3 -m unittest discover -s tests -t . -v
```

| Arquivo | O que verifica |
|---|---|
| `tests/test_streams.py` | ida e volta do formato binário, envio parcial (`quantidade`), quantidade inválida, fluxo truncado, TCP e pipe `q1b \| q2b` |
| `tests/test_serializacao.py` | empacotamento JSON, mensagem TCP fragmentada, fluxo cliente-servidor, erros de negócio, vendas concorrentes sem vender além do estoque |
| `tests/test_multicast.py` | formato das mensagens, endereço classe D, autenticação recusada, 3 clientes recebendo ao mesmo tempo, leaveGroup/joinGroup, rajada concorrente |
| `tests/test_votacao.py` | apuração (percentuais, vencedor, empate, sem votos), voto duplicado, prazo, remoção de candidato, fluxo completo via rede com nota multicast |

## 11. Problemas comuns

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
| Cliente multicast autentica mas não recebe nada | Firewall bloqueando UDP, rede sem suporte a multicast (algumas redes Wi-Fi) ou interface errada: tente `--interface IP_LOCAL` no cliente e no servidor. Na mesma máquina, tudo funciona pela interface local. |
| Votação recusa votos logo no início | O prazo (`--duracao`) já terminou; reinicie o servidor com um prazo maior. |

## 12. Roteiro de demonstração

1. Mostre `models/peca_de_roupa.py` e `models/venda.py` (objetos de domínio) e `services/` (regras de negócio).
2. Mostre `streams/loja_output_stream.py` e `streams/loja_input_stream.py`: como os bytes são escritos e lidos.
3. Execute `q1b | q2b`, depois `q1c` e `q2c`, depois `q2d` e `q1d` em dois terminais.
4. Execute `serialization.server` e `serialization.client --demo`: mostre request, reply, JSON e reconstrução de objetos.
5. Execute `multicast.servidor` e três `multicast.cliente`; envie mensagens pelo console, faça `sair`/`entrar` em um cliente e uma `rajada 10`.
6. Execute `votacao.servidor --duracao 90`, um admin e dois eleitores: adicione um candidato, envie uma nota, vote, tente votar duas vezes e mostre o resultado após o prazo.
7. Rode `python3 -m unittest discover -s tests -t .` para mostrar os testes automatizados.

## 13. Relação com o enunciado

| Requisito do documento | Onde demonstrar |
|---|---|
| Pelo menos duas classes de dados e duas classes de serviço | `models/` (`PecaDeRoupa` e subclasses, `Loja`, `Venda`) e `services/` (`EstoqueService`, `VendasService`) |
| Item 1-a: destino, conjunto e quantidade no construtor do stream de saída | `streams/loja_output_stream.py` |
| Item 1-b / 1-c / 1-d: saída padrão, arquivo, servidor TCP | `demos_stream/q1b.py`, `q1c.py`, `q1d.py` (com `q2d.py`) |
| Item 2-a: origem no construtor do stream de entrada | `streams/loja_input_stream.py` |
| Item 2-b / 2-c / 2-d: entrada padrão, arquivo, cliente TCP | `demos_stream/q2b.py`, `q2c.py`, `q2d.py` (com `q1d.py`) |
| Item 3 e 3-a: serialização, request/reply empacotados e desempacotados nos dois lados | `serialization/protocolo.py`, `client.py`, `server.py` |
| Item 4-a: grupo classe D com porta fixa, joinGroup/leaveGroup | `multicast/grupo.py`, comandos `entrar`/`sair` do cliente |
| Item 4-b: NOTIFICACAO, ALERTA e ATUALIZACAO em JSON | `multicast/mensagens.py`, `multicast/servidor.py` |
| Item 4-c: múltiplos clientes recebendo simultaneamente | `multicast/demo.py`, vários `multicast.cliente` |
| Item 4-d: thread de escuta + thread de interação; servidor multithread | `multicast/cliente.py`, `multicast/servidor.py` (seção 8.3) |
| Item 4-e: TCP para autenticação, UDP multicast para mensagens | `multicast/servidor.py` (`AUTENTICAR`) e `publicar()` |
| Extra: login, candidatos e votos via TCP; prazo; apuração; admin; notas via multicast; servidor multithread; JSON | `votacao/` (seção 9) |
| Testes | `tests/` (seção 10) |
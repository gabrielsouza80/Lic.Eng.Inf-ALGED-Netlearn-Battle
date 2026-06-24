# NetLearn Battle

NetLearn Battle é um jogo educativo sobre Redes de Computadores. A interface principal é uma página web criada com Flask. O aluno cria conta, escolhe um nível e joga **sessões de 5 perguntas**; no fim vê o resumo, o histórico, as estatísticas e o ranking. Há ainda um **modo treino** (repetir perguntas erradas), uma **área de professor** e uma **versão TCP** (servidor + cliente) que joga uma sessão completa por sockets.

O projeto é académico e fácil de defender oralmente. Não usa base de dados: todos os dados ficam em ficheiros JSON. Usa apenas Python padrão (incluindo a biblioteca `ipaddress`) e Flask; não usa React, Django, Bootstrap, Tailwind nem JavaScript complexo.

## Como executar a versão web

É necessário Python 3.10 ou superior.

```bash
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000` no navegador. Opcionalmente pode definir `FLASK_SECRET_KEY`; sem essa variável é gerada uma chave temporária segura.

## Níveis e motores de cálculo

As perguntas combinam **perguntas fixas** (JSON) com **perguntas geradas automaticamente**. Em cada sessão usam-se no máximo 2 perguntas fixas e o resto é gerado, para haver variedade.

| Nível | Tema | Motor | Certa | Errada |
| --- | --- | --- | ---: | ---: |
| 1 | IPv4 básico (/8, /16, /24) | `services/ip_service.py` | +10 | -5 |
| 2 | Sub-redes IPv4 (/25../27) | `services/ip_service.py` | +20 | -10 |
| 3 | Super-redes IPv4 (/21../23) | `services/ip_service.py` | +30 | -15 |
| 4 | IPv6 simples | `services/ip_service.py` | +40 | -20 |
| 5 | ACLs (primeira correspondência) | `services/acl_service.py` | +50 | -25 |

- **IPv4/IPv6** (`ip_service.py`): calcula Network ID, broadcast/último endereço, "mesma rede?" e sub-redes, com a biblioteca padrão `ipaddress`. Gera perguntas de escolha múltipla com 4 opções e a posição da resposta certa ao acaso.
- **ACL** (`acl_service.py`): avalia regras por ordem e aplica a **primeira regra que faz match** (com *deny* implícito no fim). Tem 5 geradores: permit/deny, primeira regra, ordem das regras, ACE em falta e ACL para um servidor.

## Sessão de jogo, Queue e Stack

1. O aluno faz login e escolhe um nível (`POST /play`).
2. `GameService.build_session_questions` cria 5 perguntas (fixas + geradas).
3. As perguntas entram numa **Queue (FIFO)**: a primeira a entrar é a primeira a sair (`dequeue`).
4. Cada resposta (`POST /answer`) é corrigida **no servidor**, o score é atualizado e a próxima pergunta é retirada da Queue.
5. As tentativas da sessão são acumuladas numa **Stack (LIFO)** e, no fim, gravadas em `attempts.json` pela ordem cronológica correta.
6. É gravado um resumo da sessão em `sessions.json` (`session_id`, nível, certas, pontos, score final).

- **Queue** (`structures/queue.py`): organiza as perguntas. FIFO — *First In, First Out*.
- **Stack** (`structures/stack.py`): guarda as tentativas antes de persistir. LIFO — *Last In, First Out*.

## Modo treino

Em `/training` o aluno repete as perguntas onde falhou (reconstruídas a partir de `attempts.json` e colocadas numa Queue). O treino **não altera o score**, serve só para praticar.

## Estatísticas

As estatísticas do aluno (`/stats`) vêm de `attempts.json` e `sessions.json`: total, certas, erradas, taxa global, **taxa por nível**, **taxa por tipo de pergunta**, média/mediana/moda do tempo de resposta, tópico com mais erros e **evolução do score por sessão**.

## Área de professor

A rota `/teacher` é uma página simples de consulta (sem login de professor). Mostra estatísticas globais, taxa por nível e por tipo, **distribuição de scores por quartis** (Q1, Q2/mediana, Q3, mínimo, máximo), ranking Top 5 e tentativas recentes. Tem também um formulário que **gera o comando** para iniciar uma sessão TCP (não inicia o processo).

## Versão TCP (servidor e cliente)

A pasta `network/` contém um servidor e um cliente que jogam uma sessão completa por sockets TCP, trocando mensagens JSON (uma por linha). O **servidor é a autoridade**: valida sempre as respostas do seu lado e **nunca envia o índice da resposta correta** dentro da pergunta. Cada cliente tem a sua própria Queue de perguntas, tal como na web, e a sessão é persistida nos mesmos ficheiros JSON.

Protocolo (mensagem do cliente → resposta do servidor):

| Cliente | Servidor |
| --- | --- |
| `AUTH` | `AUTH_RESULT` |
| `START` | `QUESTION` ou `ERROR` |
| `ANSWER` | `ANSWER_RESULT` |
| `NEXT` | `QUESTION` ou `END` |
| `RANKING` | `RANKING` |
| `STATS` | `STATS` |
| (tipo desconhecido / JSON inválido) | `ERROR` |

O servidor é robusto a JSON malformado, tipos desconhecidos e *timeout* de inatividade. Para testar, abra dois terminais:

```bash
python network/server.py --host 127.0.0.1 --port 5001 --level 1 --questions 5
python network/client.py --host 127.0.0.1 --port 5001 --level 1
```

## Ficheiros JSON

Conteúdo do jogo (versionado no repositório):

- `data/questions.json`: perguntas fixas dos níveis 1 a 4.
- `data/acls.json`: ACLs, pacotes e perguntas fixas do nível 5.

Dados de execução (gerados pela app, ignorados pelo Git — use os `.example.json` como modelo):

- `data/users.json`: username, salt e hash SHA-256 da password (nunca em texto simples).
- `data/scores.json`: score atual de cada utilizador.
- `data/attempts.json`: histórico de respostas (tópico, tipo, opções, resposta dada/correta, pontos, tempo, score).
- `data/sessions.json`: resumo de cada sessão jogada.

No primeiro arranque, os ficheiros de execução são criados automaticamente vazios.

## Login

No registo, a aplicação cria um `salt` aleatório e guarda apenas o hash SHA-256 de `salt + password`. No login, recalcula o hash e compara-o com o valor guardado (`secrets.compare_digest`).

## Testes

### Testes Python (unittest)

```bash
python -m unittest discover -s tests/python -v
```

Verificam: Queue (FIFO) e Stack (LIFO); leitura/escrita de JSON; atualização de score; estatísticas; **motor IPv4/IPv6**; **motor ACL e primeira correspondência**; construção de sessões; e o **servidor TCP** (pergunta sem índice correto e erro para tipo desconhecido).

### Testes funcionais (Robot Framework)

Num terminal inicie `python app.py`; noutro execute:

```bash
robot tests/robot/web_tests.robot
```

Abrem o navegador (Chrome) e verificam páginas iniciais, login, registo, regras, ranking, professor/quartis e os redirecionamentos para login.

## Documentação adicional

A pasta `docs/` contém: `especificacao.md` (mapa dos requisitos), `relatorio.md` (relatório base), `poster.md` (conteúdo do poster) e `diagramas.md` (diagramas Mermaid de casos de uso e Gantt).

## Como explicar ao professor

Flask cria a interface web e não há base de dados — os dados ficam só em JSON. A `Queue` organiza as 5 perguntas da sessão e a `Stack` guarda as tentativas antes de as persistir. Níveis 1-4 usam o motor de IP (`ipaddress`) e o nível 5 usa o motor de ACL com primeira correspondência. As respostas são sempre validadas no servidor, tanto na web como na versão TCP. O score/ranking vêm de `scores.json`; histórico e estatísticas de `attempts.json`/`sessions.json`. O projeto é pequeno mas cobre autenticação, estruturas de dados, persistência, estatística (incl. quartis), redes (IPv4/IPv6/ACL e TCP) e uma interface web.

## Limitações e melhorias futuras

- A interface web é a principal; a versão TCP é funcional mas usada em terminal.
- A área de professor é pública (consulta académica), sem login dedicado.
- Não tem proteção CSRF nos formulários (projeto académico).
- Melhorias futuras: mais perguntas fixas, dificuldade adaptativa, login de professor e mais validações de segurança.

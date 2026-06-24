# NetLearn Battle

NetLearn Battle é um jogo educativo sobre Redes de Computadores. A interface principal é uma página web criada com Flask. O aluno cria conta, faz login, escolhe um nível, responde a uma sessão de perguntas e consulta o score, histórico, estatísticas e ranking.

O projeto foi pensado para ser fácil de entender e apresentar num contexto académico. Não usa base de dados: todos os dados são guardados em ficheiros JSON.

## Como executar a versão web

É necessário Python 3.10 ou superior.

```powershell
cd C:\Faculdade\Interdisciplinaryproject2
pip install -r requirements.txt
py -3 app.py
```

Abra `http://127.0.0.1:5000` no navegador.

Opcionalmente, pode definir `FLASK_SECRET_KEY` antes de iniciar a aplicação. Sem esta variável, é criada uma chave segura temporária.

## Ponto de entrada

Pode iniciar a aplicação com qualquer um destes comandos:

```powershell
python app.py
```

ou:

```powershell
python main.py
```

Ambos iniciam a aplicação web Flask.

## Ficheiros JSON

- `data/users.json`: username, salt e hash da password. A password nunca é guardada em texto simples.
- `data/scores.json`: score atual de cada utilizador.
- `data/attempts.json`: histórico das respostas, incluindo tópico, resposta escolhida, resposta correta, pontos e tempo.
- `data/questions.json`: perguntas fixas dos níveis 1 a 4.
- `data/acls.json`: perguntas fixas de ACL para o nível 5.

As perguntas vêm de JSON para manter o projeto simples, previsível e fácil de validar.

### Repor dados de utilização

Para apagar apenas as contas, pontuações e tentativas criadas durante os testes ou utilização, com a aplicação Flask parada, execute:

```powershell
python reset_data.py
```

Escreva `SIM` para confirmar. Este comando limpa `users.json`, `scores.json` e `attempts.json`. Não altera `questions.json` nem `acls.json`, porque esses ficheiros contêm as perguntas do jogo.

## Login

No registo, a aplicação cria um `salt` aleatório e guarda apenas o hash SHA-256 de `salt + password`. No login, calcula novamente o hash e compara-o com o valor guardado.

## Como funciona o jogo

1. O aluno faz login.
2. Escolhe um nível.
3. `GameService` lê as perguntas no JSON correto.
4. As perguntas são colocadas numa `Queue`.
5. A primeira pergunta é retirada com `dequeue()` e mostrada na página.
6. O aluno responde.
7. A tentativa é colocada numa `Stack`, retirada com `pop()` e guardada em `attempts.json`.
8. O score é atualizado em `scores.json`.

Os níveis 1 a 4 geram perguntas de Network ID, Broadcast, mesma rede e IPv6
usando a biblioteca `ipaddress`. Os endereços IPv4 são sorteados de redes
privadas variadas (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) para
evitar repetição. Cada sessão web cria uma Queue FIFO de cinco perguntas. O
modo treino reutiliza perguntas erradas guardadas no histórico.

O nível 5 usa regras e pacotes de `acls.json`: a ACL é avaliada por ordem e a
primeira regra compatível decide `permit` ou `deny`. Se nenhuma regra
corresponder, o comportamento padrão é `deny`.

### Queue

`Queue` organiza as perguntas. Usa FIFO: *First In, First Out*. A primeira pergunta colocada é a primeira pergunta retirada.

### Stack

`Stack` guarda uma tentativa antes de a persistir. Usa LIFO: *Last In, First Out*. A última tentativa colocada é a primeira a sair.

## IPv4

As perguntas de IPv4 usam a biblioteca `ipaddress` para calcular Network ID,
Broadcast e verificar se dois endereços pertencem à mesma rede. Os endereços
são gerados aleatoriamente dentro de redes privadas (`10.0.0.0/8`,
`172.16.0.0/12`, `192.168.0.0/16`). Os níveis definem o prefixo:

- Nível 1: /8, /16, /24
- Nível 2: /25, /26, /27
- Nível 3: /21, /22, /23

Para perguntas de "mesmo segmento", o sistema gera pares que às vezes
pertencem à mesma rede (resposta "Sim") e às vezes não (resposta "Não"),
garantindo variedade.

## IPv6

As perguntas de IPv6 usam endereços `2001:db8::/32` (documentação RFC 3849).
Incluem Network ID, verificação de mesma rede, contagem de sub-redes e a
particularidade de o IPv6 não possuir endereço de broadcast.

## ACL

As ACLs são avaliadas pela primeira regra compatível (first match). O sistema
percorre as regras por ordem e aplica a primeira que corresponde ao pacote. Se
nenhuma regra corresponder, o comportamento padrão é `deny`.

Os tipos de pergunta ACL são:

1. **permit/deny** — dada uma ACL e um pacote, identificar se permite ou bloqueia.
2. **primeira regra** — identificar a primeira regra que fez match.
3. **ordem correta** — dada uma lista de regras, escolher a ordem que produz o
   comportamento esperado.
4. **ACE em falta** — dada uma ACL incompleta, escolher a regra em falta.
5. **ACL para servidor** — dado um servidor e serviços ativos, escolher a ACL
   correta para permitir acesso externo.

## Pontuação

| Nível | Tema | Certa | Errada |
| --- | --- | ---: | ---: |
| 1 | IPv4 básico | +10 | -5 |
| 2 | Sub-redes IPv4 | +20 | -10 |
| 3 | Super-redes IPv4 | +30 | -15 |
| 4 | IPv6 simples | +40 | -20 |
| 5 | ACLs simples | +50 | -25 |

## Ranking e estatísticas

O ranking Top 5 é calculado a partir de `scores.json`, ordenado do maior score para o menor.

As estatísticas vêm de `attempts.json` e mostram total de perguntas, certas, erradas, taxa global e por nível, média, mediana, moda do tempo de resposta, tópico com mais erros e score atual.

## Área de professor

A rota `http://127.0.0.1:5000/teacher` é uma página pública e simples, sem autenticação de professor. Mostra:

- total de perguntas respondidas, certas e erradas;
- taxa global de acerto;
- taxa de acerto por nível;
- taxa de acerto por tipo de pergunta (network_id, broadcast, etc.);
- quartis de score (mínimo, Q1, Q2, Q3, máximo);
- ranking Top 5;
- tentativas recentes de todos os alunos.

Também gera um comando TCP com host e porta para o
professor copiar para o terminal.

## Demonstração TCP

A pasta `network/` contém `server.py` e `client.py`. É uma demonstração de comunicação cliente-servidor através de sockets TCP e mensagens JSON.

O servidor é a autoridade: valida sempre as respostas do seu lado, calcula pontos,
guarda a tentativa em `attempts.json`, atualiza `scores.json` e **nunca envia o
índice da resposta correta** dentro da pergunta.

No modo TCP, cada pergunta fica associada ao estado do cliente. Após
`ANSWER_SUBMIT`, a pergunta ativa é removida para impedir respostas repetidas
à mesma pergunta. Se o cliente tentar responder sem pergunta ativa, o servidor
devolve erro controlado.

### Mensagens oficiais do protocolo

| Cliente envia | Servidor responde | Descrição |
|---|---|---|
| `AUTH_REQUEST` | `AUTH_RESPONSE` | Autenticação do utilizador |
| `QUESTION_REQUEST` | `QUESTION_PUSH` | Pedido de pergunta (sem `correct_index`) |
| `ANSWER_SUBMIT` | `ANSWER_RESULT` | Submissão de resposta; inclui `is_correct`, `points`, `correct_answer` e `score` |
| `SCORE_UPDATE` | `SCORE_UPDATE` | Consulta separada do score atual |
| `RANKING_REQUEST` | `RANKING_RESPONSE` | Pedido de ranking |
| `STATS_REQUEST` | `STATS_RESPONSE` | Pedido de estatísticas |
| `END_SESSION` | `END_SESSION` | Fim de sessão |

### Exemplo de conversa TCP

```
Cliente → {"type": "AUTH_REQUEST", "username": "aluno1", "password": "1234"}
Servidor → {"type": "AUTH_RESPONSE", "success": true}

Cliente → {"type": "QUESTION_REQUEST", "level": 1}
Servidor → {"type": "QUESTION_PUSH", "question": {
              "question": "Qual é o Network ID de 192.168.1.10/24?",
              "options": ["192.168.1.0", "192.168.1.255", "192.168.0.0", "192.168.2.0"],
              "level": 1, "topic": "IPv4 básico"}}

Cliente → {"type": "ANSWER_SUBMIT", "selected_index": 0}
Servidor → {"type": "ANSWER_RESULT", "is_correct": true, "points": 10,
             "correct_answer": "192.168.1.0", "score": 40}

Cliente → {"type": "SCORE_UPDATE"}
Servidor → {"type": "SCORE_UPDATE", "score": 40}

Cliente → {"type": "END_SESSION"}
Servidor → {"type": "END_SESSION", "message": "Sessão terminada pelo cliente."}
```

A resposta `QUESTION_PUSH` nunca inclui `correct_index`, `points_correct` nem `points_wrong`. O servidor valida internamente a resposta do aluno, calcula os pontos conforme o nível e persiste a tentativa.

### Como executar

Para testar, abra dois terminais:

```powershell
python network/server.py
python network/client.py
```

```powershell
py -3 network/server.py --host 127.0.0.1 --port 5001
py -3 network/client.py --host 127.0.0.1 --port 5001
```

O Flask usa a porta `5000` e o TCP usa a porta `5001`, por isso podem funcionar ao mesmo tempo. Não é um jogo online completo e não está integrado com a interface web.

Na versão web, a sessão de jogo usa uma Queue com 5 perguntas. Na versão TCP,
existe uma demonstração cliente-servidor com autenticação, envio de pergunta,
resposta, atualização de score, ranking e estatísticas. A parametrização
completa de uma sessão TCP com várias perguntas por nível e quantidade fica
como melhoria futura.

## Testes

Os testes Python validam a lógica interna do projeto. Os testes Robot validam a interface web no navegador.

### Testes Python com unittest

```powershell
py -3 -m unittest discover -s tests/python -v
```

Estes testes verificam:

- Queue com comportamento FIFO;
- Stack com comportamento LIFO;
- registo, hash, salt e login;
- atualização de score e ordenação do ranking;
- estatísticas básicas (total, taxa global, quartis, taxa por tipo);
- leitura e escrita de JSON num ficheiro temporário;
- geração de perguntas IPv4/IPv6 para todos os níveis;
- mensagens oficiais do protocolo TCP (AUTH_REQUEST, QUESTION_REQUEST, etc.);
- ACL: permit/deny, primeira regra compatível, deny padrão;
- Network ID e broadcast IPv4, same_network com True e False;
- IPv6 Network ID e same_network.

Também existem testes para garantir que um score não numérico, uma tentativa
incompleta ou um JSON malformado não derrubam as páginas. Registos inválidos
simplesmente não entram nesses cálculos.

### Testes funcionais com Robot Framework

```powershell
robot --outputdir tests/robot/results tests/robot
```

Os resultados (`output.xml`, `log.html`, `report.html` e logs Flask) ficam em `tests/robot/results/`. No VS Code, a configuração do RobotCode também guarda os resultados nessa pasta.

Veja também `tests/robot/README.md`: explica a diferença entre o resumo (`report.html`) e os passos detalhados (`log.html`).

Os testes Robot validam registo, login, fluxo de jogo, sessão completa de
5 perguntas, persistência, ranking, estatísticas, área do professor e cenários
inválidos. `web_tests_e2e.robot` executa o fluxo completo: registo, login, os
cinco níveis e depois histórico, estatísticas, ranking, professor, regras e
logout. `web_tests_session.robot` valida uma sessão de 5 perguntas dentro do
mesmo nível, incluindo o botão "Próxima pergunta" e o resumo final. Os casos
inválidos abrem o seu próprio navegador e criam uma sessão própria quando
necessário. Por isso, os testes criam contas, scores e tentativas reais.

Na última validação, passaram 60 testes unitários e 9 testes Robot: 1 fluxo E2E,
6 validações inválidas, 1 teste de persistência e 1 teste de sessão completa.

Todas as suites Robot usam os ficheiros reais em `data/`. A conta usada no teste de persistência está definida em `tests/robot/test_credentials.json`: `gabrielsouza80` com password `808005`. O teste cria a conta se necessário, joga, termina sessão e entra novamente para confirmar persistência.

O teste de ranking verifica se existem pelo menos três jogadores com tentativas. Se não existirem, cria por registo os jogadores em falta, faz login em cada um e executa uma jogada. Depois compara a ordem mostrada no Top 5 com a ordem calculada a partir de `data/scores.json`. A suite inválida agrupa as validações sem login num único fluxo e, depois de um login único, valida submissão sem opção, índice de resposta inválido, resposta sem pergunta e nível inexistente.

Os testes Robot iniciam Flask automaticamente na porta `5002`, separada da aplicação normal na porta `5000`. O Chrome abre de forma visível para poder acompanhar a navegação. A velocidade visual é definida por `${VISUAL_SPEED}` em `resources/common.resource` e está em 100 milissegundos por ação. É necessário ter Google Chrome instalado. O Flask fica ativo durante cada suite, mas cada caso abre e fecha o seu próprio navegador antes de o próximo começar. Não clique em vários botões verdes nem execute duas suites em terminais diferentes ao mesmo tempo.

Se o Flask não iniciar, consulte `flask-error.log` na pasta de resultados do Robot para ver a causa.

No VS Code, o RobotCode pode usar um Python interno diferente. Por isso, o ficheiro Robot inicia Flask com `py -3`, que usa o Python normal do Windows onde foram instaladas as dependências do projeto. As suites Robot usam os JSON reais em `data/`, por isso cada execução cria registos, tentativas e scores reais.

Se aparecer um erro a indicar que a versão de `ChromeDriver` não é compatível com o Chrome, remova ou atualize o ChromeDriver antigo que estiver no `PATH`. O Selenium Manager descarrega automaticamente um driver compatível quando não encontra um driver manual antigo.

## Como explicar ao professor

O NetLearn Battle é uma aplicação educativa sobre redes de computadores,
desenvolvida em Python e Flask. O aluno cria conta, faz login, escolhe um
nível e responde a uma sessão de perguntas sobre IPv4, IPv6 e ACLs. Cada
resposta gera feedback imediato, altera o score e fica registada em JSON.
O projeto usa Queue para organizar perguntas, Stack para registar tentativas,
estatísticas para acompanhar desempenho e TCP para demonstrar comunicação
cliente-servidor com mensagens JSON.

## Limitações

- A aplicação web é a interface principal.
- A parte TCP é apenas demonstrativa e não está integrada no jogo web.
- A área de professor é pública e não tem autenticação específica.
- A aplicação é académica e não tem segurança profissional completa (ex.: CSRF).
- Os dados são guardados em JSON, sem gestão de concorrência para vários utilizadores.
- As perguntas de ACL para ordem, ACE em falta e servidor são geradas com opções fixas, sem variação dinâmica.

## Melhorias futuras

- Mais variedade de perguntas geradas dinamicamente.
- Integração entre o servidor TCP e o jogo web.
- Autenticação específica para a área do professor.
- Proteção CSRF nos formulários.
- Gestão de concorrência nos ficheiros JSON.

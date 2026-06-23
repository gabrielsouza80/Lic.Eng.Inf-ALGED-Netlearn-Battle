# NetLearn Battle

NetLearn Battle é um jogo educativo simples sobre Redes de Computadores. A aplicação principal é uma página web criada com Flask. O aluno cria uma conta, escolhe um nível, responde a uma pergunta e consulta o seu score, histórico, estatísticas e ranking.

O projeto foi pensado para ser fácil de entender e apresentar num contexto académico. Não usa base de dados: todos os dados são guardados em ficheiros JSON.

## Como executar a versão web

É necessário Python 3.10 ou superior.

```powershell
cd C:\Faculdade\Interdisciplinaryproject2
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000` no navegador.

Opcionalmente, pode definir `FLASK_SECRET_KEY` antes de iniciar a aplicação. Sem esta variável, é criada uma chave segura temporária.

## Versão terminal

`main.py` foi mantido apenas como indicação para a versão principal. Para executar o projeto, use `python app.py`.

## Ficheiros JSON

- `data/users.json`: username, salt e hash da password. A password nunca é guardada em texto simples.
- `data/scores.json`: score atual de cada utilizador.
- `data/attempts.json`: histórico das respostas, incluindo tópico, resposta escolhida, resposta correta, pontos e tempo.
- `data/questions.json`: perguntas fixas dos níveis 1 a 4.
- `data/acls.json`: perguntas fixas de ACL para o nível 5.

As perguntas vêm de JSON para manter o projeto simples, previsível e fácil de validar.

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

### Queue

`Queue` organiza as perguntas. Usa FIFO: *First In, First Out*. A primeira pergunta colocada é a primeira pergunta retirada.

### Stack

`Stack` guarda uma tentativa antes de a persistir. Usa LIFO: *Last In, First Out*. A última tentativa colocada é a primeira a sair.

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

A rota `http://127.0.0.1:5000/teacher` é uma página pública e simples, sem autenticação de professor. Mostra o ranking Top 5, total de perguntas respondidas por todos os alunos, taxa global, taxa por nível e tentativas recentes. Também recorda que a criação de ligação TCP está demonstrada em `network/server.py`.

## Demonstração TCP

A pasta `network/` contém `server.py` e `client.py`. É uma demonstração separada de comunicação cliente-servidor através de sockets TCP e mensagens JSON.

Mensagens demonstradas: `AUTH_REQUEST`, `AUTH_RESPONSE`, `QUESTION_REQUEST`, `QUESTION_PUSH`, `ANSWER_SUBMIT`, `ANSWER_RESULT` e `SCORE_UPDATE`.

Para testar, abra dois terminais:

```powershell
python network/server.py
python network/client.py
```

Não é um jogo online completo e não está integrado com a interface web.

## Testes

Os testes Python validam a lógica interna do projeto. Os testes Robot validam a interface web no navegador.

### Testes Python com unittest

```powershell
python -m unittest discover -s tests/python -v
```

Estes testes verificam:

- Queue com comportamento FIFO;
- Stack com comportamento LIFO;
- atualização de score;
- estatísticas básicas;
- leitura e escrita de JSON num ficheiro temporário.

### Testes funcionais com Robot Framework

Primeiro, inicie a aplicação web num terminal:

```powershell
python app.py
```

Noutro terminal, execute:

```powershell
robot tests/robot/web_tests.robot
```

Os testes Robot abrem o navegador e verificam a página inicial, login, registo, regras, ranking e o redirecionamento do dashboard quando não existe login. É necessário ter Google Chrome instalado.

## Como explicar ao professor

Flask cria a interface web, mas não guarda dados numa base de dados. Os dados ficam apenas em JSON. A `Queue` organiza as perguntas e a `Stack` guarda uma tentativa antes de a persistir. O score e o ranking vêm de `scores.json`; o histórico e as estatísticas vêm de `attempts.json`. A pasta `network/` contém uma demonstração simples de TCP com JSON. O projeto é pequeno, mas cobre autenticação, estruturas de dados, persistência, estatística, redes e uma interface web.

## Limitações e melhorias futuras

- A aplicação web é a interface principal.
- A parte TCP é apenas demonstrativa e não está integrada no jogo web.
- A área de professor é pública e apenas serve para consulta académica.
- As perguntas são fixas e carregadas de JSON.
- A aplicação é académica e não tem segurança profissional completa, por exemplo proteção CSRF nos formulários.
- Melhorias futuras: mais perguntas, perguntas aleatórias, melhor gestão de sessões e mais validações de segurança.

# Mini-especificação — NetLearn Battle

**Autor:** Gabriel Souza  
**Modalidade:** trabalho individual

## Objetivo
Jogo educativo web sobre IPv4, IPv6 e ACLs, com autenticação, pontuação e persistência JSON.

## Menus
Visitante: início, login, registo, ranking e regras. Aluno: dashboard, jogar, treino, histórico e estatísticas. Professor: estatísticas globais e comando TCP.

## Estrutura
`app.py` apresenta Flask; `services/` contém regras; `structures/` contém Queue e Stack; `data/` guarda JSON; `network/` demonstra TCP; `tests/` valida o projeto.

## Plano de testes
Validar registo/login, páginas protegidas, cinco níveis, pontuação, Queue, Stack, histórico, estatísticas, ranking, treino e mensagens TCP.

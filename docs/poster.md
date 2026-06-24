# Poster — NetLearn Battle

Conteúdo sugerido para o poster do Projeto Integrador (texto base; adaptar ao layout gráfico).

## Título

**NetLearn Battle — aprender Redes a jogar**

## Subtítulo

Jogo educativo de IPv4, IPv6 e ACLs, com interface web (Flask) e versão TCP, sem base de dados.

## O problema

Aprender endereçamento IP e ACLs é abstrato. Faltam ferramentas simples para praticar com correção imediata.

## A solução

Um jogo por níveis (1 a 5) com sessões de 5 perguntas, correção no servidor, score, ranking, estatísticas e modo treino.

## Como funciona (4 passos)

1. Login do aluno.
2. Escolhe o nível.
3. Responde a 5 perguntas (Queue FIFO).
4. Vê o resumo; as tentativas são guardadas (Stack LIFO) em JSON.

## Tecnologias

- Python padrão + Flask
- Biblioteca `ipaddress` (IPv4/IPv6)
- Estruturas Queue e Stack
- Persistência em JSON (sem base de dados)
- Sockets TCP + JSON (versão cliente-servidor)
- Testes: unittest + Robot Framework

## Destaques técnicos

- Motor real de IPv4/IPv6 (Network ID, broadcast, sub-redes).
- Motor de ACL com **primeira correspondência** e *deny* implícito.
- Servidor (web e TCP) valida sempre as respostas e nunca envia a solução.
- Estatísticas com taxa por nível/tipo, tempos e **quartis** de score.

## Resultados

Projeto pequeno e didático que cobre autenticação, estruturas de dados, persistência, cálculo de redes, estatística e redes TCP.

## Equipa / Unidade curricular

Licenciatura em Engenharia Informática — ALGED / Projeto Integrador.

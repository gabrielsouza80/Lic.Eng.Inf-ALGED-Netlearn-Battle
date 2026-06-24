# Relatório base — NetLearn Battle

Relatório base para a defesa do Projeto Integrador. Pode ser copiado e adaptado.

## 1. Introdução

O NetLearn Battle é um jogo educativo sobre Redes de Computadores. O objetivo é ajudar os alunos a praticar endereçamento IPv4, IPv6 e listas de controlo de acesso (ACL) de forma interativa, respondendo a perguntas organizadas por níveis de dificuldade.

## 2. Objetivos

- Criar uma aplicação web simples com autenticação.
- Aplicar as estruturas de dados Queue (FIFO) e Stack (LIFO).
- Guardar todos os dados em ficheiros JSON, sem base de dados.
- Implementar motores de cálculo reais de IPv4, IPv6 e ACL.
- Disponibilizar estatísticas para o aluno e para o professor.
- Demonstrar comunicação cliente-servidor por TCP com mensagens JSON.

## 3. Arquitetura

- **Interface web**: Flask (`app.py` + `templates/` + `static/`).
- **Serviços** (`services/`): autenticação, jogo, IP, ACL, scores, estatísticas e acesso a JSON.
- **Estruturas** (`structures/`): `Queue` e `Stack`.
- **Rede** (`network/`): servidor e cliente TCP.
- **Dados** (`data/`): JSON com conteúdo do jogo e dados de execução.

Fluxo de uma sessão: o aluno escolhe o nível → o jogo cria 5 perguntas (fixas + geradas) → as perguntas entram numa Queue → cada resposta é validada no servidor e a próxima pergunta é retirada da Queue → as tentativas são guardadas via Stack em `attempts.json` e o resumo em `sessions.json`.

## 4. Estruturas de dados

- **Queue (FIFO)**: ordena as perguntas da sessão. A primeira a entrar é a primeira a sair.
- **Stack (LIFO)**: acumula as tentativas antes de gravar. Como a Stack inverte a ordem, voltamos a inverter para manter a ordem cronológica.

## 5. Motores de cálculo

- **IPv4/IPv6** (`ip_service.py`): usa a biblioteca padrão `ipaddress` para calcular Network ID, broadcast/último endereço, verificar se dois endereços estão na mesma rede e calcular sub-redes.
- **ACL** (`acl_service.py`): avalia as regras por ordem e aplica a primeira que faz match (princípio da primeira correspondência), com *deny* implícito no fim.

## 6. Estatísticas

Para o aluno: total de perguntas, certas/erradas, taxa global, por nível e por tipo, tempos (média, mediana, moda) e evolução do score por sessão. Para o professor: estatísticas globais e distribuição de scores por quartis.

## 7. Comunicação TCP

O servidor (`network/server.py`) usa sockets TCP e mensagens JSON. É a autoridade que valida as respostas e nunca envia a solução. Cada cliente tem a sua Queue de perguntas. O servidor é robusto a JSON inválido, tipos desconhecidos e timeout.

## 8. Testes

Testes unitários (unittest) para Queue, Stack, JSON, scores, estatísticas, motor IPv4/IPv6, motor ACL, sessões e servidor TCP. Testes funcionais (Robot Framework) para a interface web.

## 9. Conclusão

O projeto cumpre os requisitos obrigatórios mantendo-se simples e fácil de explicar: cobre autenticação, estruturas de dados, persistência, cálculo de redes, estatística, comunicação TCP e uma interface web.

## 10. Trabalho futuro

Mais perguntas, dificuldade adaptativa, login de professor e melhorias de segurança (por exemplo, proteção CSRF).

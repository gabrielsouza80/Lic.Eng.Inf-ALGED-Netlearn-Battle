# Especificação e mapa de requisitos

Documento curto que liga cada requisito obrigatório do Projeto Integrador à parte do código que o cumpre.

## Objetivo

Jogo educativo de Redes de Computadores, com interface web (Flask) e versão TCP, persistência apenas em JSON, usando as estruturas de dados Queue e Stack.

## Mapa de requisitos

| # | Requisito | Onde está implementado |
| --- | --- | --- |
| 1 | Autenticação (registo/login com password protegida) | `services/auth_service.py` (salt + hash SHA-256), `app.py` (`/register`, `/login`) |
| 2 | Estrutura Queue (FIFO) | `structures/queue.py`; usada na sessão de jogo (`services/game_service.py`, `app.py`) e no TCP (`network/server.py`) |
| 3 | Estrutura Stack (LIFO) | `structures/stack.py`; usada para guardar as tentativas (`GameService.save_session_attempts`) |
| 4 | Persistência em JSON (sem base de dados) | `services/json_service.py` e ficheiros em `data/` |
| 5 | Motor de cálculo IPv4 (níveis 1-3) | `services/ip_service.py` (Network ID, broadcast, mesma rede) com `ipaddress` |
| 6 | Motor de cálculo IPv6 (nível 4) | `services/ip_service.py` (network id, último endereço, mesma rede, sub-redes) |
| 7 | Motor de ACL com primeira correspondência (nível 5) | `services/acl_service.py` (`evaluate_acl`) + 5 geradores |
| 8 | Sessão de jogo com várias perguntas | `app.py` (`/play`, `/answer`) + `GameService.build_session_questions` (5 perguntas) |
| 9 | Estatísticas do aluno e do professor | `services/stats_service.py` (taxa por nível/tipo, tempos, evolução, quartis) |
| 10 | Comunicação TCP cliente-servidor com JSON | `network/server.py` e `network/client.py` |
| 11 | Testes automáticos | `tests/python/` (unittest) e `tests/robot/` (Robot Framework) |
| 12 | Documentação | `README.md` e pasta `docs/` |

## Regras de pontuação

| Nível | Tema | Certa | Errada |
| --- | --- | ---: | ---: |
| 1 | IPv4 básico | +10 | -5 |
| 2 | Sub-redes IPv4 | +20 | -10 |
| 3 | Super-redes IPv4 | +30 | -15 |
| 4 | IPv6 simples | +40 | -20 |
| 5 | ACLs | +50 | -25 |

## Decisões de simplicidade

- Sem base de dados: só JSON.
- Sem frameworks de frontend: HTML + CSS simples servidos por Flask.
- Perguntas: mistura de fixas (JSON) e geradas automaticamente.
- O servidor (web e TCP) é sempre quem valida as respostas.

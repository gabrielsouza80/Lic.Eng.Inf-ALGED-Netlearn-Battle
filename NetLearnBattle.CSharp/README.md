# NetLearn Battle — Versão C#

Migração do projeto NetLearn Battle de Python/Flask para C# com ASP.NET Core Razor Pages.

## Como executar

Requisitos: [.NET 8.0 SDK](https://dotnet.microsoft.com/download)

```powershell
cd NetLearnBattle.CSharp
dotnet run
```

Abrir `http://localhost:5002` no navegador.

## Estrutura do projeto

```
NetLearnBattle.CSharp/
├── Models/           # Modelos (User, Question, Attempt, etc.)
├── Services/         # Lógica (JsonService, AuthService, ScoreService, IpService, AclService, StatsService)
├── Data/             # Ficheiros JSON
│   ├── acls.json
│   ├── questions.json
│   └── examples/     # Modelos de dados (versionados)
├── Pages/            # Razor Pages
├── wwwroot/css/      # Estilos
├── Network/          # (reservado para TCP)
├── Tests/            # (reservado para testes)
└── Program.cs        # Ponto de entrada
```

## Ficheiros de dados

- `Data/questions.json` — perguntas de exemplo para os níveis 1 a 4
- `Data/acls.json` — cenários de ACL para o nível 5
- `Data/examples/` — modelos da estrutura esperada dos JSONs locais
- `Data/users.json`, `Data/scores.json`, `Data/attempts.json` — dados locais gerados pela aplicação, ignorados pelo Git

## Funcionalidades implementadas

### Fase 1 — Autenticação e base

- Registo de conta com hash SHA-256 + salt
- Login e logout com sessão
- Dashboard com score atual
- Persistência em JSON

### Fase 2 — Jogo web com sessão de 5 perguntas

- Escolha de nível (1 a 5)
- Sessão de jogo com 5 perguntas usando Queue FIFO
- A primeira pergunta inserida na Queue é a primeira apresentada ao aluno
- Feedback imediato (correto/errado) com pontos
- Resumo da sessão com total de certas, erradas e pontos
- Tentativas guardadas em `Data/attempts.json`
- Histórico de tentativas por utilizador
- Pontuação por nível (nível 1: +10/-5, nível 2: +20/-10, etc.)

### Fase 3 — Motores reais de IPv4, IPv6 e ACL (concluída)

- **IpService** — motor de IPv4 e IPv6 com geração dinâmica de perguntas
- **AclService** — motor de ACL com avaliação de regras por ordem
- Perguntas geradas dinamicamente, não fixas
- Níveis 1 a 5 com pontuação real
- **Correção:** `CalculateIpv4Broadcast` — cast para `(byte)` no cálculo bitwise para evitar resultados incorretos em prefixos não alinhados a 8 bits (ex: /25, /26, /27, /21, /22, /23)

## Níveis de jogo

| Nível | Tópico | Pontuação |
|-------|--------|-----------|
| 1 | IPv4 básico (/8, /16, /24) | +10 / -5 |
| 2 | Sub-redes IPv4 (/25, /26, /27) | +20 / -10 |
| 3 | Super-redes IPv4 (/21, /22, /23) | +30 / -15 |
| 4 | IPv6 (Network ID, mesmo segmento, sub-redes, conceitos) | +40 / -20 |
| 5 | ACLs (permit/deny, primeira regra, ordenação, ACE e servidor) | +50 / -25 |

## Motores implementados

### IPv4 (IpService)

O motor IPv4 gera perguntas de:

- **Network ID** — calcular o endereço de rede a partir de um IP e prefixo
- **Broadcast** — calcular o endereço de broadcast
- **Mesmo segmento** — determinar se dois IPs estão na mesma rede

Usa `System.Net.IPAddress` e operações bitwise para calcular máscaras, network IDs e broadcasts.

Redes privadas usadas: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16.

### IPv6 (IpService)

O motor IPv6 gera perguntas de:

- **Network ID IPv6** — calcular o prefixo de rede
- **Mesmo segmento IPv6** — comparar dois endereços IPv6
- **Sub-redes IPv6** — calcular sub-rede com prefixo maior
- **Conceito de broadcast** — pergunta conceptual sobre broadcast em IPv6

**Nota importante:** IPv6 não tem broadcast tradicional como IPv4. O projeto trata esse caso como conceito, explicando que "IPv6 não usa broadcast tradicional".

### ACL (AclService)

O motor ACL:

- Percorre as regras por ordem
- Aplica a primeira regra compatível (first-match)
- Se nenhuma regra combinar, devolve "deny" (comportamento padrão)
- Protocolo "any" ou "ip" combina com qualquer protocolo IP
- Source/Destination "any" combina com qualquer IP
- Suporta notação CIDR para IPs (ex: 192.168.1.0/24)

O nível 5 alterna cinco tipos de perguntas: `permit/deny`, primeira regra
compatível, ordenação de regras, ACE em falta e ACL para servidor. Uma sessão
de cinco perguntas apresenta os cinco tipos, o que facilita a demonstração
académica.

### Fase 4 — Estatísticas e ranking (concluída)

- **StatsService** — serviço de estatísticas do aluno e do professor
- **Página Stats** — estatísticas do aluno autenticado:
  - Score atual, total de perguntas, certas, erradas, taxa de acerto
  - Taxa por nível e por tópico
  - Média, mediana e moda do tempo de resposta
  - Tópico onde mais falha (mínimo 5 tentativas)
  - Evolução do score por sessão
- **Página Ranking** — Top 5 público (ordenado por score decrescente)
- **Página Teacher** — estatísticas globais públicas:
  - Totais globais, taxa global
  - Taxa por nível e por tópico
  - Distribuição de scores (quartis: min, Q1, mediana, Q3, max)
  - Tentativas recentes (últimas 20)
  - Ranking Top 5
  - Nota académica sobre a área ser pública
- **Dashboard** atualizado com links para Estatísticas, Ranking e Professor
- Robusto com JSON vazio — mostra mensagens amigáveis
- Tempo de resposta calculado no servidor entre a apresentação e a resposta
- Evolução de score agregada por sessão: nível, perguntas, certas, erradas,
  pontos da sessão e score final

## Páginas da aplicação

| Rota | Página | Autenticação |
|------|--------|-------------|
| `/` | Home | Pública |
| `/Register` | Registo | Pública |
| `/Login` | Login | Pública |
| `/Dashboard` | Dashboard do aluno | Requer login |
| `/Play` | Jogo (escolher nível e responder) | Requer login |
| `/Result` | Resultado da pergunta | Requer login |
| `/Summary` | Resumo da sessão | Requer login |
| `/History` | Histórico de tentativas | Requer login |
| `/Stats` | Estatísticas do aluno | Requer login |
| `/Ranking` | Ranking Top 5 | Pública |
| `/Teacher` | Área do professor (estatísticas globais) | Pública |

## Próximas fases

- Demonstração TCP
- Testes unitários e funcionais

## Migração

Esta versão replica a lógica do projeto original em Python/Flask, mantendo a mesma estrutura de dados JSON e o mesmo fluxo de autenticação, mas utilizando ASP.NET Core Razor Pages e C#.

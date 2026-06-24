# Relatórios dos testes Robot

Execute os testes com:

```powershell
robot --outputdir tests/robot/results tests/robot
```

Depois da execução, abra os ficheiros dentro de `results/`:

- `report.html`: resumo com testes passados/falhados e tags;
- `log.html`: detalhe de cada teste, incluindo mensagens `[PASSO]` e `[VALIDAR]`;
- `output.xml`: resultado técnico usado pelo Robot Framework.

As tags organizam o relatório:

- `e2e`: fluxo completo de um aluno;
- `valido`: navegação e jogo sem erros;
- `negativo`: bloqueios, mensagens de erro e validações;
- `autenticacao`: registo, login e sessão;
- `autorizacao`: páginas protegidas;
- `jogo`: níveis, resposta e pontos;
- `persistencia`: confirmação de dados depois de novo login.

Os testes são executados um de cada vez. Use `report.html` para o resumo e `log.html` para acompanhar cada passo e validação.

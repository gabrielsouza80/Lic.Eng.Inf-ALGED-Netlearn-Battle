*** Settings ***
Documentation    [Secções 38 e 39] Fluxos válidos da aplicação web NetLearn Battle.
Resource         resources/common.resource
Suite Setup      Iniciar Ambiente de Teste
Suite Teardown   Terminar Ambiente de Teste

*** Test Cases ***
Página Inicial Mostra Projeto
    Go To    ${BASE_URL}/
    Title Should Be    NetLearn Battle
    Page Should Contain    NetLearn Battle

Registo De Novo Utilizador
    Registar Utilizador    ${NEW_USER}
    Page Should Contain    Login

Login Mostra Dashboard
    Fazer Login
    Page Should Contain    O seu painel
    Page Should Contain    Jogar
    Page Should Contain    Score atual

Regras Estão Disponíveis
    Go To    ${BASE_URL}/rules
    Page Should Contain    Regras
    Page Should Contain    IPv6 simples
    Page Should Contain    ACLs simples

Nível 1 Atualiza Score
    Responder Corretamente Ao Nível    1    0    10
    Page Should Contain    +10 pontos

Nível 2 Atualiza Score
    Responder Corretamente Ao Nível    2    1    20
    Page Should Contain    +20 pontos

Nível 3 Atualiza Score
    Responder Corretamente Ao Nível    3    1    30
    Page Should Contain    +30 pontos

Nível 4 IPv6 Atualiza Score
    Responder Corretamente Ao Nível    4    1    40
    Page Should Contain    +40 pontos

Nível 5 ACL Atualiza Score
    Responder Corretamente Ao Nível    5    0    50
    Page Should Contain    +50 pontos

Histórico Mostra Tentativas
    Responder Corretamente Ao Nível    1    0    10
    Fazer Login
    Go To    ${BASE_URL}/history
    Page Should Contain    Histórico
    Page Should Contain    IPv4 básico
    Page Should Contain Element    css:[data-testid="history-row"]

Estatísticas Mostram Resultados
    Responder Corretamente Ao Nível    2    1    20
    Fazer Login
    Go To    ${BASE_URL}/stats
    Page Should Contain    Estatísticas
    Page Should Contain    Taxa de acerto por nível
    Page Should Contain    Score atual
    ${attempts}=    Obter Número De Tentativas
    ${displayed_total}=    Get Text    css:[data-testid="stat-total"] strong
    Should Be Equal As Integers    ${displayed_total}    ${attempts}

Ranking Mostra Aluno De Teste
    Responder Corretamente Ao Nível    1    0    10
    Go To    ${BASE_URL}/ranking
    Page Should Contain    Ranking Top 5
    Page Should Contain    ${TEST_USER}

Área Do Professor Mostra Dados Globais
    Responder Corretamente Ao Nível    5    0    50
    Go To    ${BASE_URL}/teacher
    Page Should Contain    Professor
    Page Should Contain    Perguntas respondidas
    Page Should Contain    Tentativas recentes
    ${attempts}=    Obter Número De Tentativas
    ${displayed_total}=    Get Text    css:[data-testid="teacher-total"] strong
    Should Be Equal As Integers    ${displayed_total}    ${attempts}

Logout Termina Sessão
    Fazer Login
    Go To    ${BASE_URL}/logout
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Be    ${BASE_URL}/

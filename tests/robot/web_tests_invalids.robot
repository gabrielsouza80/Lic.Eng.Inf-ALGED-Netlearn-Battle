*** Settings ***
Documentation    Fluxos inválidos e páginas protegidas do NetLearn Battle.
Resource         resources/common.resource
Suite Setup      Iniciar Ambiente de Teste
Suite Teardown   Terminar Ambiente de Teste

*** Test Cases ***
Login Inválido Mostra Erro
    Go To    ${BASE_URL}/login
    Input Text    name=username    utilizador_inexistente
    Input Password    name=password    password_errada
    Click Button    Entrar
    Wait Until Page Contains    Utilizador ou password incorretos.

Registo Duplicado Mostra Erro
    Go To    ${BASE_URL}/register
    Input Text    name=username    ${TEST_USER}
    Input Password    name=password    ${PASSWORD}
    Click Button    Registar
    Wait Until Page Contains    Esse utilizador já existe.

Resposta Errada Mostra Penalização
    # A primeira pergunta do nível 1 tem a opção 0 como correta; 1 é incorreta.
    Responder Ao Nível    1    1    -5    Resposta incorreta

Dashboard Exige Login
    Go To    ${BASE_URL}/logout
    Go To    ${BASE_URL}/dashboard
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login

Jogar Exige Login
    Go To    ${BASE_URL}/logout
    Go To    ${BASE_URL}/play
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login

Histórico Exige Login
    Go To    ${BASE_URL}/logout
    Go To    ${BASE_URL}/history
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login

Estatísticas Exigem Login
    Go To    ${BASE_URL}/logout
    Go To    ${BASE_URL}/stats
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login

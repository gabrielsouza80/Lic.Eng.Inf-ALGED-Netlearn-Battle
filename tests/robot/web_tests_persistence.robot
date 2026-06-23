*** Settings ***
Documentation    [Secções 8 a 12 e 38] Conta Gabriel em data/ para validar persistência.
Resource         resources/common.resource
Suite Setup      Iniciar Ambiente Real
Suite Teardown   Terminar Ambiente de Teste

*** Test Cases ***
Gabriel Regista Joga Sai E Entra Novamente
    # Garante persistência real entre dois logins na mesma conta.
    Garantir Registo Da Conta Gabriel
    Set Suite Variable    ${ACTIVE_USER}    ${EXISTING_USER}
    Fazer Login    ${EXISTING_USER}    ${EXISTING_PASSWORD}
    ${score_before}=    Obter Score Do Utilizador    ${EXISTING_USER}
    ${attempts_before}=    Obter Número De Tentativas Do Utilizador    ${EXISTING_USER}
    Responder Ao Nível    1    0    10    Resposta correta
    Click Element    css:nav a[href="/logout"]
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Be    ${BASE_URL}/
    Fazer Login    ${EXISTING_USER}    ${EXISTING_PASSWORD}
    Responder Ao Nível    2    1    20    Resposta correta
    ${score_after}=    Obter Score Do Utilizador    ${EXISTING_USER}
    ${expected_score}=    Evaluate    int($score_before) + 30
    Should Be Equal As Integers    ${score_after}    ${expected_score}
    Go To    ${BASE_URL}/history
    ${rows}=    Get Element Count    css:[data-testid="history-row"]
    ${expected_rows}=    Evaluate    int($attempts_before) + 2
    Should Be Equal As Integers    ${rows}    ${expected_rows}

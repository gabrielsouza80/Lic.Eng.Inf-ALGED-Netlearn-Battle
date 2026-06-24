*** Settings ***
Documentation    [Secções 8 a 12 e 38] Conta de teste persistente em data/ para validar persistência.
Resource         resources/common.resource
Test Setup       Preparar Teste De Persistência
Test Teardown    Finalizar Teste De Persistência

*** Test Cases ***
Utilizador Persistente Regista Joga Sai E Entra Novamente
    [Tags]    persistencia    autenticacao    score
    # Garante persistência real entre dois logins na mesma conta.
    Garantir Registo Da Conta Persistente
    Set Suite Variable    ${ACTIVE_USER}    ${EXISTING_USER}
    Fazer Login    ${EXISTING_USER}    ${EXISTING_PASSWORD}
    ${attempts_before}=    Obter Número De Tentativas Do Utilizador    ${EXISTING_USER}
    Responder Ao Nível    1    0    10    Resposta correta
    Click Element    css:nav a[href="/logout"]
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Be    ${BASE_URL}/
    Fazer Login    ${EXISTING_USER}    ${EXISTING_PASSWORD}
    Responder Ao Nível    2    1    20    Resposta correta
    ${attempts_after}=    Obter Número De Tentativas Do Utilizador    ${EXISTING_USER}
    ${expected_attempts}=    Evaluate    int($attempts_before) + 2
    Should Be Equal As Integers    ${attempts_after}    ${expected_attempts}
    Go To    ${BASE_URL}/history
    ${rows}=    Get Element Count    css:[data-testid="history-row"]
    # A página de histórico apresenta apenas as últimas 20 tentativas.
    ${expected_rows}=    Evaluate    min(20, int($attempts_before) + 2)
    Should Be Equal As Integers    ${rows}    ${expected_rows}
    Mostrar Validação    Score e histórico foram mantidos depois de logout e novo login.

*** Settings ***
Documentation    [Secções 38 e 39] Recursos partilhados pelos testes Robot do NetLearn Battle.
Library          SeleniumLibrary
Library          Process
Library          OperatingSystem
Library          DateTime
Library          Collections

*** Variables ***
# A aplicação de testes usa a porta 5002; a aplicação normal pode usar a 5000.
${BASE_URL}              http://127.0.0.1:5002
${SESSION_PASSWORD}      robot123
${VISUAL_SPEED}          700 milliseconds

*** Keywords ***
Preparar Caminhos Do Projeto
    # Lê as credenciais Gabriel de um JSON, evitando repetir dados no código Robot.
    ${project_dir}=    Evaluate    os.path.abspath(os.path.join(r'''${CURDIR}''', '..', '..', '..'))    os
    Set Suite Variable    ${PROJECT_DIR}    ${project_dir}
    ${credentials_file}=    Set Variable    ${project_dir}${/}tests${/}robot${/}test_credentials.json
    ${content}=    Get File    ${credentials_file}
    ${credentials}=    Evaluate    json.loads($content)    json
    ${username}=    Get From Dictionary    ${credentials}    username
    ${password}=    Get From Dictionary    ${credentials}    password
    Set Suite Variable    ${EXISTING_USER}    ${username}
    Set Suite Variable    ${EXISTING_PASSWORD}    ${password}

Iniciar Ambiente Real
    # Esta suite usa data/ de propósito: os registos e jogadas ficam nos dados reais.
    Preparar Caminhos Do Projeto
    Set Suite Variable    ${ACTIVE_DATA_DIR}    ${PROJECT_DIR}${/}data
    Iniciar Servidor Flask

Iniciar Ambiente Real Com Sessão Nova
    Iniciar Ambiente Real
    ${created_at}=    Get Current Date    result_format=%Y%m%d_%H%M%S_%f
    ${username}=    Set Variable    aluno_${created_at}
    Set Suite Variable    ${ACTIVE_USER}    ${username}
    Registar Utilizador    ${ACTIVE_USER}    ${SESSION_PASSWORD}
    Fazer Login    ${ACTIVE_USER}    ${SESSION_PASSWORD}

Iniciar Ambiente Real Com Registo Novo
    # Cria a conta no Setup, mas deixa o login para um único caso de teste.
    Iniciar Ambiente Real
    ${created_at}=    Get Current Date    result_format=%Y%m%d_%H%M%S_%f
    ${username}=    Set Variable    aluno_invalido_${created_at}
    Set Suite Variable    ${ACTIVE_USER}    ${username}
    Registar Utilizador    ${ACTIVE_USER}    ${SESSION_PASSWORD}

Iniciar Servidor Flask
    # Remove logs antigos para o relatório mostrar apenas a execução atual.
    ${output_log}=    Set Variable    ${CURDIR}${/}..${/}results${/}flask-output.log
    ${error_log}=    Set Variable    ${CURDIR}${/}..${/}results${/}flask-error.log
    Run Keyword And Ignore Error    Remove File    ${output_log}
    Run Keyword And Ignore Error    Remove File    ${error_log}
    Start Process    py    -3    app.py    cwd=${PROJECT_DIR}    alias=flask    env:FLASK_PORT=5002    stdout=${output_log}    stderr=${error_log}
    Open Browser    about:blank    chrome
    Maximize Browser Window
    Set Selenium Speed    ${VISUAL_SPEED}
    Wait Until Keyword Succeeds    10x    1 second    Confirmar Aplicação Ativa

Terminar Ambiente de Teste
    Close All Browsers
    Run Keyword And Ignore Error    Terminate Process    flask    kill=True

Confirmar Aplicação Ativa
    Go To    ${BASE_URL}/
    Title Should Be    NetLearn Battle

Registar Utilizador
    # Esta ação usa o formulário real de registo, não altera JSON diretamente.
    [Arguments]    ${username}    ${password}
    Go To    ${BASE_URL}/register
    Clear Element Text    name=username
    Input Text    name=username    ${username}
    Clear Element Text    name=password
    Input Password    name=password    ${password}
    Click Button    Registar
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login
    Page Should Contain    Registo efetuado. Já pode fazer login.

Fazer Login
    # Limpar antes de escrever evita texto residual/autofill do Chrome.
    [Arguments]    ${username}    ${password}
    Go To    ${BASE_URL}/login
    Clear Element Text    name=username
    Input Text    name=username    ${username}
    Clear Element Text    name=password
    Input Password    name=password    ${password}
    Click Button    Entrar
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /dashboard
    Page Should Contain    Olá, ${username}

Garantir Registo Da Conta Gabriel
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}users.json
    ${exists}=    Evaluate    any(user["username"] == "${EXISTING_USER}" for user in json.loads($content))    json
    IF    not ${exists}
        Registar Utilizador    ${EXISTING_USER}    ${EXISTING_PASSWORD}
    END

Confirmar Página Protegida Exige Login
    [Arguments]    ${path}
    Go To    ${BASE_URL}${path}
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login
    Page Should Contain    Faça login para continuar.

Responder Ao Nível
    [Arguments]    ${level}    ${answer_index}    ${points}    ${result_message}
    ${score_before}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_before}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    Go To    ${BASE_URL}/play
    Click Button    id=level-${level}
    Wait Until Page Contains    Pergunta
    Select Radio Button    choice    ${answer_index}
    Click Button    Confirmar resposta
    Wait Until Page Contains Element    xpath=//h1[normalize-space()='${result_message}']    5 seconds
    Page Should Contain    ${points} pontos
    ${score_after}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_after}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    ${expected_score}=    Evaluate    int($score_before) + int($points)
    ${expected_attempts}=    Evaluate    int($attempts_before) + 1
    Should Be Equal As Integers    ${score_after}    ${expected_score}
    Should Be Equal As Integers    ${attempts_after}    ${expected_attempts}

Obter Score Do Utilizador
    [Arguments]    ${username}
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}scores.json
    ${scores}=    Evaluate    json.loads($content)    json
    ${score}=    Evaluate    $scores.get($username, 0)
    RETURN    ${score}

Obter Número De Tentativas Do Utilizador
    [Arguments]    ${username}
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}attempts.json
    ${attempts}=    Evaluate    json.loads($content)    json
    ${count}=    Evaluate    sum(1 for attempt in $attempts if attempt["username"] == "${username}")
    RETURN    ${count}

Obter Última Tentativa
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}attempts.json
    ${attempt}=    Evaluate    json.loads($content)[-1]    json
    RETURN    ${attempt}

Garantir Três Jogadores Com Tentativas
    # Ranking é uma exceção ao login único: para testar várias pessoas, cada nova conta joga uma vez.
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}attempts.json
    ${attempts}=    Evaluate    json.loads($content)    json
    ${players}=    Evaluate    sorted(set(attempt["username"] for attempt in $attempts))
    ${missing}=    Evaluate    max(0, 3 - len($players))
    FOR    ${index}    IN RANGE    ${missing}
        ${created_at}=    Get Current Date    result_format=%Y%m%d_%H%M%S_%f
        ${username}=    Set Variable    ranking_${created_at}_${index}
        Registar Utilizador    ${username}    ${SESSION_PASSWORD}
        Set Suite Variable    ${ACTIVE_USER}    ${username}
        Fazer Login    ${ACTIVE_USER}    ${SESSION_PASSWORD}
        Responder Ao Nível    1    0    10    Resposta correta
        Click Element    css:nav a[href="/logout"]
    END

Obter Top 5 Esperado
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}scores.json
    ${scores}=    Evaluate    json.loads($content)    json
    ${top_five}=    Evaluate    [name for name, score in sorted($scores.items(), key=lambda item: (-item[1], item[0].lower()))[:5]]
    RETURN    ${top_five}

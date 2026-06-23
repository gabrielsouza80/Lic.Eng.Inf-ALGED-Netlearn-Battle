*** Settings ***
Documentation    [Secções 38 e 39] Recursos partilhados pelos testes Robot do NetLearn Battle.
Library          SeleniumLibrary
Library          Process
Library          OperatingSystem
Library          DateTime
Library          Collections

*** Variables ***
${BASE_URL}          http://127.0.0.1:5002
${PASSWORD}          robot123
${VISUAL_SPEED}      700 milliseconds

*** Keywords ***
Iniciar Ambiente de Teste
    # Cada execução usa JSON temporário e não altera os dados reais em data/.
    ${project_dir}=    Evaluate    os.path.abspath(os.path.join(r'''${CURDIR}''', '..', '..', '..'))    os
    ${data_dir}=    Set Variable    ${CURDIR}${/}..${/}results${/}test-data
    Set Suite Variable    ${TEST_DATA_DIR}    ${data_dir}
    Remove Directory    ${data_dir}    recursive=True
    Create Directory    ${data_dir}
    Copy File    ${project_dir}${/}data${/}questions.json    ${data_dir}${/}questions.json
    Copy File    ${project_dir}${/}data${/}acls.json    ${data_dir}${/}acls.json
    Create File    ${data_dir}${/}users.json    []
    Create File    ${data_dir}${/}scores.json    {}
    Create File    ${data_dir}${/}attempts.json    []
    ${timestamp}=    Get Time    epoch
    Set Suite Variable    ${TEST_USER}    aluno_robot_${timestamp}
    Set Suite Variable    ${NEW_USER}    novo_robot_${timestamp}
    # py -3 usa o Python normal do Windows, onde Flask foi instalado.
    # A porta 5002 evita conflito com a aplicação normal na porta 5000.
    Start Process    py    -3    app.py    cwd=${project_dir}    alias=flask    env:NETLEARN_DATA_DIR=${data_dir}    env:FLASK_PORT=5002    stdout=${CURDIR}${/}..${/}results${/}flask-output.log    stderr=${CURDIR}${/}..${/}results${/}flask-error.log
    Open Browser    about:blank    chrome
    Maximize Browser Window
    Set Selenium Speed    ${VISUAL_SPEED}
    Wait Until Keyword Succeeds    10x    1 second    Confirmar Aplicação Ativa
    Registar Utilizador    ${TEST_USER}

Terminar Ambiente de Teste
    Close All Browsers
    Run Keyword And Ignore Error    Terminate Process    flask    kill=True

Confirmar Aplicação Ativa
    Go To    ${BASE_URL}/
    Title Should Be    NetLearn Battle

Registar Utilizador
    [Arguments]    ${username}
    Go To    ${BASE_URL}/register
    Input Text    name=username    ${username}
    Input Password    name=password    ${PASSWORD}
    Click Button    Registar
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login

Fazer Login
    Go To    ${BASE_URL}/login
    Input Text    name=username    ${TEST_USER}
    Input Password    name=password    ${PASSWORD}
    Click Button    Entrar
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /dashboard

Responder Corretamente Ao Nível
    [Arguments]    ${level}    ${answer_index}    ${points}
    Responder Ao Nível    ${level}    ${answer_index}    ${points}    Resposta correta

Responder Ao Nível
    [Arguments]    ${level}    ${answer_index}    ${points}    ${result_message}
    ${score_before}=    Obter Score Atual
    ${attempts_before}=    Obter Número De Tentativas
    Fazer Login
    Go To    ${BASE_URL}/play
    Click Button    level-${level}
    Wait Until Page Contains    Pergunta
    Select Radio Button    choice    ${answer_index}
    Click Button    Confirmar resposta
    Wait Until Page Contains    ${result_message}
    Page Should Contain    ${points} pontos
    ${score_after}=    Obter Score Atual
    ${attempts_after}=    Obter Número De Tentativas
    ${expected_score}=    Evaluate    int($score_before) + int($points)
    ${expected_attempts}=    Evaluate    int($attempts_before) + 1
    Should Be Equal As Integers    ${score_after}    ${expected_score}
    Should Be Equal As Integers    ${attempts_after}    ${expected_attempts}
    Verificar Última Tentativa    ${points}

Obter Score Atual
    ${content}=    Get File    ${TEST_DATA_DIR}${/}scores.json
    ${scores}=    Evaluate    json.loads($content)    json
    ${score}=    Evaluate    $scores.get($TEST_USER, 0)
    RETURN    ${score}

Obter Número De Tentativas
    ${content}=    Get File    ${TEST_DATA_DIR}${/}attempts.json
    ${attempts}=    Evaluate    json.loads($content)    json
    ${count}=    Get Length    ${attempts}
    RETURN    ${count}

Verificar Última Tentativa
    [Arguments]    ${expected_points}
    ${content}=    Get File    ${TEST_DATA_DIR}${/}attempts.json
    ${attempts}=    Evaluate    json.loads($content)    json
    ${last_attempt}=    Evaluate    $attempts[-1]
    ${username}=    Get From Dictionary    ${last_attempt}    username
    ${points}=    Get From Dictionary    ${last_attempt}    points
    ${is_correct}=    Get From Dictionary    ${last_attempt}    is_correct
    Should Be Equal    ${username}    ${TEST_USER}
    Should Be Equal As Integers    ${points}    ${expected_points}
    Should Be True    ${is_correct} == (${expected_points} > 0)

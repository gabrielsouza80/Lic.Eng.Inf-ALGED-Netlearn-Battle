*** Settings ***
Documentation    [Secções 38 e 39] Recursos partilhados pelos testes Robot do NetLearn Battle.
Library          SeleniumLibrary
Library          Process
Library          OperatingSystem
Library          DateTime
Library          Collections
Library          String

*** Variables ***
# A aplicação de testes usa a porta 5002; a aplicação normal pode usar a 5000.
${BASE_URL}              http://127.0.0.1:5002
${SESSION_PASSWORD}      robot123
# Ritmo rápido, mas ainda visível: semelhante a uma pessoa a clicar depressa.
${VISUAL_SPEED}          100 milliseconds
# Valores iniciais para o RobotCode reconhecer variáveis que o Setup preenche em execução.
${PROJECT_DIR}           ${EMPTY}
${ACTIVE_DATA_DIR}       ${EMPTY}
${ACTIVE_USER}           ${EMPTY}
${EXISTING_USER}         ${EMPTY}
${EXISTING_PASSWORD}     ${EMPTY}

*** Keywords ***
Iniciar Registo No Console
    Log To Console    \n========== [TESTE] ${TEST NAME} ==========

Finalizar Registo No Console
    Log To Console    \n[RESULTADO] ${TEST NAME}: ${TEST STATUS}

Mostrar Passo
    [Arguments]    ${message}
    # A quebra inicial evita que o texto fique misturado com o resumo do Robot.
    Log To Console    \n[PASSO] ${message}
    Log    [PASSO] ${message}

Mostrar Validação
    [Arguments]    ${message}
    Log To Console    \n[VALIDAR] ${message}
    Log    [VALIDAR] ${message}

Preparar Caminhos Do Projeto
    # Lê as credenciais de teste de um JSON, evitando repetir dados no código Robot.
    # Se o ficheiro test_credentials.json não existir, usa o exemplo.
    ${project_dir}=    Evaluate    os.path.abspath(os.path.join(r'''${CURDIR}''', '..', '..', '..'))    os
    Set Suite Variable    ${PROJECT_DIR}    ${project_dir}
    ${credentials_file}=    Set Variable    ${project_dir}${/}tests${/}robot${/}test_credentials.json
    ${example_file}=    Set Variable    ${project_dir}${/}tests${/}robot${/}test_credentials.example.json
    ${has_credentials}=    Run Keyword And Return Status    File Should Exist    ${credentials_file}
    ${has_example}=    Run Keyword And Return Status    File Should Exist    ${example_file}
    IF    ${has_credentials}
        ${source}=    Set Variable    ${credentials_file}
        ${content}=    Get File    ${source}
        ${credentials}=    Evaluate    json.loads($content)    json
        ${username}=    Get From Dictionary    ${credentials}    username
        ${password}=    Get From Dictionary    ${credentials}    password
    ELSE IF    ${has_example}
        ${source}=    Set Variable    ${example_file}
        ${content}=    Get File    ${source}
        ${credentials}=    Evaluate    json.loads($content)    json
        ${username}=    Get From Dictionary    ${credentials}    username
        ${password}=    Get From Dictionary    ${credentials}    password
    ELSE
        ${username}=    Set Variable    aluno_teste
        ${password}=    Set Variable    password_teste
    END
    Set Suite Variable    ${EXISTING_USER}    ${username}
    Set Suite Variable    ${EXISTING_PASSWORD}    ${password}

Iniciar Ambiente Real
    # Esta suite usa data/ de propósito: os registos e jogadas ficam nos dados reais.
    Iniciar Servidor Real
    Abrir Navegador

Iniciar Servidor Real
    Preparar Caminhos Do Projeto
    Set Suite Variable    ${ACTIVE_DATA_DIR}    ${PROJECT_DIR}${/}data
    Iniciar Servidor Flask

Abrir Navegador
    # ChromeDriver escreve mensagens técnicas (DevTools e TensorFlow) no terminal.
    # Estas opções reduzem o ruído e guardam o restante no ficheiro de resultados.
    ${driver_log}=    Set Variable    ${CURDIR}${/}..${/}results${/}chromedriver.log
    ${chrome_service}=    Evaluate    selenium.webdriver.chrome.service.Service(log_output=r'''${driver_log}''')    modules=selenium.webdriver.chrome.service
    Open Browser    about:blank    chrome    options=add_argument('--log-level=3');add_experimental_option('excludeSwitches',['enable-logging'])    service=${chrome_service}
    Maximize Browser Window
    Set Selenium Speed    ${VISUAL_SPEED}
    Wait Until Keyword Succeeds    10x    1 second    Confirmar Aplicação Ativa

Iniciar Ambiente Real Com Sessão Nova
    Iniciar Servidor Real
    Abrir Navegador Com Sessão Nova

Abrir Navegador Com Sessão Nova
    Abrir Navegador
    ${created_at}=    Get Current Date    result_format=%Y%m%d_%H%M%S_%f
    ${username}=    Set Variable    aluno_${created_at}
    Set Suite Variable    ${ACTIVE_USER}    ${username}
    Registar Utilizador    ${ACTIVE_USER}    ${SESSION_PASSWORD}
    Fazer Login    ${ACTIVE_USER}    ${SESSION_PASSWORD}

Iniciar Ambiente Real Com Registo Novo
    # Cria a conta no Setup, mas deixa o login para um único caso de teste.
    Iniciar Servidor Real
    Abrir Navegador Com Registo Novo

Abrir Navegador Com Registo Novo
    Abrir Navegador
    ${created_at}=    Get Current Date    result_format=%Y%m%d_%H%M%S_%f
    ${username}=    Set Variable    aluno_invalido_${created_at}
    Set Suite Variable    ${ACTIVE_USER}    ${username}
    Registar Utilizador    ${ACTIVE_USER}    ${SESSION_PASSWORD}

Iniciar Ambiente Real Com Utilizador Novo
    # A conta é apenas preparada aqui. O primeiro teste end-to-end faz o registo.
    Iniciar Ambiente Real
    ${created_at}=    Get Current Date    result_format=%Y%m%d_%H%M%S_%f
    ${username}=    Set Variable    aluno_e2e_${created_at}
    Set Suite Variable    ${ACTIVE_USER}    ${username}

Preparar Teste Inválido Sem Sessão
    Iniciar Registo No Console
    Abrir Navegador Com Registo Novo

Preparar Teste Inválido Com Sessão
    Iniciar Registo No Console
    Abrir Navegador Com Sessão Nova

Finalizar Teste Com Navegador
    Fechar Navegador
    Finalizar Registo No Console

Preparar Teste De Persistência
    Iniciar Registo No Console
    Iniciar Ambiente Real

Finalizar Teste De Persistência
    Terminar Ambiente de Teste
    Finalizar Registo No Console

Iniciar Servidor Flask
    # Remove logs antigos para o relatório mostrar apenas a execução atual.
    ${output_log}=    Set Variable    ${CURDIR}${/}..${/}results${/}flask-output.log
    ${error_log}=    Set Variable    ${CURDIR}${/}..${/}results${/}flask-error.log
    Run Keyword And Ignore Error    Remove File    ${output_log}
    Run Keyword And Ignore Error    Remove File    ${error_log}
    # `py -3` cria um processo intermediário no Windows. Descobrimos primeiro o
    # executável real para o Teardown conseguir fechar exatamente o Flask certo.
    ${python_result}=    Run Process    py    -3    -c    import sys; print(sys.executable)
    ${python_executable}=    Strip String    ${python_result.stdout}
    Start Process    ${python_executable}    app.py    cwd=${PROJECT_DIR}    alias=flask    env:FLASK_PORT=5002    stdout=${output_log}    stderr=${error_log}
Terminar Ambiente de Teste
    Fechar Navegador
    Terminar Servidor De Teste

Fechar Navegador
    # Fecha a janela deste caso antes de a próxima abrir uma nova sessão.
    Close All Browsers

Terminar Servidor De Teste
    Run Keyword And Ignore Error    Terminate Process    flask    kill=True
    # Espera o Windows libertar a porta 5002 e os ficheiros de log antes do próximo teste.
    Run Keyword And Ignore Error    Wait For Process    flask    timeout=5 seconds

Confirmar Aplicação Ativa
    Go To    ${BASE_URL}/
    Title Should Be    NetLearn Battle

Abrir Página Inicial
    # Cada caso começa numa página conhecida, mas o navegador mantém a sessão do login inicial.
    Go To    ${BASE_URL}/

Registar Utilizador
    # Esta ação usa o formulário real de registo, não altera JSON diretamente.
    [Arguments]    ${username}    ${password}
    Mostrar Passo    Registar utilizador ${username}.
    Go To    ${BASE_URL}/register
    Clear Element Text    name=username
    Input Text    name=username    ${username}
    Clear Element Text    name=password
    Input Password    name=password    ${password}
    Click Button    Registar
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login
    Page Should Contain    Registo efetuado. Já pode fazer login.
    Mostrar Validação    Registo aceite e mensagem de sucesso apresentada.

Fazer Login
    # Limpar antes de escrever evita texto residual/autofill do Chrome.
    [Arguments]    ${username}    ${password}
    Mostrar Passo    Fazer login como ${username}.
    Go To    ${BASE_URL}/login
    Clear Element Text    name=username
    Input Text    name=username    ${username}
    Clear Element Text    name=password
    Input Password    name=password    ${password}
    Click Button    Entrar
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /dashboard
    Page Should Contain    Olá, ${username}
    Mostrar Validação    Login aceite e dashboard apresentado.

Garantir Registo Da Conta Persistente
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}users.json
    ${exists}=    Evaluate    any(user["username"] == "${EXISTING_USER}" for user in json.loads($content))    json
    IF    not ${exists}
        Registar Utilizador    ${EXISTING_USER}    ${EXISTING_PASSWORD}
    END

Confirmar Página Protegida Exige Login
    [Arguments]    ${path}
    Mostrar Passo    Tentar abrir ${path} sem autenticação.
    Go To    ${BASE_URL}${path}
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login
    Page Should Contain    Faça login para continuar.
    Mostrar Validação    Página bloqueada e aviso de login apresentado.

Responder Ao Nível
    [Arguments]    ${level}    ${answer_index}    ${points}    ${result_message}    ${correct_answer}=${NONE}
    Mostrar Passo    Nível ${level}: escolher opção ${answer_index}; esperado ${result_message}, ${points} pontos.
    ${score_before}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_before}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    Go To    ${BASE_URL}/play
    Click Button    id=level-${level}
    Wait Until Page Contains    Pergunta
    Select Radio Button    choice    ${answer_index}
    Click Button    Confirmar resposta
    # Perguntas IPv4/IPv6 são geradas e opções são misturadas. O fluxo valida
    # feedback real, sem assumir que um índice fixo será sempre a resposta certa.
    Wait Until Page Contains Element    xpath=//h1[normalize-space()='Resposta correta' or normalize-space()='Resposta incorreta']    5 seconds
    IF    $correct_answer is not None
        # Confirma o feedback correto quando o aluno escolhe uma opção errada.
        Page Should Contain    A resposta correta era: ${correct_answer}
    END
    ${score_after}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_after}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    ${expected_attempts}=    Evaluate    int($attempts_before) + 1
    Should Be Equal As Integers    ${attempts_after}    ${expected_attempts}
    Should Not Be Equal As Integers    ${score_after}    ${score_before}
    Mostrar Validação    Nível ${level}: feedback, score e tentativa confirmados.

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

Obter Estatísticas Pessoais
    [Arguments]    ${username}
    # RobotCode pode usar um Python fora da pasta do projeto. Adicionamos a raiz
    # antes do import para calcular o valor esperado com o mesmo StatsService.
    ${stats}=    Evaluate    __import__('sys').path.insert(0, r'''${PROJECT_DIR}''') or __import__('services.stats_service', fromlist=['StatsService']).StatsService().personal_statistics($username)
    RETURN    ${stats}

Obter Estatísticas Globais
    ${stats}=    Evaluate    __import__('sys').path.insert(0, r'''${PROJECT_DIR}''') or __import__('services.stats_service', fromlist=['StatsService']).StatsService().global_statistics()
    RETURN    ${stats}

Obter Última Tentativa
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}attempts.json
    ${attempt}=    Evaluate    json.loads($content)[-1]    json
    RETURN    ${attempt}

Garantir Três Jogadores Com Tentativas
    # Para verificar uma ordenação real, existem pelo menos três contas com jogadas.
    ${original_user}=    Set Variable    ${ACTIVE_USER}
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
    # O E2E continua com a conta original depois de preparar o ranking.
    Set Suite Variable    ${ACTIVE_USER}    ${original_user}
    Fazer Login    ${ACTIVE_USER}    ${SESSION_PASSWORD}

Obter Top 5 Esperado
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}scores.json
    ${scores}=    Evaluate    json.loads($content)    json
    ${top_five}=    Evaluate    [name for name, score in sorted($scores.items(), key=lambda item: (-item[1], item[0].lower()))[:5]]
    RETURN    ${top_five}

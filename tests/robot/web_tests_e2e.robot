*** Settings ***
Documentation    [Secções 1 a 34] Fluxo end-to-end completo, isolado num navegador.
Resource         resources/common.resource
Suite Setup      Iniciar Ambiente Real Com Utilizador Novo
Suite Teardown   Terminar Ambiente de Teste
Test Setup       Iniciar Registo No Console
Test Teardown    Finalizar Registo No Console

*** Test Cases ***
Fluxo End To End Do Projeto
    [Tags]    e2e    valido    navegacao
    # Registo e login.
    Mostrar Passo    Abrir página inicial e confirmar nome do projeto.
    Go To    ${BASE_URL}/
    Page Should Contain Element    xpath=//h1[normalize-space()='NetLearn Battle']
    Click Element    css:a.button.secondary[href="/register"]
    Clear Element Text    name=username
    Input Text    name=username    ${ACTIVE_USER}
    Clear Element Text    name=password
    Input Password    name=password    ${SESSION_PASSWORD}
    Click Button    Registar
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /login
    Page Should Contain    Registo efetuado. Já pode fazer login.
    Mostrar Validação    Formulário de registo e mensagem de sucesso confirmados.
    Fazer Login    ${ACTIVE_USER}    ${SESSION_PASSWORD}
    Page Should Contain    Olá, ${ACTIVE_USER}

    # Todos os níveis são respondidos antes de avançar para as páginas seguintes.
    Responder Ao Nível    1    0    10    Resposta correta
    Responder Ao Nível    2    1    20    Resposta correta
    Responder Ao Nível    3    1    30    Resposta correta
    Responder Ao Nível    4    1    40    Resposta correta
    Responder Ao Nível    5    0    50    Resposta correta
    # Erro normal: opção válida, mas diferente da resposta certa.
    Responder Ao Nível    1    1    -5    Resposta incorreta

    # Depois do jogo, usa os botões do dashboard para consultar uma página de cada vez.
    Click Element    css:a[href="/dashboard"]
    Page Should Contain Element    xpath=//h1[normalize-space()='O seu painel']
    Mostrar Validação    Dashboard aberto pelo botão do resultado.
    Click Element    css:a[href="/history"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Histórico']
    ${attempts}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    ${history_rows}=    Get Element Count    css:[data-testid="history-row"]
    Should Be Equal As Integers    ${history_rows}    ${attempts}
    Mostrar Validação    Histórico mostra todas as ${attempts} tentativas do aluno.
    Click Element    css:nav a[href="/dashboard"]
    Click Element    css:a[href="/stats"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Estatísticas']
    ${personal_stats}=    Obter Estatísticas Pessoais    ${ACTIVE_USER}
    ${displayed_total}=    Get Text    css:[data-testid="stat-total"] strong
    ${expected_total}=    Get From Dictionary    ${personal_stats}    total
    ${expected_correct}=    Get From Dictionary    ${personal_stats}    correct
    ${expected_wrong}=    Get From Dictionary    ${personal_stats}    wrong
    ${expected_accuracy}=    Get From Dictionary    ${personal_stats}    accuracy
    ${expected_score}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    Should Be Equal As Integers    ${displayed_total}    ${expected_total}
    Element Text Should Be    css:[data-testid="stat-correct"] strong    ${expected_correct}
    Element Text Should Be    css:[data-testid="stat-wrong"] strong    ${expected_wrong}
    Element Text Should Be    css:[data-testid="stat-accuracy"] strong    ${expected_accuracy}%
    # O score aparece numa frase fixa; a verificação completa evita depender da
    # estrutura visual interna do cartão de estatísticas.
    Page Should Contain    Score atual: ${expected_score} pontos
    Mostrar Validação    Estatísticas mostram totais, taxa e score calculados corretamente.
    Click Element    css:nav a[href="/dashboard"]
    Garantir Três Jogadores Com Tentativas
    Click Element    css:a[href="/ranking"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Ranking Top 5']
    ${expected_top_five}=    Obter Top 5 Esperado
    ${expected_count}=    Get Length    ${expected_top_five}
    ${ranking_rows}=    Get Element Count    css:ol.ranking li
    Should Be Equal As Integers    ${ranking_rows}    ${expected_count}
    FOR    ${index}    IN RANGE    ${expected_count}
        ${username}=    Get From List    ${expected_top_five}    ${index}
        ${position}=    Evaluate    int($index) + 1
        Page Should Contain Element    xpath=//ol[contains(@class, 'ranking')]/li[${position}]/span[normalize-space()='${username}']
    END
    Mostrar Validação    Ranking corresponde ao Top 5 de scores.json.
    Click Element    css:nav a[href="/teacher"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Professor']
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}attempts.json
    ${all_attempts}=    Evaluate    json.loads($content)    json
    ${expected_global_total}=    Get Length    ${all_attempts}
    ${teacher_total}=    Get Text    css:[data-testid="teacher-total"] strong
    ${global_stats}=    Obter Estatísticas Globais
    ${expected_global_correct}=    Get From Dictionary    ${global_stats}    correct
    ${expected_global_wrong}=    Get From Dictionary    ${global_stats}    wrong
    ${expected_global_accuracy}=    Get From Dictionary    ${global_stats}    accuracy
    Should Be Equal As Integers    ${teacher_total}    ${expected_global_total}
    Page Should Contain Element    xpath=//div[contains(@class, 'stat')][.//span[normalize-space()='Respostas certas']]//strong[normalize-space()='${expected_global_correct}']
    Page Should Contain Element    xpath=//div[contains(@class, 'stat')][.//span[normalize-space()='Respostas erradas']]//strong[normalize-space()='${expected_global_wrong}']
    Page Should Contain Element    xpath=//div[contains(@class, 'stat')][.//span[normalize-space()='Taxa global']]//strong[normalize-space()='${expected_global_accuracy}%']
    Mostrar Validação    Área do professor mostra totais e taxa global corretos.
    Click Element    css:nav a[href="/rules"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Regras']
    Page Should Contain    +50
    Mostrar Validação    Página de regras apresenta a pontuação do nível 5.
    Click Element    css:nav a[href="/logout"]
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Be    ${BASE_URL}/
    Mostrar Validação    Logout terminou a sessão e voltou à página inicial.

*** Settings ***
Documentation    [Secções 38 e 39] Fluxos válidos usando uma conta real criada no Suite Setup.
Resource         resources/common.resource
Suite Setup      Iniciar Ambiente Real Com Sessão Nova
Suite Teardown   Terminar Ambiente de Teste

*** Test Cases ***
Página Inicial Mostra Projeto
    # Confirma texto principal e botão Login da página inicial.
    Go To    ${BASE_URL}/
    Page Should Contain Element    xpath=//h1[normalize-space()='NetLearn Battle']
    Click Element    css:a.button[href="/login"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Login']

Página De Registo Mostra Formulário
    Go To    ${BASE_URL}/
    Click Element    css:a.button.secondary[href="/register"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Criar conta']

Dashboard E Links Funcionam
    # Cada card do dashboard deve abrir a página que anuncia.
    Go To    ${BASE_URL}/dashboard
    Page Should Contain    Olá, ${ACTIVE_USER}
    Click Element    css:a[href="/play"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Escolha um nível']
    Go To    ${BASE_URL}/dashboard
    Click Element    css:a[href="/history"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Histórico']
    Go To    ${BASE_URL}/dashboard
    Click Element    css:a[href="/stats"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Estatísticas']
    Go To    ${BASE_URL}/dashboard
    Click Element    css:a[href="/ranking"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Ranking Top 5']

Página De Regras Está Disponível
    Go To    ${BASE_URL}/dashboard
    Click Element    css:nav a[href="/rules"]
    Page Should Contain Element    xpath=//h1[normalize-space()='Regras']
    Page Should Contain    ACLs simples

Níveis Atualizam Score
    # Exercita os cinco botões de nível e as pontuações definidas no enunciado.
    Responder Ao Nível    1    0    10    Resposta correta
    Responder Ao Nível    2    1    20    Resposta correta
    Responder Ao Nível    3    1    30    Resposta correta
    Responder Ao Nível    4    1    40    Resposta correta
    Responder Ao Nível    5    0    50    Resposta correta

Resposta Errada Aplica Penalização
    Responder Ao Nível    1    1    -5    Resposta incorreta

Histórico E Estatísticas Mostram Dados Corretos
    Go To    ${BASE_URL}/history
    ${attempts}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    ${rows}=    Get Element Count    css:[data-testid="history-row"]
    Should Be Equal As Integers    ${rows}    ${attempts}
    Go To    ${BASE_URL}/stats
    ${displayed_total}=    Get Text    css:[data-testid="stat-total"] strong
    Should Be Equal As Integers    ${displayed_total}    ${attempts}
    ${displayed_correct}=    Get Text    css:[data-testid="stat-correct"] strong
    Should Be Equal As Integers    ${displayed_correct}    5
    ${displayed_wrong}=    Get Text    css:[data-testid="stat-wrong"] strong
    Should Be Equal As Integers    ${displayed_wrong}    1

Logout Pelo Botão Termina Sessão
    Click Element    css:nav a[href="/logout"]
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Be    ${BASE_URL}/

Ranking Cria Jogadores Reais Se Necessário
    # O resultado visual é comparado com a ordenação calculada a partir de scores.json.
    Garantir Três Jogadores Com Tentativas
    ${expected_top_five}=    Obter Top 5 Esperado
    Go To    ${BASE_URL}/ranking
    ${expected_count}=    Get Length    ${expected_top_five}
    ${displayed_count}=    Get Element Count    css:ol.ranking li
    Should Be Equal As Integers    ${displayed_count}    ${expected_count}
    FOR    ${index}    IN RANGE    ${expected_count}
        ${username}=    Get From List    ${expected_top_five}    ${index}
        ${position}=    Evaluate    int($index) + 1
        Page Should Contain Element    xpath=//ol[contains(@class, 'ranking')]/li[${position}]/span[normalize-space()='${username}']
    END

Página Do Professor Mostra Dados Reais
    Click Element    css:nav a[href="/teacher"]
    ${content}=    Get File    ${ACTIVE_DATA_DIR}${/}attempts.json
    ${all_attempts}=    Evaluate    json.loads($content)    json
    ${attempt_count}=    Get Length    ${all_attempts}
    ${displayed_total}=    Get Text    css:[data-testid="teacher-total"] strong
    Should Be Equal As Integers    ${displayed_total}    ${attempt_count}
    Page Should Contain    Nota sobre TCP

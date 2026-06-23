*** Settings ***
Documentation    [Secções 13, 14 e 38] Validações sem sessão e ações inválidas com sessão.
Resource         resources/common.resource
Suite Setup      Iniciar Ambiente Real Com Registo Novo
Suite Teardown   Terminar Ambiente de Teste

*** Test Cases ***
Validações Sem Login Num Único Fluxo
    # Páginas públicas continuam disponíveis para visitantes.
    Go To    ${BASE_URL}/
    Page Should Contain Element    xpath=//h1[normalize-space()='NetLearn Battle']
    Go To    ${BASE_URL}/login
    Page Should Contain Element    xpath=//h1[normalize-space()='Login']
    Input Text    name=username    utilizador_inexistente
    Input Password    name=password    password_errada
    Click Button    Entrar
    Page Should Contain    Utilizador ou password incorretos.
    Go To    ${BASE_URL}/register
    Input Text    name=username    ${ACTIVE_USER}
    Input Password    name=password    ${SESSION_PASSWORD}
    Click Button    Registar
    Page Should Contain    Esse utilizador já existe.
    Go To    ${BASE_URL}/ranking
    Page Should Contain Element    xpath=//h1[normalize-space()='Ranking Top 5']
    Go To    ${BASE_URL}/rules
    Page Should Contain Element    xpath=//h1[normalize-space()='Regras']
    Go To    ${BASE_URL}/teacher
    Page Should Contain Element    xpath=//h1[normalize-space()='Professor']
    # Estas páginas são bloqueadas e apresentam um aviso, não só um redirecionamento.
    Confirmar Página Protegida Exige Login    /dashboard
    Confirmar Página Protegida Exige Login    /play
    Confirmar Página Protegida Exige Login    /history
    Confirmar Página Protegida Exige Login    /stats

Login Único Para Testes Inválidos Com Sessão
    Fazer Login    ${ACTIVE_USER}    ${SESSION_PASSWORD}
    Page Should Contain Element    xpath=//h1[normalize-space()='O seu painel']

Não Permite Submeter Sem Escolher Opção
    # O atributo HTML required bloqueia o envio antes de criar tentativa.
    ${score_before}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_before}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    Go To    ${BASE_URL}/play
    Click Button    id=level-1
    Wait Until Page Contains    Pergunta
    Click Button    Confirmar resposta
    Location Should Contain    /play
    Page Should Contain Element    xpath=//h1[normalize-space()='Pergunta']
    ${score_after}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_after}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    Should Be Equal As Integers    ${score_after}    ${score_before}
    Should Be Equal As Integers    ${attempts_after}    ${attempts_before}

Índice De Resposta Inválido É Penalizado
    # JavaScript altera o value após a escolha para simular um pedido manipulado.
    ${score_before}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_before}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    Go To    ${BASE_URL}/play
    Click Button    id=level-1
    Wait Until Page Contains    Pergunta
    Select Radio Button    choice    0
    Execute JavaScript    document.querySelector('input[name="choice"]:checked').value = '99';
    Click Button    Confirmar resposta
    Wait Until Page Contains Element    xpath=//h1[normalize-space()='Resposta incorreta']    5 seconds
    ${score_after}=    Obter Score Do Utilizador    ${ACTIVE_USER}
    ${attempts_after}=    Obter Número De Tentativas Do Utilizador    ${ACTIVE_USER}
    ${expected_score}=    Evaluate    int($score_before) - 5
    ${expected_attempts}=    Evaluate    int($attempts_before) + 1
    Should Be Equal As Integers    ${score_after}    ${expected_score}
    Should Be Equal As Integers    ${attempts_after}    ${expected_attempts}
    ${last_attempt}=    Obter Última Tentativa
    ${selected_answer}=    Get From Dictionary    ${last_attempt}    selected_answer
    Should Be Equal    ${selected_answer}    Sem resposta

Resposta Sem Pergunta Redireciona Para Jogar
    # Não existe botão normal para este caso; o formulário criado aqui simula POST inválido.
    Go To    ${BASE_URL}/dashboard
    Execute JavaScript    document.body.insertAdjacentHTML('beforeend', '<form id="invalid-answer" method="post" action="/answer"></form>'); document.getElementById('invalid-answer').submit();
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /play
    Page Should Contain    Escolha um nível antes de responder.

Nível Inexistente Mostra Erro E Mantém Sessão
    # Altera o nível escondido do formulário para testar a validação do servidor.
    Go To    ${BASE_URL}/play
    Execute JavaScript    document.querySelector('input[name="level"]').value = '99';
    Click Button    id=level-1
    Wait Until Page Contains    Não existem perguntas para este nível.
    Go To    ${BASE_URL}/dashboard
    Page Should Contain    Olá, ${ACTIVE_USER}

*** Settings ***
Documentation    [Secções 13, 14 e 38] Testes inválidos independentes, com navegador próprio.
Resource         resources/common.resource
Suite Setup      Iniciar Servidor Real
Suite Teardown   Terminar Servidor De Teste
Test Setup       Preparar Teste Inválido Sem Sessão
Test Teardown    Finalizar Teste Com Navegador

*** Test Cases ***
Login Inicial Para Testes Inválidos Com Sessão
    [Tags]    negativo    autenticacao
    # Cada caso abre um navegador próprio; este caso prova que uma sessão válida é criada.
    Fazer Login    ${ACTIVE_USER}    ${SESSION_PASSWORD}
    Page Should Contain Element    xpath=//h1[normalize-space()='O seu painel']
    Mostrar Validação    Sessão válida criada para testar ações inválidas autenticadas.

Não Permite Submeter Sem Escolher Opção
    [Tags]    negativo    validacao-formulario
    [Setup]    Preparar Teste Inválido Com Sessão
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
    Mostrar Validação    Navegador bloqueou envio sem opção; dados não mudaram.

Índice De Resposta Inválido É Penalizado
    [Tags]    negativo    jogo    seguranca
    [Setup]    Preparar Teste Inválido Com Sessão
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
    Mostrar Validação    Índice inválido foi tratado como sem resposta e penalizado.

Resposta Sem Pergunta Redireciona Para Jogar
    [Tags]    negativo    jogo
    [Setup]    Preparar Teste Inválido Com Sessão
    # Não existe botão normal para este caso; o formulário criado aqui simula POST inválido.
    Go To    ${BASE_URL}/dashboard
    Execute JavaScript    document.body.insertAdjacentHTML('beforeend', '<form id="invalid-answer" method="post" action="/answer"></form>'); document.getElementById('invalid-answer').submit();
    Wait Until Keyword Succeeds    5x    500 milliseconds    Location Should Contain    /play
    Page Should Contain    Escolha um nível antes de responder.
    Mostrar Validação    Pedido sem pergunta foi redirecionado com mensagem de aviso.

Nível Inexistente Mostra Erro E Mantém Sessão
    [Tags]    negativo    jogo
    [Setup]    Preparar Teste Inválido Com Sessão
    # Altera o nível escondido do formulário para testar a validação do servidor.
    Go To    ${BASE_URL}/play
    Execute JavaScript    document.querySelector('input[name="level"]').value = '99';
    Click Button    id=level-1
    Wait Until Page Contains    Não existem perguntas para este nível.
    Go To    ${BASE_URL}/dashboard
    Page Should Contain    Olá, ${ACTIVE_USER}
    Mostrar Validação    Nível inválido mostrou erro e não terminou a sessão.

Validações Sem Login Num Único Fluxo
    [Tags]    negativo    autorizacao    paginas-protegidas
    # Páginas públicas continuam disponíveis para visitantes.
    Go To    ${BASE_URL}/
    Page Should Contain Element    xpath=//h1[normalize-space()='NetLearn Battle']
    Go To    ${BASE_URL}/login
    Page Should Contain Element    xpath=//h1[normalize-space()='Login']
    ${invalid_user}=    Set Variable    inexistente_${ACTIVE_USER}
    Input Text    name=username    ${invalid_user}
    Input Password    name=password    password_errada
    Click Button    Entrar
    Wait Until Page Contains    Utilizador ou password incorretos.    5 seconds
    # O username existe, mas a password está errada: valida a comparação do hash.
    Go To    ${BASE_URL}/login
    Input Text    name=username    ${ACTIVE_USER}
    Input Password    name=password    password_errada
    Click Button    Entrar
    Wait Until Page Contains    Utilizador ou password incorretos.    5 seconds
    Go To    ${BASE_URL}/register
    Input Text    name=username    ab
    Input Password    name=password    ${SESSION_PASSWORD}
    Execute JavaScript    document.querySelector('form').submit();
    Page Should Contain    O utilizador deve ter pelo menos 3 caracteres alfanuméricos.
    Clear Element Text    name=username
    Clear Element Text    name=password
    Input Text    name=username    nome invalido
    Input Password    name=password    ${SESSION_PASSWORD}
    Execute JavaScript    document.querySelector('form').submit();
    Page Should Contain    O utilizador deve ter pelo menos 3 caracteres alfanuméricos.
    Clear Element Text    name=username
    Clear Element Text    name=password
    Input Text    name=username    utilizador_valido
    Input Password    name=password    123
    Execute JavaScript    document.querySelector('form').submit();
    Page Should Contain    A password deve ter pelo menos 4 caracteres.
    Clear Element Text    name=username
    Clear Element Text    name=password
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
    Mostrar Validação    Todas as páginas protegidas recusaram acesso sem login.

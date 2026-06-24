*** Settings ***
Documentation    [Secções 14 e 27] Sessão completa de 5 perguntas num nível.
Resource         resources/common.resource
Suite Setup      Iniciar Ambiente Real Com Sessão Nova
Suite Teardown   Terminar Ambiente de Teste
Test Setup       Abrir Página Inicial

*** Keywords ***
Iniciar Sessão No Nível
    [Arguments]    ${level}
    Go To    ${BASE_URL}/play
    Click Button    id=level-${level}
    Wait Until Page Contains    Pergunta

Responder Pergunta Atual
    [Arguments]    ${answer_index}
    Select Radio Button    choice    ${answer_index}
    Click Button    Confirmar resposta
    Wait Until Page Contains Element    xpath=//h1[normalize-space()='Resposta correta' or normalize-space()='Resposta incorreta']    5 seconds

Avançar Para Próxima Pergunta
    Click Element    link=Próxima pergunta
    Wait Until Page Contains    Pergunta

*** Test Cases ***
Sessão Completa De 5 Perguntas
    [Tags]    sessao    navegacao
    Mostrar Passo    Iniciar sessão no nível 1.
    Iniciar Sessão No Nível    1
    FOR    ${i}    IN RANGE    4
        Responder Pergunta Atual    0
        Avançar Para Próxima Pergunta
    END
    Responder Pergunta Atual    0
    Page Should Contain    Escolher novo nível
    Page Should Contain Element    xpath=//h2[normalize-space()='Resumo da sessão']
    Mostrar Validação    Sessão de 5 perguntas concluída com resumo e opção de novo nível.

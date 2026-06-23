*** Settings ***
Documentation    Testes funcionais simples da interface web NetLearn Battle.
Library          SeleniumLibrary
Suite Setup      Abrir Navegador
Suite Teardown   Close All Browsers

*** Variables ***
${BASE_URL}      http://127.0.0.1:5000

*** Keywords ***
Abrir Navegador
    # A aplicação Flask deve estar a correr antes de iniciar estes testes.
    Open Browser    ${BASE_URL}    chrome
    Maximize Browser Window

*** Test Cases ***
Abrir Página Inicial
    Go To    ${BASE_URL}/
    Title Should Be    NetLearn Battle

Página Inicial Mostra Nome do Projeto
    Go To    ${BASE_URL}/
    Page Should Contain    NetLearn Battle

Abrir Página de Login
    Go To    ${BASE_URL}/login
    Page Should Contain    Login

Abrir Página de Registo
    Go To    ${BASE_URL}/register
    Page Should Contain    Criar conta

Abrir Página de Regras
    Go To    ${BASE_URL}/rules
    Page Should Contain    Regras

Abrir Página de Ranking
    Go To    ${BASE_URL}/ranking
    Page Should Contain    Ranking Top 5

Dashboard Exige Login
    Go To    ${BASE_URL}/dashboard
    Location Should Contain    /login

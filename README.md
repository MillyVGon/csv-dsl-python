# DSL para Manipulação de Arquivos CSV com Lexer e Parser em Python

Este projeto implementa uma Linguagem Específica de Domínio (DSL) voltada para a manipulação de arquivos CSV, desenvolvida em Python utilizando as bibliotecas PLY (Lex/Yacc) e Pandas. A linguagem permite que usuários realizem operações típicas de processamento de dados de forma simples, sem a necessidade de escrever o código diretamente.

A DSL oferece suporte a comandos como carregamento de arquivos, filtragem de dados, seleção de colunas, agrupamento, ordenação, atualização de valores, junção entre tabelas, remoção de duplicatas e exportação para JSON. Internamente, o projeto utiliza uma tabela de símbolos baseada em Árvore Binária de Busca (BST) para gerenciamento de identificadores, além de um analisador léxico e sintático completos.

## Exemplo de Uso
 1 > LOAD "organizations.csv"       
 2 > FILTER "Industry" = "Plastics"
 3 > SELECT "Name", "Website", "Number of employees"
 4 > SORT_BY "Number of employees" ASC
 5 > EXPORT_JSON "filtered_organizations.json"
 6 > exit

[LOAD: Arquivo 'organizations.csv' carregado com sucesso.],
[FILTER: Arquivo filtrado: Industry = Plastics.],
[SELECT: Coluna(s) 'Name, Website, Number of employees' selecionada(s).],
[SORT_BY: Valores da coluna 'Number of employees' ordenados no formato 'ASC'.],
[EXPORT_JSON: Arquivo exportado com sucesso para '\DSL_CSV\src\arqsJSON\filtered_organizations.json'.]
import ply.lex as lex
import ply.yacc as yacc
import pandas as pd 
import os

# ----------------------- LEXER -----------------------
# Lista de tokens
tokens = [
    'ID', 'STRING', 'NUMBER_INT', 'NUMBER_FLOAT',
    'PLUS', 'DASH', 'ASTERISK', 'SLASH', 'EQUALS', 
    'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE', 'COMMA'
]

# Expressões regulares para tokens simples
t_PLUS = r'\+'
t_DASH = r'-'
t_ASTERISK = r'\*'
t_SLASH = r'/'
t_EQ = r'=='
t_NEQ = r'!='
t_LE = r'<='
t_GE = r'>='
t_EQUALS = r'='
t_LT = r'<'
t_GT = r'>'
t_COMMA = r','

# Lista de palavras reservadas
reserved = {
    'LOAD': 'LOAD', 
    'FILTER': 'FILTER',
    'SELECT': 'SELECT',
    'GROUP_BY': 'GROUP_BY',
    'SORT_BY': 'SORT_BY',
    'UPDATE': 'UPDATE',
    'SAVE': 'SAVE',
    'JOIN': 'JOIN',
    'EXPORT_JSON': 'EXPORT_JSON',
    'REMOVE_DUPLICATES': 'REMOVE_DUPLICATES',
    'WHERE': 'WHERE',
    'ON' : 'ON',
    'ASC' : 'ASC',
    'DESC' : 'DESC'
}
tokens = tokens + list(reserved.values())

# Criação do nó da árvore (folha a esquerda e direita)
class TreeNode:
    def __init__(self, name, symbol_type):
        self.name = name
        self.symbol_type = symbol_type
        self.left = None
        self.right = None

# Criação da tabela de símbolos da estrutura da Árvore Binária de Busca (BST)
class SymbolTableBST:
    # Inicializa a tabela de símbolos
    def __init__(self):
        self.root = None

    # Insere um novo símbolo na tabela
    def insert(self, name, symbol_type):
        if self.root is None:
            self.root = TreeNode(name, symbol_type)
        else:
            self._insert(self.root, name, symbol_type)

    # Função recursiva para inserir um novo nó na árvore
    def _insert(self, node, name, symbol_type):
        if name < node.name:
            if node.left is None:
                node.left = TreeNode(name, symbol_type)
            else:
                self._insert(node.left, name, symbol_type)
        elif name > node.name:
            if node.right is None:
                node.right = TreeNode(name, symbol_type)
            else:
                self._insert(node.right, name, symbol_type)
        else:
            print(f"Erro: Identificador '{name}' já declarado")

    # Pesquisa um símbolo na tabela
    def lookup(self, name):
        return self._lookup(self.root, name)
    
    # Função recursiva para buscar um nó
    def _lookup(self, node, name):
        if node is None:
            return None
        if name == node.name:
            return node.symbol_type
        elif name < node.name:
            return self._lookup(node.left, name)
        else:
            return self._lookup(node.right, name)

    # Retorna uma representação da tabela de símbolos
    def __repr__(self):
        return self._repr(self.root)

    # Função recursiva para gerar a string de representação da árvore
    def _repr(self, node):
        if node is None:
            return ""
        left = self._repr(node.left)
        right = self._repr(node.right)
        return f"{left} {node.name}: {node.symbol_type}\n{right}"
    
symbol_table = SymbolTableBST()

for word, symbol_type in reserved.items():
    symbol_table.insert(word, symbol_type)

# Definindo identificadores
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value.upper()
    t.type = symbol_table.lookup(t.value)
    if t.type is None:
        symbol_table.insert(t.value, tokens[0])
        t.type = tokens[0]
    return t

# Identificador de strings
def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

# Expressões regulares para números INT e FLOAT
def t_NUMBER_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_NUMBER_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Definindo ignorância de espaços em branco
t_ignore = ' \t'

# Definindo nova linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Tratamento de erros
def t_error(t):
    print(f"Caractere inválido na posição {t.lexpos}: {t.value[0]}")
    t.lexer.skip(1)

# Construtor do lexer
lexer = lex.lex()

# ----------------------- PARSER -----------------------
df = None

# Função de teste para o lexer
def test_lexer(data):
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

# Inicio do programa
def p_program(p):
    '''program : command'''
    p[0] = p[1]

# Organização dos comandos
def p_command(p):
    '''command : command_list
               | command_list command'''
    p[0] = p[1] if len(p) == 2 else f"{p[1]}, {p[2]}"

# Lista de comandos do programa
def p_command_list(p):
    '''command_list : load 
                    | filter 
                    | select 
                    | group_by 
                    | sort_by 
                    | update 
                    | save 
                    | join 
                    | export_json 
                    | remove_duplicates'''
    p[0] = p[1]

def p_load(p):
    '''load : LOAD STRING'''
    global df
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file = p[2] if os.path.isabs(p[2]) else os.path.join(BASE_DIR, "arqsCSV", p[2])

    try:
        df = pd.read_csv(file, encoding='utf-8')
        p[0] = f"\n[LOAD: Arquivo '{p[2]}' carregado com sucesso.]"
    except FileNotFoundError as e:
        p[0] = f"\n[LOAD: Erro ao carregar o arquivo. Detalhes: {e}.]"

def p_filter(p):
    '''filter : FILTER STRING EQUALS STRING
              | FILTER STRING EQ STRING
              | FILTER STRING rel factor'''
    global df
    column = p[2]
    val = p[4]

    if df is not None:
        if column in df.columns:
            try: 
                if p[3] in ['=', '==']:
                    df = df[df[column] == val]
                elif p[3] in ['!=']:
                    df = df[df[column] != val]
                elif p[3] in ['<']:
                    df = df[df[column] < val]
                elif p[3] in ['<=']:
                    df = df[df[column] <= val]
                elif p[3] in ['>']:
                    df = df[df[column] > val]
                else:
                    df = df[df[column] >= val]
                p[0] = f"\n[FILTER: Arquivo filtrado: {column} {p[3]} {val}.]"
            except KeyError as e:
                p[0] = f"\n[FILTER: Condição inválida! Detalhes: {e}.]"
        else:
            p[0] = f"\n[FILTER: Coluna '{column}' não encontrada no arquivo.]"
    else:
        p[0] = "\n[FILTER: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_select(p):
    '''select : SELECT columns'''
    global df
    columns = p[2]
    
    if df is not None:
        cols = [col.strip() for col in columns.split(",")]
        try:
            df = df[cols]
            p[0] = f"\n[SELECT: Coluna(s) '{columns}' selecionada(s).]"
        except KeyError as e:
            p[0] = f"\n[SELECT: Erro ao acessar uma ou mais colunas. Detalhes: {e}.]"
    else:
        p[0] = "\n[SELECT: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_group_by(p):
    '''group_by : GROUP_BY STRING'''
    global df
    column = p[2]

    if df is not None:
        if column in df.columns:
            try:
                df = df.groupby(f'{column}')
                df = df.size().reset_index(name='Count')
                p[0] = f"\n[GROUP_BY: Dados agrupados por '{column}']"
            except Exception as e:
                p[0] = f"\n[GROUP_BY: Erro ao agrupar dados. Detalhes: {e}]"
        else:
            p[0] = f"\n[GROUP_BY: Coluna '{column}' não encontrada no arquivo.]"
    else:
        p[0] = "\n[GROUP_BY: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_sort_by(p):
    '''sort_by : SORT_BY STRING ASC
              | SORT_BY STRING DESC'''
    global df
    column = p[2]
    
    if df is not None:
        if column in df.columns:
            if p[3] in ['ASC']:
                df = df.sort_values(by=f"{column}", ascending=True)
            else:
                df = df.sort_values(by=f"{column}", ascending=False)
            p[0] = f"\n[SORT_BY: Valores da coluna '{column}' ordenados no formato '{p[3]}'.]"
        else:
            p[0] = f"\n[SORT_BY: Coluna(s) '{column}' selecionada(s).]"
    else:
        p[0] = "\n[SORT_BY: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_update(p):
    '''update : UPDATE STRING EQUALS STRING WHERE STRING EQUALS STRING
              | UPDATE STRING EQUALS factor WHERE STRING EQUALS STRING
              | UPDATE STRING EQUALS STRING PLUS factor WHERE STRING EQUALS STRING
              | UPDATE STRING EQUALS STRING DASH factor WHERE STRING EQUALS STRING
              | UPDATE STRING EQUALS STRING ASTERISK factor WHERE STRING EQUALS STRING
              | UPDATE STRING EQUALS STRING SLASH factor WHERE STRING EQUALS STRING'''
    global df
    column = p[2]
    
    if df is not None:
        if column in df.columns:
            try: 
                if len(p) == 9:
                    df.loc[df[f"{p[6]}"] == f"{p[8]}", f"{column}"] = p[4]
                else:
                    if p[5] in ['+']:
                        df.loc[df[f"{p[8]}"] == f"{p[10]}", f"{column}"] += p[6]
                    elif p[5] in ['-']:
                        df.loc[df[f"{p[8]}"] == f"{p[10]}", f"{column}"] -= p[6]
                    elif p[5] in ['*']:
                        df.loc[df[f"{p[8]}"] == f"{p[10]}", f"{column}"] *= p[6]
                    else:
                        df.loc[df[f"{p[8]}"] == f"{p[10]}", f"{column}"] /= p[6]
                p[0] = f"\n[UPDATE: Tabela {column} atualizada.]"
            except KeyError as e:
                p[0] = f"\n[UPDATE: Condição inválida! Detalhes: {e}.]"
        else:
            p[0] = f"\n[UPDATE: Coluna '{column}' não encontrada no arquivo.]"
    else:
        p[0] = "\n[UPDATE: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_save(p):
    '''save : SAVE STRING'''
    global df
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file = p[2] if os.path.isabs(p[2]) else os.path.join(BASE_DIR, "arqsCSV", p[2])

    if df is not None:
        try:
            df.to_csv(file, index=False, encoding='utf-8')
            p[0] = f"\n[SAVE: Arquivo salvado em: '{file}'.]"
        except FileNotFoundError as e:
            p[0] = f"\n[SAVE: Erro ao salvar o arquivo. Detalhes: {e}.]"
    else:
        p[0] = "\n[SAVE: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_join(p):
    '''join : JOIN STRING ON STRING'''
    global df
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file = p[2] if os.path.isabs(p[2]) else os.path.join(BASE_DIR, "arqsCSV", p[2])
    column = p[4]
    
    if df is not None:
        try:
            df2 = pd.read_csv(file, encoding='utf-8')

            if column in df.columns and column in df2.columns:
                df = pd.merge(df, df2, on=f"{column}", how='inner')
                p[0] = f"\n[JOIN: Arquivo '{p[2]}' unido com sucesso na coluna '{column}']"
            else:
                p[0] = f"\n[JOIN: Coluna '{column}' não encontrada em ambos os arquivos.]"
        except FileNotFoundError:
            p[0] = f"\n[JOIN: Arquivo '{column}' não encontrado.]"
        except Exception as e:
            p[0] = f"\n[JOIN: Erro ao realizar a junção. Detalhes: {e}]"
    else:
        p[0] = "\n[JOIN: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_export_json(p):
    '''export_json : EXPORT_JSON STRING'''
    global df
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file = p[2] if os.path.isabs(p[2]) else os.path.join(BASE_DIR, "arqsJSON", p[2])
    
    if df is not None:
        try:
            df.to_json(file, orient='records', indent=4)
            p[0] = f"\n[EXPORT_JSON: Arquivo exportado com sucesso para '{file}'.]"
        except Exception as e:
            p[0] = f"\n[EXPORT_JSON: Erro ao exportar para JSON. Detalhes: {e}.]"
    else:
        p[0] = "\n[EXPORT_JSON: Nenhum arquivo carregado. Use LOAD primeiro.]"

def p_remove_duplicates(p):
    '''remove_duplicates : REMOVE_DUPLICATES STRING'''
    global df
    column = p[2]
    
    if df is not None:
        if column in df.columns:
            lines_bef = len(df)
            df.drop_duplicates(subset=f"{column}", keep='first', inplace=True)
            lines_aft = len(df)
            lines_rem = lines_bef - lines_aft
            p[0] = f"\n[REMOVE_DUPLICATES: {lines_rem} duplicata(s) removida(s) com base na coluna '{column}']"
        else:
            p[0] = f"\n[REMOVE_DUPLICATES: Coluna '{column}' não encontrada no arquivo.]"
    else:
        p[0] = "\n[REMOVE_DUPLICATES: Nenhum arquivo carregado. Use LOAD primeiro.]"

# Define uma ou mais colunas
def p_columns(p):
    '''columns : STRING
               | STRING COMMA columns'''
    p[0] = p[1] if len(p) == 2 else f"{p[1]}, {p[3]}"

# Define os operadores relacionais
def p_rel(p):
    '''rel : EQUALS
           | EQ
           | NEQ
           | LT
           | LE
           | GT
           | GE'''
    p[0] = p[1]
    
# Define os operandos das expressões
def p_factor(p):
    '''factor : NUMBER_INT
              | NUMBER_FLOAT'''
    p[0] = p[1]
     
# Tratamento de erros de sintaxe
def p_error(p):
    print(f"Erro de sintaxe na posição {p.lexpos}: {p.value}" if p else "Erro de sintaxe no final da entrada")

# Construtor do parser
parser = yacc.yacc()

# Função de teste para o parser
def test_parser(data):
    result = parser.parse(data)
    return result

# Função para realizar a entrada de dados
def input_data():
    print("Bem vindo! Por favor, insira seu código linha por linha.")
    print("COMANDOS EXISTENTES:\n"
          '1. LOAD "caminho": Carregar um arquivo CSV para manipulação.\n'
          '2. FILTER "coluna" "condição": Filtrar linhas com base em uma condição específica.\n'
          '3. SELECT "coluna(s)": Selecionar colunas para visualização ou exportação.\n'
          '4. GROUP_BY "coluna": Agrupar os dados pela coluna especificada.\n'
          '5. SORT_BY "coluna" ASC/DESC: Ordenar os dados de modo Ascendente ou Descendente, de acordo com uma coluna específica.\n'
          '6. UPDATE "coluna" "novo_valor" WHERE "condição": Atualizar valores em uma coluna com base em uma condição.\n'
          '7. SAVE "caminho": Salvar o arquivo CSV após as modificações.\n'
          '8. JOIN "outro_arquivo" ON "coluna": Realizar um join com outro arquivo CSV, baseado em uma coluna comum.\n'
          '9. EXPORT_JSON "caminho": Exportar o arquivo CSV modificado para o formato JSON.\n'
          '10. REMOVE_DUPLICATES "coluna": Remover linhas duplicadas com base em uma coluna.')
    print("Digite 'exit' em uma linha separada para finalizar a entrada.")
    lines = ""
    line_no = 1
    line = input(f"{line_no:2d} > ")
    while line.lower() != "exit":
        lines = lines + "\n" + line
        line_no = line_no + 1
        line = input(f"{line_no:2d} > ")
    return lines

# Função principal
def main():
    data = input_data()
    result = test_parser(data)
    print(result)

if __name__ == "__main__":
    main()
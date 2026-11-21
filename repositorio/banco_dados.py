import sqlite3
from dominio.entidades import Usuario
from dominio.enums import PapelUsuario

def inicializar_banco():
    # Cria (ou conecta) ao arquivo do banco de dados
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    # Cria a tabela de usuários se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            nome TEXT,
            email TEXT,
            papel TEXT,
            localizacao TEXT,
            ativo BOOLEAN
        )
    ''')
    
    # Verifica se já existem usuários cadastrados
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        usuarios_iniciais = [
            ("u1", "ADM", "", "", "", True),
            ("u2", "Giovanni", "giovanni@aosltd.net", "gerente", "brasil", True),
            ("u3", "Augusto", "augusto@aosltd.net", "ceo", "brasil", True),
            ("u4", "Gustavo", "gustavo@aosltd.net", "ceo", "brasil", True),
        ]
        cursor.executemany('INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?)', usuarios_iniciais)
        conn.commit()
    
    conn.close()

def buscar_todos_usuarios():
    conn = sqlite3.connect('estoque.db')
    conn.row_factory = sqlite3.Row # Permite acessar os campos pelo nome
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    linhas = cursor.fetchall()
    conn.close()
    
    return [dict(linha) for linha in linhas]

def buscar_usuario_por_id(id_usuario):
    conn = sqlite3.connect('estoque.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id_usuario,))
    linha = cursor.fetchone()
    conn.close()
    
    return dict(linha) if linha else None

def inicializar_tabela_categorias():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            nome TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def buscar_categorias():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nome FROM categorias ORDER BY nome ASC')
    linhas = cursor.fetchall()
    conn.close()
    return [linha[0] for linha in linhas]

def salvar_categoria(nome: str):
    if not nome.strip():
        return
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    # O "INSERT OR IGNORE" evita erro se a categoria já existir
    cursor.execute('INSERT OR IGNORE INTO categorias (nome) VALUES (?)', (nome.strip(),))
    conn.commit()
    conn.close()
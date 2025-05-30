import sqlite3
import pandas as pd
import os

# Define o nome do arquivo do banco de dados
DB_NAME = 'academia.db'
# Define o caminho para a pasta de dados CSV
DATA_FOLDER = 'data'

def conectar_bd():
    """Conecta ao banco de dados SQLite."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def criar_tabelas(conn):
    """Cria as tabelas no banco de dados."""
    cursor = conn.cursor()

    # Tabela clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        telefone TEXT,
        data_nascimento DATE
    )
    """)
    print("Tabela 'clientes' criada ou já existente.")

    # Tabela instrutores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instrutores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        especialidade TEXT
    )
    """)
    print("Tabela 'instrutores' criada ou já existente.")

    # Tabela planos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        preco_mensal REAL NOT NULL,
        duracao_meses INTEGER NOT NULL
    )
    """)
    print("Tabela 'planos' criada ou já existente.")

    # Tabela exercicios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        grupo_muscular TEXT
    )
    """)
    print("Tabela 'exercicios' criada ou já existente.")

    # Tabela treinos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        instrutor_id INTEGER NOT NULL,
        plano_id INTEGER NOT NULL,
        data_inicio DATE NOT NULL,
        data_fim DATE,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
        FOREIGN KEY (instrutor_id) REFERENCES instrutores (id) ON DELETE SET NULL,
        FOREIGN KEY (plano_id) REFERENCES planos (id) ON DELETE RESTRICT
    )
    """)
    print("Tabela 'treinos' criada ou já existente.")

    # Tabela treino_exercicio
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treino_exercicio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        treino_id INTEGER NOT NULL,
        exercicio_id INTEGER NOT NULL,
        series INTEGER,
        repeticoes TEXT,
        FOREIGN KEY (treino_id) REFERENCES treinos (id) ON DELETE CASCADE,
        FOREIGN KEY (exercicio_id) REFERENCES exercicios (id) ON DELETE CASCADE
    )
    """)
    print("Tabela 'treino_exercicio' criada ou já existente.")

    # Tabela pagamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        data_pagamento DATE NOT NULL,
        valor REAL NOT NULL,
        pago BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
    )
    """)
    print("Tabela 'pagamentos' criada ou já existente.")

    conn.commit()
    print("Criação/verificação de tabelas concluída.")


def popular_tabela_csv(conn, nome_tabela, nome_arquivo_csv):
    """Popula uma tabela com dados de um arquivo CSV."""
    caminho_csv = os.path.join(DATA_FOLDER, nome_arquivo_csv)
    if not os.path.exists(caminho_csv):
        print(f"AVISO: Arquivo CSV '{caminho_csv}' não encontrado. Tabela '{nome_tabela}' não populada.")
        return

    try:
        # Define colunas que devem ser tratadas como data
        date_columns = []
        if nome_tabela == 'clientes':
            date_columns = ['data_nascimento']
        elif nome_tabela == 'pagamentos':
            date_columns = ['data_pagamento']
        
        # Lê o CSV para um DataFrame do pandas
        # parse_dates tentará converter as colunas especificadas para datetime objects
        df = pd.read_csv(caminho_csv, parse_dates=date_columns)

        # Tratamento especial para colunas booleanas
        if nome_tabela == 'pagamentos' and 'pago' in df.columns:
            # Mapeia diversos formatos de booleano para 0 ou 1
            map_bool = {'True': 1, 'False': 0, 'sim': 1, 'nao': 0, '1': 1, '0': 0, 1: 1, 0: 0,
                        'TRUE': 1, 'FALSE': 0, 'Sim': 1, 'Nao': 0, 'SIM': 1, 'NAO': 0}
            # Converte para string primeiro para garantir que o map funcione com '1'/'0' do CSV
            df['pago'] = df['pago'].astype(str).map(map_bool).fillna(0).astype(int)


        # Remove a coluna 'id' do DataFrame se ela existir no CSV,
        # pois o 'id' da tabela é AUTOINCREMENT.
        # Se o seu CSV já tem IDs que você quer manter E eles são únicos E a tabela está vazia,
        # você pode precisar de uma lógica diferente ou remover o AUTOINCREMENT da PK.
        # Para este exemplo, vamos assumir que os IDs serão gerados pelo banco.
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
            print(f"Coluna 'id' removida do CSV para a tabela '{nome_tabela}' (será autoincrementada).")

        # Insere os dados do DataFrame na tabela SQL
        # if_exists='append': adiciona os dados. Se a tabela já tiver dados, eles serão mantidos.
        #                    Se houver conflitos de chave única (ex: email duplicado em clientes),
        #                    a inserção da linha conflitante falhará.
        # index=False: não escreve o índice do DataFrame como uma coluna na tabela SQL.
        df.to_sql(nome_tabela, conn, if_exists='append', index=False)
        
        print(f"Dados do arquivo '{nome_arquivo_csv}' inseridos na tabela '{nome_tabela}' com sucesso.")

    except pd.errors.EmptyDataError:
        print(f"AVISO: O arquivo CSV '{caminho_csv}' está vazio. Tabela '{nome_tabela}' não populada.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo CSV '{caminho_csv}' não encontrado!")
    except Exception as e:
        print(f"Ocorreu um erro ao popular a tabela '{nome_tabela}' com o arquivo '{nome_arquivo_csv}': {e}")


if __name__ == '__main__':
    conn = None
    try:
        conn = conectar_bd()
        print(f"Conectado ao banco de dados '{DB_NAME}' com sucesso.")

        # 1. Criar as tabelas
        criar_tabelas(conn)

        # 2. Popular as tabelas a partir dos CSVs
        print("\nIniciando povoamento das tabelas a partir de arquivos CSV...")
        # (Você especificou CSVs para estas tabelas)
        popular_tabela_csv(conn, 'clientes', 'clientes.csv')
        popular_tabela_csv(conn, 'instrutores', 'instrutores.csv')
        popular_tabela_csv(conn, 'planos', 'planos.csv')
        popular_tabela_csv(conn, 'exercicios', 'exercicios.csv')
        popular_tabela_csv(conn, 'pagamentos', 'pagamentos.csv')
        # Adicione chamadas para outras tabelas se tiver CSVs para elas

        print("\nPovoamento de tabelas concluído.")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro com o SQLite: {e}")
    except Exception as e:
        print(f"Ocorreu um erro geral: {e}")
    finally:
        if conn:
            conn.close()
            print(f"\nConexão com o banco de dados '{DB_NAME}' fechada.")
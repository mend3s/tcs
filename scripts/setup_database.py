import sqlite3
import pandas as pd
import os

# --- Caminhos (mantendo a lógica, mas um iniciante poderia simplificar ainda mais) ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_NAME = os.path.join(PROJECT_ROOT, 'academia.db')
DATA_FOLDER = os.path.join(PROJECT_ROOT, 'data')
# --- Fim dos Caminhos ---

def conectar_bd():
    """Conecta ao banco de dados SQLite."""
    print(f"Tentando conectar ao banco de dados: {DB_NAME}")
    conn = sqlite3.connect(DB_NAME)
    print("Conexão estabelecida.")
    return conn

def criar_tabelas(conn):
    """Cria as tabelas no banco de dados de forma simples."""
    cursor = conn.cursor()
    print("\n--- Criando Tabelas (se não existirem) ---")

    # Tabela clientes (ajustada conforme sua última especificação)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER,
        sexo TEXT,
        email TEXT UNIQUE NOT NULL,
        telefone TEXT,
        plano_id INTEGER,
        instrutor_id INTEGER,
        treino_id INTEGER,
        FOREIGN KEY (plano_id) REFERENCES planos (id) ON DELETE SET NULL,
        FOREIGN KEY (instrutor_id) REFERENCES instrutores (id) ON DELETE SET NULL,
        FOREIGN KEY (treino_id) REFERENCES treinos (id) ON DELETE SET NULL
    )
    """)
    print("- Tabela 'clientes' verificada/criada.")

    # Tabela instrutores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instrutores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        especialidade TEXT
    )
    """)
    print("- Tabela 'instrutores' verificada/criada.")

    # Tabela planos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        preco_mensal REAL NOT NULL,
        duracao_meses INTEGER NOT NULL
    )
    """)
    print("- Tabela 'planos' verificada/criada.")

    # Tabela exercicios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        grupo_muscular TEXT
    )
    """)
    print("- Tabela 'exercicios' verificada/criada.")

    # Tabela treinos (com campos adicionais para nome, objetivo, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_treino TEXT,
        cliente_id INTEGER,
        instrutor_id INTEGER,
        plano_id INTEGER,
        data_inicio DATE,
        data_fim DATE,
        objetivo TEXT,
        tipo_treino TEXT,
        descricao_treino TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE SET NULL,
        FOREIGN KEY (instrutor_id) REFERENCES instrutores (id) ON DELETE SET NULL,
        FOREIGN KEY (plano_id) REFERENCES planos (id) ON DELETE SET NULL
    )
    """)
    print("- Tabela 'treinos' verificada/criada.")

    # Tabela treino_exercicio (ajustada para colunas do CSV e da tabela)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treino_exercicio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        treino_id INTEGER NOT NULL,
        exercicio_id INTEGER NOT NULL,
        series TEXT,
        repeticoes TEXT,
        carga TEXT,
        descanso_segundos INTEGER,
        ordem INTEGER,
        observacoes_exercicio TEXT,
        FOREIGN KEY (treino_id) REFERENCES treinos (id) ON DELETE CASCADE,
        FOREIGN KEY (exercicio_id) REFERENCES exercicios (id) ON DELETE CASCADE
    )
    """)
    print("- Tabela 'treino_exercicio' verificada/criada.")

    # Tabela pagamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        data_pagamento DATE NOT NULL,
        valor REAL NOT NULL,
        pago BOOLEAN NOT NULL DEFAULT 0
    )
    """)
    # Removida a FK para clientes na tabela pagamentos para simplificar e evitar dependência na ordem de população
    # Em um sistema real, a FK é importante: FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
    print("- Tabela 'pagamentos' verificada/criada.")

    conn.commit()
    print("--- Criação de tabelas concluída. ---")


def popular_tabela_csv_simples(conn, nome_tabela, nome_arquivo_csv):
    """Popula uma tabela com dados de um arquivo CSV de forma SIMPLIFICADA."""
    caminho_csv = os.path.join(DATA_FOLDER, nome_arquivo_csv)
    print(f"\nProcessando: Tabela '{nome_tabela}' com arquivo '{nome_arquivo_csv}'")

    if not os.path.exists(caminho_csv):
        print(f"  AVISO: Arquivo CSV '{nome_arquivo_csv}' NÃO ENCONTRADO em '{DATA_FOLDER}'. Tabela '{nome_tabela}' não será populada.")
        return

    try:
        # Define colunas de data para parsing, se houver
        date_cols = []
        if nome_tabela == 'pagamentos': # Apenas 'pagamentos' tem data no CSV, conforme exemplo
            date_cols = ['data_pagamento']

        df = pd.read_csv(caminho_csv, parse_dates=date_cols, dayfirst=(nome_tabela == 'pagamentos'))
        print(f"  Lido CSV '{nome_arquivo_csv}'. {len(df)} linhas encontradas.")

        if df.empty:
            print(f"  AVISO: O arquivo CSV '{nome_arquivo_csv}' está vazio. Nada para inserir em '{nome_tabela}'.")
            return

        # Para a tabela 'treino_exercicio', o CSV pode ter colunas extras como 'treino' e 'exercicio' (nomes)
        # A tabela SQL espera: treino_id, exercicio_id, series, repeticoes, carga, etc.
        if nome_tabela == 'treino_exercicio':
            colunas_sql_treino_exercicio = ['treino_id', 'exercicio_id', 'series', 'repeticoes', 'carga', 'descanso_segundos', 'ordem', 'observacoes_exercicio']
            # Seleciona apenas as colunas do CSV que existem na definição da tabela SQL
            colunas_para_usar = [col for col in colunas_sql_treino_exercicio if col in df.columns]
            print(f"  Para 'treino_exercicio', usando colunas do CSV: {colunas_para_usar}")
            if not all(item in df.columns for item in ['treino_id', 'exercicio_id']):
                 print(f"  ERRO: CSV para 'treino_exercicio' não tem 'treino_id' ou 'exercicio_id'. Não é possível popular.")
                 return
            df = df[colunas_para_usar]


        # Converte 'pago' para 0 ou 1 na tabela de pagamentos
        if nome_tabela == 'pagamentos' and 'pago' in df.columns:
            map_boolean = {'True': 1, 'False': 0, 'sim': 1, 'nao': 0, '1': 1, '0': 0, 1:1, 0:0}
            df['pago'] = df['pago'].astype(str).str.strip().str.lower().map(map_boolean).fillna(0).astype(int)
            print("  Coluna 'pago' convertida para 0/1.")

        # Remove a coluna 'id' do DataFrame se ela existir no CSV, pois o banco gerará o ID.
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
            print("  Coluna 'id' removida do DataFrame (o banco irá gerar).")

        df.to_sql(nome_tabela, conn, if_exists='append', index=False)
        print(f"  SUCESSO: Dados de '{nome_arquivo_csv}' inseridos em '{nome_tabela}'.")

    except Exception as e:
        print(f"  ERRO ao processar '{nome_arquivo_csv}' para a tabela '{nome_tabela}': {e}")
        # Para um iniciante, mostrar o traceback pode ser útil ou confuso.
        # traceback.print_exc() # Descomente para ver o erro detalhado


if __name__ == '__main__':
    print("--- Iniciando Script de Setup do Banco de Dados (Versão Simples) ---")
    

    # if os.path.exists(DB_NAME):
    #     print(f"AVISO: Banco de dados '{DB_NAME}' existente será removido para recriação.")
    #     os.remove(DB_NAME)

    conn = None # Inicializa a variável de conexão
    try:
        conn = conectar_bd()
        criar_tabelas(conn)

        print("\n--- Populando Tabelas com Dados dos CSVs (se existirem) ---")
        # A ordem aqui pode ser importante se houver chaves estrangeiras estritas
        # e os IDs nos CSVs forem IDs literais (não nomes para lookup).
        # 1. Tabelas sem dependências diretas nos CSVs (ou com IDs já resolvidos nos CSVs)
        popular_tabela_csv_simples(conn, 'instrutores', 'instrutores.csv')
        popular_tabela_csv_simples(conn, 'planos', 'planos.csv')
        popular_tabela_csv_simples(conn, 'exercicios', 'exercicios.csv')
        
        # 2. Tabela clientes (pode referenciar planos, instrutores, treinos)
        # Certifique-se que os IDs em clientes_academia.csv para plano_id, instrutor_id, treino_id
        # já existem nas respectivas tabelas se as FKs forem estritas.
        # Para esta versão simples, ON DELETE SET NULL nas FKs de clientes dá mais flexibilidade.
        popular_tabela_csv_simples(conn, 'clientes', 'clientes_academia.csv')

        # 3. Tabela treinos (NÃO ESTÁ SENDO POPULADA POR CSV NESTE SCRIPT)
        # Se 'treino_exercicios.csv' depende de 'treinos.id', a tabela 'treinos'
        # precisa ser populada ANTES de 'treino_exercicio'.
        print("\nAVISO IMPORTANTE: A tabela 'treinos' não está sendo populada por CSV neste script.")
        print("Para que 'treino_exercicio' seja populada corretamente, a tabela 'treinos' deve")
        print("conter os 'treino_id's referenciados no arquivo 'treino_exercicios.csv'.")
        # Você precisaria de um 'treinos.csv' e uma chamada como:
        # popular_tabela_csv_simples(conn, 'treinos', 'treinos.csv')

        # 4. Tabela treino_exercicio (depende de 'treinos.id' e 'exercicios.id')
        popular_tabela_csv_simples(conn, 'treino_exercicio', 'treino_exercicios.csv')
        
        # 5. Tabela pagamentos (depende de 'clientes.id')
        # Removi a FK na criação para simplificar a ordem, mas em produção ela é vital.
        # Se a FK estivesse ativa, 'clientes' precisaria ser populada antes.
        popular_tabela_csv_simples(conn, 'pagamentos', 'pagamentos.csv')
        
        print("\n--- Povoamento de tabelas (tentativa) concluído. ---")

    except sqlite3.Error as e_sqlite:
        print(f"ERRO SQLite durante o setup: {e_sqlite}")
    except Exception as e_geral:
        print(f"ERRO GERAL durante o setup: {e_geral}")
    finally:
        if conn:
            conn.close()
            print(f"\nConexão com o banco de dados '{DB_NAME}' fechada.")
    print("--- Script de Setup Finalizado. ---")

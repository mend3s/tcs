import sqlite3 # Se não estiver já no topo do seu database.py

# --- Cole aqui as definições do seu arquivo database.py ---
# Ou, se este for um novo script, importe as funções:
# from database_module import (DB_NAME, conectar_bd, _fetch_all, _fetch_one,
#                            get_all_clients, get_all_plans, get_pagamentos_by_client_id,
#                            get_all_exercises, get_clients_with_current_plan_info,
#                            get_workouts_with_exercises, get_payment_stats_for_client,
#                            get_active_client_count_per_instructor)
# Certifique-se que as funções _fetch_all e _fetch_one têm o tratamento de erro que imprime o erro SQLite específico.

# Exemplo (colocando as definições de função aqui para ser auto-contido,
# mas no seu caso elas já existem no seu database.py):

DB_NAME = 'academia.db' # Certifique-se que este é o nome correto e o arquivo está acessível

def conectar_bd():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Para acessar colunas pelo nome
    return conn

def _fetch_all(query, params=None):
    """Executa uma query e retorna todos os resultados."""
    conn = None
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    except sqlite3.Error as e:
        print(f"!!!!!!!! ERRO DE BANCO DE DADOS (_fetch_all) !!!!!!!!")
        print(f"Query: {query}")
        print(f"Params: {params}")
        print(f"Erro SQLite específico: {type(e).__name__} - {e}")
        return [] # Retorna lista vazia em caso de erro
    finally:
        if conn:
            conn.close()

def _fetch_one(query, params=None):
    """Executa uma query e retorna um único resultado."""
    conn = None
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return dict(result) if result else None
    except sqlite3.Error as e:
        print(f"!!!!!!!! ERRO DE BANCO DE DADOS (_fetch_one) !!!!!!!!")
        print(f"Query: {query}")
        print(f"Params: {params}")
        print(f"Erro SQLite específico: {type(e).__name__} - {e}")
        return None # Retorna None em caso de erro
    finally:
        if conn:
            conn.close()

# --- Suas funções de busca de dados (get_all_clients, etc.) ---
# Copie-as do seu arquivo database.py original para cá se este for um novo script,
# ou simplesmente use-as se você estiver modificando o if __name__ == '__main__' do database.py

def get_all_clients():
    """Retorna todos os clientes."""
    query = "SELECT id, nome, email, telefone, data_nascimento FROM clientes ORDER BY nome;"
    return _fetch_all(query)

def get_all_plans():
    """Retorna todos os planos."""
    query = "SELECT id, nome, preco_mensal, duracao_meses FROM planos ORDER BY nome;"
    return _fetch_all(query)

def get_all_intrutores():
    """Retorna todos os instrutores."""
    query = "SELECT id, nome, especialidade FROM instrutores ORDER BY nome;"
    return _fetch_all(query)

def get_pagamentos_by_client_id(cliente_id):
    """Retorna todos os pagamentos de um cliente específico."""
    query = """
        SELECT p.id, p.cliente_id, c.nome as cliente_nome, p.data_pagamento, p.valor, p.pago
        FROM pagamentos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.cliente_id = ?
        ORDER BY p.data_pagamento DESC;
    """
    return _fetch_all(query, (cliente_id,))

# Adicione outras funções GET que você queira testar aqui...
# Ex: get_all_exercises, get_clients_with_current_plan_info, etc.

# --- Bloco Principal para Testar as Buscas ---
if __name__ == '__main__':
    print(f"--- Iniciando busca de dados no banco '{DB_NAME}' ---")
    print("Lembre-se: este script assume que o banco de dados já existe e está populado.\n")

    # 1. Testar listagem de todos os clientes
    print("--- Listando Clientes ---")
    clientes = get_all_clients()
    if clientes: # Verifica se a lista não é None e não está vazia
        for cliente in clientes:
            print(f"  ID: {cliente['id']}, Nome: {cliente['nome']}, Email: {cliente['email']}")
    elif isinstance(clientes, list) and not clientes: # Se for uma lista vazia
        print("  Nenhum cliente encontrado (tabela vazia ou erro na busca - verifique msgs acima).")
    # Se _fetch_all retorna None em erro, você precisaria de: else: print("Erro ao buscar clientes.")
    print("-" * 40)

    # 2. Testar listagem de todos os planos
    print("\n--- Listando Planos ---")
    planos = get_all_plans()
    if planos:
        for plano in planos:
            print(f"  ID: {plano['id']}, Nome: {plano['nome']}, Preço: R${plano['preco_mensal']:.2f}, Duração: {plano['duracao_meses']} meses")
    elif isinstance(planos, list) and not planos:
        print("  Nenhum plano encontrado (tabela vazia ou erro na busca - verifique msgs acima).")
    print("-" * 40)

    # 2.1. Testar listagem de todos os instrutores
    print("\n--- Listando Instrutores ---")
    instrutores = get_all_intrutores()
    if instrutores:
        for instrutores in instrutores:
            print(f"  ID: {instrutores['id']}, Nome: {instrutores['nome']}, especialidade: {instrutores['especialidade']}")
    elif isinstance(instrutores, list) and not instrutores:
        print("  Nenhum instrutor encontrado (tabela vazia ou erro na busca - verifique msgs acima).")
    print("-" * 40)

    # 3. Testar pagamentos de um cliente específico (ex: cliente com ID 1)
    #    Certifique-se que existe um cliente com ID 1 e alguns pagamentos para ele no seu DB.
    CLIENTE_ID_PARA_TESTE = 1
    print(f"\n--- Listando Pagamentos do Cliente ID: {CLIENTE_ID_PARA_TESTE} ---")
    pagamentos = get_pagamentos_by_client_id(CLIENTE_ID_PARA_TESTE)
    if pagamentos:
        for pagamento in pagamentos:
            print(f"  ID Pag: {pagamento['id']}, Cliente: {pagamento['cliente_nome']}, Data: {pagamento['data_pagamento']}, Valor: R${pagamento['valor']:.2f}, Pago: {pagamento['pago']}")
    elif isinstance(pagamentos, list) and not pagamentos:
        print(f"  Nenhum pagamento encontrado para o cliente ID {CLIENTE_ID_PARA_TESTE} (cliente sem pagamentos, cliente não existe ou erro na busca - verifique msgs acima).")
    print("-" * 40)

    # Adicione aqui chamadas para outras funções de busca que você implementou e quer testar:
    # print("\n--- Listando Exercícios ---")
    # exercicios = get_all_exercises()
    # if exercicios:
    #     for ex in exercicios:
    #         print(f"  ID: {ex['id']}, Nome: {ex['nome']}, Grupo: {ex['grupo_muscular']}")
    # ... e assim por diante para as outras funções ...

    print("\n--- Busca de dados concluída ---")
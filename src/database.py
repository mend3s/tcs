import sqlite3
import os

# --- DEFINIÇÃO ROBUSTA DE CAMINHOS ---
# Diretório onde este script (database.py) está localizado
# Se database.py estiver em uma pasta 'src', SCRIPT_DIR será '.../seu_projeto/src'
SCRIPT_DIR_DB = os.path.dirname(os.path.abspath(__file__))

# Diretório raiz do projeto (um nível acima se database.py estiver em 'src', ou o mesmo se estiver na raiz)
# Ajuste conforme a estrutura do seu projeto. Se database.py está na raiz, PROJECT_ROOT_DB = SCRIPT_DIR_DB
PROJECT_ROOT_DB = os.path.dirname(SCRIPT_DIR_DB) # Assume que database.py está em 'src'
# Se database.py estiver na raiz do projeto, use:
# PROJECT_ROOT_DB = SCRIPT_DIR_DB

DB_NAME = os.path.join(PROJECT_ROOT_DB, 'academia.db')

def conectar_bd():
    """Conecta ao banco de dados SQLite e configura row_factory."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row # Para acessar colunas pelo nome
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados '{DB_NAME}': {e}")
        raise # Re-levanta a exceção para que o chamador saiba que falhou

def _fetch_all(query, params=None, conn_externa=None):
    """Executa uma query e retorna todos os resultados como lista de dicionários."""
    conn = conn_externa if conn_externa else conectar_bd()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    except sqlite3.Error as e:
        print(f"Erro em _fetch_all com query '{query[:50]}...': {e}")
        return [] # Retorna lista vazia em caso de erro
    finally:
        if not conn_externa and conn: # Só fecha se a conexão foi aberta nesta função
            conn.close()

def _fetch_one(query, params=None, conn_externa=None):
    """Executa uma query e retorna um único resultado como dicionário."""
    conn = conn_externa if conn_externa else conectar_bd()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return dict(result) if result else None
    except sqlite3.Error as e:
        print(f"Erro em _fetch_one com query '{query[:50]}...': {e}")
        return None # Retorna None em caso de erro
    finally:
        if not conn_externa and conn:
            conn.close()

def _execute_query(query, params=None, conn_externa=None):
    """Executa uma query de modificação (INSERT, UPDATE, DELETE)."""
    conn = conn_externa if conn_externa else conectar_bd()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid # Útil para INSERTs com autoincrement
    except sqlite3.Error as e:
        print(f"Erro em _execute_query com query '{query[:50]}...': {e}")
        if conn and not conn_externa: # Só faz rollback se a conexão foi aberta aqui e ainda existe
             conn.rollback()
        return None
    finally:
        if not conn_externa and conn:
            conn.close()

# --- Funções para Clientes ---
def get_all_clients():
    """Retorna todos os clientes com as novas colunas."""
    query = """
        SELECT id, nome, idade, sexo, email, telefone, plano_id, instrutor_id, treino_id
        FROM clientes ORDER BY nome;
    """
    return _fetch_all(query)

def add_client(nome, email, idade=None, sexo=None, telefone=None, plano_id=None, instrutor_id=None, treino_id=None):
    """Adiciona um novo cliente."""
    query = """
        INSERT INTO clientes (nome, idade, sexo, email, telefone, plano_id, instrutor_id, treino_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (nome, idade, sexo, email, telefone, plano_id, instrutor_id, treino_id)
    return _execute_query(query, params)

# --- Funções para Instrutores ---
def get_all_instructors():
    """Retorna todos os instrutores."""
    query = "SELECT id, nome, especialidade FROM instrutores ORDER BY nome;"
    return _fetch_all(query)

def add_instructor(nome, especialidade=None):
    """Adiciona um novo instrutor."""
    query = "INSERT INTO instrutores (nome, especialidade) VALUES (?, ?)"
    return _execute_query(query, (nome, especialidade))

# --- Funções para Planos ---
def get_all_plans():
    """Retorna todos os planos."""
    query = "SELECT id, nome, preco_mensal, duracao_meses FROM planos ORDER BY nome;"
    return _fetch_all(query)

def add_plan(nome, preco_mensal, duracao_meses):
    """Adiciona um novo plano."""
    query = "INSERT INTO planos (nome, preco_mensal, duracao_meses) VALUES (?, ?, ?)"
    return _execute_query(query, (nome, preco_mensal, duracao_meses))

# --- Funções para Exercícios ---
def get_all_exercises():
    """Retorna todos os exercícios."""
    query = "SELECT id, nome, grupo_muscular FROM exercicios ORDER BY nome;"
    return _fetch_all(query)

def add_exercise(nome, grupo_muscular=None):
    """Adiciona um novo exercício."""
    query = "INSERT INTO exercicios (nome, grupo_muscular) VALUES (?, ?)"
    return _execute_query(query, (nome, grupo_muscular))

# --- Funções para Treinos ---
def add_treino(nome_treino, data_inicio, cliente_id=None, instrutor_id=None, plano_id=None,
               data_fim=None, objetivo=None, tipo_treino=None, descricao_treino=None):
    """Adiciona um novo treino principal."""
    query = """
        INSERT INTO treinos 
            (nome_treino, cliente_id, instrutor_id, plano_id, data_inicio, data_fim, objetivo, tipo_treino, descricao_treino)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (nome_treino, cliente_id, instrutor_id, plano_id, data_inicio, data_fim, objetivo, tipo_treino, descricao_treino)
    return _execute_query(query, params)

def add_exercise_to_treino(treino_id, exercicio_id, series=None, repeticoes=None, carga=None,
                           descanso_segundos=None, ordem=None, observacoes_exercicio=None):
    """Adiciona um exercício a um treino específico na tabela treino_exercicio."""
    query = """
        INSERT INTO treino_exercicio
            (treino_id, exercicio_id, series, repeticoes, carga, descanso_segundos, ordem, observacoes_exercicio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (treino_id, exercicio_id, series, repeticoes, carga, descanso_segundos, ordem, observacoes_exercicio)
    return _execute_query(query, params)

def get_workouts_with_exercises(cliente_id=None, instrutor_id=None):
    """
    Filtra e mostra treinos e seus exercícios.
    Retorna uma lista de treinos, onde cada treino contém uma lista de seus exercícios.
    """
    conn = conectar_bd() # Usar uma conexão para toda a operação
    
    base_query_treinos = """
        SELECT
            t.id AS treino_id,
            t.nome_treino,
            t.data_inicio,
            t.data_fim,
            t.objetivo,
            t.tipo_treino,
            t.descricao_treino,
            c.id AS cliente_id,
            c.nome AS cliente_nome,
            i.id AS instrutor_id,
            i.nome AS instrutor_nome,
            pl.id AS plano_id,
            pl.nome AS plano_nome
        FROM treinos t
        LEFT JOIN clientes c ON t.cliente_id = c.id
        LEFT JOIN instrutores i ON t.instrutor_id = i.id
        LEFT JOIN planos pl ON t.plano_id = pl.id
    """
    conditions = []
    params_query_treinos = []

    if cliente_id:
        conditions.append("t.cliente_id = ?")
        params_query_treinos.append(cliente_id)
    if instrutor_id:
        conditions.append("t.instrutor_id = ?")
        params_query_treinos.append(instrutor_id)
    
    if conditions:
        base_query_treinos += " WHERE " + " AND ".join(conditions)
    
    base_query_treinos += " ORDER BY t.data_inicio DESC, t.id DESC;"

    treinos = _fetch_all(base_query_treinos, tuple(params_query_treinos), conn_externa=conn)

    query_exercicios_treino = """
        SELECT
            te.id,
            e.nome AS exercicio_nome,
            e.grupo_muscular,
            te.series,
            te.repeticoes,
            te.carga,
            te.descanso_segundos,
            te.ordem,
            te.observacoes_exercicio
        FROM treino_exercicio te
        JOIN exercicios e ON te.exercicio_id = e.id
        WHERE te.treino_id = ?
        ORDER BY te.ordem ASC, te.id ASC;
    """
    
    for treino in treinos:
        # Usar a mesma conexão 'conn' para buscar os exercícios
        exercicios_do_treino = _fetch_all(query_exercicios_treino, (treino['treino_id'],), conn_externa=conn)
        treino['exercicios'] = exercicios_do_treino
    
    if conn:
        conn.close() # Fechar a conexão principal no final

    return treinos

# --- Funções para Pagamentos ---
def get_pagamentos_by_client_id(cliente_id):
    """Retorna todos os pagamentos de um cliente específico."""
    # Assumindo que a FK para clientes existe na tabela pagamentos para integridade
    query = """
        SELECT p.id, p.cliente_id, c.nome as cliente_nome, p.data_pagamento, p.valor, p.pago
        FROM pagamentos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.cliente_id = ?
        ORDER BY p.data_pagamento DESC;
    """
    return _fetch_all(query, (cliente_id,))

def add_pagamento(cliente_id, data_pagamento, valor, pago=0):
    """Adiciona um novo pagamento."""
    query = "INSERT INTO pagamentos (cliente_id, data_pagamento, valor, pago) VALUES (?, ?, ?, ?)"
    return _execute_query(query, (cliente_id, data_pagamento, valor, pago))

# --- Funções de Relatório/Dashboard (Exemplos) ---
def get_clients_with_current_plan_info():
    """
    Lista todos os clientes e tenta encontrar informações do plano do seu treino mais recente.
    Se o cliente tiver um plano_id direto, essa informação também pode ser usada.
    Esta versão foca no plano do último treino.
    """
    query = """
    SELECT
        c.id AS cliente_id,
        c.nome AS cliente_nome,
        c.email AS cliente_email,
        c.idade AS cliente_idade,
        c.sexo AS cliente_sexo,
        c.telefone AS cliente_telefone,
        pl_cliente.nome AS plano_direto_cliente, -- Plano direto do cliente
        p_treino.nome AS plano_ultimo_treino,
        t.nome_treino AS ultimo_treino_nome,
        t.data_inicio AS ultimo_treino_data_inicio,
        t.data_fim AS ultimo_treino_data_fim
    FROM clientes c
    LEFT JOIN planos pl_cliente ON c.plano_id = pl_cliente.id -- Join para o plano direto do cliente
    LEFT JOIN (
        SELECT 
            cliente_id, 
            plano_id,
            nome_treino, 
            data_inicio, 
            data_fim,
            ROW_NUMBER() OVER(PARTITION BY cliente_id ORDER BY data_inicio DESC, id DESC) as rn
        FROM treinos
    ) t ON c.id = t.cliente_id AND t.rn = 1 -- Pega o treino mais recente por cliente
    LEFT JOIN planos p_treino ON t.plano_id = p_treino.id -- Join para o plano do último treino
    ORDER BY c.id;
    """
    return _fetch_all(query)

def get_payment_stats_for_client(cliente_id):
    """Retorna o total de pagamentos e o último pagamento de um cliente."""
    query_total = """
        SELECT SUM(valor) as total_pago
        FROM pagamentos
        WHERE cliente_id = ? AND pago = 1;
    """
    total_pago_result = _fetch_one(query_total, (cliente_id,))
    total_pago = total_pago_result['total_pago'] if total_pago_result and total_pago_result['total_pago'] is not None else 0.0

    query_last_payment = """
        SELECT data_pagamento, valor
        FROM pagamentos
        WHERE cliente_id = ? AND pago = 1
        ORDER BY data_pagamento DESC
        LIMIT 1;
    """
    last_payment = _fetch_one(query_last_payment, (cliente_id,))

    return {
        "cliente_id": cliente_id,
        "total_pago": total_pago,
        "ultimo_pagamento_data": last_payment['data_pagamento'] if last_payment else None,
        "ultimo_pagamento_valor": last_payment['valor'] if last_payment else None
    }

def get_active_client_count_per_instructor():
    """
    Retorna quantos clientes distintos cada instrutor atende,
    baseado em treinos que não têm data_fim ou cuja data_fim é no futuro.
    """
    query = """
    SELECT
        i.id AS instrutor_id,
        i.nome AS instrutor_nome,
        i.especialidade AS instrutor_especialidade,
        -- Conta os clientes distintos associados a cada instrutor.
        -- Se 'c.id' for a chave primária da tabela 'clientes'.
        COUNT(DISTINCT c.id) AS numero_clientes_ativos
    FROM
        instrutores i
    LEFT JOIN
        -- Faz a junção com a tabela 'clientes' para encontrar os clientes de cada instrutor.
        -- A ligação é feita entre 'instrutores.id' e 'clientes.instrutor_id'.
        clientes c ON i.id = c.instrutor_id
    GROUP BY
        i.id, i.nome, i.especialidade
    ORDER BY
        numero_clientes_ativos DESC, i.nome;
    """
    return _fetch_all(query)

# --- Funções para Selectboxes em formulários (exemplos) ---
def get_all_clients_for_select():
    """Retorna (id, nome) de todos os clientes para selectboxes."""
    query = "SELECT id, nome FROM clientes ORDER BY nome ASC;"
    return _fetch_all(query) # _fetch_all já retorna lista de dicts

def get_all_instructors_for_select():
    """Retorna (id, nome) de todos os instrutores para selectboxes."""
    query = "SELECT id, nome FROM instrutores ORDER BY nome ASC;"
    return _fetch_all(query)

def get_all_plans_for_select():
    """Retorna (id, nome) de todos os planos para selectboxes."""
    query = "SELECT id, nome FROM planos ORDER BY nome ASC;"
    return _fetch_all(query)

def get_all_exercises_for_select():
    """Retorna (id, nome) de todos os exercícios globais para selectboxes."""
    query = "SELECT id, nome FROM exercicios ORDER BY nome ASC;"
    return _fetch_all(query)

def get_all_treinos_for_select():
    """Retorna (id, nome_treino) de todos os treinos para selectboxes."""
    query = "SELECT id, nome_treino FROM treinos WHERE nome_treino IS NOT NULL ORDER BY nome_treino ASC;"
    return _fetch_all(query)


if __name__ == '__main__':
    # Testes rápidos (descomente para testar individualmente após popular o banco)
    print("Executando testes do database.py...")
    
    # É importante que o banco 'academia.db' exista e esteja populado para os testes.
    # Você pode rodar o script setup_database_academia_v3_simples.py primeiro.

    print("\n--- Testando get_all_clients() ---")
    todos_os_clientes = get_all_clients()
    if todos_os_clientes:
        for cliente in todos_os_clientes[:3]: # Mostra os 3 primeiros
            print(cliente)
    else:
        print("Nenhum cliente encontrado ou a tabela está vazia.")
    
    print("\n--- Testando get_all_instructors() ---")
    todos_os_instrutores = get_all_instructors()
    if todos_os_instrutores:
        for instrutor in todos_os_instrutores[:3]:
            print(instrutor)
    else:
        print("Nenhum instrutor encontrado.")

    print("\n--- Testando get_all_exercises() ---")
    todos_os_exercicios = get_all_exercises()
    if todos_os_exercicios:
        for exercicio in todos_os_exercicios[:3]:
            print(exercicio)
    else:
        print("Nenhum exercício encontrado.")

    print("\n--- Testando get_workouts_with_exercises (sem filtro) ---")
    treinos_todos = get_workouts_with_exercises()
    if treinos_todos:
        for treino in treinos_todos[:2]: # Mostra os 2 primeiros treinos com seus exercícios
            print(f"Treino ID: {treino.get('treino_id')}, Nome: {treino.get('nome_treino')}, Cliente: {treino.get('cliente_nome')}")
            if treino.get('exercicios'):
                for ex in treino['exercicios'][:2]: # Mostra os 2 primeiros exercícios do treino
                    print(f"  - Ex ID: {ex.get('id')}, Nome: {ex.get('exercicio_nome')}, Series: {ex.get('series')}, Reps: {ex.get('repeticoes')}")
            else:
                print("  - Sem exercícios associados.")
    else:
        print("Nenhum treino encontrado.")

    print("\n--- Testando get_clients_with_current_plan_info() ---")
    clientes_planos = get_clients_with_current_plan_info()
    if clientes_planos:
        for cp_info in clientes_planos[:3]:
            print(cp_info)
    else:
        print("Nenhuma informação de cliente com plano encontrada.")

    print("\nTestes concluídos.")

#configurações de cards 

def count_total_clientes():
    """Retorna o número total de clientes cadastrados."""
    query = "SELECT COUNT(*) AS total_clientes FROM clientes;"
    result = _fetch_one(query)
    return result['total_clientes'] if result and 'total_clientes' in result else 0

def count_total_instrutores():
    """Retorna o número total de clientes cadastrados."""
    query = "SELECT COUNT(*) AS total_instrutores FROM instrutores;"
    result = _fetch_one(query)
    return result['total_instrutores'] if result and 'total_instrutores' in result else 0

def count_clientes_por_plano():
    """
    Retorna a contagem de clientes para cada plano.
    Espera-se que a tabela 'clientes' tenha 'plano_id' e
    a tabela 'planos' tenha 'id' e 'nome'.
    """
    query = """
        SELECT
            p.nome AS nome_plano,
            COUNT(c.id) AS total_clientes
        FROM clientes c
        JOIN planos p ON c.plano_id = p.id
        GROUP BY p.nome
        ORDER BY p.nome;
    """
    return _fetch_all(query)

def count_pagamentosn():

    query ="""
        SELECT COUNT(*) AS total_pago 
        FROM pagamentos 
        WHERE pago = 0; 
        """
    result = _fetch_one(query)
    return result['total_pago'] if result and 'total_pago' in result else 0
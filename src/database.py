import sqlite3
import os

# --- DEFINIÇÃO ROBUSTA DE CAMINHOS ---
SCRIPT_DIR_DB = os.path.dirname(os.path.abspath(__file__))
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
        raise

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
        return [] 
    finally:
        if not conn_externa and conn:
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
        return None
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
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Erro em _execute_query com query '{query[:50]}...': {e}")
        if conn and not conn_externa: 
             conn.rollback()
        return None
    finally:
        if not conn_externa and conn:
            conn.close()

# --- Funções para Clientes ---
def get_all_clients():
    """Retorna todos os clientes com as colunas especificadas."""
    # Ajuste esta query conforme as colunas REAIS da sua tabela 'clientes'
    # A query original tinha: id, nome, idade, sexo, email, telefone, plano_id, instrutor_id, treino_id
    # Se você simplificou para autenticação, pode ser: id, nome, email, telefone, data_nascimento, (hashed_password, role)
    # Vou usar uma versão mais genérica baseada em interações recentes.
    # Adapte para as colunas que você efetivamente tem e precisa.
    query = """
        SELECT id, nome, email, telefone, data_nascimento 
        FROM clientes ORDER BY nome; 
    """
    # Se você tem as colunas de autenticação e quer listá-las aqui (cuidado com senhas hashed):
    # query = "SELECT id, nome, email, telefone, data_nascimento, role FROM clientes ORDER BY nome;"
    # Se você tem as colunas da versão original da query:
    # query = "SELECT id, nome, idade, sexo, email, telefone, plano_id, instrutor_id, treino_id FROM clientes ORDER BY nome;"
    return _fetch_all(query)

def add_client(nome, email, telefone=None, data_nascimento=None, idade=None, sexo=None, plano_id=None, instrutor_id=None, treino_id=None, password_plano=None, role='user'):
    """
    Adiciona um novo cliente.
    Inclui password_plano (para senha em texto plano, que será hashed) e role.
    Ajuste os parâmetros e a query conforme as colunas da sua tabela 'clientes'.
    """
    # Se você NÃO estiver armazenando senhas hashed aqui e sim usando um sistema de auth separado
    # remova password_plano e role dos params e da query.
    # Se estiver (como no nosso exemplo de auth com BD), você precisaria hashear a senha aqui ANTES de inserir.
    # Por ora, vou manter os campos da sua query original, mas sem lógica de hash aqui.
    # A lógica de hash deve ser feita ANTES de chamar esta função, ou esta função deve recebê-la.
    # Para o exemplo, vou omitir a senha, assumindo que ela é gerenciada em outro lugar ou
    # que esta função não é para criar usuários logáveis diretamente.
    query = """
        INSERT INTO clientes (nome, email, telefone, data_nascimento, idade, sexo, plano_id, instrutor_id, treino_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
    """
    # Se sua tabela 'clientes' tem 'password' e 'role' e você quer definir ao criar:
    # query = """
    #     INSERT INTO clientes (nome, email, telefone, data_nascimento, password, role, idade, sexo, plano_id, instrutor_id, treino_id)
    #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    # """
    # params = (nome, email, telefone, data_nascimento, hashed_password_aqui, role, idade, sexo, plano_id, instrutor_id, treino_id)

    params = (nome, email, telefone, data_nascimento, idade, sexo, plano_id, instrutor_id, treino_id)
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
    conn = conectar_bd() 
    
    base_query_treinos = """
        SELECT
            t.id AS treino_id, t.nome_treino, t.data_inicio, t.data_fim,
            t.objetivo, t.tipo_treino, t.descricao_treino,
            c.id AS cliente_id, c.nome AS cliente_nome,
            i.id AS instrutor_id, i.nome AS instrutor_nome,
            pl.id AS plano_id, pl.nome AS plano_nome
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
            te.id, e.nome AS exercicio_nome, e.grupo_muscular,
            te.series, te.repeticoes, te.carga,
            te.descanso_segundos, te.ordem, te.observacoes_exercicio
        FROM treino_exercicio te
        JOIN exercicios e ON te.exercicio_id = e.id
        WHERE te.treino_id = ?
        ORDER BY te.ordem ASC, te.id ASC;
    """
    
    for treino in treinos:
        exercicios_do_treino = _fetch_all(query_exercicios_treino, (treino['treino_id'],), conn_externa=conn)
        treino['exercicios'] = exercicios_do_treino
    
    if conn:
        conn.close()

    return treinos

# --- Funções para Pagamentos ---
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

def add_pagamento(cliente_id, data_pagamento, valor, pago=0):
    """Adiciona um novo pagamento."""
    query = "INSERT INTO pagamentos (cliente_id, data_pagamento, valor, pago) VALUES (?, ?, ?, ?)"
    return _execute_query(query, (cliente_id, data_pagamento, valor, pago))

# --- Funções de Relatório/Dashboard ---
def get_clients_with_current_plan_info():
    """Lista clientes com informações do plano do seu treino mais recente e/ou plano direto."""
    query = """
    SELECT
        c.id AS cliente_id, c.nome AS cliente_nome, c.email AS cliente_email,
        c.idade AS cliente_idade, c.sexo AS cliente_sexo, c.telefone AS cliente_telefone,
        pl_cliente.nome AS plano_direto_cliente, 
        p_treino.nome AS plano_ultimo_treino,
        t.nome_treino AS ultimo_treino_nome,
        t.data_inicio AS ultimo_treino_data_inicio,
        t.data_fim AS ultimo_treino_data_fim
    FROM clientes c
    LEFT JOIN planos pl_cliente ON c.plano_id = pl_cliente.id 
    LEFT JOIN (
        SELECT 
            cliente_id, plano_id, nome_treino, data_inicio, data_fim,
            ROW_NUMBER() OVER(PARTITION BY cliente_id ORDER BY data_inicio DESC, id DESC) as rn
        FROM treinos
    ) t ON c.id = t.cliente_id AND t.rn = 1 
    LEFT JOIN planos p_treino ON t.plano_id = p_treino.id 
    ORDER BY c.nome;
    """
    return _fetch_all(query)

def get_payment_stats_for_client(cliente_id):
    """Retorna o total de pagamentos e o último pagamento de um cliente."""
    # Implementação como fornecida anteriormente
    query_total = "SELECT SUM(valor) as total_pago FROM pagamentos WHERE cliente_id = ? AND pago = 1;"
    total_pago_result = _fetch_one(query_total, (cliente_id,))
    total_pago = total_pago_result['total_pago'] if total_pago_result and total_pago_result['total_pago'] is not None else 0.0

    query_last_payment = """
        SELECT data_pagamento, valor FROM pagamentos
        WHERE cliente_id = ? AND pago = 1 ORDER BY data_pagamento DESC LIMIT 1;
    """
    last_payment = _fetch_one(query_last_payment, (cliente_id,))
    return {
        "cliente_id": cliente_id, "total_pago": total_pago,
        "ultimo_pagamento_data": last_payment['data_pagamento'] if last_payment else None,
        "ultimo_pagamento_valor": last_payment['valor'] if last_payment else None
    }

def get_active_client_count_per_instructor():
    """Retorna quantos clientes distintos cada instrutor atende (ativos)."""
    query = """
    SELECT
        i.id AS instrutor_id, i.nome AS instrutor_nome, i.especialidade AS instrutor_especialidade,
        COUNT(DISTINCT t.cliente_id) AS numero_clientes_ativos
    FROM instrutores i
    LEFT JOIN treinos t ON i.id = t.instrutor_id 
                        AND (t.data_fim IS NULL OR t.data_fim >= date('now'))
    GROUP BY i.id, i.nome, i.especialidade
    ORDER BY numero_clientes_ativos DESC, i.nome;
    """
    return _fetch_all(query)

# --- Funções para Selectboxes ---
def get_all_clients_for_select():
    query = "SELECT id, nome FROM clientes ORDER BY nome ASC;"
    return _fetch_all(query)

def get_all_instructors_for_select():
    query = "SELECT id, nome FROM instrutores ORDER BY nome ASC;"
    return _fetch_all(query)

def get_all_plans_for_select():
    query = "SELECT id, nome FROM planos ORDER BY nome ASC;"
    return _fetch_all(query)

def get_all_exercises_for_select():
    query = "SELECT id, nome FROM exercicios ORDER BY nome ASC;"
    return _fetch_all(query)

def get_all_treinos_for_select():
    query = "SELECT id, nome_treino FROM treinos WHERE nome_treino IS NOT NULL ORDER BY nome_treino ASC;"
    return _fetch_all(query)

# --- Funções para Autenticação (se estiver usando DB para usuários logáveis) ---
def get_client_credentials_by_email(email: str): # Ou get_user_credentials_by_username
    """Busca credenciais de um cliente/usuário pelo email para autenticação."""
    # Adapte esta query para a tabela e colunas corretas onde você armazena
    # email (usado como username), hashed_password e role.
    # Se for a tabela 'clientes':
    query = """
        SELECT id, nome AS nome_completo, email, hashed_password, role 
        FROM clientes 
        WHERE email = ?
    """
    # Se for uma tabela 'usuarios' separada:
    # query = "SELECT id, nome_completo, username, email, hashed_password, role FROM usuarios WHERE email = ? OR username = ?"
    # params = (email,email)
    return _fetch_one(query, (email,))


def get_total_clients_count():
    """Retorna o número total de clientes."""
    query = "SELECT COUNT(id) as total_clientes FROM clientes;"
    result = _fetch_one(query)
    return result['total_clientes'] if result and 'total_clientes' in result else 0


if __name__ == '__main__':
    print("Executando testes do database.py...")
    
    print("\n--- Testando get_all_clients() ---")
    todos_os_clientes = get_all_clients()
    if todos_os_clientes:
        for cliente in todos_os_clientes[:2]: print(cliente) # Mostra os 2 primeiros
    else:
        print("Nenhum cliente.")
    
    print("\n--- Testando get_all_instructors() ---")
    todos_os_instrutores = get_all_instructors()
    if todos_os_instrutores:
        for instrutor in todos_os_instrutores[:2]: print(instrutor)
    else:
        print("Nenhum instrutor.")

    # ... (outros testes podem ser adicionados ou descomentados conforme necessário) ...
    
    # Teste de uma função de selectbox
    print("\n--- Testando get_all_plans_for_select() ---")
    planos_select = get_all_plans_for_select()
    if planos_select:
        for plano in planos_select[:2]: print(plano)
    else:
        print("Nenhum plano para selectbox.")

    # Teste de uma função de relatório
    print("\n--- Testando get_active_client_count_per_instructor() ---")
    instrutor_clientes = get_active_client_count_per_instructor()
    if instrutor_clientes:
        for item in instrutor_clientes[:2]: print(item)
    else:
        print("Nenhuma contagem de clientes por instrutor.")

    print("\nTestes concluídos.")


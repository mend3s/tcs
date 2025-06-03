# app.py
import streamlit as st
import streamlit_pills as stp
import pandas as pd
from src import database
from datetime import date, timedelta
# from src import database # Mantenha para suas funções de BD

import streamlit_authenticator as stauth # Biblioteca de autenticação
import yaml
from yaml.loader import SafeLoader # Para carregar o YAML de forma segura

conn = database.conectar_bd() 

# --- Configuração da Página (DEVE SER A PRIMEIRA CHAMADA DO STREAMLIT) ---
st.set_page_config(
    page_title="Sistema Academia",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. Carregar Configurações do Autenticador ---
try:
    with open('config.yaml', 'r', encoding='utf-8') as file: # Adicionado encoding='utf-8'
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("ERRO CRÍTICO: Arquivo de configuração 'config.yaml' não encontrado. "
             "Crie este arquivo no mesmo diretório do app.py conforme a documentação.")
    st.stop() # Impede a execução do restante do script
except Exception as e:
    st.error(f"Erro ao carregar o arquivo config.yaml: {e}")
    st.stop()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
    # config.get('preauthorized') # Use config.get se 'preauthorized' for opcional
)

# --- Inicialização de variáveis de estado da sessão específicas do app ---
if "pagina_selecionada" not in st.session_state:
    st.session_state.pagina_selecionada = "Dashboard"
# 'role_usuario' será definido após o login bem-sucedido

# --- Interface de Login ---
# O authenticator.login() gerencia o estado de autenticação internamente
# e define st.session_state["authentication_status"], st.session_state["name"], st.session_state["username"]
authenticator.login() # 'main' é o padrão para localização do formulário

if st.session_state["authentication_status"]:
    # --- USUÁRIO AUTENTICADO ---

    # Buscar e definir o papel do usuário no session_state
    try:
        user_logged_in = st.session_state["username"]
        st.session_state.role_usuario = config['credentials']['usernames'][user_logged_in].get('role', 'user') # Default para 'user'
    except KeyError:
        st.error("Não foi possível determinar o papel do usuário. Contate o administrador.")
        st.session_state.role_usuario = 'user' # Papel padrão em caso de erro

    # Botão de Logout e informações do usuário na Sidebar
    with st.sidebar:
        st.write(f"Bem-vindo(a), **{st.session_state['name']}**!") # 'name' vem do config.yaml
        sidebar_caption = f"Usuário: {st.session_state['username']}"
        if st.session_state.get("role_usuario"): # Verifica se role_usuario existe
            sidebar_caption += f" (Papel: {st.session_state.role_usuario.capitalize()})"
        st.caption(sidebar_caption)
        authenticator.logout("Sair", key="logout_button_sidebar") # 'key' é importante
        st.markdown("---")

    # --- Menu de Navegação com Pills (Área Principal) ---
    opcoes_menu_base = ["Dashboard", "Clientes", "Treinos", "Pagamentos"]
    icones_menu_base = ["🏠", "👥", "🏋️", "💳"]
    
    if st.session_state.get("role_usuario") == "admin":
        opcoes_menu_pills = opcoes_menu_base 
        icones_menu_pills = icones_menu_base
    else:
        opcoes_menu_pills = opcoes_menu_base
        icones_menu_pills = icones_menu_base
    
    # Lógica para manter a pill selecionada (ou ir para Dashboard como padrão)
    current_page_in_options = st.session_state.pagina_selecionada in opcoes_menu_pills
    if not current_page_in_options and opcoes_menu_pills: # Se a página salva não é válida (ex: admin deslogou)
        st.session_state.pagina_selecionada = opcoes_menu_pills[0] # Volta para a primeira opção (Dashboard)
        default_index = 0
    elif opcoes_menu_pills:
         default_index = opcoes_menu_pills.index(st.session_state.pagina_selecionada)
    else: # Caso raro de não haver opções
        default_index = 0

    if opcoes_menu_pills: # Só mostra pills se houver opções
        pagina_atual = stp.pills(
            label="Navegação Principal:",
            options=opcoes_menu_pills,
            icons=icones_menu_pills,
            index=default_index,
            key="menu_pills_main"
        )
        st.session_state.pagina_selecionada = pagina_atual
    else:
        pagina_atual = None # Nenhuma página para mostrar

    # --- Conteúdo da Página Selecionada ---
    
    if pagina_atual == "Dashboard":
        st.title("🏠 Dashboard")
        st.header(f"Olá, {st.session_state['name']}!") 
        total_clientes = database.count_total_clientes()
        total_instrutores = database.count_total_instrutores()
        dados_planos = database.count_clientes_por_plano()
        totalpago = database.count_pagamentosn()

            # Definindo o estilo do card
        col1, col2 = st.columns(2)
        # Construir a lista de planos em HTML para dentro do card
        lista_html_interna = ""
        if dados_planos:
            lista_html_interna += "<ul style='list-style-type: none; padding-top: 8px; padding-left: 20px; margin: 0; text-align: left;'>" # Corrigido pading_top e adicionado padding-left
            for item in dados_planos:
                lista_html_interna += f"<li style='color: white; margin-bottom: 5px; font-size: 1em;'><strong>{item['nome_plano']}:</strong> {item['total_clientes']} ativos</li>" # Ajustado margin e font-size
            lista_html_interna += "</ul>"
        else:
            lista_html_interna = "<p style='color: white; text-align: center;'>Nenhum dado de plano encontrado.</p>"

# Criando as colunas para os dois primeiros cards
        col1, col2, col3 = st.columns(3)
            # Card para Clientes por Plano
            
            
        with col1:
                card_clientes = f"""
                <div style="
                    background-color: #ABDDA4; 
                padding: 16px; 
                border-radius: 16px; /* Arredondamento mais comum */
                color: white; 
                text-align: center; 
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); 
                max-width: 300px; 
                margin: 16px auto;
                ">
                    <h2 style="color: white; margin-bottom: 10px; font-size: 1.5em; border-bottom: 1px solid rgba(255,255,255,0.3);text-align: center;">CLIENTES ATIVOS</h2>
                    <h1 style="color: white; margin-top: 0px; font-size: 2.5em;text-align: center;">{total_clientes}</h1>
                </div>
                """
                st.markdown(card_clientes, unsafe_allow_html=True)
                
        with col2:
                card_instrutores = f"""
                <div style="
                    background-color: #D53E4F; 
                padding: 16px; 
                border-radius: 25px; /* Arredondamento mais comum */
                color: white; 
                text-align: center; 
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); 
                max-width: 300px; 
                margin: 16px auto;
                ">
                    <h2 style="color: white; margin-bottom: 10px; font-size: 1.5em; border-bottom: 1px solid rgba(255,255,255,0.3);text-align: center;">INSTRUTORES ATIVOS</h2>
                    <h1 style="color: white; margin-top: 0px; font-size: 2.5em; text-align: center;">{total_instrutores}</h1>
                </div>
                """
                st.markdown(card_instrutores, unsafe_allow_html=True)
            # Card para Clientes por Plano
        
        
        with col3:

            card_pagamentos = f"""
                <div style="
                    background-color: #F9A603; 
                padding: 16px; 
                border-radius: 25px; /* Arredondamento mais comum */
                color: white; 
                text-align: center; 
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); 
                max-width: 300px; 
                margin: 16px auto;
                ">
                    <h2 style="color: white; margin-bottom: 10px; font-size: 1.5em; border-bottom: 1px solid rgba(255,255,255,0.3);text-align: center;">PAGAMENTO PENDENTE</h2>
                    <h1 style="color: white; margin-top: 0px; font-size: 2.5em; text-align: center;">{totalpago}</h1>
                </div>
                """
            st.markdown(card_pagamentos, unsafe_allow_html=True)
        st.markdown("---")
        card_clientes_por_plano = f"""
            <div style="
                background-color: #66C5CC; 
                padding: 16px; 
                border-radius: 25px; /* Arredondamento mais comum */
                color: white; 
                text-align: center;  
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); 
                max-width: 300px; 
                margin: 16px auto;
            ">
                <h2 style="color: white; margin-bottom: 10px; text-align: center; font-size: 2em; border-bottom: 1px solid rgba(255,255,255,0.3);">CLIENTES & PLANOS</h2>
                <div style="margin-top: 10px; text-align: center;">
                    {lista_html_interna}
                </div>
            </div>    
            """
        st.markdown(card_clientes_por_plano, unsafe_allow_html=True)
        
    elif pagina_atual == "Clientes":
        st.title("👨‍💻 Gestão de Clientes")
        st.markdown("Gerencie os clientes da sua academia: visualize, adicione e veja seus planos.")

        tab_selecionada = st.radio("Escolha uma opção", ["Lista de Clientes", "Cadastrar Novo Cliente"])

        if tab_selecionada == "Lista de Clientes":
            st.header("Lista de Clientes e Seus Planos")

            clientes_info = database.get_clients_with_current_plan_info()

            if clientes_info:
                df_clientes = pd.DataFrame(clientes_info)
            
                df_clientes_display = df_clientes[[ 
                'cliente_nome', 
                'cliente_email', 
                'cliente_telefone', 
                'plano_direto_cliente',
                ]].copy()
            
                df_clientes_display.columns = [
                'Nome do Cliente', 
                'Email', 
                'Telefone', 
                'Plano Associado (Direto)'
                ]

                filtro_cliente_nome = st.text_input("Filtrar clientes por nome:", "")
                if filtro_cliente_nome:
                    df_clientes_display = df_clientes_display[df_clientes_display['Nome do Cliente'].str.contains(filtro_cliente_nome, case=False, na=False)]

                st.dataframe(df_clientes_display, use_container_width=True)
            else:
                st.info("Nenhum cliente cadastrado ainda.")

        if tab_selecionada == "Cadastrar Novo Cliente":
            st.header("Cadastrar Novo Cliente")

            with st.form("form_cadastro_cliente", clear_on_submit=True):
                nome = st.text_input("Nome do Cliente", help="Nome completo do cliente.")
                email = st.text_input("Email do Cliente", help="Email único do cliente.")
            
                col1, col2 = st.columns(2)
                with col1:
                    idade = st.number_input("Idade", min_value=0, max_value=120, value=None, help="Idade do cliente.", format="%d")
                with col2:
                    sexo = st.selectbox("Sexo", ["", "Masculino", "Feminino", "Outro"], index=0, help="Gênero do cliente.")
            
                telefone = st.text_input("Telefone", help="Telefone de contato (ex: (XX) XXXXX-XXXX).")

                planos_disponiveis = database.get_all_plans_for_select()
                instrutores_disponiveis = database.get_all_instructors_for_select()

                lista_planos_nomes = [p['nome'] for p in planos_disponiveis] if planos_disponiveis else []
                lista_instrutores_nomes = [i['nome'] for i in instrutores_disponiveis] if instrutores_disponiveis else []
            
                planos_nome_para_id = {p['nome']: p['id'] for p in planos_disponiveis} if planos_disponiveis else {}
                instrutores_nome_para_id = {i['nome']: i['id'] for i in instrutores_disponiveis} if instrutores_disponiveis else {}

                col3, col4 = st.columns(2)
                with col3:
                    plano_selecionado_nome = None 
                    if lista_planos_nomes:
                        plano_selecionado_nome = st.selectbox(
                        "Plano Associado", 
                        options=lista_planos_nomes, 
                        index=0, 
                        help="Plano que o cliente está associado."
                        )
                    else:
                        st.error("ERRO: Nenhum plano disponível. Cadastre planos primeiro (na página de planos).")
                        plano_selecionado_nome = "" 
        
                with col4:
                    instrutor_selecionado_nome = None 
                    if lista_instrutores_nomes:
                        instrutor_selecionado_nome = st.selectbox(
                        "Instrutor Principal", 
                        options=lista_instrutores_nomes, 
                        index=0, 
                        help="Instrutor principal do cliente."
                        )
                    else:
                        st.error("ERRO: Nenhum instrutor disponível. Cadastre instrutores primeiro (na página de instrutores).")
                        instrutor_selecionado_nome = ""

                submitted = st.form_submit_button("Cadastrar Cliente")

            if submitted:
                if not nome:
                    st.error("Nome do Cliente é obrigatório.")
                elif not email:
                    st.error("Email do Cliente é obrigatório.")
                elif "@" not in email:
                    st.error("Por favor, insira um email válido.")
                elif not plano_selecionado_nome: 
                    st.error("Plano Associado é obrigatório e nenhum plano está disponível ou foi selecionado.")
                elif not instrutor_selecionado_nome: 
                    st.error("Instrutor Principal é obrigatório e nenhum instrutor está disponível ou foi selecionado.")
                else:
                    plano_id = planos_nome_para_id.get(plano_selecionado_nome)
                    instrutor_id = instrutores_nome_para_id.get(instrutor_selecionado_nome)
                    treino_id = None
                    
                    client_id = database.add_client(nome, email, idade, sexo, telefone, plano_id, instrutor_id, treino_id)
                    if client_id:
                        st.success(f"Cliente '{nome}' cadastrado com sucesso! ID: {client_id}")
                    else:
                        st.error("Erro ao cadastrar cliente. Verifique se o email já existe ou outros dados.")

    elif pagina_atual == "Treinos":
        st.title("🏋️ Gerenciamento de Treinos")

        tab_visualizar, tab_cadastrar_treino_exercicios, tab_banco_exercicios = st.tabs([
            "Consultar Treinos", "Cadastrar Novo Treino Completo", "Banco de Exercícios"
        ])

        with tab_visualizar:
            st.subheader("Consultar Treinos Existentes")
            try:
                # Carregar dados para filtros
                clientes_select_filtro = database.get_all_clients_for_select()
                instrutores_select_filtro = database.get_all_instructors_for_select()

                opcoes_clientes_filtro = {"-- Todos os Clientes --": None}
                if clientes_select_filtro:
                    for c in clientes_select_filtro: 
                        if c.get('nome'): opcoes_clientes_filtro[c['nome']] = c['id']
                
                opcoes_instrutores_filtro = {"-- Todos os Instrutores --": None}
                if instrutores_select_filtro:
                    for i in instrutores_select_filtro: 
                        if i.get('nome'): opcoes_instrutores_filtro[i['nome']] = i['id']

                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    cliente_filtro_nome_sel = st.selectbox("Filtrar por Cliente:", list(opcoes_clientes_filtro.keys()), key="filtro_cliente_treino_page")
                with col_f2:
                    instrutor_filtro_nome_sel = st.selectbox("Filtrar por Instrutor:", list(opcoes_instrutores_filtro.keys()), key="filtro_instrutor_treino_page")
                
                cliente_id_para_filtro = opcoes_clientes_filtro.get(cliente_filtro_nome_sel)
                instrutor_id_para_filtro = opcoes_instrutores_filtro.get(instrutor_filtro_nome_sel)

                # Buscar treinos com base nos filtros
                treinos_encontrados_data = database.get_workouts_with_exercises(
                    cliente_id=cliente_id_para_filtro, 
                    instrutor_id=instrutor_id_para_filtro
                ) 

                if treinos_encontrados_data:
                    st.write(f"Encontrados {len(treinos_encontrados_data)} treinos:")
                    for treino_idx, treino_info in enumerate(treinos_encontrados_data):
                        exp_label = f"**{treino_info.get('nome_treino', f'Treino ID: {treino_info.get('treino_id')}')}**"
                        if treino_info.get('cliente_nome'): exp_label += f" - Cliente: {treino_info['cliente_nome']}"
                        if treino_info.get('instrutor_nome'): exp_label += f" - Instrutor: {treino_info['instrutor_nome']}"
                        
                        with st.expander(exp_label):
                            st.markdown(f"**ID do Treino:** {treino_info.get('treino_id')}")
                            st.markdown(f"**Objetivo:** {treino_info.get('objetivo', 'N/A')} | **Tipo:** {treino_info.get('tipo_treino', 'N/A')}")
                            st.markdown(f"**Descrição:** {treino_info.get('descricao_treino', 'N/A')}")
                            st.markdown(f"**Data Início:** {treino_info.get('data_inicio', 'N/A')} | **Data Fim:** {treino_info.get('data_fim', 'N/A')}")
                            st.markdown(f"**Plano Associado:** {treino_info.get('plano_nome', 'N/A')}")
                            
                            exercicios_deste_treino = treino_info.get('exercicios')
                            if exercicios_deste_treino:
                                st.markdown("**Exercícios do Treino:**")
                                df_ex = pd.DataFrame(exercicios_deste_treino)
                                cols_ex_ver = ['ordem', 'exercicio_nome', 'series', 'repeticoes', 'carga', 'descanso_segundos', 'observacoes_exercicio']
                                cols_ex_ver_existentes = [col for col in cols_ex_ver if col in df_ex.columns]
                                st.table(df_ex[cols_ex_ver_existentes])
                            else:
                                st.info("Este treino não possui exercícios detalhados.")
                else:
                    st.info("Nenhum treino encontrado com os filtros aplicados.")
            except Exception as e:
                st.error(f"Erro ao carregar ou filtrar treinos: {e}")

            st.markdown("---")
            st.subheader("Clientes Ativos por Instrutor")
            try:
                instrutor_clientes_data = database.get_active_client_count_per_instructor() # Passa conn implicitamente
                if instrutor_clientes_data:
                    df_instrutor_clientes = pd.DataFrame(instrutor_clientes_data)
                    col_instr_cli_display = ['instrutor_nome', 'instrutor_especialidade', 'numero_clientes_ativos']
                    col_instr_cli_existentes = [col for col in col_instr_cli_display if col in df_instrutor_clientes.columns]
                    st.dataframe(df_instrutor_clientes[col_instr_cli_existentes], use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma informação de clientes por instrutor disponível.")
            except Exception as e:
                st.error(f"Erro ao carregar contagem de clientes por instrutor: {e}")


        with tab_cadastrar_treino_exercicios:
            st.subheader("Cadastrar Novo Treino e Adicionar Exercícios")

            # Passo 1: Dados do Treino Principal
            with st.form("form_dados_treino_principal_multi_tab", clear_on_submit=False):
                st.markdown("##### 1. Detalhes do Treino Principal")
                form_nome_t_p_val = st.text_input("Nome do Treino*", key="form_nome_t_p_multi_val")
                form_data_inicio_t_p_val = st.date_input("Data de Início*", value=date.today(), key="form_data_inicio_t_p_multi_val")
                form_data_fim_t_p_val = st.date_input("Data de Fim (Opcional)", value=None, key="form_data_fim_t_p_multi_val")
                form_desc_t_p_val = st.text_area("Descrição", key="form_desc_t_p_multi_val")
                form_tipo_t_p_val = st.text_input("Tipo (Ex: A, Full Body)", key="form_tipo_t_p_multi_val")
                form_obj_t_p_val = st.text_input("Objetivo (Ex: Hipertrofia)", key="form_obj_t_p_multi_val")

                form_op_cli_cad, form_op_inst_cad, form_op_plan_cad = {"-- Nenhum --": None}, {"-- Nenhum --": None}, {"-- Nenhum --": None}
                try:
                    clientes_s_form = database.get_all_clients_for_select()
                    instrutores_s_form = database.get_all_instructors_for_select()
                    planos_s_form = database.get_all_plans_for_select()

                    if clientes_s_form:
                        for c_ in clientes_s_form: 
                            if c_.get('nome'): form_op_cli_cad[c_['nome']] = c_['id']
                    if instrutores_s_form:
                        for i_ in instrutores_s_form: 
                            if i_.get('nome'): form_op_inst_cad[i_['nome']] = i_['id']
                    if planos_s_form:
                        for p_ in planos_s_form: 
                            if p_.get('nome'): form_op_plan_cad[p_['nome']] = p_['id']
                except Exception as e:
                    st.warning(f"Erro ao carregar opções para formulário de treino (cadastro): {e}")

                form_cliente_nome_cad = st.selectbox("Cliente (Opcional):", list(form_op_cli_cad.keys()), key="form_cliente_t_p_multi_cad")
                form_instrutor_nome_cad = st.selectbox("Instrutor (Opcional):", list(form_op_inst_cad.keys()), key="form_instrutor_t_p_multi_cad")
                form_plano_nome_cad = st.selectbox("Plano (Opcional):", list(form_op_plan_cad.keys()), key="form_plano_t_p_multi_cad")
                
                submit_passo1_cad = st.form_submit_button("Confirmar Dados do Treino e Prosseguir para Exercícios")

                if submit_passo1_cad:
                    if not form_nome_t_p_val:
                        st.warning("Nome do treino é obrigatório.")
                    else:
                        st.session_state.nome_treino_sendo_criado = form_nome_t_p_val
                        st.session_state.dados_treino_principal_temp = {
                            "nome_treino": form_nome_t_p_val, 
                            "data_inicio": form_data_inicio_t_p_val.isoformat(),
                            "data_fim": form_data_fim_t_p_val.isoformat() if form_data_fim_t_p_val else None,
                            "descricao_treino": form_desc_t_p_val, "tipo_treino": form_tipo_t_p_val,
                            "objetivo": form_obj_t_p_val,
                            "cliente_id": form_op_cli_cad.get(form_cliente_nome_cad),
                            "instrutor_id": form_op_inst_cad.get(form_instrutor_nome_cad),
                            "plano_id": form_op_plan_cad.get(form_plano_nome_cad)
                        }
                        st.session_state.exercicios_para_treino_atual = [] 
                        st.session_state.proxima_ordem_exercicio = 1
                        st.info(f"Dados do treino '{form_nome_t_p_val}' confirmados. Adicione os exercícios abaixo.")
                        
            if st.session_state.get("nome_treino_sendo_criado"): 
                st.markdown("---")
                st.markdown(f"##### 2. Adicionar Exercícios ao Treino: **{st.session_state.nome_treino_sendo_criado}**")
                
                form_op_ex_globais_cad = {"-- Selecione --": None}
                try:
                    exercicios_globais_cad = database.get_all_exercises_for_select()
                    if exercicios_globais_cad:
                        for ex_g in exercicios_globais_cad: 
                            if ex_g.get('nome'): form_op_ex_globais_cad[ex_g['nome']] = ex_g['id']
                except Exception as e:
                    st.error(f"Erro ao carregar exercícios globais para o formulário (cadastro): {e}")
                    
                with st.form("form_add_exercicio_lista_cad", clear_on_submit=True):
                    form_ex_nome_sel_cad = st.selectbox("Exercício Global*", list(form_op_ex_globais_cad.keys()), key="form_sel_ex_para_lista_cad")
                    form_ordem_ex_cad = st.number_input("Ordem*", min_value=1, value=st.session_state.proxima_ordem_exercicio, step=1, key="form_ordem_ex_lista_cad")
                    form_series_ex_cad = st.text_input("Séries*", key="form_series_ex_lista_cad")
                    form_reps_ex_cad = st.text_input("Repetições*", key="form_reps_ex_lista_cad")
                    form_carga_ex_cad = st.text_input("Carga", key="form_carga_ex_lista_cad")
                    form_descanso_ex_cad = st.number_input("Descanso (segundos)", min_value=0, step=15, key="form_descanso_ex_lista_cad")
                    form_obs_ex_cad = st.text_area("Observações", key="form_obs_ex_lista_cad")
                    
                    add_ex_lista_btn_cad = st.form_submit_button("➕ Adicionar à Lista")

                    if add_ex_lista_btn_cad:
                        if form_ex_nome_sel_cad != "-- Selecione --" and form_series_ex_cad and form_reps_ex_cad:
                            form_ex_id_cad = form_op_ex_globais_cad.get(form_ex_nome_sel_cad) 
                            if form_ex_id_cad is not None:
                                st.session_state.exercicios_para_treino_atual.append({
                                    "exercicio_id": form_ex_id_cad, "nome_exercicio": form_ex_nome_sel_cad, "ordem": form_ordem_ex_cad,
                                    "series": form_series_ex_cad, "repeticoes": form_reps_ex_cad, "carga": form_carga_ex_cad,
                                    "descanso_segundos": form_descanso_ex_cad, "observacoes_exercicio": form_obs_ex_cad
                                })
                                st.success(f"'{form_ex_nome_sel_cad}' adicionado à lista.")
                                st.session_state.exercicios_para_treino_atual.sort(key=lambda x: x['ordem'])
                                st.session_state.proxima_ordem_exercicio = max(ex_['ordem'] for ex_ in st.session_state.exercicios_para_treino_atual) + 1 if st.session_state.exercicios_para_treino_atual else 1
                            else:
                                st.error(f"Exercício '{form_ex_nome_sel_cad}' não encontrado no mapeamento.")
                        else:
                            st.warning("Selecione um exercício e preencha Séries e Repetições.")
                
                if st.session_state.exercicios_para_treino_atual:
                    st.markdown("**Exercícios na lista para este treino:**")
                    df_ex_lista_cad = pd.DataFrame(st.session_state.exercicios_para_treino_atual)
                    cols_ex_df_disp_cad = ['ordem', 'nome_exercicio', 'series', 'repeticoes', 'carga', 'descanso_segundos', 'observacoes_exercicio']
                    cols_ex_df_exist_cad = [col_ for col_ in cols_ex_df_disp_cad if col_ in df_ex_lista_cad.columns]
                    st.table(df_ex_lista_cad[cols_ex_df_exist_cad])
                    if st.button("🗑️ Limpar todos os exercícios da lista", key="btn_limpar_lista_ex_form_cad"):
                        st.session_state.exercicios_para_treino_atual = []
                        st.session_state.proxima_ordem_exercicio = 1
                        st.rerun()

                st.markdown("---")
                if st.button("💾 Salvar Treino Completo com Exercícios", type="primary", use_container_width=True, key="btn_salvar_treino_completo_form_cad"):
                    dados_treino_principal_final = st.session_state.get("dados_treino_principal_temp", {})
                    if not dados_treino_principal_final or not dados_treino_principal_final.get("nome_treino"):
                        st.error("Dados do treino principal não foram confirmados. Preencha e confirme o Passo 1.")
                    elif not st.session_state.exercicios_para_treino_atual:
                        st.error("Adicione pelo menos um exercício à lista (Passo 2).")
                    else:
                        novo_treino_id_db = database.add_treino(
                        dados_treino_principal_final['nome_treino'],
                        dados_treino_principal_final['data_inicio'],
                        cliente_id=dados_treino_principal_final.get('cliente_id'), # Exemplo, ajuste conforme seus dados
                        instrutor_id=dados_treino_principal_final.get('instrutor_id'), # Exemplo
                        plano_id=dados_treino_principal_final.get('plano_id'), # Exemplo
                        data_fim=dados_treino_principal_final.get('data_fim'), # Exemplo
                        objetivo=dados_treino_principal_final.get('objetivo'), # Exemplo
                        tipo_treino=dados_treino_principal_final.get('tipo_treino'), # Exemplo
                        descricao_treino=dados_treino_principal_final.get('descricao_treino')
                        # Remova a linha: conn_externa=conn
                        )
                        if novo_treino_id_db:
                            todos_ex_salvos_final_db = True
                            for ex_info_final_db in st.session_state.exercicios_para_treino_atual:
                                res_add_ex_final_db = database.add_exercise_to_treino(
                                    novo_treino_id_db,
                                    ex_info_final_db['exercicio_id'],
                                    ex_info_final_db['series'],
                                    ex_info_final_db['repeticoes'], # Certifique-se de que todos os argumentos posicionais e nomeados estão corretos
                                    ex_info_final_db['carga'],
                                    ex_info_final_db['descanso_segundos'],
                                    ex_info_final_db['ordem'],
                                    ex_info_final_db['observacoes_exercicio']
                                    
                            )
                                if res_add_ex_final_db is None: 
                                    todos_ex_salvos_final_db = False
                                    st.error(f"Falha ao salvar o exercício '{ex_info_final_db['nome_exercicio']}' no treino ID {novo_treino_id_db}.")
                                    break
                            
                            if todos_ex_salvos_final_db:
                                st.success(f"Treino '{dados_treino_principal_final['nome_treino']}' e seus exercícios salvos com ID: {novo_treino_id_db}!")
                                st.session_state.exercicios_para_treino_atual = []
                                st.session_state.nome_treino_sendo_criado = ""
                                st.session_state.dados_treino_principal_temp = {}
                                st.session_state.proxima_ordem_exercicio = 1
                                st.rerun()
                            else:
                                st.error(f"Alguns exercícios não puderam ser salvos. O treino principal foi criado (ID: {novo_treino_id_db}), mas pode estar incompleto.")
                        else:
                            st.error("Falha ao salvar os dados do treino principal.")

        with tab_banco_exercicios:
            st.subheader("Banco Global de Exercícios")
            try:
                exercicios_globais_data = database.get_all_exercises()
                if exercicios_globais_data:
                    df_ex_globais = pd.DataFrame(exercicios_globais_data)
                    st.dataframe(df_ex_globais[['id', 'nome', 'grupo_muscular']], use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum exercício no banco global.")
            except Exception as e:
                st.error(f"Erro ao carregar banco de exercícios: {e}")

            with st.expander("➕ Adicionar Novo Exercício ao Banco Global"):
                with st.form("form_novo_exercicio_global_tab"):
                    form_nome_ex_g_val = st.text_input("Nome do Exercício*")
                    form_grupo_musc_ex_g_val = st.text_input("Grupo Muscular")
                    submit_ex_g_form = st.form_submit_button("Salvar Exercício Global")

                    if submit_ex_g_form:
                        if not form_nome_ex_g_val:
                            st.warning("Nome do exercício é obrigatório.")
                        else:
                            novo_ex_g_id_db = database.add_exercise(form_nome_ex_g_val, form_grupo_musc_ex_g_val, conn_externa=conn)
                            if novo_ex_g_id_db:
                                st.success(f"Exercício '{form_nome_ex_g_val}' adicionado ao banco global com ID: {novo_ex_g_id_db}!")
                                st.rerun()
                            else:
                                st.error("Falha ao adicionar exercício global. Verifique se já existe.")
        

    elif pagina_atual == "Pagamentos":
        st.title("💳 Pagamentos")
        st.header("Gerenciamento de Pagamentos")
        
        tab_ver_pagamentos, tab_registrar_pagamento = st.tabs(["Consultar Pagamentos", "Registrar Novo Pagamento"])
        with tab_ver_pagamentos:
            st.subheader("Consultar Pagamentos de Clientes")
            try:
                clientes_select_pag = database.get_all_clients_for_select()
                op_cli_pag = {"-- Selecione um Cliente --": None}
                if clientes_select_pag:
                    for c in clientes_select_pag: op_cli_pag[c['nome']] = c['id']
                
                cliente_nome_pag_sel = st.selectbox("Cliente:", list(op_cli_pag.keys()), key="sel_cliente_pag")

                if cliente_nome_pag_sel != "-- Selecione um Cliente --":
                    cliente_id_pag = op_cli_pag.get(cliente_nome_pag_sel) 
                    if cliente_id_pag:
                        st.markdown(f"#### Histórico de Pagamentos de: **{cliente_nome_pag_sel}**")
                        pagamentos_cliente = database.get_pagamentos_by_client_id(cliente_id_pag)
                        if pagamentos_cliente:
                            df_pag = pd.DataFrame(pagamentos_cliente)
                            df_pag['pago'] = df_pag['pago'].apply(lambda x: "Sim" if x == 1 else "Não")
                            st.dataframe(df_pag[['data_pagamento', 'valor', 'pago']], hide_index=True, use_container_width=True)
                        else:
                            st.info("Nenhum pagamento registrado para este cliente.")

                        stats_pag = database.get_payment_stats_for_client(cliente_id_pag)
                        st.metric("Total Pago", f"R$ {stats_pag.get('total_pago', 0):.2f}")
                        if stats_pag.get('ultimo_pagamento_data'):
                            data_ult_pag = pd.to_datetime(stats_pag['ultimo_pagamento_data']).strftime('%d/%m/%Y') if stats_pag['ultimo_pagamento_data'] else "N/A"
                            st.write(f"Último Pagamento: R$ {stats_pag.get('ultimo_pagamento_valor', 0):.2f} em {data_ult_pag}")
                            
            except Exception as e:
                st.error(f"Erro ao carregar dados de pagamentos: {e}")
                
        with tab_registrar_pagamento:
            st.subheader("Registrar Novo Pagamento")
            op_cli_reg_pag = {"-- Selecione um Cliente --": None}
            try:
                clientes_select_reg_pag = database.get_all_clients_for_select()
                if clientes_select_reg_pag:
                    for c in clientes_select_reg_pag: op_cli_reg_pag[c['nome']] = c['id']
            except Exception as e:
                st.error(f"Erro ao carregar clientes para registro de pagamento: {e}")
                
            with st.form("form_novo_pagamento"):
                cliente_nome_reg_pag_sel = st.selectbox("Cliente*", list(op_cli_reg_pag.keys()), key="sel_cliente_reg_pag")
                data_pag_form = st.date_input("Data do Pagamento*", value=date.today())
                valor_pag_form = st.number_input("Valor Pago (R$)*", min_value=0.01, format="%.2f")
                status_pago_form = st.checkbox("Pagamento Confirmado (Pago)?", value=True)
                
                submit_pag = st.form_submit_button("Registrar Pagamento")

                if submit_pag:
                    if cliente_nome_reg_pag_sel == "-- Selecione um Cliente --":
                        st.warning("Selecione um cliente.")
                    elif not valor_pag_form or valor_pag_form <=0:
                        st.warning("Informe um valor válido para o pagamento.")
                    else:
                        cliente_id_reg_pag = op_cli_reg_pag.get(cliente_nome_reg_pag_sel) 
                        if cliente_id_reg_pag:
                            pago_status_db = 1 if status_pago_form else 0
                            
                            novo_pag_id = database.add_pagamento(cliente_id_reg_pag, data_pag_form.isoformat(), valor_pag_form, pago_status_db)
                            if novo_pag_id:
                                st.success(f"Pagamento de R$ {valor_pag_form:.2f} para '{cliente_nome_reg_pag_sel}' registrado com ID: {novo_pag_id}!")
                                st.rerun()
                            else:
                                st.error("Falha ao registrar pagamento.")
                        else:
                            st.error("Cliente selecionado para pagamento não encontrado.")

elif st.session_state["authentication_status"] is False:
    st.error('Nome de usuário/senha incorretos.')
    # O formulário de login já está visível acima por padrão
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, insira seu nome de usuário e senha para acessar o sistema.')
    # O formulário de login já está visível acima por padrão
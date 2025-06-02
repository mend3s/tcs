# app.py
import streamlit as st
import streamlit_pills as stp
import pandas as pd
from src import database
# from src import database # Mantenha para suas funções de BD

import streamlit_authenticator as stauth # Biblioteca de autenticação
import yaml
from yaml.loader import SafeLoader # Para carregar o YAML de forma segura

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
        opcoes_menu_pills = opcoes_menu_base + ["Configurações Admin"]
        icones_menu_pills = icones_menu_base + ["⚙️"]
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
        #     clientes_data = database.get_all_clients()
        #     if clientes_data:
        #         df = pd.DataFrame(clientes_data)
        #         st.subheader("Alguns Clientes:")
        #         st.dataframe(df[['id', 'nome', 'email']].head(), use_container_width=True, hide_index=True)
        # except ImportError:
        #     st.warning("Módulo 'database' não encontrado para carregar dados no dashboard.")
        # except Exception as e:
        #     st.error(f"Erro ao carregar dados para o dashboard: {e}")
    elif pagina_atual == "Clientes":
        st.title("👥 Clientes")
        if st.session_state.get("role_usuario") == "admin":
            st.write("Bem-vindo à área de gerenciamento de clientes.")

            clientes_data = database.get_clients_with_current_plan_info()

            if clientes_data:
                df = pd.DataFrame(clientes_data)

                st.subheader("Tabela de clientes com treino atual")

                st.dataframe(df[['cliente_id', 'cliente_nome', 'cliente_email', 'plano_nome', 'plano_preco', 'treino_data_inicio', 'treino_data_fim']])
            else:
                st.warning("Nenhum cliente encontrado.")
        else:
            st.error("Acesso Negado. Esta área é restrita a administradores.")
            st.header("Gerenciamento de Clientes")


    elif pagina_atual == "Treinos":
        st.title("🏋️ Treinos")
        st.header("Gerenciamento de Treinos")
        # ... (seu código para a página de Treinos) ...

    elif pagina_atual == "Pagamentos":
        st.title("💳 Pagamentos")
        st.header("Gerenciamento de Pagamentos")
        # ... (seu código para a página de Pagamentos) ...

    elif pagina_atual == "Configurações Admin":
        st.title("⚙️ Configurações Administrativas")
        st.header("Painel do Administrador")
        if st.session_state.get("role_usuario") == "admin":
            st.write("Bem-vindo à área de configurações do administrador.")
            # ... (seu código para a página de Admin) ...
        else:
            st.error("Acesso Negado. Esta área é restrita a administradores.")

elif st.session_state["authentication_status"] is False:
    st.error('Nome de usuário/senha incorretos.')
    # O formulário de login já está visível acima por padrão
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, insira seu nome de usuário e senha para acessar o sistema.')
    # O formulário de login já está visível acima por padrão
import streamlit as st
from repositorio.memoria import RepositorioMemoria
from servicos.amostra_service import AmostraService
from servicos.alerta_servico import AlertaService
from dominio.entidades import Usuario
from dominio.enums import PapelUsuario, StatusAmostra
from dominio.erros import ErroBase

# Configuração da página (Layout wide)
st.set_page_config(
    page_title="Estoque de Amostras", 
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Esconde o menu padrão do Streamlit
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Cria o "banco" de dados na memória
@st.cache_resource
def get_servicos():
    repo = RepositorioMemoria()
    return repo, AmostraService(repo), AlertaService(repo)

repo, service, alerta_service = get_servicos()

# Simulando usuários
user_brasil = Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL, localizacao="brasil")
user_escritorio = Usuario(nome="Maria", email="maria@teste.com", papel=PapelUsuario.ESCRITORIO, localizacao="china")

# --- MENU LATERAL RETRÁTIL ---
# --- MENU LATERAL RETRÁTIL (Nativo do Streamlit) ---
with st.sidebar:
    st.markdown("### 📦 Menu")
    pagina = st.radio(
        "Navegação",
        ["Dashboard", "Nova Amostra", "Movimentar Estoque", "Em Breve"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.subheader("👤 Quem está acessando?")
    usuario_logado = st.radio(
        "Selecione o perfil:", 
        [user_brasil, user_escritorio], 
        format_func=lambda u: f"{u.nome} ({u.localizacao.title()})"
    )

# --- CONTEÚDO DAS PÁGINAS ---

if pagina == "Dashboard":
    # Define as cores baseadas no escritório do usuário
    if usuario_logado.localizacao == "brasil":
        cor_fundo = "linear-gradient(to right, #009c3b, #ffdf00)" # Verde/Amarelo
    else:
        cor_fundo = "linear-gradient(to right, #de2910, #ffde00)" # Vermelho/Amarelo

    # Cabeçalho personalizado
    st.markdown(
        f"""
        <div style="background: {cor_fundo}; padding: 20px; border-radius: 10px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1 style="margin: 0; font-size: 28px; color: white;">Olá, {usuario_logado.nome}</h1>
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 5px; font-weight: bold; color: white;">
                📍 {usuario_logado.localizacao.title()}
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Título e Botão de Nova Amostra
    col_titulo, col_botao = st.columns([4, 1])
    with col_titulo:
        st.subheader("Minhas Amostras:")
    with col_botao:
        # Se clicar em Nova Amostra aqui, poderíamos redirecionar, mas por enquanto fica no menu
        pass

    # Listagem de Amostras em Cards (Grade de 4 colunas)
    amostras = repo.listar_todas()
    if amostras:
        # Mostra no máximo 4 amostras no dashboard
        amostras_dashboard = amostras[:4]
        
        cols = st.columns(4)
        for index, amostra in enumerate(amostras_dashboard):
            with cols[index % 4]:
                with st.container(border=True):
                    st.markdown(f"**{amostra.id}**")
                    st.write(f"**Cliente:** {amostra.cliente}")
                    st.write(f"**Status:** {amostra.status.value}")
    else:
        st.info("Nenhuma amostra cadastrada ainda.")

    st.divider()

    # Alertas embaixo
    col_alertas, col_breve = st.columns([2, 1])
    with col_alertas:
        st.subheader("Resumo dos Alertas")
        alertas = alerta_service.gerar_alertas(limite_estoque=30, limite_transito=15, limite_analise=10)
        if not alertas:
            st.success("Tudo em ordem! Nenhum alerta no momento.")
        else:
            for a in alertas:
                st.warning(f"**{a['tipo'].replace('_', ' ').title()}**: {a['mensagem']}")
                
    with col_breve:
        st.subheader("Em Breve")
        st.info("Gráficos e integrações futuras.")

elif pagina == "Nova Amostra":
    st.title("➕ Cadastrar Nova Amostra")
    
    if usuario_logado.papel != PapelUsuario.BRASIL and usuario_logado.papel != PapelUsuario.ADMIN:
        st.error("⛔ Apenas o escritório do Brasil pode cadastrar novas amostras.")
    else:
        with st.form("form_nova_amostra"):
            descricao = st.text_input("Descrição da amostra")
            fornecedor = st.text_input("Fornecedor")
            cliente = st.text_input("Cliente")
            quantidade = st.number_input("Quantidade pedida", min_value=1, value=1, step=1)
            
            submitted = st.form_submit_button("Cadastrar Amostra")
            
            if submitted:
                try:
                    nova = service.criar_amostra(
                        usuario=usuario_logado, descricao=descricao, fornecedor=fornecedor, 
                        cliente=cliente, responsavel_br_id=usuario_logado.id, quantidade_pedida=int(quantidade)
                    )
                    st.success(f"Amostra {nova.id} cadastrada com sucesso!")
                except ErroBase as e:
                    st.error(f"Erro: {e}")
                except ValueError as e:
                    st.error(f"Erro de validação: {e}")

elif pagina == "Movimentar Estoque":
    # O código que já fizemos na etapa anterior
    st.title("🔄 Movimentar Amostra")
    
    amostras = repo.listar_todas()
    if not amostras:
        st.info("Nenhuma amostra para movimentar.")
    else:
        amostra_selecionada = st.selectbox(
            "Selecione a amostra:", 
            amostras, 
            format_func=lambda a: f"{a.id} - {a.descricao} (Atual: {a.status.value})"
        )
        
        novo_status = st.selectbox(
            "Mudar para qual status?",
            list(StatusAmostra),
            format_func=lambda s: s.value
        )
        
        lista_status = list(StatusAmostra)
        esta_voltando = lista_status.index(novo_status) < lista_status.index(amostra_selecionada.status)
        
        motivo = None
        if esta_voltando:
            st.warning("⚠️ Você está retornando o status desta amostra.")
            motivo = st.text_area("Justificativa (Adendo obrigatório):", placeholder="Ex: Cliente mudou de ideia, erro de digitação, etc.")
            
        if st.button("Confirmar Mudança"):
            try:
                service.mudar_status_amostra(usuario_logado, amostra_selecionada.id, novo_status, motivo_adendo=motivo)
                st.success("Status alterado com sucesso!")
                st.rerun()
            except ErroBase as e:
                st.error(f"Erro: {e}")

elif pagina == "Em Breve":
    st.title("Em Breve")
    st.write("Esta área está reservada para futuras atualizações.")
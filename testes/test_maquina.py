import pytest
from dominio.enums import StatusAmostra, PapelUsuario
from dominio.entidades import Amostra, Usuario
from dominio.maquina_estado import mudar_status
from dominio.erros import ErroPermissao, ErroTransicaoInvalida

@pytest.fixture
def amostra_valida():
    return Amostra(
        descricao="Tecido", fornecedor="Fornecedor X", 
        cliente="Cliente Y", responsavel_br_id="123", quantidade_pedida=1
    )

@pytest.fixture
def usuario_brasil():
    return Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL)

def test_mudar_status_com_sucesso(amostra_valida, usuario_brasil):
    # Solicitada -> Aguardando Pagamento
    mudar_status(amostra_valida, StatusAmostra.AGUARDANDO_PAGAMENTO, usuario_brasil)
    assert amostra_valida.status == StatusAmostra.AGUARDANDO_PAGAMENTO
    assert amostra_valida.versao == 2

def test_bloquear_transicao_invalida(amostra_valida, usuario_brasil):
    # Tentar pular do Solicitada direto pro Estoque (deve dar erro)
    with pytest.raises(ErroTransicaoInvalida):
        mudar_status(amostra_valida, StatusAmostra.EM_ESTOQUE, usuario_brasil)

def test_bloquear_usuario_sem_permissao(amostra_valida):
    # Escritório tentando pagar a amostra (só Brasil pode)
    usuario_escritorio = Usuario(nome="Maria", email="maria@teste.com", papel=PapelUsuario.ESCRITORIO)
    with pytest.raises(ErroPermissao):
        mudar_status(amostra_valida, StatusAmostra.AGUARDANDO_PAGAMENTO, usuario_escritorio)
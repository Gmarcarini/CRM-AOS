import pytest
from repositorio.memoria import RepositorioMemoria
from servicos.amostra_service import AmostraService
from dominio.entidades import Usuario
from dominio.enums import StatusAmostra, PapelUsuario
from dominio.erros import ErroPermissao

@pytest.fixture
def setup():
    repo = RepositorioMemoria()
    service = AmostraService(repo)
    usuario_brasil = Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL)
    usuario_escritorio = Usuario(nome="Maria", email="maria@teste.com", papel=PapelUsuario.ESCRITORIO)
    return service, repo, usuario_brasil, usuario_escritorio

def test_criar_amostra_com_id_sequencial(setup):
    service, repo, user_brasil, _ = setup
    
    amostra1 = service.criar_amostra(user_brasil, "Tecido", "Fornecedor A", "Cliente X", "u1", 1)
    amostra2 = service.criar_amostra(user_brasil, "Botão", "Fornecedor B", "Cliente Y", "u1", 2)
    
    # Verifica se o ID seguiu o padrão (ignorando o ano exato)
    assert amostra1.id.endswith("-0001")
    assert amostra2.id.endswith("-0002")
    assert len(repo.listar_todas()) == 2

def test_escritorio_nao_pode_criar_amostra(setup):
    service, _, _, user_escritorio = setup
    
    # Escritório tentando criar deve dar erro de permissão
    with pytest.raises(ErroPermissao):
        service.criar_amostra(user_escritorio, "Teste", "Forn", "Cli", "u1", 1)

def test_mudar_status_pelo_servico(setup):
    service, _, user_brasil, _ = setup
    
    amostra = service.criar_amostra(user_brasil, "Tecido", "Fornecedor A", "Cliente X", "u1", 1)
    
    # Muda o status pelo serviço
    service.mudar_status_amostra(user_brasil, amostra.id, StatusAmostra.AGUARDANDO_PAGAMENTO)
    
    # Busca do repositório para confirmar que foi salvo
    amostra_atualizada = service.repo.buscar_por_id(amostra.id)
    assert amostra_atualizada.status == StatusAmostra.AGUARDANDO_PAGAMENTO
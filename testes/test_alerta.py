import pytest
from datetime import datetime, timedelta
from repositorio.memoria import RepositorioMemoria
from servicos.amostra_service import AmostraService
from servicos.alerta_servico import AlertaService
from dominio.entidades import Usuario
from dominio.enums import StatusAmostra, PapelUsuario

@pytest.fixture
def setup():
    repo = RepositorioMemoria()
    service = AmostraService(repo)
    alerta_service = AlertaService(repo)
    user_brasil = Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL)
    return service, alerta_service, user_brasil

def test_alerta_estoque_parado(setup):
    service, alerta_service, user = setup
    
    # Cria a amostra
    amostra = service.criar_amostra(user, "Tecido", "Forn", "Cli", "u1", 1)
    
    # Simula a amostra no estoque há 40 dias
    amostra.status = StatusAmostra.EM_ESTOQUE
    amostra.status_desde = datetime.now() - timedelta(days=40)
    
    alertas = alerta_service.gerar_alertas(limite_estoque=30, limite_transito=15, limite_analise=10)
    
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "parada_estoque"
    assert alertas[0]["dias"] == 40

def test_sem_alerta_se_recente(setup):
    service, alerta_service, user = setup
    
    # Cria a amostra (status inicial é SOLICITADA)
    service.criar_amostra(user, "Tecido", "Forn", "Cli", "u1", 1)
    
    # Se a amostra acabou de ser criada, não deve ter alerta
    alertas = alerta_service.gerar_alertas(limite_estoque=30, limite_transito=15, limite_analise=10)
    
    assert len(alertas) == 0
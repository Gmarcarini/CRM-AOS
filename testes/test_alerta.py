"""Alertas de amostra parada.

Única alteração de teste autorizada neste bloco (B3-bis): a persistência
explícita em `test_alerta_estoque_parado`. O motivo é conceitual, não cosmético —
com cópias defensivas (B3), mutar o objeto devolvido pelo repositório não chega
ao estado armazenado. O teste funcionava justamente por causa do acoplamento que
o contrato está eliminando.
"""

from datetime import datetime, timedelta

import pytest

from dominio.entidades import Usuario
from dominio.enums import PapelUsuario, StatusAmostra
from repositorio.memoria import RepositorioMemoria
from servicos.alerta_servico import AlertaService
from servicos.amostra_service import AmostraService


@pytest.fixture
def setup():
    repo = RepositorioMemoria()
    service = AmostraService(repo)
    alerta_service = AlertaService(repo)
    user_brasil = Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL)
    return service, alerta_service, user_brasil


def test_alerta_estoque_parado(setup):
    service, alerta_service, user = setup

    amostra = service.criar_amostra(user, "Tecido", "Forn", "Cli", "u1", 1)

    # Simula a amostra no estoque há 40 dias.
    amostra.status = StatusAmostra.EM_ESTOQUE
    amostra.status_desde = datetime.now() - timedelta(days=40)
    # B3-bis: persistência explícita. O repositório devolve cópia; sem este
    # salvamento a mutação acima não existe para o AlertaService.
    service.repo.salvar_amostra(amostra)

    alertas = alerta_service.gerar_alertas(limite_estoque=30, limite_transito=15, limite_analise=10)

    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "parada_estoque"
    assert alertas[0]["dias"] == 40


def test_sem_alerta_se_recente(setup):
    service, alerta_service, user = setup

    service.criar_amostra(user, "Tecido", "Forn", "Cli", "u1", 1)

    alertas = alerta_service.gerar_alertas(limite_estoque=30, limite_transito=15, limite_analise=10)

    assert len(alertas) == 0
"""Cobertura mínima da fábrica de repositórios e do seed.

Dois comportamentos que a aceitação do Bloco B exige e que hoje só são
verificados rodando o uvicorn à mão:

1. `semear` é idempotente — pode rodar em todo start da API sem duplicar.
2. `criar_repositorio` falha alto em configuração inválida, em vez de degradar
   para o mock em silêncio.
"""

import pytest

from repositorio.factory import criar_repositorio
from repositorio.memoria import RepositorioMemoria
from repositorio.seed import semear


def test_semear_duas_vezes_nao_duplica_usuarios():
    repo = RepositorioMemoria()

    semear(repo)
    primeira_contagem = len(repo.listar_usuarios())

    semear(repo)
    segunda_contagem = len(repo.listar_usuarios())

    assert primeira_contagem == 5
    assert segunda_contagem == 5


def test_criar_repositorio_com_backend_invalido_falha_alto(monkeypatch):
    monkeypatch.setenv("REPOSITORIO", "mockk")

    with pytest.raises(ValueError, match="REPOSITORIO inválido"):
        criar_repositorio()


def test_criar_repositorio_supabase_ainda_nao_implementado(monkeypatch):
    monkeypatch.setenv("REPOSITORIO", "supabase")

    with pytest.raises(NotImplementedError):
        criar_repositorio()


def test_criar_repositorio_mock_devolve_instancia_nova(monkeypatch):
    monkeypatch.setenv("REPOSITORIO", "mock")

    primeiro = criar_repositorio()
    segundo = criar_repositorio()

    assert isinstance(primeiro, RepositorioMemoria)
    assert primeiro is not segundo
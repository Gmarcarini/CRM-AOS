"""Testes do núcleo de máquina de estados da amostra."""

import pytest

from dominio.entidades import Amostra, Usuario
from dominio.enums import PapelUsuario, StatusAmostra
from dominio.erros import ErroPermissao
from dominio.maquina_estado import aplicar_mudanca_status, validar_permissao_mudanca


@pytest.fixture
def amostra_valida() -> Amostra:
    return Amostra(
        descricao="Tecido",
        fornecedor="Fornecedor X",
        cliente_id="cliente-1",
        responsavel_br_id="u1",
        quantidade_pedida=1,
    )


@pytest.fixture
def usuario_brasil() -> Usuario:
    return Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL)


def test_aplicar_mudanca_incrementa_versao(amostra_valida):
    aplicar_mudanca_status(amostra_valida, StatusAmostra.AGUARDANDO_PAGAMENTO)

    assert amostra_valida.status == StatusAmostra.AGUARDANDO_PAGAMENTO
    assert amostra_valida.versao == 2


def test_aplicar_mudanca_registra_chegada_em_analise(amostra_valida):
    aplicar_mudanca_status(amostra_valida, StatusAmostra.SOB_ANALISE)

    assert amostra_valida.data_chegada_analise is not None


def test_aplicar_mudanca_registra_entrada_em_estoque(amostra_valida):
    aplicar_mudanca_status(amostra_valida, StatusAmostra.EM_ESTOQUE)

    assert amostra_valida.data_entrada_estoque is not None


def test_bloquear_usuario_inativo(amostra_valida, usuario_brasil):
    usuario_brasil.ativo = False

    with pytest.raises(ErroPermissao):
        validar_permissao_mudanca(amostra_valida, usuario_brasil)


def test_bloquear_escritorio_em_amostra_finalizada(amostra_valida):
    usuario_escritorio = Usuario(
        nome="Maria", email="maria@teste.com", papel=PapelUsuario.ESCRITORIO
    )
    amostra_valida.status = StatusAmostra.ENCERRADA

    with pytest.raises(ErroPermissao):
        validar_permissao_mudanca(amostra_valida, usuario_escritorio)


def test_permitir_brasil_em_amostra_finalizada(amostra_valida, usuario_brasil):
    amostra_valida.status = StatusAmostra.ENCERRADA

    # Não deve levantar exceção.
    validar_permissao_mudanca(amostra_valida, usuario_brasil)
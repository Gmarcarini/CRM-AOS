"""Testes da máquina de estados da amostra.

TRÊS TESTES AQUI SÃO xfail(strict=True) DE PROPÓSITO.

Eles especificam `mudar_status`, que ainda não existe em
`dominio/maquina_estado.py`. A função é a dívida declarada do Bloco D.

Enquanto ela não existir, estes testes falham com ImportError e o pytest os
reporta como XFAIL — comportamento esperado, não regressão.

Quando `mudar_status` for implementada e os testes passarem, o pytest reporta
XPASS e, por causa de strict=True, converte isso em FALHA de suíte. É o gatilho
obrigatório para remover a marca. XPASS não deve ser silenciado.

O import de `mudar_status` fica DENTRO de cada teste, e não no topo do módulo:
erro de import no topo quebra a coleta do arquivo inteiro e os marcadores xfail
nunca são avaliados.

REGRA DA SPRINT: teste existente só muda quando a instrução autoriza
nominalmente. Se um teste bloqueia a entrega, a saída é xfail (como aqui), skip
com motivo escrito, ou reportar o bloqueio — nunca reescrever a asserção para
caber no código que já existe.
"""

import pytest

from dominio.entidades import Amostra, Usuario
from dominio.enums import PapelUsuario, StatusAmostra
from dominio.erros import ErroPermissao, ErroTransicaoInvalida
from dominio.maquina_estado import (
    aplicar_mudanca_status,
    validar_permissao_mudanca,
)

# Motivo único, reutilizado nos três marcadores pendentes.
MOTIVO_BLOCO_D = (
    "mudar_status ainda não existe em dominio/maquina_estado.py; "
    "implementação prevista no Bloco D"
)


# --- Fixtures compartilhadas ------------------------------------------------


@pytest.fixture
def amostra_valida() -> Amostra:
    return Amostra(
        descricao="Tecido",
        fornecedor="Fornecedor X",
        cliente_id="Cliente Y",
        responsavel_br_id="123",
        quantidade_pedida=1,
    )


@pytest.fixture
def usuario_brasil() -> Usuario:
    return Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL)


# --- Especificação de mudar_status (pendente, Bloco D) ----------------------


@pytest.mark.xfail(strict=True, reason=MOTIVO_BLOCO_D)
def test_mudar_status_com_sucesso(amostra_valida, usuario_brasil):
    """Transição válida deve aplicar o novo status e incrementar a versão."""
    from dominio.maquina_estado import mudar_status

    mudar_status(amostra_valida, StatusAmostra.AGUARDANDO_PAGAMENTO, usuario_brasil)

    assert amostra_valida.status == StatusAmostra.AGUARDANDO_PAGAMENTO
    assert amostra_valida.versao == 2


@pytest.mark.xfail(strict=True, reason=MOTIVO_BLOCO_D)
def test_bloquear_transicao_invalida(amostra_valida, usuario_brasil):
    """REGRA: não é permitido pular de SOLICITADA direto para EM_ESTOQUE."""
    from dominio.maquina_estado import mudar_status

    with pytest.raises(ErroTransicaoInvalida):
        mudar_status(amostra_valida, StatusAmostra.EM_ESTOQUE, usuario_brasil)


@pytest.mark.xfail(strict=True, reason=MOTIVO_BLOCO_D)
def test_bloquear_usuario_sem_permissao(amostra_valida):
    """REGRA: escritório não move amostra para AGUARDANDO_PAGAMENTO."""
    from dominio.maquina_estado import mudar_status

    usuario_escritorio = Usuario(
        nome="Maria", email="maria@teste.com", papel=PapelUsuario.ESCRITORIO
    )

    with pytest.raises(ErroPermissao):
        mudar_status(
            amostra_valida, StatusAmostra.AGUARDANDO_PAGAMENTO, usuario_escritorio
        )


# --- Cobertura de aplicar_mudanca_status (já existe) ------------------------


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


# --- Cobertura de validar_permissao_mudanca (já existe) ---------------------


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
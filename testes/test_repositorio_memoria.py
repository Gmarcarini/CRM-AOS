"""Prova imediata de que a memória honra o contrato do Bloco B.

Escopo: nomenclatura por agregado, integridade do agregado e — o ponto central —
cópia defensiva. A suíte de contrato parametrizada por implementação
(`testes/contrato/`) é o Bloco E e vai promover e expandir estes casos; repetir
aqui a matriz completa criaria duas suítes divergindo com o tempo.
"""

import pytest

from dominio.entidades import (
    Amostra,
    Cliente,
    Contato,
    ItemPedido,
    Pedido,
    Usuario,
)
from dominio.enums import PapelUsuario
from dominio.erros import EntidadeNaoEncontrada
from repositorio.contrato import RepositorioCompleto
from repositorio.memoria import RepositorioMemoria


@pytest.fixture
def repo() -> RepositorioMemoria:
    """Instância limpa por caso: sem estado compartilhado entre testes."""
    return RepositorioMemoria()


# --- Construtores de apoio -------------------------------------------------


def _amostra(descricao: str = "Tecido", quantidade: int = 3) -> Amostra:
    return Amostra(
        descricao=descricao,
        fornecedor="Fornecedor X",
        cliente_id="cliente-1",
        responsavel_br_id="u1",
        quantidade_pedida=quantidade,
    )


def _cliente(contatos: list[Contato]) -> Cliente:
    return Cliente(
        razao_social="Cliente Y LTDA",
        codigo="001",
        cnpj="11222333000181",
        usuario_responsavel_id="u1",
        contatos=contatos,
    )


def _contato(nome: str) -> Contato:
    return Contato(nome=nome, telefone="(+55) 51 99153-1100", email=f"{nome.lower()}@y.com")


def _pedido(itens: list[ItemPedido], documentos: list[dict]) -> Pedido:
    return Pedido(
        cliente_id="cliente-1",
        fornecedor_id="fornecedor-1",
        codigo="TM2611CB-TC01",
        sigla_cliente="CB",
        sigla_produto="TC",
        numero_sequencial=1,
        ano_mes="2611",
        criado_por_id="u1",
        itens=itens,
        documentos=documentos,
    )


# --- Conformidade estrutural do contrato ----------------------------------
# Não usa isinstance: `@runtime_checkable` é proibido (compara nomes, não
# assinaturas). Verificar presença de cada método é honesto quanto ao que se
# pode afirmar sem executar comportamento.


def test_repositorio_memoria_declara_todos_os_metodos_do_contrato():
    metodos_do_contrato = [nome for nome in dir(RepositorioCompleto) if not nome.startswith("_")]
    ausentes = [nome for nome in metodos_do_contrato if not hasattr(RepositorioMemoria, nome)]
    assert ausentes == []


# --- Agregado amostra ------------------------------------------------------


def test_salvar_e_buscar_amostra_preserva_todos_os_campos(repo):
    amostra = _amostra()
    repo.salvar_amostra(amostra)

    recuperada = repo.buscar_amostra_por_id(amostra.id)

    assert recuperada == amostra


def test_buscar_amostra_inexistente_lanca_entidade_nao_encontrada(repo):
    with pytest.raises(EntidadeNaoEncontrada):
        repo.buscar_amostra_por_id("AM-0000-9999")


# --- Agregado cliente ------------------------------------------------------


def test_cliente_preserva_todos_os_contatos(repo):
    cliente = _cliente([_contato("Ana"), _contato("Bruno")])
    repo.salvar_cliente(cliente)

    recuperado = repo.buscar_cliente_por_id(cliente.id)

    assert [contato.nome for contato in recuperado.contatos] == ["Ana", "Bruno"]
    # Contatos devem ser objetos distintos, não as mesmas instâncias.
    assert recuperado.contatos[0] is not cliente.contatos[0]


def test_mutar_objeto_devolvido_nao_altera_estado_armazenado(repo):
    """O teste mais importante do bloco.

    É o que impede o padrão "muta e esquece de salvar": em memória ele
    funcionaria; num banco real, o dado simplesmente não é gravado.
    """
    cliente = _cliente([_contato("Ana")])
    repo.salvar_cliente(cliente)

    devolvido = repo.buscar_cliente_por_id(cliente.id)
    devolvido.razao_social = "ALTERADO"
    devolvido.contatos[0].nome = "ALTERADO"

    armazenado = repo.buscar_cliente_por_id(cliente.id)

    assert armazenado.razao_social == "Cliente Y LTDA"
    assert armazenado.contatos[0].nome == "Ana"


def test_excluir_cliente_remove_e_busca_seguinte_falha(repo):
    cliente = _cliente([])
    repo.salvar_cliente(cliente)

    repo.excluir_cliente(cliente.id)

    with pytest.raises(EntidadeNaoEncontrada):
        repo.buscar_cliente_por_id(cliente.id)


# --- Agregado pedido -------------------------------------------------------


def test_pedido_preserva_itens_e_documentos(repo):
    pedido = _pedido(
        [
            ItemPedido(nome_produto="Toalha", quantidade=10, unidade_medida="PC", preco_unitario=2.5),
            ItemPedido(nome_produto="Toalha premium", quantidade=5, unidade_medida="PC", preco_unitario=4.0),
        ],
        [{"nome": "PI.pdf", "caminho": "uploads/PI.pdf", "data_upload": "2026-11-26T10:00:00"}],
    )
    repo.salvar_pedido(pedido)

    recuperado = repo.buscar_pedido_por_id(pedido.id)

    assert len(recuperado.itens) == 2
    assert recuperado.itens[0].valor_total == 25.0
    assert len(recuperado.documentos) == 1
    assert recuperado.documentos[0]["nome"] == "PI.pdf"


def test_salvar_pedido_duas_vezes_nao_duplica(repo):
    pedido = _pedido([], [])
    repo.salvar_pedido(pedido)

    pedido.sigla_produto = "CB"
    repo.salvar_pedido(pedido)

    assert len(repo.listar_pedidos()) == 1
    assert repo.buscar_pedido_por_id(pedido.id).sigla_produto == "CB"


# --- Categorias ------------------------------------------------------------


def test_salvar_categoria_duas_vezes_mantem_uma_ocorrencia_ordenada(repo):
    repo.salvar_categoria("Zíper")
    repo.salvar_categoria("  Embalagens  ")  # normalizado pelo repositório
    repo.salvar_categoria("Embalagens")

    assert repo.listar_categorias() == ["Embalagens", "Zíper"]


def test_categoria_vazia_e_ignorada(repo):
    repo.salvar_categoria("   ")

    assert repo.listar_categorias() == []

def _usuario(
    nome: str = "Giovanni",
    email: str = "giovanni@aosltd.net",
) -> Usuario:
    return Usuario(
        id="u1",
        nome=nome,
        email=email,
        papel=PapelUsuario.ADMIN,
        localizacao="brasil",
    )


def test_buscar_usuario_por_email_ignora_caixa(repo):
    repo.salvar_usuario(_usuario())

    encontrado = repo.buscar_usuario_por_email("GIOVANNI@AOSLTD.NET")

    assert encontrado is not None
    assert encontrado.id == "u1"


def test_buscar_usuario_por_email_inexistente_devolve_none(repo):
    assert repo.buscar_usuario_por_email("ninguem@aosltd.net") is None
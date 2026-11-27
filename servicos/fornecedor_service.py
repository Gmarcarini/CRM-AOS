"""Cadastro e edição de fornecedor.

Depende de `FornecedorComCategorias` porque cadastrar fornecedor também
alimenta o autocomplete de categorias: a categoria digitada livremente passa a
existir no sistema. É a menor dependência possível — dois protocolos, não o
repositório inteiro.
"""

from dominio.entidades import Fornecedor
from dominio.erros import ErroValidacao
from repositorio.contrato import FornecedorComCategorias


class FornecedorService:
    def __init__(self, repositorio: FornecedorComCategorias) -> None:
        self.repo = repositorio

    def criar_fornecedor(self, dados: dict, usuario_responsavel_id: str) -> Fornecedor:
        if not dados.get("nome") or not dados.get("nome_contato"):
            raise ErroValidacao("Nome e Nome do Contato são obrigatórios.")

        categoria = dados.get("categoria_produtos", "")
        if categoria:
            # Normalização e descarte de vazio são do repositório, não daqui.
            self.repo.salvar_categoria(categoria)

        novo_fornecedor = Fornecedor(
            nome=dados["nome"],
            nome_contato=dados["nome_contato"],
            categoria_produtos=categoria,
            usuario_responsavel_id=usuario_responsavel_id,
            pedidos=dados.get("pedidos", []),
        )
        self.repo.salvar_fornecedor(novo_fornecedor)
        return novo_fornecedor

    def editar_fornecedor(self, fornecedor: Fornecedor, dados: dict) -> Fornecedor:
        if not dados.get("nome") or not dados.get("nome_contato"):
            raise ErroValidacao("Nome e Nome do Contato são obrigatórios.")

        categoria = dados.get("categoria_produtos", "")
        if categoria:
            self.repo.salvar_categoria(categoria)

        fornecedor.nome = dados["nome"]
        fornecedor.nome_contato = dados["nome_contato"]
        fornecedor.categoria_produtos = categoria
        fornecedor.pedidos = dados.get("pedidos", fornecedor.pedidos)

        self.repo.salvar_fornecedor(fornecedor)
        return fornecedor
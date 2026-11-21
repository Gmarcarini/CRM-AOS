from repositorio.memoria import RepositorioMemoria
from dominio.entidades import Fornecedor
from dominio.erros import ErroValidacao
from repositorio.banco_dados import salvar_categoria

class FornecedorService:
    def __init__(self, repositorio: RepositorioMemoria):
        self.repo = repositorio

    def criar_fornecedor(self, dados: dict, usuario_responsavel_id: str) -> Fornecedor:
        if not dados.get("nome") or not dados.get("nome_contato"):
            raise ErroValidacao("Nome e Nome do Contato são obrigatórios.")

        if dados.get("categoria_produtos"):
            salvar_categoria(dados["categoria_produtos"])

        novo_fornecedor = Fornecedor(
            nome=dados["nome"],
            nome_contato=dados["nome_contato"],
            categoria_produtos=dados.get("categoria_produtos", ""),
            usuario_responsavel_id=usuario_responsavel_id,
            pedidos=dados.get("pedidos", [])
        )
        
        self.repo.salvar_fornecedor(novo_fornecedor)
        return novo_fornecedor

    def editar_fornecedor(self, fornecedor: Fornecedor, dados: dict) -> Fornecedor:
        if not dados.get("nome") or not dados.get("nome_contato"):
            raise ErroValidacao("Nome e Nome do Contato são obrigatórios.")
        
        if dados.get("categoria_produtos"):
            salvar_categoria(dados["categoria_produtos"])
            
        fornecedor.nome = dados["nome"]
        fornecedor.nome_contato = dados["nome_contato"]
        fornecedor.categoria_produtos = dados.get("categoria_produtos", "")
        fornecedor.pedidos = dados.get("pedidos", fornecedor.pedidos)
        
        self.repo.salvar_fornecedor(fornecedor)
        return fornecedor
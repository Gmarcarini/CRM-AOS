from typing import Dict, List
from dominio.entidades import Amostra, Adendo, Cliente, Fornecedor, Pedido

class RepositorioMemoria:
    def __init__(self):
        self._amostras: Dict[str, Amostra] = {}
        self._adendos: List[Adendo] = []
        self._clientes: Dict[str, Cliente] = {}
        self._fornecedores: Dict[str, Fornecedor] = {}
        self._pedidos: Dict[str, Pedido] = {}
    
    def salvar(self, amostra: Amostra) -> None:
        self._amostras[amostra.id] = amostra
        
    def buscar_por_id(self, id_amostra: str) -> Amostra:
        amostra = self._amostras.get(id_amostra)
        if not amostra:
            raise ValueError("Amostra não encontrada.")
        return amostra
        
    def listar_todas(self) -> List[Amostra]:
        return list(self._amostras.values())

    def salvar_adendo(self, adendo: Adendo) -> None:
        self._adendos.append(adendo)
        
    def listar_adendos_por_amostra(self, amostra_id: str) -> List[Adendo]:
        return [a for a in self._adendos if a.amostra_id == amostra_id]

    def salvar_cliente(self, cliente: Cliente) -> None:
        self._clientes[cliente.id] = cliente
        
    def buscar_cliente_por_id(self, id_cliente: str) -> Cliente:
        cliente = self._clientes.get(id_cliente)
        if not cliente:
            raise ValueError("Cliente não encontrado.")
        return cliente
        
    def listar_clientes(self) -> List[Cliente]:
        return list(self._clientes.values())

    def salvar_fornecedor(self, fornecedor: Fornecedor) -> None:
        self._fornecedores[fornecedor.id] = fornecedor
        
    def buscar_fornecedor_por_id(self, id_fornecedor: str) -> Fornecedor:
        fornecedor = self._fornecedores.get(id_fornecedor)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado.")
        return fornecedor
        
    def listar_fornecedores(self) -> List[Fornecedor]:
        return list(self._fornecedores.values())

    def salvar_pedido(self, pedido: Pedido) -> None:
        self._pedidos[pedido.id] = pedido
        
    def buscar_pedido_por_id(self, id_pedido: str) -> Pedido:
        pedido = self._pedidos.get(id_pedido)
        if not pedido:
            raise ValueError("Pedido não encontrado.")
        return pedido
        
    def listar_pedidos(self) -> List[Pedido]:
        return list(self._pedidos.values())


"""Entidades de domínio do CRM AOS.

Dataclasses puras: sem dependência de FastAPI, Streamlit ou banco de dados.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from dominio.enums import (
    PapelUsuario,
    ProcessoPedido,
    StatusAmostra,
    StatusCliente,
    StatusPedido,
)


@dataclass
class Usuario:
    nome: str
    email: str
    papel: PapelUsuario
    localizacao: str = "brasil"  # brasil | china
    ativo: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Amostra:
    descricao: str
    fornecedor: str
    cliente_id: str
    responsavel_br_id: str
    quantidade_pedida: int
    # Status e controle
    status: StatusAmostra = StatusAmostra.SOLICITADA
    versao: int = 1
    # Identificadores
    id: str = field(default_factory=lambda: str(uuid4()))
    token_qr: str = field(default_factory=lambda: str(uuid4()))
    # Datas
    data_criacao: datetime = field(default_factory=datetime.now)
    status_desde: datetime = field(default_factory=datetime.now)
    # Opcionais
    quantidade_recebida: Optional[int] = None
    localizacao: Optional[str] = None
    data_chegada_analise: Optional[datetime] = None
    data_entrada_estoque: Optional[datetime] = None


@dataclass
class Adendo:
    amostra_id: str
    status_anterior: StatusAmostra
    status_novo: StatusAmostra
    motivo: str
    data_criacao: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Contato:
    nome: str
    telefone: str
    email: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Cliente:
    razao_social: str
    codigo: str
    cnpj: str
    usuario_responsavel_id: str
    status: StatusCliente = StatusCliente.ATIVO
    # Endereço
    rua: str = ""
    numero: str = ""
    sala: Optional[str] = ""
    bairro: str = ""
    cidade: str = ""
    estado: str = ""
    pais: str = "Brasil"
    # Contatos
    contatos: List[Contato] = field(default_factory=list)
    # Controle
    data_cadastro: datetime = field(default_factory=datetime.now)
    status_desde: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Fornecedor:
    nome: str
    nome_contato: str
    categoria_produtos: str
    usuario_responsavel_id: str
    pedidos: List[str] = field(default_factory=list)
    data_cadastro: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ItemPedido:
    nome_produto: str
    quantidade: float
    unidade_medida: str
    preco_unitario: float
    id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def valor_total(self) -> float:
        return self.quantidade * self.preco_unitario


@dataclass
class Pedido:
    """Agregado de pedido de importação.

    Definição ÚNICA: a versão anterior, sem criado_por_id, itens e documentos,
    era sobrescrita no mesmo módulo e causava perda silenciosa de campo.
    """

    cliente_id: str
    fornecedor_id: str
    codigo: str  # Ex: TM2611CB-TC03
    sigla_cliente: str  # Ex: CB
    sigla_produto: str  # Ex: TC
    numero_sequencial: int  # Ex: 3
    ano_mes: str  # Ex: 2611
    criado_por_id: str
    status: StatusPedido = StatusPedido.ATIVO
    processo_atual: ProcessoPedido = ProcessoPedido.AGUARDANDO_PAGAMENTO_1
    motivo_standby: Optional[str] = None
    motivo_cancelamento: Optional[str] = None
    itens: List[ItemPedido] = field(default_factory=list)
    amostras_ids: List[str] = field(default_factory=list)
    documentos: List[dict] = field(default_factory=list)
    feedback: Optional[str] = None
    data_criacao: datetime = field(default_factory=datetime.now)
    data_modificacao: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))
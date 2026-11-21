from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from dominio.enums import StatusAmostra, PapelUsuario, StatusCliente, StatusPedido, ProcessoPedido
import re


@dataclass
class Usuario:
    nome: str
    email: str
    papel: PapelUsuario
    localizacao: str = "brasil" # <-- NOVO (brasil ou china)
    ativo: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class Amostra:
    descricao: str
    fornecedor: str
    cliente_id: str
    responsavel_br_id: str
    quantidade_pedida: int
    
    # Status e Controle
    status: StatusAmostra = StatusAmostra.SOLICITADA
    versao: int = 1
    
    # Identificadores
    id: str = field(default_factory=lambda: str(uuid4()))
    token_qr: str = field(default_factory=lambda: str(uuid4()))
    
    # Datas
    data_criacao: datetime = field(default_factory=datetime.now)
    status_desde: datetime = field(default_factory=datetime.now)
    
    # Opcionais (que começam vazios)
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
    status: StatusCliente = StatusCliente.ATIVO # Padrão é Ativo
    
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
    pedidos: List[str] = field(default_factory=list) # Lista simples por enquanto
    data_cadastro: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class Pedido:
    cliente_id: str
    fornecedor_id: str
    codigo: str # Ex: TM2611CB-TC03
    sigla_cliente: str # Ex: CB
    sigla_produto: str # Ex: TC
    numero_sequencial: int # Ex: 3
    ano_mes: str # Ex: 2611
    
    status: StatusPedido = StatusPedido.ATIVO
    processo_atual: ProcessoPedido = ProcessoPedido.AGUARDANDO_PAGAMENTO_1
    motivo_standby: Optional[str] = None
    
    amostras_ids: List[str] = field(default_factory=list)
    feedback: Optional[str] = None
    
    data_criacao: datetime = field(default_factory=datetime.now)
    data_modificacao: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))


from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from dominio.enums import StatusPedido, ProcessoPedido

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
    cliente_id: str
    fornecedor_id: str
    codigo: str
    sigla_cliente: str
    sigla_produto: str
    numero_sequencial: int
    ano_mes: str
    criado_por_id: str  # <-- NOVO: Quem criou o pedido
    
    status: StatusPedido = StatusPedido.ATIVO
    processo_atual: ProcessoPedido = ProcessoPedido.AGUARDANDO_PAGAMENTO_1
    motivo_standby: Optional[str] = None
    motivo_cancelamento: Optional[str] = None # <-- NOVO: Para o botão de cancelar
    
    itens: List[ItemPedido] = field(default_factory=list) # <-- NOVO: A tabela de produtos
    
    amostras_ids: List[str] = field(default_factory=list)
    documentos: List[dict] = field(default_factory=list) # <-- NOVO: Lista para guardar nome e caminho do arquivo
    feedback: Optional[str] = None
    
    data_criacao: datetime = field(default_factory=datetime.now)
    data_modificacao: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))
    
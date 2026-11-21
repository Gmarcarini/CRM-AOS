from enum import Enum

class StatusAmostra(Enum):
    SOLICITADA = "solicitada"
    AGUARDANDO_PAGAMENTO = "aguardando_pagamento"
    AGUARDANDO_PRODUCAO = "aguardando_producao"
    EM_TRANSITO = "em_transito"
    SOB_ANALISE = "sob_analise"
    EM_ESTOQUE = "em_estoque"
    ENVIADA_AO_CLIENTE = "enviada_ao_cliente"
    ENCERRADA = "encerrada"
    DESCARTADA = "descartada"
    CANCELADA = "cancelada"
    EXTRAVIADA = "extraviada"

class PapelUsuario(Enum):
    BRASIL = "brasil"
    ESCRITORIO = "escritorio"
    ADMIN = "admin"

class StatusCliente(Enum):
    ATIVO = "ativo"
    STANDBY = "standby"
    INATIVO = "inativo"

class StatusPedido(Enum):
    ATIVO = "ativo"
    STANDBY = "standby"
    INATIVO = "inativo"

class ProcessoPedido(Enum):
    AGUARDANDO_PAGAMENTO_1 = "aguardando_pagamento_1"
    EM_PRODUCAO = "em_producao"
    AGUARDANDO_VISTORIA = "aguardando_vistoria"
    AGUARDANDO_PAGAMENTO_2 = "aguardando_pagamento_2"
    CARREGANDO = "carregando"
    AGUARDANDO_PORTO_CHINA = "aguardando_porto_china"
    EM_FRETE = "em_frete"
    ENTREGUE_PORTO_BRASIL = "entregue_porto_brasil"
    FINALIZADO = "finalizado"
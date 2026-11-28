"""API HTTP (FastAPI) do CRM AOS.

Única porta de entrada do backend: expõe os endpoints consumidos pelo frontend
React (estoque-frontend) e delega toda regra de negócio aos serviços.

Regra de ouro desta camada: ela não sabe qual backend de persistência está por
trás. O repositório vem exclusivamente de `repositorio.factory`, e o seed roda
uma única vez na inicialização.
"""

from typing import List, Optional

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dominio.entidades import Usuario
from dominio.enums import PapelUsuario, ProcessoPedido, StatusAmostra, StatusCliente
from dominio.erros import EntidadeNaoEncontrada, ErroBase, ErroPermissao, ErroValidacao
from repositorio.factory import criar_repositorio
from repositorio.seed import semear
from servicos.amostra_service import AmostraService
from servicos.cliente_service import ClienteService
from servicos.fornecedor_service import FornecedorService
from servicos.pedido_service import PedidoService

# --- INFRAESTRUTURA ---------------------------------------------------------

app = FastAPI(title="API Estoque de Amostras")

# CORS: o React roda em outra porta durante o desenvolvimento.
# TODO(Bloco C): substituir o curinga por lista explícita vinda do ambiente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A fábrica é o único ponto do sistema autorizado a instanciar repositório.
repo = criar_repositorio()
semear(repo)

service = AmostraService(repo)
cliente_service = ClienteService(repo)
fornecedor_service = FornecedorService(repo)
pedido_service = PedidoService(repo)


def _usuario_ou_401(usuario_id: str) -> Usuario:
    """Resolve o usuário do header `x-usuario-id` ou aborta com 401.

    Ponto único de tradução enquanto a dependência `usuario_atual` não existe.
    TODO(Bloco C3): substituir por dependência injetada em todas as rotas.
    """
    try:
        return repo.buscar_usuario_por_id(usuario_id)
    except EntidadeNaoEncontrada:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.") from None


# --- MODELOS DE DADOS (payloads recebidos do React) -------------------------


class ContatoRequest(BaseModel):
    nome: str
    telefone: str
    email: str


class NovoClienteRequest(BaseModel):
    razao_social: str
    codigo: str
    cnpj: str
    status: StatusCliente = StatusCliente.ATIVO
    rua: str = ""
    numero: str = ""
    sala: Optional[str] = ""
    bairro: str = ""
    cidade: str = ""
    estado: str = ""
    pais: str = "Brasil"
    contatos: List[ContatoRequest] = []


class EditarClienteRequest(NovoClienteRequest):
    pass


class NovaAmostraRequest(BaseModel):
    descricao: str
    fornecedor: str
    cliente: str
    quantidade_pedida: int


class MudarStatusRequest(BaseModel):
    novo_status: StatusAmostra
    motivo_adendo: Optional[str] = None


class NovoFornecedorRequest(BaseModel):
    nome: str
    nome_contato: str
    categoria_produtos: str = ""
    pedidos: List[str] = []


class EditarFornecedorRequest(NovoFornecedorRequest):
    pass


class NovoPedidoRequest(BaseModel):
    """Payload de criação de pedido.

    ATENÇÃO: `extra="forbid"` está deliberadamente ausente. O frontend envia
    hscode, incoterm, portos, tempo_producao e pagamentos, que o backend ignora
    hoje. Ligar forbid sem criar esses campos quebra a criação de pedido em
    produção. A correção é um commit indivisível (entidade + request + response
    + frontend) e pertence à Sprint 1.
    """

    cliente_id: str
    fornecedor_id: str
    sigla_cliente: str
    sigla_produto: str


class MudarProcessoRequest(BaseModel):
    novo_processo: ProcessoPedido


class ItemPedidoRequest(BaseModel):
    nome_produto: str
    quantidade: float
    unidade_medida: str
    preco_unitario: float


class CancelarPedidoRequest(BaseModel):
    motivo: str


# --- ROTAS: CLIENTES --------------------------------------------------------


@app.get("/clientes")
def listar_clientes():
    return [
        {
            "id": cliente.id,
            "razao_social": cliente.razao_social,
            "codigo": cliente.codigo,
            "cnpj": cliente.cnpj,
            "status": cliente.status.value,
            "cidade": cliente.cidade,
            "rua": cliente.rua,
            "numero": cliente.numero,
            "sala": cliente.sala,
            "bairro": cliente.bairro,
            "estado": cliente.estado,
            "pais": cliente.pais,
            "usuario_responsavel_id": cliente.usuario_responsavel_id,
            "contatos": [
                {"nome": contato.nome, "telefone": contato.telefone, "email": contato.email}
                for contato in cliente.contatos
            ],
        }
        for cliente in repo.listar_clientes()
    ]


@app.post("/clientes")
def criar_cliente(req: NovoClienteRequest, x_usuario_id: str = Header(...)):
    usuario = _usuario_ou_401(x_usuario_id)
    try:
        dados = req.model_dump()
        dados["status"] = req.status.value
        novo = cliente_service.criar_cliente(dados, usuario_responsavel_id=usuario.id)
        return {"mensagem": "Cliente criado", "id": novo.id}
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


@app.put("/clientes/{cliente_id}")
def editar_cliente(
    cliente_id: str,
    req: EditarClienteRequest,
    x_usuario_id: str = Header(...),
):
    """Edição restrita ao responsável ou a um admin.

    Antes o usuário vinha do SQLite como `dict` (`usuario["papel"] != "admin"`).
    Agora vem do repositório como `Usuario`, então a comparação é com o enum —
    mais seguro: string livre não sobrevive a erro de digitação do lado do banco.
    """
    try:
        cliente = repo.buscar_cliente_por_id(cliente_id)
        usuario = _usuario_ou_401(x_usuario_id)
        if cliente.usuario_responsavel_id != usuario.id and usuario.papel != PapelUsuario.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para editar este cliente.",
            )
        dados = req.model_dump()
        dados["status"] = req.status.value
        cliente_service.editar_cliente(cliente, dados)
        return {"mensagem": "Cliente atualizado com sucesso"}
    except EntidadeNaoEncontrada as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


# --- ROTAS: AMOSTRAS --------------------------------------------------------


@app.get("/amostras")
def listar_amostras():
    return [
        {
            "id": amostra.id,
            "descricao": amostra.descricao,
            # A entidade guarda cliente_id; o contrato público do front é "cliente".
            "cliente": amostra.cliente_id,
            "status": amostra.status.value,
        }
        for amostra in repo.listar_amostras()
    ]


@app.post("/amostras")
def criar_amostra(req: NovaAmostraRequest):
    # TODO(Bloco C3): substituir o usuário fixo pela dependência `usuario_atual`.
    usuario_brasil = Usuario(
        nome="João",
        email="joao@teste.com",
        papel=PapelUsuario.BRASIL,
        localizacao="brasil",
    )
    try:
        nova = service.criar_amostra(
            usuario=usuario_brasil,
            descricao=req.descricao,
            fornecedor=req.fornecedor,
            cliente=req.cliente,
            responsavel_br_id=usuario_brasil.id,
            quantidade_pedida=req.quantidade_pedida,
        )
        return {"mensagem": "Amostra criada", "id": nova.id}
    except ErroValidacao as erro:
        # Validação de entrada levantada pelo serviço — 400, nunca 500.
        raise HTTPException(status_code=400, detail=str(erro)) from erro


@app.put("/amostras/{amostra_id}/status")
def mudar_status(amostra_id: str, req: MudarStatusRequest):
    # TODO(Bloco C3): substituir o usuário fixo pela dependência `usuario_atual`.
    usuario_brasil = Usuario(
        nome="João",
        email="joao@teste.com",
        papel=PapelUsuario.BRASIL,
        localizacao="brasil",
    )
    try:
        service.mudar_status_amostra(
            usuario=usuario_brasil,
            amostra_id=amostra_id,
            novo_status=req.novo_status,
            motivo_adendo=req.motivo_adendo,
        )
        return {"mensagem": "Status alterado com sucesso"}
    except EntidadeNaoEncontrada as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except ErroBase as erro:
        raise HTTPException(status_code=403, detail=str(erro)) from erro


# --- ROTAS: USUÁRIOS E CATEGORIAS -------------------------------------------


@app.get("/usuarios")
def listar_usuarios():
    """Serialização explícita, campo a campo.

    `dataclasses.asdict` não converte `Enum` puro de forma consistente e
    devolveria o objeto do enum. O frontend usa `usuario.id` (header
    `x-usuario-id`) e `usuario.papel.toUpperCase()` na sidebar, então `papel`
    precisa sair como string.
    """
    return [
        {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "papel": usuario.papel.value,
            "localizacao": usuario.localizacao,
        }
        for usuario in repo.listar_usuarios()
    ]


@app.get("/categorias")
def listar_categorias():
    return repo.listar_categorias()


@app.post("/categorias")
def criar_categoria(nome: str):
    # Mantido como query param: mudar o formato do endpoint é contrato de API
    # e não pertence a este bloco.
    repo.salvar_categoria(nome)
    return {"mensagem": "Categoria salva"}


# --- ROTAS: FORNECEDORES ----------------------------------------------------


@app.get("/fornecedores")
def listar_fornecedores():
    return [
        {
            "id": fornecedor.id,
            "nome": fornecedor.nome,
            "nome_contato": fornecedor.nome_contato,
            "categoria_produtos": fornecedor.categoria_produtos,
            "usuario_responsavel_id": fornecedor.usuario_responsavel_id,
            "pedidos": fornecedor.pedidos,
        }
        for fornecedor in repo.listar_fornecedores()
    ]


@app.post("/fornecedores")
def criar_fornecedor(req: NovoFornecedorRequest, x_usuario_id: str = Header(...)):
    try:
        dados = req.model_dump()
        novo = fornecedor_service.criar_fornecedor(dados, usuario_responsavel_id=x_usuario_id)
        return {"mensagem": "Fornecedor criado", "id": novo.id}
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

@app.put("/fornecedores/{fornecedor_id}")
def editar_fornecedor(
    fornecedor_id: str,
    req: EditarFornecedorRequest,
    x_usuario_id: str = Header(...),
):
    try:
        fornecedor = repo.buscar_fornecedor_por_id(fornecedor_id)
        usuario = _usuario_ou_401(x_usuario_id)
        if fornecedor.usuario_responsavel_id != usuario.id and usuario.papel != PapelUsuario.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para editar este fornecedor.",
            )
        fornecedor_service.editar_fornecedor(fornecedor, req.model_dump())
        return {"mensagem": "Fornecedor atualizado com sucesso"}
    except EntidadeNaoEncontrada as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


# --- ROTAS: PEDIDOS ---------------------------------------------------------


@app.get("/pedidos")
def listar_pedidos():
    return [
        {
            "id": pedido.id,
            "codigo": pedido.codigo,
            "cliente_id": pedido.cliente_id,
            "fornecedor_id": pedido.fornecedor_id,
            "status": pedido.status.value,
            "processo_atual": pedido.processo_atual.value,
            "motivo_standby": pedido.motivo_standby,
            "data_criacao": pedido.data_criacao.isoformat(),
            "amostras_ids": pedido.amostras_ids,
            "sigla_produto": pedido.sigla_produto,
            "sigla_cliente": pedido.sigla_cliente,
            "numero_sequencial": pedido.numero_sequencial,
            "ano_mes": pedido.ano_mes,
            "criado_por_id": pedido.criado_por_id,
            "itens": [
                {
                    "id": item.id,
                    "nome_produto": item.nome_produto,
                    "quantidade": item.quantidade,
                    "unidade_medida": item.unidade_medida,
                    "preco_unitario": item.preco_unitario,
                    "valor_total": item.valor_total,
                }
                for item in pedido.itens
            ],
            "documentos": pedido.documentos,
            "feedback": pedido.feedback,
        }
        for pedido in repo.listar_pedidos()
    ]


@app.post("/pedidos")
def criar_pedido(req: NovoPedidoRequest, x_usuario_id: str = Header(...)):
    try:
        dados = req.model_dump()
        novo = pedido_service.criar_pedido(dados, usuario_id=x_usuario_id)
        return {"mensagem": "Pedido criado", "id": novo.id, "codigo_gerado": novo.codigo}
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

@app.put("/pedidos/{pedido_id}/processo")
def mudar_processo_pedido(pedido_id: str, req: MudarProcessoRequest):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        pedido_service.mudar_processo(pedido, req.novo_processo)
        return {"mensagem": "Processo atualizado com sucesso"}
    except EntidadeNaoEncontrada as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


@app.post("/pedidos/{pedido_id}/itens")
def adicionar_item_pedido(pedido_id: str, req: ItemPedidoRequest):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        item = pedido_service.adicionar_item(pedido, req.model_dump())
        return {"mensagem": "Item adicionado", "id": item.id}
    except EntidadeNaoEncontrada as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


@app.post("/pedidos/{pedido_id}/cancelar")
def cancelar_pedido(
    pedido_id: str,
    req: CancelarPedidoRequest,
    x_usuario_id: str = Header(...),
):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        pedido_service.cancelar_pedido(pedido, x_usuario_id, req.motivo)
        return {"mensagem": "Pedido cancelado"}
    except EntidadeNaoEncontrada as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ErroPermissao as erro:
        raise HTTPException(status_code=403, detail=str(erro)) from erro
    except ErroValidacao as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


@app.post("/pedidos/{pedido_id}/documentos")
def upload_documento(pedido_id: str, arquivo: UploadFile = File(...)):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        caminho = pedido_service.anexar_documento(pedido, arquivo)
        return {"mensagem": "Documento anexado com sucesso", "caminho": caminho}
    except EntidadeNaoEncontrada as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
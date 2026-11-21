from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Importando a nossa lógica que já está pronta!
from repositorio.memoria import RepositorioMemoria
from servicos.amostra_service import AmostraService
from dominio.entidades import Usuario, ItemPedido
from dominio.enums import PapelUsuario, StatusAmostra, StatusCliente, StatusPedido, ProcessoPedido
from dominio.erros import ErroBase, ErroValidacao, ErroPermissao
from servicos.cliente_service import ClienteService
from repositorio.banco_dados import (
    inicializar_banco, buscar_todos_usuarios, buscar_usuario_por_id,
    inicializar_tabela_categorias, buscar_categorias, salvar_categoria
)
from servicos.fornecedor_service import FornecedorService
from servicos.pedido_service import PedidoService
from dominio.enums import StatusPedido, ProcessoPedido


# Inicializa o app e o nosso repositório em memória
app = FastAPI(title="API Estoque de Amostras")
repo = RepositorioMemoria()
service = AmostraService(repo)
cliente_service = ClienteService(repo)
fornecedor_service = FornecedorService(repo)
inicializar_banco()
inicializar_tabela_categorias()
pedido_service = PedidoService(repo)

# Configura o CORS para permitir que o React (que vai rodar em outra porta) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, mude para o domínio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DADOS (O que o React vai enviar) ---
# 1. PRIMEIRO OS MODELOS MENORES (Contato)
class ContatoRequest(BaseModel):
    nome: str
    telefone: str
    email: str

# 2. DEPOIS OS MODELOS QUE USAM OS MENORES (Cliente)
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

# 3. O Modelo de Edição usa os mesmos campos do Novo
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

# --- ROTAS DA API ---

@app.get("/clientes")
def listar_clientes():
    clientes = repo.listar_clientes()
    return [{
        "id": c.id,
        "razao_social": c.razao_social,
        "codigo": c.codigo,
        "cnpj": c.cnpj,
        "status": c.status.value,
        "cidade": c.cidade,
        "rua": c.rua,
        "numero": c.numero,
        "sala": c.sala,
        "bairro": c.bairro,
        "estado": c.estado,
        "pais": c.pais,
        "usuario_responsavel_id": c.usuario_responsavel_id,
        "contatos": [{"nome": ct.nome, "telefone": ct.telefone, "email": ct.email} for ct in c.contatos]
    } for c in clientes]

@app.post("/clientes")
def criar_cliente(req: NovoClienteRequest, x_usuario_id: str = Header(...)):
    try:
        dados = req.model_dump()
        dados["status"] = req.status.value
        
        novo = cliente_service.criar_cliente(dados, usuario_responsavel_id=x_usuario_id)
        return {"mensagem": "Cliente criado", "id": novo.id}
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/clientes/{cliente_id}")
def editar_cliente(cliente_id: str, req: EditarClienteRequest, x_usuario_id: str = Header(...)):
    try:
        cliente = repo.buscar_cliente_por_id(cliente_id)
        
        usuario = buscar_usuario_por_id(x_usuario_id)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
            
        if cliente.usuario_responsavel_id != usuario["id"] and usuario["papel"] != "admin":
            raise HTTPException(status_code=403, detail="Você não tem permissão para editar este cliente.")
        
        # Pega os dados do Pydantic e transforma em dicionário
        dados = req.model_dump()
        dados["status"] = req.status.value
        
        # Chama o serviço para salvar
        cliente_service.editar_cliente(cliente, dados)
        
        return {"mensagem": "Cliente atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/amostras")
def listar_amostras():
    amostras = repo.listar_todas()
    return [{
        "id": a.id,
        "descricao": a.descricao,
        "cliente": a.cliente,
        "status": a.status.value
    } for a in amostras]

@app.post("/amostras")
def criar_amostra(req: NovaAmostraRequest):
    usuario_brasil = Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL, localizacao="brasil")
    try:
        nova = service.criar_amostra(
            usuario=usuario_brasil, descricao=req.descricao, fornecedor=req.fornecedor,
            cliente=req.cliente, responsavel_br_id=usuario_brasil.id, quantidade_pedida=req.quantidade_pedida
        )
        return {"mensagem": "Amostra criada", "id": nova.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/amostras/{amostra_id}/status")
def mudar_status(amostra_id: str, req: MudarStatusRequest):
    usuario_brasil = Usuario(nome="João", email="joao@teste.com", papel=PapelUsuario.BRASIL, localizacao="brasil")
    try:
        service.mudar_status_amostra(
            usuario=usuario_brasil, 
            amostra_id=amostra_id, 
            novo_status=req.novo_status, 
            motivo_adendo=req.motivo_adendo
        )
        return {"mensagem": "Status alterado com sucesso"}
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ErroBase as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/usuarios")
def listar_usuarios():
    usuarios = buscar_todos_usuarios()
    return [{
        "id": u["id"],
        "nome": u["nome"],
        "papel": u["papel"],
        "localizacao": u["localizacao"]
    } for u in usuarios]

@app.get("/fornecedores")
def listar_fornecedores():
    fornecedores = repo.listar_fornecedores()
    return [{
        "id": f.id,
        "nome": f.nome,
        "nome_contato": f.nome_contato,
        "categoria_produtos": f.categoria_produtos,
        "usuario_responsavel_id": f.usuario_responsavel_id,
        "pedidos": f.pedidos
    } for f in fornecedores]

@app.post("/fornecedores")
def criar_fornecedor(req: NovoFornecedorRequest, x_usuario_id: str = Header(...)):
    try:
        dados = req.model_dump()
        novo = fornecedor_service.criar_fornecedor(dados, usuario_responsavel_id=x_usuario_id)
        return {"mensagem": "Fornecedor criado", "id": novo.id}
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/fornecedores/{fornecedor_id}")
def editar_fornecedor(fornecedor_id: str, req: EditarFornecedorRequest, x_usuario_id: str = Header(...)):
    try:
        fornecedor = repo.buscar_fornecedor_por_id(fornecedor_id)
        
        usuario = buscar_usuario_por_id(x_usuario_id)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
            
        if fornecedor.usuario_responsavel_id != usuario["id"] and usuario["papel"] != "admin":
            raise HTTPException(status_code=403, detail="Você não tem permissão para editar este fornecedor.")
        
        dados = req.model_dump()
        fornecedor_service.editar_fornecedor(fornecedor, dados)
        return {"mensagem": "Fornecedor atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/categorias")
def listar_categorias():
    return buscar_categorias()

@app.post("/categorias")
def criar_categoria(nome: str):
    salvar_categoria(nome)
    return {"mensagem": "Categoria salva"}

@app.get("/pedidos")
def listar_pedidos():
    pedidos = repo.listar_pedidos()
    return [{
        "id": p.id,
        "codigo": p.codigo,
        "cliente_id": p.cliente_id,
        "fornecedor_id": p.fornecedor_id,
        "status": p.status.value,
        "processo_atual": p.processo_atual.value,
        "motivo_standby": p.motivo_standby,
        "data_criacao": p.data_criacao.isoformat(),
        "amostras_ids": p.amostras_ids,
        "sigla_produto": p.sigla_produto,
        "sigla_cliente": p.sigla_cliente,
        # --- NOVOS CAMPOS ---
        "criado_por_id": p.criado_por_id,
        "itens": [{
            "id": i.id, "nome_produto": i.nome_produto, "quantidade": i.quantidade, 
            "unidade_medida": i.unidade_medida, "preco_unitario": i.preco_unitario, 
            "valor_total": i.valor_total
        } for i in p.itens],
        "documentos": p.documentos,
        "feedback": p.feedback
    } for p in pedidos]

@app.post("/pedidos")
def criar_pedido(req: NovoPedidoRequest, x_usuario_id: str = Header(...)): # <-- Adicionado Header
    try:
        dados = req.model_dump()
        # Passando o x_usuario_id para o serviço
        novo = pedido_service.criar_pedido(dados, usuario_id=x_usuario_id) 
        return {"mensagem": "Pedido criado", "id": novo.id, "codigo_gerado": novo.codigo}
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/pedidos/{pedido_id}/processo")
def mudar_processo_pedido(pedido_id: str, req: MudarProcessoRequest):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        pedido_service.mudar_processo(pedido, req.novo_processo)
        return {"mensagem": "Processo atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pedidos/{pedido_id}/itens")
def adicionar_item_pedido(pedido_id: str, req: ItemPedidoRequest):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        item = pedido_service.adicionar_item(pedido, req.model_dump())
        return {"mensagem": "Item adicionado", "id": item.id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pedidos/{pedido_id}/cancelar")
def cancelar_pedido(pedido_id: str, req: CancelarPedidoRequest, x_usuario_id: str = Header(...)):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        pedido_service.cancelar_pedido(pedido, x_usuario_id, req.motivo)
        return {"mensagem": "Pedido cancelado"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErroPermissao as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ErroValidacao as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pedidos/{pedido_id}/documentos")
def upload_documento(pedido_id: str, arquivo: UploadFile = File(...)):
    try:
        pedido = repo.buscar_pedido_por_id(pedido_id)
        caminho = pedido_service.anexar_documento(pedido, arquivo)
        return {"mensagem": "Documento anexado com sucesso", "caminho": caminho}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
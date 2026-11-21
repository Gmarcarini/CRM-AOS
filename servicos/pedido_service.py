import os
from datetime import datetime
from fastapi import UploadFile
from repositorio.memoria import RepositorioMemoria
from dominio.entidades import Pedido, ItemPedido
from dominio.enums import StatusPedido, ProcessoPedido
from dominio.erros import ErroValidacao, ErroPermissao

class PedidoService:
    def __init__(self, repositorio: RepositorioMemoria):
        self.repo = repositorio

    def gerar_codigo(self, sigla_cliente: str, sigla_produto: str) -> tuple:
        agora = datetime.now()
        ano_mes = agora.strftime("%y%m")
        
        pedidos_existentes = self.repo.listar_pedidos()
        sequencial = 1
        for p in pedidos_existentes:
            if p.ano_mes == ano_mes and p.sigla_cliente == sigla_cliente and p.sigla_produto == sigla_produto:
                if p.numero_sequencial >= sequencial:
                    sequencial = p.numero_sequencial + 1

        codigo = f"TM{ano_mes}{sigla_cliente}-{sigla_produto}{sequencial:02d}"
        return codigo, ano_mes, sequencial

    # Atualizado para receber o usuario_id que criou
    def criar_pedido(self, dados: dict, usuario_id: str) -> Pedido:
        if not dados.get("cliente_id") or not dados.get("fornecedor_id"):
            raise ErroValidacao("Cliente e Fornecedor são obrigatórios.")
        if not dados.get("sigla_cliente") or not dados.get("sigla_produto"):
            raise ErroValidacao("As siglas do cliente e do produto são obrigatórias.")

        codigo, ano_mes, sequencial = self.gerar_codigo(dados["sigla_cliente"], dados["sigla_produto"])

        novo_pedido = Pedido(
            cliente_id=dados["cliente_id"],
            fornecedor_id=dados["fornecedor_id"],
            codigo=codigo,
            sigla_cliente=dados["sigla_cliente"].upper(),
            sigla_produto=dados["sigla_produto"].upper(),
            numero_sequencial=sequencial,
            ano_mes=ano_mes,
            criado_por_id=usuario_id, # <-- NOVO
            status=StatusPedido.ATIVO,
            processo_atual=ProcessoPedido.AGUARDANDO_PAGAMENTO_1
        )
        
        self.repo.salvar_pedido(novo_pedido)
        return novo_pedido

    def mudar_processo(self, pedido: Pedido, novo_processo: ProcessoPedido):
        if pedido.status == StatusPedido.STANDBY:
            raise ErroValidacao("Não é possível avançar o processo enquanto o pedido estiver em Standby.")
            
        pedido.processo_atual = novo_processo
        pedido.data_modificacao = datetime.now()
        self.repo.salvar_pedido(pedido)

    # --- NOVOS MÉTODOS ---

    def adicionar_item(self, pedido: Pedido, item_dados: dict) -> ItemPedido:
        novo_item = ItemPedido(
            nome_produto=item_dados["nome_produto"],
            quantidade=float(item_dados["quantidade"]),
            unidade_medida=item_dados["unidade_medida"],
            preco_unitario=float(item_dados["preco_unitario"])
        )
        pedido.itens.append(novo_item)
        pedido.data_modificacao = datetime.now()
        self.repo.salvar_pedido(pedido)
        return novo_item

    def cancelar_pedido(self, pedido: Pedido, usuario_id: str, motivo: str):
        if pedido.criado_por_id != usuario_id:
            raise ErroPermissao("Apenas o criador do pedido pode cancelá-lo.")
        if not motivo.strip():
            raise ErroValidacao("O motivo do cancelamento é obrigatório.")
        
        pedido.status = StatusPedido.INATIVO 
        pedido.motivo_cancelamento = motivo
        pedido.data_modificacao = datetime.now()
        self.repo.salvar_pedido(pedido)

    def anexar_documento(self, pedido: Pedido, arquivo: UploadFile):
        os.makedirs("uploads", exist_ok=True)
        caminho_arquivo = f"uploads/{pedido.id}_{arquivo.filename}"
        
        with open(caminho_arquivo, "wb") as buffer:
            buffer.write(arquivo.file.read())
            
        pedido.documentos.append({
            "nome": arquivo.filename,
            "caminho": caminho_arquivo,
            "data_upload": datetime.now().isoformat()
        })
        self.repo.salvar_pedido(pedido)
        return caminho_arquivo
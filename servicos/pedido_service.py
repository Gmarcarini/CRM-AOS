"""Regras do pedido de importação.

O pedido é um agregado: itens e documentos vivem dentro dele e são gravados
junto. Por isso o serviço sempre manipula o agregado inteiro e chama
`salvar_pedido` uma vez — padrão que a Sprint 1 vai replicar no Supabase (RPC ou
coluna jsonb), sem transação de cliente.
"""

import os
from datetime import datetime

from fastapi import UploadFile

from dominio.entidades import ItemPedido, Pedido
from dominio.enums import ProcessoPedido, StatusPedido
from dominio.erros import ErroPermissao, ErroValidacao
from repositorio.contrato import PedidoRepositorio


class PedidoService:
    def __init__(self, repositorio: PedidoRepositorio) -> None:
        self.repo = repositorio

    def gerar_codigo(self, sigla_cliente: str, sigla_produto: str) -> tuple[str, str, int]:
        """Código legível do pedido: TM + AAMM + sigla cliente + sigla produto + sequencial.

        Ex.: TM2611CB-TC01. O sequencial é por combinação (mês, cliente,
        produto), não global — dois clientes no mesmo mês têm numeração
        independente.
        """
        ano_mes = datetime.now().strftime("%y%m")
        sequencial = 1

        for pedido in self.repo.listar_pedidos():
            mesma_serie = (
                pedido.ano_mes == ano_mes
                and pedido.sigla_cliente == sigla_cliente
                and pedido.sigla_produto == sigla_produto
            )
            if mesma_serie and pedido.numero_sequencial >= sequencial:
                sequencial = pedido.numero_sequencial + 1

        codigo = f"TM{ano_mes}{sigla_cliente}-{sigla_produto}{sequencial:02d}"
        return codigo, ano_mes, sequencial

    def criar_pedido(self, dados: dict, usuario_id: str) -> Pedido:
        if not dados.get("cliente_id") or not dados.get("fornecedor_id"):
            raise ErroValidacao("Cliente e Fornecedor são obrigatórios.")

        if not dados.get("sigla_cliente") or not dados.get("sigla_produto"):
            raise ErroValidacao("As siglas do cliente e do produto são obrigatórias.")

        sigla_cliente = dados["sigla_cliente"].upper()
        sigla_produto = dados["sigla_produto"].upper()
        codigo, ano_mes, sequencial = self.gerar_codigo(sigla_cliente, sigla_produto)

        novo_pedido = Pedido(
            cliente_id=dados["cliente_id"],
            fornecedor_id=dados["fornecedor_id"],
            codigo=codigo,
            sigla_cliente=sigla_cliente,
            sigla_produto=sigla_produto,
            numero_sequencial=sequencial,
            ano_mes=ano_mes,
            criado_por_id=usuario_id,
            status=StatusPedido.ATIVO,
            processo_atual=ProcessoPedido.AGUARDANDO_PAGAMENTO_1,
        )
        self.repo.salvar_pedido(novo_pedido)
        return novo_pedido

    def mudar_processo(self, pedido: Pedido, novo_processo: ProcessoPedido) -> None:
        if pedido.status == StatusPedido.STANDBY:
            raise ErroValidacao("Não é possível avançar o processo enquanto o pedido estiver em Standby.")

        pedido.processo_atual = novo_processo
        pedido.data_modificacao = datetime.now()
        self.repo.salvar_pedido(pedido)

    def adicionar_item(self, pedido: Pedido, item_dados: dict) -> ItemPedido:
        novo_item = ItemPedido(
            nome_produto=item_dados["nome_produto"],
            quantidade=float(item_dados["quantidade"]),
            unidade_medida=item_dados["unidade_medida"],
            preco_unitario=float(item_dados["preco_unitario"]),
        )

        # O agregado é a unidade de persistência: grava o pedido com o item novo.
        pedido.itens.append(novo_item)
        pedido.data_modificacao = datetime.now()
        self.repo.salvar_pedido(pedido)
        return novo_item

    def cancelar_pedido(self, pedido: Pedido, usuario_id: str, motivo: str) -> None:
        if pedido.criado_por_id != usuario_id:
            raise ErroPermissao("Apenas o criador do pedido pode cancelá-lo.")

        if not motivo.strip():
            raise ErroValidacao("O motivo do cancelamento é obrigatório.")

        pedido.status = StatusPedido.INATIVO
        pedido.motivo_cancelamento = motivo
        pedido.data_modificacao = datetime.now()
        self.repo.salvar_pedido(pedido)

    def anexar_documento(self, pedido: Pedido, arquivo: UploadFile) -> str:
        """Grava o arquivo localmente e registra o metadado no agregado.

        Storage remoto é fora do escopo desta sprint. O caminho fica salvo no
        próprio pedido, então trocar o destino do binário depois não exige
        mudança na entidade.
        """
        os.makedirs("uploads", exist_ok=True)

        caminho_arquivo = f"uploads/{pedido.id}_{arquivo.filename}"
        with open(caminho_arquivo, "wb") as buffer:
            buffer.write(arquivo.file.read())

        pedido.documentos.append(
            {
                "nome": arquivo.filename,
                "caminho": caminho_arquivo,
                "data_upload": datetime.now().isoformat(),
            }
        )
        self.repo.salvar_pedido(pedido)
        return caminho_arquivo
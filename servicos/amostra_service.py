from datetime import datetime
from repositorio.memoria import RepositorioMemoria
from dominio.entidades import Amostra, Usuario, Adendo
from dominio.enums import StatusAmostra, PapelUsuario
from dominio.maquina_estado import validar_permissao_mudanca, aplicar_mudanca_status
from dominio.erros import ErroPermissao, ErroValidacao


class AmostraService:
    def __init__(self, repositorio: RepositorioMemoria):
        self.repo = repositorio

    def _gerar_id(self) -> str:
        """Gera IDs sequenciais: AM-2025-0001, AM-2025-0002, etc."""
        ano = datetime.now().year
        total = len(self.repo.listar_todas())
        return f"AM-{ano}-{(total + 1):04d}"

    def criar_amostra(self, usuario: Usuario, descricao: str, fornecedor: str, cliente: str, responsavel_br_id: str, quantidade_pedida: int) -> Amostra:
        # Regra: Apenas o Brasil ou Admin podem cadastrar novas amostras
        if usuario.papel not in [PapelUsuario.BRASIL, PapelUsuario.ADMIN]:
            raise ErroPermissao("Apenas o escritório do Brasil pode cadastrar novas amostras.")

        # O dev sênior pediu validação de entrada
        if quantidade_pedida <= 0:
            raise ValueError("A quantidade pedida deve ser maior que zero.")
        if not descricao.strip() or not fornecedor.strip():
            raise ValueError("Descrição e fornecedor são obrigatórios.")

        nova_amostra = Amostra(
            id=self._gerar_id(), # Forçando o ID sequencial
            descricao=descricao,
            fornecedor=fornecedor,
            cliente=cliente,
            responsavel_br_id=responsavel_br_id,
            quantidade_pedida=quantidade_pedida,
            status=StatusAmostra.SOLICITADA
        )

        self.repo.salvar(nova_amostra)
        return nova_amostra

    def mudar_status_amostra(self, usuario: Usuario, amostra_id: str, novo_status: StatusAmostra, motivo_adendo: str = None) -> None:
        amostra = self.repo.buscar_por_id(amostra_id)
        
        # 1. Valida permissão básica
        validar_permissao_mudanca(amostra, usuario)
        
        # 2. Lógica do "Pular para trás"
        ordem_status = list(StatusAmostra)
        index_atual = ordem_status.index(amostra.status)
        index_novo = ordem_status.index(novo_status)
        
        if index_novo < index_atual: # Está voltando!
            if not motivo_adendo or not motivo_adendo.strip():
                raise ErroValidacao("Para retornar o status, é obrigatório informar o motivo do adendo.")
            
            adendo = Adendo(
                amostra_id=amostra.id,
                status_anterior=amostra.status,
                status_novo=novo_status,
                motivo=motivo_adendo.strip()
            )
            self.repo.salvar_adendo(adendo)

        # 3. Aplica a mudança
        aplicar_mudanca_status(amostra, novo_status)
        self.repo.salvar(amostra)
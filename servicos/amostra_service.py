"""Regras de cadastro e movimentação de amostra.

Depende apenas de `AmostraRepositorio`: o serviço não sabe (e não deve saber)
que existe cliente, pedido ou usuário no repositório.
"""

from datetime import datetime

from dominio.entidades import Adendo, Amostra, Usuario
from dominio.enums import PapelUsuario, StatusAmostra
from dominio.erros import ErroPermissao, ErroValidacao
from dominio.maquina_estado import aplicar_mudanca_status, validar_permissao_mudanca
from repositorio.contrato import AmostraRepositorio


class AmostraService:
    def __init__(self, repositorio: AmostraRepositorio) -> None:
        self.repo = repositorio

    def _gerar_id(self) -> str:
        """Código sequencial legível: AM-2026-0001.

        TODO(Bloco C2): este cálculo usa contagem, o que quebra se uma amostra
        for removida e não é reproduzível com segurança no Supabase. A correção
        (id técnico uuid4 + campo `codigo` derivado do maior código do ano)
        pertence ao Bloco C.
        """
        ano = datetime.now().year
        total = len(self.repo.listar_amostras())
        return f"AM-{ano}-{(total + 1):04d}"

    def criar_amostra(
        self,
        usuario: Usuario,
        descricao: str,
        fornecedor: str,
        cliente: str,
        responsavel_br_id: str,
        quantidade_pedida: int,
    ) -> Amostra:
        """Cadastra amostra no status inicial SOLICITADA.

        Regra de negócio: apenas Brasil ou Admin cadastram — o pedido de amostra
        nasce na negociação, que é atribuição do escritório do Brasil.
        """
        if usuario.papel not in [PapelUsuario.BRASIL, PapelUsuario.ADMIN]:
            raise ErroPermissao("Apenas o escritório do Brasil pode cadastrar novas amostras.")

        if quantidade_pedida <= 0:
            raise ErroValidacao("A quantidade pedida deve ser maior que zero.")
        
        if not descricao.strip() or not fornecedor.strip():
            raise ErroValidacao("Descrição e fornecedor são obrigatórios.")

        nova_amostra = Amostra(
            id=self._gerar_id(),
            descricao=descricao,
            fornecedor=fornecedor,
            cliente_id=cliente,  # entidade usa cliente_id; parâmetro mantém o nome histórico
            responsavel_br_id=responsavel_br_id,
            quantidade_pedida=quantidade_pedida,
            status=StatusAmostra.SOLICITADA,
        )
        self.repo.salvar_amostra(nova_amostra)
        return nova_amostra

    def mudar_status_amostra(
        self,
        usuario: Usuario,
        amostra_id: str,
        novo_status: StatusAmostra,
        motivo_adendo: str | None = None,
    ) -> None:
        """Muda o status, exigindo adendo quando a amostra retrocede.

        O repositório devolve cópia, então a amostra mutada aqui só existe no
        estado armazenado depois do `salvar_amostra` no fim do método. Se alguém
        remover essa linha, a mudança some — e é isso que o teste de contrato
        protege.
        """
        amostra = self.repo.buscar_amostra_por_id(amostra_id)

        validar_permissao_mudanca(amostra, usuario)

        ordem_status = list(StatusAmostra)
        index_atual = ordem_status.index(amostra.status)
        index_novo = ordem_status.index(novo_status)

        if index_novo < index_atual:  # está retrocedendo
            if not motivo_adendo or not motivo_adendo.strip():
                raise ErroValidacao("Para retornar o status, é obrigatório informar o motivo do adendo.")

            self.repo.salvar_adendo(
                Adendo(
                    amostra_id=amostra.id,
                    status_anterior=amostra.status,
                    status_novo=novo_status,
                    motivo=motivo_adendo.strip(),
                )
            )

        aplicar_mudanca_status(amostra, novo_status)
        self.repo.salvar_amostra(amostra)
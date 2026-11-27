"""Alertas operacionais: sinalizam amostra parada há tempo demais no status.

Serviço de leitura. Não escreve nada, por isso depende só da leitura do
contrato de amostra — e recebe o "agora" por parâmetro para o teste não
depender do relógio da máquina.
"""

from datetime import datetime

from dominio.enums import StatusAmostra
from repositorio.contrato import AmostraRepositorio


class AlertaService:
    def __init__(self, repositorio: AmostraRepositorio) -> None:
        self.repo = repositorio

    def _dias_no_status(self, desde: datetime, agora: datetime) -> int:
        """Diferença em dias inteiros; `.days` já trunca para baixo."""
        return (agora - desde).days

    def gerar_alertas(
        self,
        limite_estoque: int,
        limite_transito: int,
        limite_analise: int,
        agora: datetime | None = None,
    ) -> list[dict]:
        """Devolve um alerta por amostra que estourou o limite do seu status.

        `agora` é injetável para permitir teste determinístico no Bloco E. O
        padrão mantém o comportamento atual para quem já chama sem o parâmetro.
        """
        referencia = agora or datetime.now()
        alertas: list[dict] = []

        for amostra in self.repo.listar_amostras():
            dias = self._dias_no_status(amostra.status_desde, referencia)

            if amostra.status == StatusAmostra.EM_ESTOQUE and dias >= limite_estoque:
                alertas.append(
                    {
                        "amostra_id": amostra.id,
                        "tipo": "parada_estoque",
                        "mensagem": f"Amostra parada no estoque há {dias} dias.",
                        "dias": dias,
                    }
                )
            elif amostra.status == StatusAmostra.EM_TRANSITO and dias >= limite_transito:
                alertas.append(
                    {
                        "amostra_id": amostra.id,
                        "tipo": "transito_atrasado",
                        "mensagem": f"Amostra em trânsito há {dias} dias (possível extravio).",
                        "dias": dias,
                    }
                )
            elif amostra.status == StatusAmostra.SOB_ANALISE and dias >= limite_analise:
                alertas.append(
                    {
                        "amostra_id": amostra.id,
                        "tipo": "analise_pendente",
                        "mensagem": f"Amostra aguardando conferência há {dias} dias.",
                        "dias": dias,
                    }
                )

        return alertas
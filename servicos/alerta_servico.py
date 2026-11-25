from datetime import datetime
from typing import List

from dominio.enums import StatusAmostra
from repositorio.memoria import RepositorioMemoria

class AlertaService:
    def __init__(self, repositorio: RepositorioMemoria):
        self.repo = repositorio

    def _calcular_dias(self, data_inicio: datetime, agora: datetime) -> int:
        """Calcula a diferença em dias de forma correta (sênior - Item 6)."""
        diferenca = agora - data_inicio
        return diferenca.days # O '.days' do Python já arredonda pra baixo (floor)

    def gerar_alertas(self, limite_estoque: int, limite_transito: int, limite_analise: int) -> List[dict]:
        amostras = self.repo.listar_todas()
        agora = datetime.now()
        alertas = []

        for amostra in amostras:
            # Calcula quantos dias a amostra está no status atual
            dias_no_status = self._calcular_dias(amostra.status_desde, agora)
            
            # 1. Parada no estoque
            if amostra.status == StatusAmostra.EM_ESTOQUE and dias_no_status >= limite_estoque:
                alertas.append({
                    "amostra_id": amostra.id,
                    "tipo": "parada_estoque",
                    "mensagem": f"Amostra parada no estoque há {dias_no_status} dias.",
                    "dias": dias_no_status
                })
            
            # 2. Trânsito atrasado
            elif amostra.status == StatusAmostra.EM_TRANSITO and dias_no_status >= limite_transito:
                alertas.append({
                    "amostra_id": amostra.id,
                    "tipo": "transito_atrasado",
                    "mensagem": f"Amostra em trânsito há {dias_no_status} dias (possível extravio).",
                    "dias": dias_no_status
                })
            
            # 3. Análise pendente (chegou no escritório mas não foi etiquetada)
            elif amostra.status == StatusAmostra.SOB_ANALISE and dias_no_status >= limite_analise:
                alertas.append({
                    "amostra_id": amostra.id,
                    "tipo": "analise_pendente",
                    "mensagem": f"Amostra aguardando conferência há {dias_no_status} dias.",
                    "dias": dias_no_status
                })

        return alertas
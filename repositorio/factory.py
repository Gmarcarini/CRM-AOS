"""Ponto único de escolha do backend de persistência.

Regra estrutural do projeto: NENHUM módulo fora daqui instancia repositório.
`api.py` chama a fábrica uma vez, no nível do módulo. Isso é o que permite
trocar memória por Supabase (Sprint 1) mexendo em um arquivo só.

Sem `lru_cache`, de propósito. A API chama uma vez, então cache não traz ganho;
e os testes chamam a fábrica diretamente, precisando de instância limpa a cada
caso. Cache transformaria isolamento de teste em vazamento de estado — o pior
tipo de bug, porque aparece em teste não relacionado.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from repositorio.contrato import RepositorioCompleto
from repositorio.memoria import RepositorioMemoria

BACKENDS_ACEITOS: tuple[str, ...] = ("mock", "supabase")


class Configuracoes(BaseSettings):
    """Configuração lida do ambiente.

    `REPOSITORIO` é o nome da variável; o atributo `repositorio` é lido sem
    diferenciar caixa. O `.env` é conveniência local — em produção valem as
    variáveis do processo, que têm precedência sobre o arquivo.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    repositorio: str = "mock"


def criar_repositorio() -> RepositorioCompleto:
    """Resolve e devolve o backend de persistência configurado.

    Falha alto e cedo em configuração inválida. Cair em silêncio no mock
    esconderia erro de digitação na variável de ambiente e faria a aplicação
    subir "vazia" em produção — pior que não subir.
    """
    backend = Configuracoes().repositorio.strip().lower()

    if backend == "mock":
        return RepositorioMemoria()

    if backend == "supabase":
        raise NotImplementedError("Backend Supabase previsto para a Sprint 1")

    aceitos = ", ".join(BACKENDS_ACEITOS)
    raise ValueError(f"REPOSITORIO inválido: {backend!r}. Valores aceitos: {aceitos}.")
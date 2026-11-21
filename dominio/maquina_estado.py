from dominio.enums import StatusAmostra, PapelUsuario
from dominio.entidades import Amostra, Usuario
from dominio.erros import ErroPermissao
from datetime import datetime

def validar_permissao_mudanca(amostra: Amostra, usuario: Usuario) -> None:
    """Verifica se o usuário tem permissão básica de mexer na amostra."""
    if not usuario.ativo:
        raise ErroPermissao("Usuário inativo não pode realizar operações.")
        
    # Regras básicas: Brasil e Admin podem tudo. Escritório não pode cancelar/descartar.
    if usuario.papel == PapelUsuario.ESCRITORIO:
        if amostra.status in [StatusAmostra.ENCERRADA, StatusAmostra.CANCELADA, StatusAmostra.DESCARTADA]:
            raise ErroPermissao("Amostras finalizadas só podem ser alteradas pelo Brasil.")

def aplicar_mudanca_status(amostra: Amostra, novo_status: StatusAmostra) -> None:
    """Aplica a mudança e atualiza as datas automáticas."""
    agora = datetime.now()
    amostra.status = novo_status
    amostra.status_desde = agora
    amostra.versao += 1
    
    if novo_status == StatusAmostra.SOB_ANALISE:
        amostra.data_chegada_analise = agora
    elif novo_status == StatusAmostra.EM_ESTOQUE:
        amostra.data_entrada_estoque = agora
class ErroBase(Exception):
    """Classe base para todos os erros do nosso sistema."""
    pass

class ErroValidacao(ErroBase):
    """Quando o usuário digita algo errado (ex: quantidade negativa)."""
    pass

class ErroPermissao(ErroBase):
    """Quando o usuário tenta fazer algo que não tem direito."""
    pass

class ErroTransicaoInvalida(ErroBase):
    """Quando tentamos pular uma etapa (ex: de Solicitada direto pro Estoque)."""
    pass
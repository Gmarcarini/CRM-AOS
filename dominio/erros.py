"""Erros de domínio do CRM AOS.

Contrato desta hierarquia: é o vocabulário fechado de falhas que a camada de
aplicação pode traduzir para HTTP. Nada de `ValueError` atravessando fronteira —
`ValueError` pode significar validação, parsing ou ausência de dado, e o
receptor não tem como distinguir.
"""


class ErroBase(Exception):
    """Raiz da hierarquia. Qualquer `except ErroBase` cobre o sistema inteiro."""


class ErroValidacao(ErroBase):
    """Entrada inválida: quantidade negativa, CNPJ malformado, campo obrigatório."""


class ErroPermissao(ErroBase):
    """Usuário autenticado tentando operação que o papel dele não permite."""


class ErroTransicaoInvalida(ErroBase):
    """Salto proibido na máquina de estados (ex.: Solicitada -> Em Estoque)."""


class EntidadeNaoEncontrada(ErroBase):
    """Ausência de registro — o único erro que um repositório pode lançar.

    Existe para separar "não existe" de "está inválido". Com ele, o mapeamento
    para HTTP 404 acontece em um ponto só (Bloco C), em vez de cada rota decidir
    se `ValueError` significa 400 ou 404.
    """
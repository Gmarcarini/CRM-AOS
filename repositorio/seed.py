"""Semeadura inicial do backend de persistência.

Duas escolhas estruturais:

1. IDs FIXOS (`u1`..`u5`), não UUID. O frontend guarda o usuário escolhido no
   `localStorage` e o devolve no header `x-usuario-id` a cada requisição. Id
   estável mantém esse contrato previsível entre reinícios e deixa os testes
   determinísticos.

2. IDEMPOTÊNCIA por id. `semear` pode rodar em todo start da API sem duplicar
   ninguém: só insere o que ainda não existe. Nada de "apagar e recriar", que
   destruiria dados reais assim que o backend deixar de ser memória.
"""

from dominio.entidades import Usuario
from dominio.enums import PapelUsuario
from dominio.erros import EntidadeNaoEncontrada
from repositorio.contrato import RepositorioCompleto

# TODO_CONFIRMAR: papéis reais dos sócios.
# Os três estão como ADMIN porque precisam enxergar e editar qualquer registro.
# O banco antigo usava "gerente" e "ceo", valores que NÃO existem em
# PapelUsuario — foram descartados em vez de inventar papéis novos no enum.
#
# TODO_CONFIRMAR: nomes e e-mails dos dois perfis da China.
# "TODO_CONFIRMAR" é literal e greppável de propósito: placeholder visível é
# melhor que dado inventado passando por real.
# ESCRITORIO é o único papel não administrativo disponível no enum; um papel
# próprio para a China é mudança de enum e não pertence a este bloco.
USUARIOS_INICIAIS: list[Usuario] = [
    Usuario(
        id="u1",
        nome="Giovanni",
        email="giovanni@aosltd.net",
        papel=PapelUsuario.ADMIN,
        localizacao="brasil",
    ),
    Usuario(
        id="u2",
        nome="Augusto",
        email="augusto@aosltd.net",
        papel=PapelUsuario.ADMIN,
        localizacao="brasil",
    ),
    Usuario(
        id="u3",
        nome="Gustavo",
        email="gustavo@aosltd.net",
        papel=PapelUsuario.ADMIN,
        localizacao="brasil",
    ),
    Usuario(
        id="u4",
        nome="TODO_CONFIRMAR",
        email="TODO_CONFIRMAR",
        papel=PapelUsuario.ESCRITORIO,
        localizacao="china",
    ),
    Usuario(
        id="u5",
        nome="TODO_CONFIRMAR",
        email="TODO_CONFIRMAR",
        papel=PapelUsuario.ESCRITORIO,
        localizacao="china",
    ),
]

# TODO_CONFIRMAR: lista real de categorias de fornecedor.
# Lista vazia é honesta. Categoria inventada contamina o autocomplete de
# Fornecedores, que é alimentado justamente por esta lista.
CATEGORIAS_INICIAIS: list[str] = []


def _usuario_inexistente(repo: RepositorioCompleto, id_usuario: str) -> bool:
    """Traduz `EntidadeNaoEncontrada` em booleano, para o fluxo do seed ficar
    legível (existência é pergunta, não erro)."""
    try:
        repo.buscar_usuario_por_id(id_usuario)
    except EntidadeNaoEncontrada:
        return True
    return False


def semear(repo: RepositorioCompleto) -> None:
    """Garante usuários e categorias iniciais sem duplicar nada.

    Atenção: as instâncias de `Usuario` vêm de uma constante de módulo. Como o
    repositório guarda cópias defensivas, o objeto do módulo nunca é mutado pelo
    estado armazenado — o risco de vazamento entre execuções está coberto.
    """
    for usuario in USUARIOS_INICIAIS:
        if _usuario_inexistente(repo, usuario.id):
            repo.salvar_usuario(usuario)

    for categoria in CATEGORIAS_INICIAIS:
        repo.salvar_categoria(categoria)
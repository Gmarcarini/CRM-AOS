"""Implementação de referência em memória do contrato de persistência.

Esta classe é o padrão-ouro de comportamento: qualquer backend futuro
(Supabase) precisa se comportar exatamente assim para passar na suíte de
contrato do Bloco E.

Duas garantias sustentam isso:

1. ISOLAMENTO DE OBJETO. `salvar` guarda cópia; `buscar`/`listar` devolvem
   cópia. Sem isso, o serviço muta o objeto devolvido e o estado muda sem
   `salvar` — bug que nunca aparece em memória e aparece imediatamente em banco
   real, mascarando o defeito até a produção.

2. EXCLUSIVIDADE. Um `threading.RLock` por instância protege todo o estado.
   `uvicorn` atende requisições concorrentes e dicionário Python não é seguro
   para escrita simultânea. Lock de módulo seria errado: duas instâncias
   independentes se bloqueariam sem necessidade e os testes perderiam
   isolamento entre casos.

Armadilha tratada explicitamente: `dataclasses.replace` é cópia RASA. Os campos
de lista continuam apontando para a mesma lista. Por isso cada agregado com
coleção tem um helper `_copiar_*` que reconstrói a coleção e os objetos dentro
dela. Copiar só o invólucro seria fachada de cópia.
"""

import threading
from dataclasses import replace

from dominio.entidades import Adendo, Amostra, Cliente, Fornecedor, Pedido, Usuario
from dominio.erros import EntidadeNaoEncontrada


# --- Helpers de cópia defensiva --------------------------------------------
# Um por agregado: o nome do helper documenta onde a cópia é profunda.


def _copiar_usuario(usuario: Usuario) -> Usuario:
    """Sem coleções: `replace` puro já garante independência."""
    return replace(usuario)


def _copiar_adendo(adendo: Adendo) -> Adendo:
    """Sem coleções: `replace` puro já garante independência."""
    return replace(adendo)


def _copiar_amostra(amostra: Amostra) -> Amostra:
    """Hoje sem coleções; o helper existe para não reabrir a discussão quando
    `Amostra` ganhar lista (histórico de trânsito, anexos)."""
    return replace(amostra)


def _copiar_cliente(cliente: Cliente) -> Cliente:
    """Agregado com coleção: cada contato é reconstruído individualmente."""
    return replace(
        cliente,
        contatos=[replace(contato) for contato in cliente.contatos],
    )


def _copiar_fornecedor(fornecedor: Fornecedor) -> Fornecedor:
    """Agregado com coleção de ids: a lista é reconstruída, não compartilhada."""
    return replace(fornecedor, pedidos=list(fornecedor.pedidos))


def _copiar_pedido(pedido: Pedido) -> Pedido:
    """Agregado mais profundo: itens (objetos), amostras (ids) e documentos.

    Documentos são `dict` dentro de lista — `dict(documento)` é obrigatório.
    Sem isso, mutar `pedido.documentos[0]["nome"]` no objeto devolvido alteraria
    o estado armazenado.
    """
    return replace(
        pedido,
        itens=[replace(item) for item in pedido.itens],
        amostras_ids=list(pedido.amostras_ids),
        documentos=[dict(documento) for documento in pedido.documentos],
    )


class RepositorioMemoria:
    """Backend em RAM.

    Não herda dos `Protocol` de propósito: a conformidade é estrutural e é
    cobrada por comportamento (Bloco E), não por declaração de ancestralidade.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._usuarios: dict[str, Usuario] = {}
        self._categorias: set[str] = set()
        self._clientes: dict[str, Cliente] = {}
        self._fornecedores: dict[str, Fornecedor] = {}
        self._pedidos: dict[str, Pedido] = {}
        self._amostras: dict[str, Amostra] = {}
        self._adendos: list[Adendo] = []

    # --- Agregado usuário ---------------------------------------------------

    def salvar_usuario(self, usuario: Usuario) -> None:
        with self._lock:
            self._usuarios[usuario.id] = _copiar_usuario(usuario)

    def buscar_usuario_por_id(self, id_usuario: str) -> Usuario:
        with self._lock:
            usuario = self._usuarios.get(id_usuario)
            if usuario is None:
                raise EntidadeNaoEncontrada("Usuário não encontrado.")
            return _copiar_usuario(usuario)

    def listar_usuarios(self) -> list[Usuario]:
        with self._lock:
            return [_copiar_usuario(usuario) for usuario in self._usuarios.values()]

    def excluir_usuario(self, id_usuario: str) -> None:
        with self._lock:
            if self._usuarios.pop(id_usuario, None) is None:
                raise EntidadeNaoEncontrada("Usuário não encontrado.")

    # --- Categorias ---------------------------------------------------------

    def salvar_categoria(self, nome: str) -> None:
        """Normaliza e ignora vazio em silêncio — comportamento herdado da
        versão SQLite (`salvar_categoria` retornava cedo em branco) e esperado
        pelo frontend, que envia o campo conforme o usuário digita."""
        categoria = nome.strip()
        if not categoria:
            return
        with self._lock:
            self._categorias.add(categoria)

    def listar_categorias(self) -> list[str]:
        """Ordem alfabética: o autocomplete de Fornecedores depende dela."""
        with self._lock:
            return sorted(self._categorias)

    def excluir_categoria(self, nome: str) -> None:
        categoria = nome.strip()
        with self._lock:
            if categoria not in self._categorias:
                raise EntidadeNaoEncontrada("Categoria não encontrada.")
            self._categorias.discard(categoria)

    # --- Agregado cliente ---------------------------------------------------

    def salvar_cliente(self, cliente: Cliente) -> None:
        with self._lock:
            self._clientes[cliente.id] = _copiar_cliente(cliente)

    def buscar_cliente_por_id(self, id_cliente: str) -> Cliente:
        with self._lock:
            cliente = self._clientes.get(id_cliente)
            if cliente is None:
                raise EntidadeNaoEncontrada("Cliente não encontrado.")
            return _copiar_cliente(cliente)

    def listar_clientes(self) -> list[Cliente]:
        with self._lock:
            return [_copiar_cliente(cliente) for cliente in self._clientes.values()]

    def excluir_cliente(self, id_cliente: str) -> None:
        with self._lock:
            if self._clientes.pop(id_cliente, None) is None:
                raise EntidadeNaoEncontrada("Cliente não encontrado.")

    # --- Agregado fornecedor ------------------------------------------------

    def salvar_fornecedor(self, fornecedor: Fornecedor) -> None:
        with self._lock:
            self._fornecedores[fornecedor.id] = _copiar_fornecedor(fornecedor)

    def buscar_fornecedor_por_id(self, id_fornecedor: str) -> Fornecedor:
        with self._lock:
            fornecedor = self._fornecedores.get(id_fornecedor)
            if fornecedor is None:
                raise EntidadeNaoEncontrada("Fornecedor não encontrado.")
            return _copiar_fornecedor(fornecedor)

    def listar_fornecedores(self) -> list[Fornecedor]:
        with self._lock:
            return [
                _copiar_fornecedor(fornecedor)
                for fornecedor in self._fornecedores.values()
            ]

    def excluir_fornecedor(self, id_fornecedor: str) -> None:
        with self._lock:
            if self._fornecedores.pop(id_fornecedor, None) is None:
                raise EntidadeNaoEncontrada("Fornecedor não encontrado.")

    # --- Agregado pedido ----------------------------------------------------

    def salvar_pedido(self, pedido: Pedido) -> None:
        """Grava o agregado inteiro. Salvar duas vezes o mesmo id atualiza no
        lugar, porque o id é a chave do dicionário — sem duplicação."""
        with self._lock:
            self._pedidos[pedido.id] = _copiar_pedido(pedido)

    def buscar_pedido_por_id(self, id_pedido: str) -> Pedido:
        with self._lock:
            pedido = self._pedidos.get(id_pedido)
            if pedido is None:
                raise EntidadeNaoEncontrada("Pedido não encontrado.")
            return _copiar_pedido(pedido)

    def listar_pedidos(self) -> list[Pedido]:
        with self._lock:
            return [_copiar_pedido(pedido) for pedido in self._pedidos.values()]

    def excluir_pedido(self, id_pedido: str) -> None:
        with self._lock:
            if self._pedidos.pop(id_pedido, None) is None:
                raise EntidadeNaoEncontrada("Pedido não encontrado.")

    # --- Agregado amostra ---------------------------------------------------

    def salvar_amostra(self, amostra: Amostra) -> None:
        with self._lock:
            self._amostras[amostra.id] = _copiar_amostra(amostra)

    def buscar_amostra_por_id(self, id_amostra: str) -> Amostra:
        with self._lock:
            amostra = self._amostras.get(id_amostra)
            if amostra is None:
                raise EntidadeNaoEncontrada("Amostra não encontrada.")
            return _copiar_amostra(amostra)

    def listar_amostras(self) -> list[Amostra]:
        with self._lock:
            return [_copiar_amostra(amostra) for amostra in self._amostras.values()]

    def excluir_amostra(self, id_amostra: str) -> None:
        with self._lock:
            if self._amostras.pop(id_amostra, None) is None:
                raise EntidadeNaoEncontrada("Amostra não encontrada.")

    # --- Adendos (parte do agregado amostra) --------------------------------

    def salvar_adendo(self, adendo: Adendo) -> None:
        with self._lock:
            self._adendos.append(_copiar_adendo(adendo))

    def listar_adendos_por_amostra(self, amostra_id: str) -> list[Adendo]:
        with self._lock:
            return [
                _copiar_adendo(adendo)
                for adendo in self._adendos
                if adendo.amostra_id == amostra_id
            ]

    # --- Compatibilidade temporária ----------------------------------------
    # `testes/test_servico.py` chama os nomes genéricos antigos do agregado de
    # amostra e NÃO pode ser editado neste bloco (B3-bis autoriza só
    # test_alerta.py). Estes dois delegados mantêm a suíte verde sem reescrever
    # asserção nenhuma, e preservam o contrato novo como o único oficial.
    # TODO(Bloco E): remover os dois junto com a atualização de test_servico.

    def buscar_por_id(self, id_amostra: str) -> Amostra:
        """DEPRECADO. Use `buscar_amostra_por_id`."""
        return self.buscar_amostra_por_id(id_amostra)

    def listar_todas(self) -> list[Amostra]:
        """DEPRECADO. Use `listar_amostras`."""
        return self.listar_amostras()
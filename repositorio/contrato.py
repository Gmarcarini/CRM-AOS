"""Contrato de persistência do CRM AOS — um protocolo por agregado.

Arquitetura, e não estilo:

1. `typing.Protocol`, nunca `abc.ABC`. `RepositorioMemoria` e o futuro
   `RepositorioSupabase` são classes independentes, sem ancestral comum. Basta
   cumprirem a forma. E um protocolo novo (`ProjetoRepositorio`) entra na
   Sprint 1 sem tocar em nenhuma classe existente nem quebrar as que já existem.

2. `@runtime_checkable` está proibido. `isinstance` contra Protocol compara
   apenas NOMES de método, nunca assinaturas — passaria em uma classe que
   devolve lista onde o contrato pede objeto. Falsa segurança é pior que
   ausência de checagem. A conformidade real é cobrada pela suíte de contrato
   do Bloco E, que executa comportamento, não nomes.

3. Agregado é a unidade de persistência. `salvar_cliente` grava o cliente e
   seus contatos; `salvar_pedido` grava o pedido, seus itens e seus documentos.
   Isso não é preferência de modelagem: é o que permite gravar no Supabase
   (PostgREST, sem transação de cliente) numa única chamada, ou via RPC, sem
   deixar estado parcial em caso de falha de rede.

4. Menor dependência. Cada serviço declara o protocolo estreito que realmente
   usa. `RepositorioCompleto` existe apenas para a fábrica e para os testes;
   nenhum serviço depende dele.
"""

from typing import Protocol

from dominio.entidades import Adendo, Amostra, Cliente, Fornecedor, Pedido, Usuario


class UsuarioRepositorio(Protocol):
    """Raiz de identidade: quem opera o sistema.

    Ids são gerados na aplicação (uuid4) ou fixados no seed — nunca pelo banco.
    Se parte dos ids nascer no Postgres e parte no Python, as duas
    implementações divergem e os testes de contrato passam a mentir.
    """

    def salvar_usuario(self, usuario: Usuario) -> None: ...

    def buscar_usuario_por_id(self, id_usuario: str) -> Usuario: ...

    def listar_usuarios(self) -> list[Usuario]: ...

    def excluir_usuario(self, id_usuario: str) -> None: ...


class CategoriaRepositorio(Protocol):
    """Categoria de fornecedor: valor simples, sem id próprio.

    Normalização (strip) e descarte de vazio são responsabilidade da
    implementação, não do chamador. `listar_categorias` devolve ordem
    alfabética porque o autocomplete de Fornecedores depende dela.
    """

    def salvar_categoria(self, nome: str) -> None: ...

    def listar_categorias(self) -> list[str]: ...

    def excluir_categoria(self, nome: str) -> None: ...


class ClienteRepositorio(Protocol):
    """Agregado cliente + contatos: salvar o cliente salva os contatos."""

    def salvar_cliente(self, cliente: Cliente) -> None: ...

    def buscar_cliente_por_id(self, id_cliente: str) -> Cliente: ...

    def listar_clientes(self) -> list[Cliente]: ...

    def excluir_cliente(self, id_cliente: str) -> None: ...


class FornecedorRepositorio(Protocol):
    """Agregado fornecedor + ids de pedidos vinculados."""

    def salvar_fornecedor(self, fornecedor: Fornecedor) -> None: ...

    def buscar_fornecedor_por_id(self, id_fornecedor: str) -> Fornecedor: ...

    def listar_fornecedores(self) -> list[Fornecedor]: ...

    def excluir_fornecedor(self, id_fornecedor: str) -> None: ...


class PedidoRepositorio(Protocol):
    """Agregado pedido + itens + documentos + amostras vinculadas."""

    def salvar_pedido(self, pedido: Pedido) -> None: ...

    def buscar_pedido_por_id(self, id_pedido: str) -> Pedido: ...

    def listar_pedidos(self) -> list[Pedido]: ...

    def excluir_pedido(self, id_pedido: str) -> None: ...


class AmostraRepositorio(Protocol):
    """Agregado amostra + adendos: o adendo só existe amarrado a uma amostra.

    Nomes qualificados (`salvar_amostra`, `buscar_amostra_por_id`) são
    obrigatórios: `RepositorioCompleto` reúne todos os agregados numa única
    classe concreta, e nomes genéricos colidiriam com os de pedido e cliente.
    """

    def salvar_amostra(self, amostra: Amostra) -> None: ...

    def buscar_amostra_por_id(self, id_amostra: str) -> Amostra: ...

    def listar_amostras(self) -> list[Amostra]: ...

    def excluir_amostra(self, id_amostra: str) -> None: ...

    def salvar_adendo(self, adendo: Adendo) -> None: ...

    def listar_adendos_por_amostra(self, amostra_id: str) -> list[Adendo]: ...


class FornecedorComCategorias(FornecedorRepositorio, CategoriaRepositorio, Protocol):
    """Dependência do FornecedorService.

    Cadastrar fornecedor também alimenta o autocomplete de categorias. Em vez de
    arrastar o repositório inteiro para dentro do serviço, declara-se aqui
    exatamente a combinação que o serviço consome.
    """


class RepositorioCompleto(
    UsuarioRepositorio,
    CategoriaRepositorio,
    ClienteRepositorio,
    FornecedorRepositorio,
    PedidoRepositorio,
    AmostraRepositorio,
    Protocol,
):
    """Visão agregada — usada apenas pela fábrica e pelos testes de contrato."""
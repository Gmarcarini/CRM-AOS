"""Cadastro e edição de cliente, com validação de CNPJ e formatação de telefone.

Toda mutação termina em `salvar_cliente`: o repositório trabalha com cópias,
então mutar o objeto recebido não persiste nada por acidente. O salvamento
explícito é o que mantém a promessa do contrato.
"""

from dominio.entidades import Cliente, Contato
from dominio.enums import StatusCliente
from dominio.erros import ErroValidacao
from dominio.validacoes import formatar_telefone, validar_cnpj
from repositorio.contrato import ClienteRepositorio


class ClienteService:
    def __init__(self, repositorio: ClienteRepositorio) -> None:
        self.repo = repositorio

    def _montar_contatos(self, contatos: list[dict]) -> list[Contato]:
        """Cria contatos com o telefone já no padrão (+55) XX XXXXX-XXXX.

        A normalização vive aqui, e não no frontend: assim todo cliente entra no
        sistema com o mesmo formato, venha o dado de onde vier.
        """
        return [
            Contato(
                nome=contato["nome"],
                telefone=formatar_telefone(contato["telefone"]),
                email=contato["email"],
            )
            for contato in contatos
        ]

    def criar_cliente(self, dados: dict, usuario_responsavel_id: str) -> Cliente:
        if not dados.get("razao_social") or not dados.get("codigo") or not dados.get("cnpj"):
            raise ErroValidacao("Razão Social, Código e CNPJ são obrigatórios.")

        if not validar_cnpj(dados["cnpj"]):
            raise ErroValidacao("CNPJ inválido. Verifique os números digitados.")

        # Código é a chave legível usada na operação; duplicar quebraria relatórios.
        for existente in self.repo.listar_clientes():
            if existente.codigo == dados["codigo"]:
                raise ErroValidacao("Já existe um cliente com este código.")

        novo_cliente = Cliente(
            razao_social=dados["razao_social"],
            codigo=dados["codigo"],
            cnpj=dados["cnpj"],
            usuario_responsavel_id=usuario_responsavel_id,
            status=StatusCliente(dados.get("status", "ativo")),
            rua=dados.get("rua", ""),
            numero=dados.get("numero", ""),
            sala=dados.get("sala", ""),
            bairro=dados.get("bairro", ""),
            cidade=dados.get("cidade", ""),
            estado=dados.get("estado", ""),
            pais=dados.get("pais", "Brasil"),
            contatos=self._montar_contatos(dados.get("contatos", [])),
        )
        self.repo.salvar_cliente(novo_cliente)
        return novo_cliente

    def editar_cliente(self, cliente: Cliente, dados: dict) -> Cliente:
        if not validar_cnpj(dados["cnpj"]):
            raise ErroValidacao("CNPJ inválido. Verifique os números digitados.")

        cliente.razao_social = dados["razao_social"]
        cliente.codigo = dados["codigo"]
        cliente.cnpj = dados["cnpj"]
        cliente.status = StatusCliente(dados["status"])
        cliente.rua = dados.get("rua", "")
        cliente.numero = dados.get("numero", "")
        cliente.sala = dados.get("sala", "")
        cliente.bairro = dados.get("bairro", "")
        cliente.cidade = dados.get("cidade", "")
        cliente.estado = dados.get("estado", "")
        cliente.pais = dados.get("pais", "Brasil")
        cliente.contatos = self._montar_contatos(dados.get("contatos", []))

        self.repo.salvar_cliente(cliente)
        return cliente
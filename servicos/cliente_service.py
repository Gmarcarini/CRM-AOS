from repositorio.memoria import RepositorioMemoria
from dominio.entidades import Cliente, Contato
from dominio.enums import StatusCliente
from dominio.erros import ErroValidacao
from dominio.validacoes import validar_cnpj, formatar_telefone

class ClienteService:
    def __init__(self, repositorio: RepositorioMemoria):
        self.repo = repositorio

    def criar_cliente(self, dados: dict, usuario_responsavel_id: str) -> Cliente:
        # 1. Validações Básicas
        if not dados.get("razao_social") or not dados.get("codigo") or not dados.get("cnpj"):
            raise ErroValidacao("Razão Social, Código e CNPJ são obrigatórios.")
            
        if not validar_cnpj(dados["cnpj"]):
            raise ErroValidacao("CNPJ inválido. Verifique os números digitados.")

        # 2. Verifica código único
        for c in self.repo.listar_clientes():
            if c.codigo == dados["codigo"]:
                raise ErroValidacao("Já existe um cliente com este código.")

        # 3. Cria os objetos de Contato
        contatos_criados = []
        for c in dados.get("contatos", []):
            # Aplica a formatação aqui!
            telefone_formatado = formatar_telefone(c["telefone"])
            
            contatos_criados.append(Contato(
                nome=c["nome"], 
                telefone=telefone_formatado, 
                email=c["email"]
            ))

        # 4. Cria o Cliente
        novo_cliente = Cliente(
            razao_social=dados["razao_social"],
            codigo=dados["codigo"],
            cnpj=dados["cnpj"],
            usuario_responsavel_id=usuario_responsavel_id,
            status=StatusCliente(dados.get("status", "ativo")),
            rua=dados.get("rua", ""),
            numero=dados.get("numero", ""),
            bairro=dados.get("bairro", ""),
            cidade=dados.get("cidade", ""),
            estado=dados.get("estado", ""),
            pais=dados.get("pais", "Brasil"),
            contatos=contatos_criados
        )
        
        self.repo.salvar_cliente(novo_cliente)
        return novo_cliente

    def editar_cliente(self, cliente: Cliente, dados: dict) -> Cliente:
        # Valida CNPJ
        if not validar_cnpj(dados["cnpj"]):
            raise ErroValidacao("CNPJ inválido. Verifique os números digitados.")
            
        # Atualiza os campos básicos
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
        
        # Recria a lista de contatos com o telefone formatado
        novos_contatos = []
        for c in dados.get("contatos", []):
            novos_contatos.append(Contato(
                nome=c["nome"], 
                telefone=formatar_telefone(c["telefone"]), # Formata o telefone
                email=c["email"]
            ))
        cliente.contatos = novos_contatos
        
        self.repo.salvar_cliente(cliente)
        return cliente
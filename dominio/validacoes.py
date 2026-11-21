import re

def validar_cnpj(cnpj: str) -> bool:
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) != 14:
        return False
        
    # Elimina CNPJs óbvios (todos números iguais)
    if cnpj == cnpj[0] * 14:
        return False
        
    # Algoritmo de validação de CNPJ
    def calcular_digito(base, pesos):
        soma = sum(int(a) * b for a, b in zip(base, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    d1 = calcular_digito(cnpj[:12], pesos1)
    d2 = calcular_digito(cnpj[:12] + str(d1), pesos2)
    
    return cnpj[-2:] == f"{d1}{d2}"

def formatar_telefone(telefone: str) -> str:
    # Remove tudo que não for número
    apenas_numeros = re.sub(r'\D', '', telefone)
    
    # Se o número for muito curto, retorna como veio para o usuário corrigir
    if len(apenas_numeros) < 10:
        return telefone

    # Lógica para Brasil (Padrão)
    # Se tiver 10 ou 11 dígitos, é um número nacional sem DDI. Adicionamos o 55.
    if len(apenas_numeros) == 10 or len(apenas_numeros) == 11:
        apenas_numeros = "55" + apenas_numeros
    
    # Agora temos o DDI + DDD + Numero. Ex: 5551991531100 (13 dígitos)
    ddi = apenas_numeros[:2]
    ddd = apenas_numeros[2:4]
    numero = apenas_numeros[4:]
    
    # Formata o número (se for celular, tem 9 dígitos. Se fixo, 8)
    if len(numero) == 9:
        numero_formatado = f"{numero[:5]}-{numero[5:]}"
    elif len(numero) == 8:
        numero_formatado = f"{numero[:4]}-{numero[4:]}"
    else:
        numero_formatado = numero # Fallback caso não bata o padrão
        
    return f"(+{ddi}) {ddd} {numero_formatado}"
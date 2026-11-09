# Ponte Alimentar SP
# FIAP - Global Solution 2026.2 (CitizenTech)
# Disciplina: Computational Thinking with Python
#
# Conecta doações de alimentos excedentes às ONGs mais compatíveis
# de São Paulo, priorizando as doações mais próximas do vencimento.

import json
from datetime import datetime


# ==================== CONSTANTES ====================

CAMINHO_ARQUIVO = "dados/dados.json"
FORMATO_DATA = "%d/%m/%Y %H:%M"

REGIOES = ("Norte", "Sul", "Leste", "Oeste", "Centro")
CATEGORIAS = ("perecível", "não perecível", "preparado")
CATEGORIAS_REFRIGERADAS = ("perecível", "preparado")
STATUS_ATIVOS = ("disponível", "reservada")

QTD_MINIMA_KG = 0.1
QTD_MAXIMA_KG = 1000
CAPACIDADE_MAXIMA_KG = 10000


# ==================== ARQUIVO JSON ====================

def carregar_dados(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return dados
    except FileNotFoundError:
        print("Arquivo de dados não encontrado. O sistema vai iniciar sem registros.")
        return {"ongs": [], "doacoes": []}
    except json.JSONDecodeError:
        print("Arquivo de dados corrompido. O sistema vai iniciar sem registros.")
        return {"ongs": [], "doacoes": []}


def salvar_dados(dados, caminho):
    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        return True
    except OSError:
        print("Erro ao salvar os dados. Verifique se a pasta existe e se o arquivo não está aberto em outro programa.")
        return False


# ==================== VALIDAÇÃO DE ENTRADAS ====================

def ler_texto(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto != "":
            return texto
        print("Este campo não pode ficar vazio.")


def ler_float(mensagem, minimo, maximo):
    while True:
        texto = input(mensagem).strip().replace(",", ".")
        try:
            numero = float(texto)
        except ValueError:
            print("Valor inválido! Digite um número (ex.: 12,5).")
            continue
        if minimo <= numero <= maximo:
            return numero
        print(f"O valor deve estar entre {minimo} e {maximo}.")


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        texto = input(mensagem).strip()
        try:
            numero = int(texto)
        except ValueError:
            print("Valor inválido! Digite um número inteiro.")
            continue
        if minimo <= numero <= maximo:
            return numero
        print(f"O valor deve estar entre {minimo} e {maximo}.")


def ler_opcao(mensagem, opcoes):
    print(mensagem)
    for i in range(len(opcoes)):
        print(f"  {i + 1} - {opcoes[i]}")
    while True:
        escolha = input("Digite o número: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(opcoes):
            return opcoes[int(escolha) - 1]
        print(f"Opção inválida! Digite um número de 1 a {len(opcoes)}.")


def confirmar(mensagem):
    while True:
        resposta = input(f"{mensagem} (S/N): ").strip().upper()
        if resposta == "S":
            return True
        elif resposta == "N":
            return False
        print("Responda apenas S ou N.")


def ler_data_futura(mensagem):
    # RN03: a validade precisa estar no formato certo e no futuro
    while True:
        texto = input(mensagem).strip()
        try:
            data = datetime.strptime(texto, FORMATO_DATA)
        except ValueError:
            print("Data inválida! Use o formato dd/mm/aaaa hh:mm (ex.: 15/11/2026 18:00).")
            continue
        if data > datetime.now():
            return texto
        print("A validade não pode estar no passado.")


def selecionar_categorias():
    # A ONG precisa aceitar pelo menos uma categoria
    while True:
        aceitas = []
        for categoria in CATEGORIAS:
            if confirmar(f"A ONG aceita alimentos '{categoria}'?"):
                aceitas.append(categoria)
        if len(aceitas) > 0:
            return aceitas
        print("Selecione pelo menos uma categoria.")


# ==================== REGRAS DE NEGÓCIO ====================

def calcular_horas_restantes(validade):
    data_validade = datetime.strptime(validade, FORMATO_DATA)
    diferenca = data_validade - datetime.now()
    return diferenca.total_seconds() / 3600


def classificar_urgencia(horas):
    # RN04: quanto menos tempo até a validade, maior a urgência
    if horas <= 0:
        return "VENCIDA"
    elif horas <= 6:
        return "CRÍTICA"
    elif horas <= 24:
        return "ALTA"
    elif horas <= 72:
        return "MÉDIA"
    else:
        return "BAIXA"


def atualizar_expiradas(doacoes):
    # RN08: doação ativa que passou da validade vira "expirada"
    quantidade = 0
    for doacao in doacoes:
        if doacao["status"] in STATUS_ATIVOS and calcular_horas_restantes(doacao["validade"]) <= 0:
            doacao["status"] = "expirada"
            quantidade += 1
    return quantidade


def capacidade_disponivel(ong, doacoes):
    # O que a ONG ainda consegue receber: capacidade - recebido - reservado para ela
    reservado = 0
    for doacao in doacoes:
        if doacao["status"] == "reservada" and doacao["ong_id"] == ong["id"]:
            reservado += doacao["quantidade_kg"]
    return ong["capacidade_kg"] - ong["recebido_kg"] - reservado


def ong_compativel(ong, doacao, doacoes):
    # RN06: a ONG precisa aceitar a categoria
    if doacao["categoria"] not in ong["categorias_aceitas"]:
        return False
    # RN05: perecíveis e preparados exigem refrigeração
    elif doacao["categoria"] in CATEGORIAS_REFRIGERADAS and not ong["refrigeracao"]:
        return False
    # RN06: a ONG precisa ter capacidade para a quantidade
    elif capacidade_disponivel(ong, doacoes) < doacao["quantidade_kg"]:
        return False
    else:
        return True


def buscar_ongs_compativeis(ongs, doacao, doacoes):
    # RN07: mesma região primeiro; depois, maior capacidade disponível.
    # Cada candidata vira uma tupla (mesma_regiao, capacidade, id).
    # O Python ordena tuplas comparando o 1º item, depois o 2º, depois o 3º.
    candidatas = []
    for ong in ongs:
        if ong_compativel(ong, doacao, doacoes):
            mesma_regiao = 1 if ong["regiao"] == doacao["regiao"] else 0
            candidatas.append((mesma_regiao, capacidade_disponivel(ong, doacoes), ong["id"]))
    candidatas.sort(reverse=True)

    resultado = []
    for candidata in candidatas:
        resultado.append(buscar_por_id(ongs, candidata[2]))
    return resultado


def gerar_relatorio(dados):
    relatorio = {
        "kg_entregue": 0,
        "kg_expirado": 0,
        "kg_ativo": 0,
        "por_status": {"disponível": 0, "reservada": 0, "entregue": 0, "expirada": 0},
        "entregue_por_categoria": {},
    }
    for doacao in dados["doacoes"]:
        status = doacao["status"]
        quantidade = doacao["quantidade_kg"]
        relatorio["por_status"][status] += 1
        if status == "entregue":
            relatorio["kg_entregue"] += quantidade
            categoria = doacao["categoria"]
            relatorio["entregue_por_categoria"][categoria] = relatorio["entregue_por_categoria"].get(categoria, 0) + quantidade
        elif status == "expirada":
            relatorio["kg_expirado"] += quantidade
        else:
            relatorio["kg_ativo"] += quantidade

    total_encerrado = relatorio["kg_entregue"] + relatorio["kg_expirado"]
    if total_encerrado > 0:
        relatorio["aproveitamento"] = relatorio["kg_entregue"] / total_encerrado * 100
    else:
        relatorio["aproveitamento"] = 0
    return relatorio


# ==================== FUNÇÕES AUXILIARES ====================

def gerar_id(lista):
    # RN11: o próximo id é o maior id existente + 1
    maior = 0
    for item in lista:
        if item["id"] > maior:
            maior = item["id"]
    return maior + 1


def buscar_por_id(lista, id_procurado):
    for item in lista:
        if item["id"] == id_procurado:
            return item
    return None


def nome_da_ong(ongs, id_ong):
    ong = buscar_por_id(ongs, id_ong)
    if ong is None:
        return "-"
    return ong["nome"]


def exibir_doacao(doacao, ongs):
    horas = calcular_horas_restantes(doacao["validade"])
    linha = (f"[{doacao['id']}] {doacao['alimento']} ({doacao['categoria']}) - "
             f"{doacao['quantidade_kg']:.1f} kg | {doacao['doador']} | Zona {doacao['regiao']} | "
             f"Validade: {doacao['validade']} | Status: {doacao['status']}")
    if doacao["status"] in STATUS_ATIVOS:
        linha += f" | Urgência: {classificar_urgencia(horas)}"
    if doacao["ong_id"] is not None:
        linha += f" | ONG: {nome_da_ong(ongs, doacao['ong_id'])}"
    print(linha)


def pausar():
    input("\nPressione Enter para voltar ao menu...")


# ==================== FUNCIONALIDADES DO MENU ====================

def cadastrar_ong(dados):
    print("\n--- CADASTRAR ONG ---")
    nome = ler_texto("Nome da ONG: ")
    for ong in dados["ongs"]:
        if ong["nome"].lower() == nome.lower():
            print("Já existe uma ONG com esse nome. Cadastro cancelado.")
            return

    regiao = ler_opcao("Região de atuação:", REGIOES)
    categorias = selecionar_categorias()
    refrigeracao = confirmar("A ONG tem refrigeração?")
    if not refrigeracao:
        for categoria in categorias:
            if categoria in CATEGORIAS_REFRIGERADAS:
                print(f"Aviso: sem refrigeração, a ONG não receberá alimentos '{categoria}' (regra RN05).")
    capacidade = ler_float("Capacidade de recebimento (kg): ", 1, CAPACIDADE_MAXIMA_KG)

    nova_ong = {
        "id": gerar_id(dados["ongs"]),
        "nome": nome,
        "regiao": regiao,
        "categorias_aceitas": categorias,
        "refrigeracao": refrigeracao,
        "capacidade_kg": capacidade,
        "recebido_kg": 0.0,
    }
    dados["ongs"].append(nova_ong)
    if salvar_dados(dados, CAMINHO_ARQUIVO):
        print(f"ONG '{nome}' cadastrada com sucesso! (id {nova_ong['id']})")


def listar_ongs(dados):
    print("\n--- ONGS CADASTRADAS ---")
    if len(dados["ongs"]) == 0:
        print("Nenhuma ONG cadastrada.")
        return
    for ong in dados["ongs"]:
        refrigeracao = "sim" if ong["refrigeracao"] else "não"
        disponivel = capacidade_disponivel(ong, dados["doacoes"])
        print(f"[{ong['id']}] {ong['nome']} | Zona {ong['regiao']} | "
              f"Aceita: {', '.join(ong['categorias_aceitas'])} | Refrigeração: {refrigeracao} | "
              f"Recebido: {ong['recebido_kg']:.1f} kg | Disponível: {disponivel:.1f} de {ong['capacidade_kg']:.1f} kg")


def cadastrar_doacao(dados):
    print("\n--- CADASTRAR DOAÇÃO ---")
    doador = ler_texto("Nome do doador (estabelecimento): ")
    alimento = ler_texto("Alimento: ")
    categoria = ler_opcao("Categoria:", CATEGORIAS)
    quantidade = ler_float("Quantidade (kg): ", QTD_MINIMA_KG, QTD_MAXIMA_KG)
    regiao = ler_opcao("Região do doador:", REGIOES)
    validade = ler_data_futura("Validade (dd/mm/aaaa hh:mm): ")

    nova_doacao = {
        "id": gerar_id(dados["doacoes"]),
        "doador": doador,
        "alimento": alimento,
        "categoria": categoria,
        "quantidade_kg": quantidade,
        "regiao": regiao,
        "validade": validade,
        "status": "disponível",
        "ong_id": None,
    }
    dados["doacoes"].append(nova_doacao)
    if salvar_dados(dados, CAMINHO_ARQUIVO):
        urgencia = classificar_urgencia(calcular_horas_restantes(validade))
        print(f"Doação cadastrada com sucesso! (id {nova_doacao['id']}) - Urgência: {urgencia}")


def listar_doacoes(dados):
    print("\n--- DOAÇÕES ATIVAS (mais urgentes primeiro) ---")
    # Ordena pelas horas restantes usando tuplas (horas, id)
    ativas = []
    for doacao in dados["doacoes"]:
        if doacao["status"] in STATUS_ATIVOS:
            ativas.append((calcular_horas_restantes(doacao["validade"]), doacao["id"]))
    ativas.sort()

    if len(ativas) == 0:
        print("Nenhuma doação ativa.")
    for item in ativas:
        exibir_doacao(buscar_por_id(dados["doacoes"], item[1]), dados["ongs"])

    print("\n--- DOAÇÕES ENCERRADAS ---")
    encerradas = 0
    for doacao in dados["doacoes"]:
        if doacao["status"] not in STATUS_ATIVOS:
            exibir_doacao(doacao, dados["ongs"])
            encerradas += 1
    if encerradas == 0:
        print("Nenhuma doação encerrada.")


def encontrar_ong(dados):
    print("\n--- ENCONTRAR ONG PARA UMA DOAÇÃO ---")
    disponiveis = 0
    for doacao in dados["doacoes"]:
        if doacao["status"] == "disponível":
            exibir_doacao(doacao, dados["ongs"])
            disponiveis += 1
    if disponiveis == 0:
        print("Nenhuma doação disponível no momento.")
        return

    id_doacao = ler_inteiro("\nId da doação (0 para cancelar): ", 0, gerar_id(dados["doacoes"]))
    if id_doacao == 0:
        return
    doacao = buscar_por_id(dados["doacoes"], id_doacao)
    if doacao is None or doacao["status"] != "disponível":
        print("Doação não encontrada ou não está disponível.")
        return

    sugestoes = buscar_ongs_compativeis(dados["ongs"], doacao, dados["doacoes"])
    if len(sugestoes) == 0:
        print("Nenhuma ONG compatível com essa doação (categoria, refrigeração ou capacidade).")
        return

    print("\nONGs compatíveis (melhor opção primeiro):")
    for i in range(len(sugestoes)):
        ong = sugestoes[i]
        regiao = "mesma região" if ong["regiao"] == doacao["regiao"] else f"outra região: {ong['regiao']}"
        disponivel = capacidade_disponivel(ong, dados["doacoes"])
        print(f"  {i + 1} - {ong['nome']} ({regiao}) | Disponível: {disponivel:.1f} kg")

    escolha = ler_inteiro("Número da ONG para reservar (0 para cancelar): ", 0, len(sugestoes))
    if escolha == 0:
        print("Reserva cancelada.")
        return
    ong_escolhida = sugestoes[escolha - 1]
    doacao["status"] = "reservada"
    doacao["ong_id"] = ong_escolhida["id"]
    if salvar_dados(dados, CAMINHO_ARQUIVO):
        print(f"Doação {doacao['id']} reservada para '{ong_escolhida['nome']}'.")


def confirmar_entrega(dados):
    print("\n--- CONFIRMAR ENTREGA ---")
    reservadas = 0
    for doacao in dados["doacoes"]:
        if doacao["status"] == "reservada":
            exibir_doacao(doacao, dados["ongs"])
            reservadas += 1
    if reservadas == 0:
        print("Nenhuma doação reservada aguardando entrega.")
        return

    id_doacao = ler_inteiro("\nId da doação entregue (0 para cancelar): ", 0, gerar_id(dados["doacoes"]))
    if id_doacao == 0:
        return
    doacao = buscar_por_id(dados["doacoes"], id_doacao)
    # RN09: só doações reservadas podem ser entregues
    if doacao is None or doacao["status"] != "reservada":
        print("Doação não encontrada ou não está reservada.")
        return

    ong = buscar_por_id(dados["ongs"], doacao["ong_id"])
    if not confirmar(f"Confirmar entrega de {doacao['quantidade_kg']:.1f} kg para '{ong['nome']}'?"):
        print("Entrega não confirmada.")
        return

    # RN10: a quantidade entregue soma no recebido da ONG
    doacao["status"] = "entregue"
    ong["recebido_kg"] += doacao["quantidade_kg"]
    if salvar_dados(dados, CAMINHO_ARQUIVO):
        print("Entrega confirmada! Obrigado por combater o desperdício.")


def exibir_relatorio(dados):
    relatorio = gerar_relatorio(dados)
    print("\n--- RELATÓRIO DE IMPACTO ---")
    print(f"Alimento entregue (salvo do lixo): {relatorio['kg_entregue']:.1f} kg")
    print(f"Alimento perdido (expirado):       {relatorio['kg_expirado']:.1f} kg")
    print(f"Alimento ainda em circulação:      {relatorio['kg_ativo']:.1f} kg")
    print(f"Taxa de aproveitamento:            {relatorio['aproveitamento']:.1f}%")

    print("\nDoações por status:")
    for status, quantidade in relatorio["por_status"].items():
        print(f"  {status}: {quantidade}")

    print("\nEntregue por categoria:")
    if len(relatorio["entregue_por_categoria"]) == 0:
        print("  Nenhuma entrega registrada.")
    for categoria, kg in relatorio["entregue_por_categoria"].items():
        print(f"  {categoria}: {kg:.1f} kg")


# ==================== PROGRAMA PRINCIPAL ====================

def exibir_menu():
    print("\n===== PONTE ALIMENTAR SP =====")
    print("1 - Cadastrar ONG")
    print("2 - Listar ONGs")
    print("3 - Cadastrar doação")
    print("4 - Listar doações (por urgência)")
    print("5 - Encontrar ONG para uma doação")
    print("6 - Confirmar entrega")
    print("7 - Relatório de impacto")
    print("0 - Sair")
    opcao = input("Escolha uma opção: ").strip()
    return opcao


def main():
    dados = carregar_dados(CAMINHO_ARQUIVO)
    while True:
        # A cada volta, verifica se alguma doação venceu enquanto o programa estava aberto
        expiradas = atualizar_expiradas(dados["doacoes"])
        if expiradas > 0:
            print(f"\nAtenção: {expiradas} doação(ões) passaram da validade e foram marcadas como expiradas.")
            salvar_dados(dados, CAMINHO_ARQUIVO)

        opcao = exibir_menu()
        match opcao:
            case "1":
                cadastrar_ong(dados)
            case "2":
                listar_ongs(dados)
            case "3":
                cadastrar_doacao(dados)
            case "4":
                listar_doacoes(dados)
            case "5":
                encontrar_ong(dados)
            case "6":
                confirmar_entrega(dados)
            case "7":
                exibir_relatorio(dados)
            case "0":
                print("Obrigado por usar a Ponte Alimentar SP!")
                break
            case _:
                print("Opção inválida! Digite um número de 0 a 7.")
                continue
        pausar()


if __name__ == "__main__":
    main()

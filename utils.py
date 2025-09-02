import re
import json
import os
from datetime import date
from rapidfuzz import fuzz

# 🔹 Limpa cada linha removendo espaços e prefixos como "1-"
def limpar_linha(linha):
    linha = linha.strip()
    linha = re.sub(r'^\d+-\s*', '', linha)
    return linha

# 🔹 Importa frases de um arquivo .txt separado por linha em branco
def importar_frases_txt(caminho_txt):
    with open(caminho_txt, 'r', encoding='utf-8') as f:
        linhas = [linha.rstrip('\n') for linha in f]

    try:
        divisor = linhas.index('')
    except ValueError:
        raise ValueError("O arquivo deve conter uma linha em branco separando frases PT e EN.")

    frases_pt = [limpar_linha(l) for l in linhas[:divisor] if l.strip()]
    frases_en = [limpar_linha(l) for l in linhas[divisor+1:] if l.strip()]

    if len(frases_pt) != len(frases_en):
        raise ValueError(f"Número de frases PT ({len(frases_pt)}) diferente de EN ({len(frases_en)}).")

    frases = [{"pt": frases_pt[i], "en": frases_en[i]} for i in range(len(frases_pt))]
    return frases

# 🔹 Carrega os dados salvos no JSON
def carregar_dados(caminho_json):
    if not os.path.exists(caminho_json) or os.path.getsize(caminho_json) == 0:
        return {
            "fila": [],
            "revisadas_hoje": 0,
            "meta_diaria": 0,
            "ultima_data": ""
        }
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "fila": [],
            "revisadas_hoje": 0,
            "meta_diaria": 0,
            "ultima_data": ""
        }

# 🔹 Salva os dados no JSON
def salvar_dados(dados, caminho_json):
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# 🔹 Atualiza a fila com novas frases e reseta meta diária se for um novo dia
def atualizar_fila_com_novas(frases_novas, caminho_json):
    dados = carregar_dados(caminho_json)
    hoje = str(date.today())

    if dados["ultima_data"] != hoje:
        dados["meta_diaria"] = len(dados["fila"]) + len(frases_novas)
        dados["revisadas_hoje"] = 0
        dados["ultima_data"] = hoje

    frases_existentes = {(f["pt"], f["en"]) for f in dados["fila"]}
    novas_filtradas = [f for f in frases_novas if (f["pt"], f["en"]) not in frases_existentes]

    dados["fila"].extend(novas_filtradas)
    salvar_dados(dados, caminho_json)

# 🔹 Verifica se a resposta está correta com base na similaridade
def verificar_resposta(correta, resposta_usuario, limite=90):
    score = fuzz.ratio(correta.lower(), resposta_usuario.lower())
    return score >= limite, score

# 🔹 Processa a resposta e atualiza a fila
def processar_resposta(dados, resposta_usuario, limite=85):
    if not dados["fila"]:
        return None, 0, "Fila vazia"

    frase_atual = dados["fila"][0]
    correta = frase_atual["en"]

    correta_bool, score = verificar_resposta(correta, resposta_usuario, limite)

    if correta_bool:
        dados["fila"].pop(0)
    else:
        dados["fila"].append(dados["fila"].pop(0))

    dados["revisadas_hoje"] += 1

    return correta_bool, score, correta

# 🔹 Zera a fila e reinicia os contadores
def zerar_fila(caminho_json):
    dados = {
        "fila": [],
        "revisadas_hoje": 0,
        "meta_diaria": 0,
        "ultima_data": str(date.today())
    }
    salvar_dados(dados, caminho_json)

# 🔹 Exporta todas as frases da fila para um arquivo .txt
def exportar_fila_para_txt(dados, caminho_saida):
    frases_pt = [item["pt"] for item in dados["fila"]]
    frases_en = [item["en"] for item in dados["fila"]]

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        for frase in frases_pt:
            f.write(frase + '\n')
        f.write('\n')  # Linha em branco separadora
        for frase in frases_en:
            f.write(frase + '\n')

# 🔹 Exclui a frase atual da fila
def excluir_frase_atual(dados, caminho_json):
    if dados["fila"]:
        dados["fila"].pop(0)
        salvar_dados(dados, caminho_json)
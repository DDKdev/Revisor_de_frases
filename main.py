import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from utils import (
    importar_frases_txt,
    atualizar_fila_com_novas,
    carregar_dados,
    salvar_dados,
    processar_resposta,
    zerar_fila,
    exportar_fila_para_txt,
    excluir_frase_atual
)

CAMINHO_JSON = "data.json"
CAMINHO_TXT = "frases.txt"

dados = carregar_dados(CAMINHO_JSON)
if "acertos_hoje" not in dados:
    dados["acertos_hoje"] = 0
salvar_dados(dados, CAMINHO_JSON)

frase_revisada = None  # Armazena a última frase correta para revisão futura

def importar_frases():
    global dados
    try:
        novas = importar_frases_txt(CAMINHO_TXT)
        inseridas, duplicadas = atualizar_fila_com_novas(novas, CAMINHO_JSON)
        dados = carregar_dados(CAMINHO_JSON)
        salvar_dados(dados, CAMINHO_JSON)
        atualizar_interface()
        messagebox.showinfo(
            "Importação",
            f"{inseridas} frases adicionadas.\n{duplicadas} duplicadas ignoradas."
        )
    except Exception as e:
        messagebox.showerror("Erro ao importar", str(e))

def verificar():
    global dados, frase_revisada
    resposta = entrada.get().strip()
    if not resposta:
        return

    frase_digitada["text"] = f"Você digitou: {resposta}"

    if dados["fila"]:
        frase_revisada = dados["fila"][0]

    correta_bool, score, correta = processar_resposta(dados, resposta)
    salvar_dados(dados, CAMINHO_JSON)

    if correta_bool:
        resultado["text"] = f"✅ Correta! ({score:.1f}%)\n📌 Frase correta: {correta}"
        resultado["foreground"] = "#228B22"
        btn_revisar_novamente.pack(pady=5)
        btn_excluir_frase.pack_forget()
    else:
        frase_revisada = None
        resultado["text"] = f"❌ Errada! ({score:.1f}%)\n📌 Frase correta: {correta}"
        resultado["foreground"] = "#B22222"
        btn_revisar_novamente.pack_forget()
        btn_excluir_frase.pack(pady=5)

    entrada.delete(0, tk.END)
    atualizar_interface()

def revisar_novamente():
    global dados, frase_revisada
    if frase_revisada:
        dados["fila"].append(frase_revisada)
        salvar_dados(dados, CAMINHO_JSON)
        atualizar_interface()
        btn_revisar_novamente.pack_forget()
        btn_excluir_frase.pack_forget()
        messagebox.showinfo("Revisão", "Frase devolvida à fila para revisão futura.")
        frase_revisada = None

def excluir_frase():
    global dados, frase_revisada
    if not dados["fila"]:
        return
    excluir_frase_atual(dados, CAMINHO_JSON)
    frase_revisada = None
    dados = carregar_dados(CAMINHO_JSON)
    salvar_dados(dados, CAMINHO_JSON)
    atualizar_interface()
    resultado["text"] = ""
    resultado["foreground"] = "#000000"
    frase_digitada["text"] = ""
    btn_revisar_novamente.pack_forget()
    btn_excluir_frase.pack_forget()
    messagebox.showinfo("Exclusão", "Frase removida da fila.")

def atualizar_interface():
    if dados["fila"]:
        frase_pt["text"] = f"PT: {dados['fila'][0]['pt']}"
    else:
        frase_pt["text"] = "🐝 A fila está vazia!"

    progresso["text"] = f"Revisadas hoje: {dados['revisadas_hoje']} / Meta: {dados['meta_diaria']}"
    total_fila["text"] = f"Frases na fila: {len(dados['fila'])}"

    if dados["meta_diaria"] > 0:
        percentual = int((dados["revisadas_hoje"] / dados["meta_diaria"]) * 100)
        barra_progresso["value"] = percentual
    else:
        barra_progresso["value"] = 0

    total_revisadas = dados["revisadas_hoje"]
    acertos = dados.get("acertos_hoje", 0)

    if total_revisadas > 0:
        taxa = (acertos / total_revisadas) * 100
        taxa_acertos["text"] = f"Taxa de acertos do dia: {taxa:.1f}% ({acertos} acertos)"
    else:
        taxa_acertos["text"] = "Taxa de acertos do dia: —"

def confirmar_zerar():
    global dados, frase_revisada
    resposta = messagebox.askyesno("Zerar Fila", "Tem certeza que deseja apagar todas as frases?")
    if resposta:
        zerar_fila(CAMINHO_JSON)
        dados = carregar_dados(CAMINHO_JSON)
        frase_revisada = None
        salvar_dados(dados, CAMINHO_JSON)
        atualizar_interface()
        resultado["text"] = ""
        resultado["foreground"] = "#000000"
        frase_digitada["text"] = ""
        btn_revisar_novamente.pack_forget()
        btn_excluir_frase.pack_forget()
        messagebox.showinfo("Fila zerada", "Todas as frases foram removidas.")

def exportar_fila():
    try:
        exportar_fila_para_txt(dados, "fila_exportada.txt")
        messagebox.showinfo("Exportação", "Fila exportada com sucesso para 'fila_exportada.txt'.")
    except Exception as e:
        messagebox.showerror("Erro ao exportar", str(e))

# Interface
root = tk.Tk()
root.title("Revisor de Inglês")
root.geometry("640x600")
root.configure(bg="#f0f4ff")

style = ttk.Style()
style.theme_use("clam")

frame_main = ttk.Frame(root, padding=20)
frame_main.pack()

frase_pt = ttk.Label(frame_main, text="", font=("Arial", 14), wraplength=580)
frase_pt.pack(pady=10)

entrada = ttk.Entry(frame_main, font=("Arial", 14), width=50)
entrada.pack(pady=10)
entrada.bind("<Return>", lambda event: verificar())

btn_frame = ttk.Frame(frame_main)
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Verificar", command=verificar).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Importar Frases", command=importar_frases).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Zerar Fila", command=confirmar_zerar).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Exportar Fila", command=exportar_fila).pack(side="left", padx=5)

frase_digitada = ttk.Label(frame_main, text="", font=("Arial", 12, "italic"), foreground="#444466", wraplength=580)
frase_digitada.pack(pady=5)

resultado = ttk.Label(frame_main, text="", font=("Arial", 14), wraplength=580)
resultado.pack(pady=10)

btn_revisar_novamente = ttk.Button(frame_main, text="Revisar novamente", command=revisar_novamente)
btn_revisar_novamente.pack_forget()

btn_excluir_frase = ttk.Button(frame_main, text="Excluir frase", command=excluir_frase)
btn_excluir_frase.pack_forget()

progresso = ttk.Label(frame_main, text="", font=("Arial", 12))
progresso.pack()

total_fila = ttk.Label(frame_main, text="", font=("Arial", 12))
total_fila.pack()

barra_progresso = ttk.Progressbar(frame_main, orient="horizontal", length=400, mode="determinate")
barra_progresso.pack(pady=10)

taxa_acertos = ttk.Label(frame_main, text="", font=("Arial", 12))
taxa_acertos.pack()

atualizar_interface()
root.mainloop()
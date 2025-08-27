import tkinter as tk
from tkinter import messagebox
from utils import (
    importar_frases_txt,
    atualizar_fila_com_novas,
    carregar_dados,
    salvar_dados,
    processar_resposta,
    zerar_fila,
    exportar_fila_para_txt

)

CAMINHO_JSON = "data.json"
CAMINHO_TXT = "frases.txt"

# Carrega os dados iniciais
dados = carregar_dados(CAMINHO_JSON)

# Funções da interface
def importar_frases():
    try:
        novas = importar_frases_txt(CAMINHO_TXT)
        atualizar_fila_com_novas(novas, CAMINHO_JSON)
        global dados
        dados = carregar_dados(CAMINHO_JSON)
        atualizar_interface()
        messagebox.showinfo("Importação", f"{len(novas)} frases importadas com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro ao importar", str(e))

def verificar():
    resposta = entrada.get().strip()
    if not resposta:
        return

    frase_digitada["text"] = f"Você digitou: {resposta}"

    correta_bool, score, correta = processar_resposta(dados, resposta)
    salvar_dados(dados, CAMINHO_JSON)

    if correta_bool:
        resultado["text"] = f"✅ Correta! ({score:.1f}%)\n📌 Frase correta: {correta}"
    else:
        resultado["text"] = f"❌ Errada! ({score:.1f}%)\n📌 Frase correta: {correta}"

    entrada.delete(0, tk.END)
    atualizar_interface()

def atualizar_interface():
    if dados["fila"]:
        frase_pt["text"] = f"PT: {dados['fila'][0]['pt']}"
    else:
        frase_pt["text"] = "🎉 Fila vazia!"

    progresso["text"] = f"Revisadas hoje: {dados['revisadas_hoje']} / Meta: {dados['meta_diaria']}"
    total_fila["text"] = f"Frases na fila: {len(dados['fila'])}"

def confirmar_zerar():
    resposta = messagebox.askyesno("Zerar Fila", "Tem certeza que deseja apagar todas as frases?")
    if resposta:
        zerar_fila(CAMINHO_JSON)
        global dados
        dados = carregar_dados(CAMINHO_JSON)
        atualizar_interface()
        resultado["text"] = ""
        frase_digitada["text"] = ""
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
root.geometry("600x450")

frase_pt = tk.Label(root, text="", font=("Arial", 14), wraplength=550)
frase_pt.pack(pady=10)

entrada = tk.Entry(root, font=("Arial", 14), width=50)
entrada.pack(pady=10)

btn_verificar = tk.Button(root, text="Verificar", command=verificar)
btn_verificar.pack(pady=5)

btn_importar = tk.Button(root, text="Importar Frases", command=importar_frases)
btn_importar.pack(pady=5)

btn_zerar = tk.Button(root, text="Zerar Fila", command=confirmar_zerar)
btn_zerar.pack(pady=5)

btn_exportar = tk.Button(root, text="Exportar Fila", command=exportar_fila)
btn_exportar.pack(pady=5)

frase_digitada = tk.Label(
    root,
    text="",
    font=("Arial", 16, "italic"),
    fg="#444466",
    wraplength=550,
    justify="left"
)
frase_digitada.pack(pady=5)

resultado = tk.Label(root, text="", font=("Arial", 16), wraplength=550)
resultado.pack(pady=10)

progresso = tk.Label(root, text="", font=("Arial", 12))
progresso.pack()

total_fila = tk.Label(root, text="", font=("Arial", 12))
total_fila.pack()

atualizar_interface()
root.mainloop()
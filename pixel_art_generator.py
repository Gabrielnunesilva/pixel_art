import os
import ctypes
from tkinter import Tk, Button, Label, filedialog, Canvas, Frame, ttk
from PIL import Image, ImageTk
import numpy as np
from sklearn.cluster import KMeans

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

PALETAS = {
    "Padrão": None,
    "CGA": [(0,0,0), (0,255,255), (255,0,255), (255,255,255)],
    "Commodore 64": [(0, 0, 0), (255, 255, 255), (136, 0, 0), (170, 255, 238),
    (204, 68, 204), (0, 204, 85), (0, 0, 170), (238, 238, 119),
    (221, 136, 85), (102, 68, 0), (255, 119, 119), (51, 51, 51),
    (119, 119, 119), (170, 255, 102), (0, 136, 255), (187, 187, 187)],
    "Game Boy": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
    "NES": [(124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 40, 188),
            (148, 0, 132), (168, 0, 32), (168, 16, 0), (136, 20, 0),
            (80, 48, 0), (0, 120, 0), (0, 104, 0), (0, 88, 0),
            (0, 64, 88), (0, 0, 0), (188, 188, 188), (248, 248, 248)],
    "PICO-8": [(0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81),
               (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
               (255, 0, 77), (255, 163, 0), (255, 236, 39), (0, 228, 54),
               (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170)],
}

def escolher_imagem():
    caminho = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;")]
    )
    if caminho:
        label_arquivo.config(text=caminho)
        btn_gerar.config(state="normal")
        exibir_imagem(caminho, canvas_original)

def exibir_imagem(caminho, canvas):
    global imagens_tk
    img = Image.open(caminho)
    img.thumbnail((150, 150))
    img_tk = ImageTk.PhotoImage(img)
    canvas.config(width=img.width, height=img.height)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    imagens_tk.append(img_tk)

def aplicar_paleta(img, paleta_rgb):
    img = img.convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    flat = arr.reshape(-1, 3)

    if paleta_rgb is None:
        kmeans = KMeans(n_clusters=32, n_init=1, random_state=42)
        kmeans.fit(flat)
        paleta = np.array(kmeans.cluster_centers_)
    else:
        paleta = np.array(paleta_rgb)

    dists = np.sqrt(((flat[:, None] - paleta[None, :]) ** 2).sum(axis=2))
    indices = dists.argmin(axis=1)
    quantizados = paleta[indices].reshape(h, w, 3).astype(np.uint8)

    return Image.fromarray(quantizados)

def gerar_pixel_art():
    global imagem_pixel_art
    caminho = label_arquivo.cget("text")
    if not caminho or caminho == "Nenhuma imagem selecionada":
        return

    tamanho = int(combo_res.get())
    resolucao_selecionada = combo_output_res.get()
    img = Image.open(caminho)

    if resolucao_selecionada == "Manter resolução":
        resolucao_final = img.size  # mantém a resolução original (largura, altura)
    else:
        resolucao_final = int(resolucao_selecionada)
    nome_paleta = combo_paleta.get()
    paleta_rgb = PALETAS[nome_paleta]

    img = Image.open(caminho)
    small = img.resize((tamanho, tamanho), resample=Image.NEAREST)
    quantizada = aplicar_paleta(small, paleta_rgb)
    if isinstance(resolucao_final, tuple):
        pixel_art = quantizada.resize(resolucao_final, resample=Image.NEAREST)
    else:
        pixel_art = quantizada.resize((resolucao_final, resolucao_final), resample=Image.NEAREST)

    imagem_pixel_art = pixel_art
    exibir_pixel_art_preview(pixel_art)
    btn_salvar.config(state="normal")
    label_status.config(text="Pré-visualização gerada.\nClique em 'Salvar' para gravar.")
    

def exibir_pixel_art_preview(img):
    global imagem_pixel_tk
    visual = img.resize((640, 640), resample=Image.NEAREST)
    img_tk = ImageTk.PhotoImage(visual)
    canvas_pixel.config(width=640, height=640)
    canvas_pixel.delete("all")
    canvas_pixel.create_image(0, 0, anchor="nw", image=img_tk)
    imagem_pixel_tk = img_tk

def salvar_imagem():
    global imagem_pixel_art
    if imagem_pixel_art:
        caminho_original = label_arquivo.cget("text")
        nome_original = os.path.splitext(os.path.basename(caminho_original))[0]
        nome_sugerido = f"{nome_original}_pixel.png"
        caminho = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=nome_sugerido,
            filetypes=[("PNG Image", "*.png")],
            title="Salvar Pixel Art Como"
        )

        if caminho:
            imagem_pixel_art.save(caminho)
            label_status.config(text=f"Imagem salva em:\n{caminho}")
            os.startfile(caminho)

# Interface Tkinter
root = Tk()
root.title("Pixel Art Generator")
root.geometry("1200x700")

imagens_tk = []
imagem_pixel_tk = None
imagem_pixel_art = None

frame_top = Frame(root)
frame_top.pack(fill="both", expand=True, padx=10, pady=10)

canvas_original = Canvas(frame_top, width=150, height=150, bg="gray90")
canvas_original.pack(side="left", padx=10, pady=5)

# Controles
frame_controls = Frame(frame_top)
frame_controls.pack(side="left", padx=10, pady=5, anchor="n")

label_arquivo = Label(frame_controls, text="Nenhuma imagem selecionada", wraplength=300)
label_arquivo.pack(pady=5)

btn_escolher = Button(frame_controls, text="Escolher Imagem", command=escolher_imagem)
btn_escolher.pack(pady=5)

Label(frame_controls, text="Detalhamento dos Pixels (Padrão: 32)").pack()
combo_res = ttk.Combobox(frame_controls, values=[8, 16, 24, 32, 48, 64, 96, 128, 256, 512])
combo_res.set(32)
combo_res.pack(pady=2)

Label(frame_controls, text="Resolução final (Padrão: 512 px)").pack()
combo_output_res = ttk.Combobox(frame_controls, values=["Manter resolução", 128, 256, 320, 512, 640, 800, 1024, 2048])
combo_output_res.set(512)
combo_output_res.pack(pady=2)

Label(frame_controls, text="Paleta de Cores").pack()
combo_paleta = ttk.Combobox(frame_controls, values=list(PALETAS.keys()))
combo_paleta.set("Padrão")
combo_paleta.pack(pady=2)

btn_gerar = Button(frame_controls, text="Gerar Pixel Art", command=gerar_pixel_art, state="disabled")
btn_gerar.pack(pady=5)

btn_salvar = Button(frame_controls, text="Salvar Pixel Art", command=salvar_imagem, state="disabled")
btn_salvar.pack(pady=5)

label_status = Label(frame_controls, text="", wraplength=300)
label_status.pack(pady=10)

canvas_pixel = Canvas(frame_top, width=640, height=640, bg="gray90")
canvas_pixel.pack(side="left", padx=10, pady=5)

root.mainloop()

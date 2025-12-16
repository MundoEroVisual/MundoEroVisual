import os
import subprocess
import threading
from queue import Queue
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tempfile

# ===============================
# RUTAS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG = os.path.join(BASE_DIR, "ffmpeg.exe")
FFPROBE = os.path.join(BASE_DIR, "ffprobe.exe")

# ===============================
# COLA
# ===============================
video_queue = Queue()
processing = False

# ===============================
# UTILIDADES
# ===============================
def check_ffmpeg():
    return os.path.exists(FFMPEG) and os.path.exists(FFPROBE)

def get_audio_duration(audio):
    result = subprocess.run(
        [FFPROBE, "-v", "error",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         audio],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe falló al leer '{audio}': {result.stderr.strip()}")
    out = result.stdout.strip()
    try:
        return float(out)
    except Exception:
        raise RuntimeError(f"No se pudo obtener la duración del audio (salida: {out!r})")

# ===============================
# CREAR VIDEO (IMÁGENES EN LOOP)
# ===============================
def crear_video_principal(audio, images, img_time, output):
    audio_duration = get_audio_duration(audio)

    # generar lista concat en archivo temporal (NamedTemporaryFile para seguridad)
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    list_file = tf.name

    total_time = 0.0
    with tf:
        while total_time < audio_duration:
            for img in images:
                tf.write(f"file '{img}'\n")
                tf.write(f"duration {img_time}\n")
                total_time += float(img_time)
                if total_time >= audio_duration:
                    break

        # repetir última imagen sin duration
        tf.write(f"file '{images[-1]}'\n")

    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-i", audio,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1920:1080",
        "-c:a", "aac",
        "-t", str(audio_duration),  # 🔥 AUDIO MANDA
        output
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        # mantener el archivo de lista para diagnóstico
        raise RuntimeError(f"ffmpeg falló al crear el video: {proc.stderr.strip()}")
    try:
        os.remove(list_file)
    except Exception:
        pass

# ===============================
# CONCATENAR INTRO + VIDEO
# ===============================
def unir_intro(intro, main_video, final_output):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    list_file = tf.name
    try:
        with tf:
            tf.write(f"file '{intro}'\n")
            tf.write(f"file '{main_video}'\n")

        cmd = [
            FFMPEG, "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            final_output
        ]

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg falló al unir intro: {proc.stderr.strip()}")
    finally:
        try:
            os.remove(list_file)
        except Exception:
            pass

# ===============================
# PROCESAR VIDEO
# ===============================
def procesar_video(task):
    """Función que ejecuta la creación física del video (no toca la UI)."""
    # archivo temporal para main
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_main = tf.name
    tf.close()

    crear_video_principal(
        task["audio"],
        task["images"],
        task["img_time"],
        temp_main
    )

    if task["intro"]:
        unir_intro(task["intro"], temp_main, task["output"])
        try:
            os.remove(temp_main)
        except Exception:
            pass
    else:
        os.replace(temp_main, task["output"])

# ===============================
# PROCESAR COLA
# ===============================
def process_queue(status):
    """Worker que procesa la cola. Todas las actualizaciones de UI se realizan
    vía root.after para ejecutarse en el hilo principal de Tkinter."""
    global processing
    processing = True

    while not video_queue.empty():
        task = video_queue.get()

        # actualizar status en hilo principal
        try:
            root.after(0, lambda t=task: status.set(f"Procesando: {os.path.basename(t['output'])}"))
        except Exception:
            pass

        try:
            procesar_video(task)
        except Exception as e:
            # mostrar error en hilo principal
            root.after(0, lambda err=str(e): messagebox.showerror("Error al procesar", err))

        # eliminar primer elemento de la lista en hilo principal
        try:
            root.after(0, lambda: queue_list.delete(0))
        except Exception:
            pass

        video_queue.task_done()

    root.after(0, lambda: status.set("Cola finalizada"))
    processing = False
    root.after(0, lambda: messagebox.showinfo("Listo", "Todos los videos fueron creados"))

# ===============================
# AGREGAR A COLA
# ===============================
def add_to_queue():
    if not check_ffmpeg():
        messagebox.showerror("Error", "ffmpeg.exe o ffprobe.exe no encontrados")
        return

    task = {
        "audio": audio_var.get(),
        "images": list(images_list.get(0, tk.END)),
        "intro": intro_var.get(),
        "img_time": int(img_time_var.get()),
        "output": output_var.get()
    }

    if not task["audio"] or not task["images"] or not task["output"]:
        messagebox.showerror("Error", "Faltan datos")
        return

    video_queue.put(task)
    queue_list.insert(tk.END, os.path.basename(task["output"]))
    clear_inputs()

    if not processing:
        threading.Thread(
            target=process_queue,
            args=(status_var,),
            daemon=True
        ).start()

# ===============================
# LIMPIAR INPUTS
# ===============================
def clear_inputs():
    audio_var.set("")
    intro_var.set("")
    output_var.set("")
    try:
        images_list.delete(0, tk.END)
    except Exception:
        pass
    img_time_var.set("5")

# ===============================
# VENTANA CREAR VIDEO
# ===============================
def open_creator():
    win = tk.Toplevel(root)
    win.title("Crear Video")
    win.geometry("520x540")

    def browse(var, types):
        var.set(filedialog.askopenfilename(filetypes=types))

    tk.Label(win, text="Intro (MP4 con sonido)").pack()
    tk.Entry(win, textvariable=intro_var, width=60).pack()
    tk.Button(win, text="Cargar Intro",
              command=lambda: browse(intro_var, [("Video", "*.mp4")])).pack()

    tk.Label(win, text="Audio principal").pack()
    tk.Entry(win, textvariable=audio_var, width=60).pack()
    tk.Button(win, text="Cargar Audio",
              command=lambda: browse(audio_var, [("Audio", "*.mp3 *.wav")])).pack()

    tk.Label(win, text="Imágenes").pack()

    # lista de imágenes (lista ligada a esta ventana)
    global images_list
    images_list = tk.Listbox(win)

    def cargar_imagenes():
        files = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.jpg *.png")])
        for img in files:
            images_list.insert(tk.END, img)

    tk.Button(win, text="Cargar Imágenes", command=cargar_imagenes).pack()
    images_list.pack(pady=5)

    tk.Label(win, text="Segundos por imagen").pack()
    tk.Entry(win, textvariable=img_time_var).pack()

    tk.Label(win, text="Salida final").pack()
    tk.Entry(win, textvariable=output_var, width=60).pack()
    tk.Button(win, text="Guardar",
              command=lambda: output_var.set(
                  filedialog.asksaveasfilename(defaultextension=".mp4"))
              ).pack()

    tk.Button(win, text="Agregar a Cola",
              bg="#27ae60", fg="white",
              command=add_to_queue).pack(pady=10)

# ===============================
# VENTANA PRINCIPAL
# ===============================
root = tk.Tk()
root.title("Generador de Videos con Intro")
root.geometry("620x450")

audio_var = tk.StringVar()
intro_var = tk.StringVar()
output_var = tk.StringVar()
img_time_var = tk.StringVar(value="5")
status_var = tk.StringVar(value="Esperando")

tk.Label(root, text="Cola de Videos", font=("Arial", 14, "bold")).pack()
queue_list = tk.Listbox(root, width=75, height=10)
queue_list.pack(pady=5)

tk.Label(root, textvariable=status_var).pack(pady=10)

ttk.Button(root, text="Crear Nuevo Video", command=open_creator).pack(pady=5)
ttk.Button(root, text="Salir", command=root.quit).pack()

root.mainloop()

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONVERTIR = os.path.join(BASE_DIR, "app", "convertir.py")
CREAR_VIDEOS = os.path.join(BASE_DIR, "app", "crearvideos.py")
OUTPUT_DIR = os.path.join(BASE_DIR, "app","output")
FFMPEG = os.path.join(BASE_DIR, "app","ffmpeg.exe")
FFPROBE = os.path.join(BASE_DIR, "app","ffprobe.exe")


class ManagerApp:
    def __init__(self, root):
        self.root = root
        root.title("Manager - Convertidor y Creador de Videos")
        root.geometry("640x420")

        frame = ttk.Frame(root, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Herramientas", font=(None, 14, "bold")).pack(anchor="w")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=8)

        ttk.Button(btn_frame, text="Abrir Convertidor (TTS)", command=self.open_convertidor).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Abrir Creador de Videos", command=self.open_creador).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Abrir Carpeta de Salida", command=self.open_output).pack(side="left", padx=6)

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        info = ttk.Frame(frame)
        info.pack(fill="both", expand=True)

        self.ffmpeg_label = ttk.Label(info, text="ffmpeg: ?")
        self.ffmpeg_label.pack(anchor="w")

        ttk.Label(info, text="Archivos en output:").pack(anchor="w", pady=(8, 0))
        self.listbox = tk.Listbox(info, height=12)
        self.listbox.pack(fill="both", expand=True)

        footer = ttk.Frame(frame)
        footer.pack(fill="x", pady=6)
        ttk.Button(footer, text="Actualizar", command=self.refresh).pack(side="right")

        self.refresh()
        # refrescar cada 5s
        self.root.after(5000, self.periodic_refresh)

    def open_convertidor(self):
        if not os.path.exists(CONVERTIR):
            messagebox.showerror("Error", f"No se encontró {CONVERTIR}")
            return
        # abrir en un proceso separado para evitar conflictos de Tk
        subprocess.Popen([sys.executable, CONVERTIR], cwd=BASE_DIR)

    def open_creador(self):
        if not os.path.exists(CREAR_VIDEOS):
            messagebox.showerror("Error", f"No se encontró {CREAR_VIDEOS}")
            return
        subprocess.Popen([sys.executable, CREAR_VIDEOS], cwd=BASE_DIR)

    def open_output(self):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
        # abrir carpeta en el explorador de Windows
        subprocess.Popen(["explorer", OUTPUT_DIR])

    def refresh(self):
        ok = os.path.exists(FFMPEG) and os.path.exists(FFPROBE)
        self.ffmpeg_label.config(text=f"ffmpeg {'OK' if ok else 'NO ENCONTRADO'}")

        self.listbox.delete(0, tk.END)
        if os.path.exists(OUTPUT_DIR):
            files = sorted(os.listdir(OUTPUT_DIR))
            for f in files:
                self.listbox.insert(tk.END, f)

    def periodic_refresh(self):
        self.refresh()
        self.root.after(5000, self.periodic_refresh)


def main():
    root = tk.Tk()
    app = ManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import asyncio
import edge_tts
import os
import subprocess
import tempfile

# ================= CONFIG =================
MAX_CHARS = 4000
DEFAULT_VOICE = "es-MX-JorgeNeural"
DEFAULT_RATE = "+30%"
DEFAULT_PITCH = "-25Hz"
DEFAULT_VOLUME = "+5%"
# =========================================


def clean_text(text):
    """
    Elimina todo lo que no sean letras (incluye acentos y ñ),
    espacios y saltos de línea.
    """
    cleaned = []
    for ch in text:
        if ch.isalpha() or ch.isspace():
            cleaned.append(ch)
    return "".join(cleaned).strip()


def split_text(text, max_chars):
    blocks = []
    current = ""

    for line in text.splitlines(keepends=True):
        if len(current) + len(line) <= max_chars:
            current += line
        else:
            blocks.append(current)
            current = line

    if current.strip():
        blocks.append(current)

    return blocks


async def tts_to_file(text, path, voice, rate, pitch, volume):
    tts = edge_tts.Communicate(
        text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume
    )
    await tts.save(path)


class TTSApp:
    def __init__(self, root):
        self.root = root
        root.title("TXT → Voz limpia (Edge TTS + FFmpeg)")
        root.geometry("720x420")

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Archivo TXT:").pack(anchor="w")
        self.txt_path = ttk.Entry(frame)
        self.txt_path.pack(fill="x", pady=2)

        ttk.Button(frame, text="Cargar TXT", command=self.load_txt).pack(pady=4)

        opts = ttk.Frame(frame)
        opts.pack(fill="x", pady=6)

        ttk.Label(opts, text="Voice").grid(row=0, column=0)
        self.voice = ttk.Entry(opts, width=28)
        self.voice.insert(0, DEFAULT_VOICE)
        self.voice.grid(row=0, column=1)

        ttk.Label(opts, text="Rate").grid(row=0, column=2)
        self.rate = ttk.Entry(opts, width=8)
        self.rate.insert(0, DEFAULT_RATE)
        self.rate.grid(row=0, column=3)

        ttk.Label(opts, text="Pitch").grid(row=0, column=4)
        self.pitch = ttk.Entry(opts, width=8)
        self.pitch.insert(0, DEFAULT_PITCH)
        self.pitch.grid(row=0, column=5)

        ttk.Label(opts, text="Volume").grid(row=0, column=6)
        self.volume = ttk.Entry(opts, width=8)
        self.volume.insert(0, DEFAULT_VOLUME)
        self.volume.grid(row=0, column=7)

        self.progress = ttk.Progressbar(frame, length=600)
        self.progress.pack(pady=10)

        self.status = ttk.Label(frame, text="Listo")
        self.status.pack(anchor="w")

        ttk.Button(frame, text="Convertir a MP3", command=self.start).pack(pady=10)

    def load_txt(self):
        path = filedialog.askopenfilename(filetypes=[("TXT", "*.txt")])
        if path:
            self.txt_path.delete(0, "end")
            self.txt_path.insert(0, path)

    def start(self):
        if not self.txt_path.get():
            messagebox.showerror("Error", "Selecciona un archivo TXT")
            return
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        try:
            self.set_status("Leyendo archivo...")
            with open(self.txt_path.get(), "r", encoding="utf-8") as f:
                raw_text = f.read()

            # LIMPIEZA DEL TEXTO
            text = clean_text(raw_text)

            blocks = split_text(text, MAX_CHARS)
            total = len(blocks)

            if total == 0:
                raise RuntimeError("El archivo está vacío o fue limpiado por completo")

            self.progress["maximum"] = total

            temp_dir = tempfile.mkdtemp()
            audio_files = []

            for i, block in enumerate(blocks, 1):
                self.set_status(f"Sintetizando bloque {i}/{total}")
                audio_path = os.path.join(temp_dir, f"part_{i}.mp3")

                asyncio.run(
                    tts_to_file(
                        block,
                        audio_path,
                        self.voice.get(),
                        self.rate.get(),
                        self.pitch.get(),
                        self.volume.get()
                    )
                )

                audio_files.append(audio_path)
                self.progress["value"] = i

            self.set_status("Uniendo audios...")
            output = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3", "*.mp3")]
            )
            if not output:
                return

            list_file = os.path.join(temp_dir, "list.txt")
            with open(list_file, "w", encoding="utf-8") as f:
                for a in audio_files:
                    f.write(f"file '{a}'\n")

            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                output
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.set_status("Completado")
            messagebox.showinfo("Listo", "Audio generado correctamente")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error")

    def set_status(self, txt):
        self.status.config(text=txt)
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()

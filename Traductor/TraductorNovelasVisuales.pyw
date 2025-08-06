#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traductor Especializado para Novelas Visuales
Extrae, traduce y reinserta solo los diálogos manteniendo el formato original
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
import json
import threading
from datetime import datetime

class TraductorNovelasVisuales:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎭 Traductor de Novelas Visuales")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.archivo_original = ""
        self.dialogos_extraidos = []
        self.dialogos_traducidos = []
        self.memoria_traducciones = {}
        self.cargar_memoria()
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = ttk.Label(main_frame, text="🎭 Traductor de Novelas Visuales", 
                          font=('Arial', 16, 'bold'))
        titulo.pack(pady=(0, 20))
        
        # Frame de controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones principales
        ttk.Button(controles_frame, text="📁 CARGAR ARCHIVO", 
                  command=self.cargar_archivo).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="🔍 EXTRAER DIÁLOGOS", 
                  command=self.extraer_dialogos).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="🔄 TRADUCIR", 
                  command=self.traducir_dialogos).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="💾 GUARDAR", 
                  command=self.guardar_traduccion).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="🧠 MEMORIA", 
                  command=self.mostrar_memoria).pack(side=tk.LEFT, padx=5)
        
        # Frame de contenido
        contenido_frame = ttk.Frame(main_frame)
        contenido_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Diálogos originales
        panel_izquierdo = ttk.LabelFrame(contenido_frame, text="📝 Diálogos Originales")
        panel_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.texto_original = scrolledtext.ScrolledText(panel_izquierdo, wrap=tk.WORD, 
                                                      font=('Consolas', 10))
        self.texto_original.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel derecho - Diálogos traducidos
        panel_derecho = ttk.LabelFrame(contenido_frame, text="🌍 Diálogos Traducidos")
        panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.texto_traducido = scrolledtext.ScrolledText(panel_derecho, wrap=tk.WORD, 
                                                        font=('Consolas', 10))
        self.texto_traducido.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de estado
        self.estado = ttk.Label(main_frame, text="Listo para cargar archivo...", 
                               relief=tk.SUNKEN)
        self.estado.pack(fill=tk.X, pady=(10, 0))
        
    def cargar_archivo(self):
        """Carga el archivo de la novela visual"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de novela visual",
            filetypes=[("Archivos RenPy", "*.rpy"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            self.archivo_original = archivo
            self.actualizar_estado(f"Archivo cargado: {os.path.basename(archivo)}")
            
            # Mostrar contenido del archivo
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.texto_original.delete(1.0, tk.END)
                self.texto_original.insert(1.0, contenido)
            except UnicodeDecodeError:
                # Intentar con otras codificaciones
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(archivo, 'r', encoding=encoding) as f:
                            contenido = f.read()
                        self.texto_original.delete(1.0, tk.END)
                        self.texto_original.insert(1.0, contenido)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    messagebox.showerror("Error", "No se pudo leer el archivo")
    
    def extraer_dialogos(self):
        """Extrae solo los diálogos del archivo"""
        if not self.archivo_original:
            messagebox.showwarning("Advertencia", "Primero carga un archivo")
            return
        
        def extraer_en_hilo():
            try:
                self.actualizar_estado("Extrayendo diálogos...")
                
                # Leer archivo
                with open(self.archivo_original, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Extraer diálogos
                dialogos = self.extraer_dialogos_del_texto(contenido)
                
                # Mostrar en interfaz
                self.root.after(0, lambda: self.mostrar_dialogos_extraidos(dialogos))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error al extraer: {e}"))
        
        threading.Thread(target=extraer_en_hilo, daemon=True).start()
    
    def extraer_dialogos_del_texto(self, contenido):
        """Extrae diálogos del contenido del archivo"""
        dialogos = []
        lineas = contenido.split('\n')
        
        for i, linea in enumerate(lineas):
            # Buscar patrones de diálogos
            patrones = [
                r'^\s*([^"]+)\s*"([^"]*)"',  # Personaje "diálogo"
                r'^\s*"([^"]*)"',  # Solo "diálogo"
                r'^\s*translate\s+\w+\s+\w+:\s*$',  # Líneas de traducción
                r'^\s*#\s*([^"]+)\s*"([^"]*)"',  # Comentarios con diálogos
            ]
            
            for patron in patrones:
                match = re.match(patron, linea)
                if match:
                    if len(match.groups()) == 2:
                        personaje = match.group(1).strip()
                        dialogo = match.group(2).strip()
                        if dialogo:  # Solo si hay diálogo
                            dialogos.append({
                                'linea': i + 1,
                                'personaje': personaje,
                                'dialogo': dialogo,
                                'texto_completo': linea.strip()
                            })
                    elif len(match.groups()) == 1:
                        dialogo = match.group(1).strip()
                        if dialogo:
                            dialogos.append({
                                'linea': i + 1,
                                'personaje': '',
                                'dialogo': dialogo,
                                'texto_completo': linea.strip()
                            })
                    break
        
        return dialogos
    
    def mostrar_dialogos_extraidos(self, dialogos):
        """Muestra los diálogos extraídos en la interfaz"""
        self.dialogos_extraidos = dialogos
        
        # Limpiar panel de traducción
        self.texto_traducido.delete(1.0, tk.END)
        
        # Mostrar diálogos extraídos
        texto_mostrar = f"📊 DIÁLOGOS EXTRAÍDOS: {len(dialogos)}\n"
        texto_mostrar += "=" * 50 + "\n\n"
        
        for i, dialogo in enumerate(dialogos, 1):
            texto_mostrar += f"🔸 Diálogo {i} (Línea {dialogo['linea']}):\n"
            if dialogo['personaje']:
                texto_mostrar += f"👤 Personaje: {dialogo['personaje']}\n"
            texto_mostrar += f"💬 Diálogo: {dialogo['dialogo']}\n"
            texto_mostrar += f"📄 Original: {dialogo['texto_completo']}\n"
            texto_mostrar += "-" * 30 + "\n\n"
        
        self.texto_traducido.insert(1.0, texto_mostrar)
        self.actualizar_estado(f"Extraídos {len(dialogos)} diálogos")
    
    def traducir_dialogos(self):
        """Traduce los diálogos extraídos"""
        if not self.dialogos_extraidos:
            messagebox.showwarning("Advertencia", "Primero extrae los diálogos")
            return
        
        def traducir_en_hilo():
            try:
                self.actualizar_estado("Traduciendo diálogos...")
                
                dialogos_traducidos = []
                
                for i, dialogo in enumerate(self.dialogos_extraidos):
                    # Traducir usando memoria y servicios
                    traduccion = self.traducir_con_memoria(dialogo['dialogo'])
                    
                    dialogos_traducidos.append({
                        'linea': dialogo['linea'],
                        'personaje': dialogo['personaje'],
                        'dialogo_original': dialogo['dialogo'],
                        'dialogo_traducido': traduccion,
                        'texto_completo_original': dialogo['texto_completo']
                    })
                    
                    # Actualizar progreso
                    progreso = (i + 1) / len(self.dialogos_extraidos) * 100
                    self.root.after(0, lambda p=progreso: self.actualizar_estado(f"Traduciendo... {p:.1f}%"))
                
                self.dialogos_traducidos = dialogos_traducidos
                self.root.after(0, self.mostrar_traducciones)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error al traducir: {e}"))
        
        threading.Thread(target=traducir_en_hilo, daemon=True).start()
    
    def traducir_con_memoria(self, texto):
        """Traduce texto usando memoria y servicios"""
        # Verificar memoria
        if texto in self.memoria_traducciones:
            return self.memoria_traducciones[texto]
        
        # Traducción básica (simulada)
        traduccion = self.traducir_basico(texto)
        
        # Guardar en memoria
        self.memoria_traducciones[texto] = traduccion
        
        return traduccion
    
    def traducir_basico(self, texto):
        """Traducción básica simulada"""
        # Diccionario de traducciones comunes
        traducciones_comunes = {
            "hello": "hola",
            "goodbye": "adiós",
            "thank you": "gracias",
            "please": "por favor",
            "yes": "sí",
            "no": "no",
            "what": "qué",
            "how": "cómo",
            "where": "dónde",
            "when": "cuándo",
            "why": "por qué",
            "who": "quién",
            "I": "yo",
            "you": "tú",
            "he": "él",
            "she": "ella",
            "we": "nosotros",
            "they": "ellos",
            "am": "soy",
            "is": "es",
            "are": "son",
            "was": "era",
            "were": "eran",
            "will": "será",
            "can": "puede",
            "could": "podría",
            "would": "haría",
            "should": "debería",
            "may": "puede",
            "might": "podría"
        }
        
        # Traducción simple por palabras
        palabras = texto.lower().split()
        palabras_traducidas = []
        
        for palabra in palabras:
            # Limpiar palabra de puntuación
            palabra_limpia = re.sub(r'[^\w]', '', palabra)
            
            if palabra_limpia in traducciones_comunes:
                # Mantener puntuación original
                if palabra.endswith(('.', ',', '!', '?')):
                    palabras_traducidas.append(traducciones_comunes[palabra_limpia] + palabra[-1])
                else:
                    palabras_traducidas.append(traducciones_comunes[palabra_limpia])
            else:
                palabras_traducidas.append(palabra)
        
        return ' '.join(palabras_traducidas)
    
    def mostrar_traducciones(self):
        """Muestra las traducciones en la interfaz"""
        texto_mostrar = f"🌍 TRADUCCIONES COMPLETADAS: {len(self.dialogos_traducidos)}\n"
        texto_mostrar += "=" * 50 + "\n\n"
        
        for i, dialogo in enumerate(self.dialogos_traducidos, 1):
            texto_mostrar += f"🔸 Traducción {i} (Línea {dialogo['linea']}):\n"
            if dialogo['personaje']:
                texto_mostrar += f"👤 Personaje: {dialogo['personaje']}\n"
            texto_mostrar += f"💬 Original: {dialogo['dialogo_original']}\n"
            texto_mostrar += f"🌍 Traducido: {dialogo['dialogo_traducido']}\n"
            texto_mostrar += f"📄 Línea original: {dialogo['texto_completo_original']}\n"
            texto_mostrar += "-" * 30 + "\n\n"
        
        self.texto_traducido.delete(1.0, tk.END)
        self.texto_traducido.insert(1.0, texto_mostrar)
        self.actualizar_estado(f"Traducidos {len(self.dialogos_traducidos)} diálogos")
    
    def guardar_traduccion(self):
        """Guarda la traducción en un archivo"""
        if not self.dialogos_traducidos:
            messagebox.showwarning("Advertencia", "Primero traduce los diálogos")
            return
        
        archivo_destino = filedialog.asksaveasfilename(
            title="Guardar traducción",
            defaultextension=".rpy",
            filetypes=[("Archivos RenPy", "*.rpy"), ("Archivos de texto", "*.txt")]
        )
        
        if archivo_destino:
            try:
                # Leer archivo original
                with open(self.archivo_original, 'r', encoding='utf-8') as f:
                    contenido_original = f.read()
                
                # Crear contenido traducido
                contenido_traducido = self.reemplazar_dialogos_en_contenido(contenido_original)
                
                # Guardar archivo traducido
                with open(archivo_destino, 'w', encoding='utf-8') as f:
                    f.write(contenido_traducido)
                
                # Guardar memoria
                self.guardar_memoria()
                
                messagebox.showinfo("Éxito", f"Traducción guardada en:\n{archivo_destino}")
                self.actualizar_estado(f"Traducción guardada: {os.path.basename(archivo_destino)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")
    
    def reemplazar_dialogos_en_contenido(self, contenido_original):
        """Reemplaza los diálogos en el contenido original"""
        lineas = contenido_original.split('\n')
        lineas_traducidas = lineas.copy()
        
        # Crear diccionario de traducciones por línea
        traducciones_por_linea = {}
        for dialogo in self.dialogos_traducidos:
            traducciones_por_linea[dialogo['linea']] = dialogo['dialogo_traducido']
        
        # Reemplazar diálogos en las líneas correspondientes
        for i, linea in enumerate(lineas):
            numero_linea = i + 1
            if numero_linea in traducciones_por_linea:
                # Buscar y reemplazar el diálogo en la línea
                nueva_linea = self.reemplazar_dialogo_en_linea(linea, traducciones_por_linea[numero_linea])
                lineas_traducidas[i] = nueva_linea
        
        return '\n'.join(lineas_traducidas)
    
    def reemplazar_dialogo_en_linea(self, linea, traduccion):
        """Reemplaza el diálogo en una línea específica"""
        # Buscar patrones de diálogos
        patrones = [
            (r'([^"]+)\s*"([^"]*)"', r'\1"{}"'),  # Personaje "diálogo"
            (r'"([^"]*)"', r'"{}"'),  # Solo "diálogo"
        ]
        
        for patron, reemplazo in patrones:
            match = re.search(patron, linea)
            if match:
                return re.sub(patron, reemplazo.format(traduccion), linea)
        
        return linea
    
    def mostrar_memoria(self):
        """Muestra la memoria de traducciones"""
        ventana_memoria = tk.Toplevel(self.root)
        ventana_memoria.title("🧠 Memoria de Traducciones")
        ventana_memoria.geometry("800x600")
        
        texto_memoria = scrolledtext.ScrolledText(ventana_memoria, wrap=tk.WORD)
        texto_memoria.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        texto_mostrar = f"🧠 MEMORIA DE TRADUCCIONES: {len(self.memoria_traducciones)} entradas\n"
        texto_mostrar += "=" * 50 + "\n\n"
        
        for original, traduccion in self.memoria_traducciones.items():
            texto_mostrar += f"💬 Original: {original}\n"
            texto_mostrar += f"🌍 Traducido: {traduccion}\n"
            texto_mostrar += "-" * 30 + "\n\n"
        
        texto_memoria.insert(1.0, texto_mostrar)
    
    def cargar_memoria(self):
        """Carga la memoria de traducciones"""
        try:
            if os.path.exists('memoria_traducciones.json'):
                with open('memoria_traducciones.json', 'r', encoding='utf-8') as f:
                    self.memoria_traducciones = json.load(f)
        except Exception:
            self.memoria_traducciones = {}
    
    def guardar_memoria(self):
        """Guarda la memoria de traducciones"""
        try:
            with open('memoria_traducciones.json', 'w', encoding='utf-8') as f:
                json.dump(self.memoria_traducciones, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando memoria: {e}")
    
    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.estado.config(text=mensaje)
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TraductorNovelasVisuales()
    app.ejecutar() 
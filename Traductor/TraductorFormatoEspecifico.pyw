#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traductor Especializado para Formato de Traducción RenPy
Maneja archivos con comentarios originales y líneas vacías para traducciones
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
import json
import threading
from datetime import datetime

class TraductorFormatoEspecifico:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎭 Traductor Formato Específico RenPy")
        self.root.geometry("1400x900")
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
        titulo = ttk.Label(main_frame, text="🎭 Traductor Formato Específico RenPy", 
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
        ttk.Button(controles_frame, text="📊 ESTADÍSTICAS", 
                  command=self.mostrar_estadisticas).pack(side=tk.LEFT, padx=5)
        
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
        """Carga el archivo de traducción"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de traducción",
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
        """Extrae diálogos del formato específico"""
        if not self.archivo_original:
            messagebox.showwarning("Advertencia", "Primero carga un archivo")
            return
        
        def extraer_en_hilo():
            try:
                self.actualizar_estado("Extrayendo diálogos del formato específico...")
                
                # Leer archivo
                with open(self.archivo_original, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Extraer diálogos del formato específico
                dialogos = self.extraer_dialogos_formato_especifico(contenido)
                
                # Mostrar en interfaz
                self.root.after(0, lambda: self.mostrar_dialogos_extraidos(dialogos))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error al extraer: {e}"))
        
        threading.Thread(target=extraer_en_hilo, daemon=True).start()
    
    def extraer_dialogos_formato_especifico(self, contenido):
        """Extrae diálogos del formato específico con comentarios"""
        dialogos = []
        lineas = contenido.split('\n')
        
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            
            # Buscar líneas de etiqueta de traducción
            if linea.startswith('# game/') and 'translate' in linea:
                # Extraer información de la etiqueta
                match = re.match(r'# game/([^:]+):(\d+)', linea)
                if match:
                    archivo = match.group(1)
                    linea_numero = int(match.group(2))
                    
                    # Buscar la siguiente línea que sea translate
                    if i + 1 < len(lineas):
                        linea_translate = lineas[i + 1].strip()
                        if linea_translate.startswith('translate'):
                            # Extraer etiqueta
                            etiqueta_match = re.match(r'translate\s+(\w+)\s+(\w+):', linea_translate)
                            if etiqueta_match:
                                idioma = etiqueta_match.group(1)
                                etiqueta = etiqueta_match.group(2)
                                
                                # Buscar comentarios con diálogos en las siguientes líneas
                                j = i + 2
                                while j < len(lineas) and not lineas[j].strip().startswith('# game/'):
                                    linea_actual = lineas[j].strip()
                                    
                                    # Buscar comentarios con diálogos
                                    if linea_actual.startswith('# ') and '"' in linea_actual:
                                        # Extraer diálogo del comentario
                                        dialogo_match = re.search(r'#\s*([^"]*)"([^"]*)"', linea_actual)
                                        if dialogo_match:
                                            personaje = dialogo_match.group(1).strip()
                                            dialogo = dialogo_match.group(2).strip()
                                            
                                            if dialogo:  # Solo si hay diálogo
                                                dialogos.append({
                                                    'archivo': archivo,
                                                    'linea_original': linea_numero,
                                                    'linea_actual': j + 1,
                                                    'idioma': idioma,
                                                    'etiqueta': etiqueta,
                                                    'personaje': personaje,
                                                    'dialogo': dialogo,
                                                    'tipo': 'comentario_dialogo',
                                                    'texto_completo': linea_actual,
                                                    'linea_vacia': j + 1  # Línea donde va la traducción
                                                })
                                    
                                    j += 1
                                
                                i = j - 1  # Continuar desde donde terminamos
            
            i += 1
        
        return dialogos
    
    def mostrar_dialogos_extraidos(self, dialogos):
        """Muestra los diálogos extraídos en la interfaz"""
        self.dialogos_extraidos = dialogos
        
        # Limpiar panel de traducción
        self.texto_traducido.delete(1.0, tk.END)
        
        # Mostrar diálogos extraídos
        texto_mostrar = f"📊 DIÁLOGOS EXTRAÍDOS: {len(dialogos)}\n"
        texto_mostrar += "=" * 60 + "\n\n"
        
        for i, dialogo in enumerate(dialogos, 1):
            texto_mostrar += f"🔸 Diálogo {i}:\n"
            texto_mostrar += f"📁 Archivo: {dialogo['archivo']}\n"
            texto_mostrar += f"📍 Línea: {dialogo['linea_original']} → {dialogo['linea_actual']}\n"
            texto_mostrar += f"🏷️ Etiqueta: {dialogo['etiqueta']}\n"
            if dialogo['personaje']:
                texto_mostrar += f"👤 Personaje: {dialogo['personaje']}\n"
            texto_mostrar += f"💬 Diálogo: {dialogo['dialogo']}\n"
            texto_mostrar += f"📄 Original: {dialogo['texto_completo']}\n"
            texto_mostrar += "-" * 40 + "\n\n"
        
        self.texto_traducido.insert(1.0, texto_mostrar)
        self.actualizar_estado(f"Extraídos {len(dialogos)} diálogos del formato específico")
    
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
                        'archivo': dialogo['archivo'],
                        'linea_original': dialogo['linea_original'],
                        'linea_actual': dialogo['linea_actual'],
                        'idioma': dialogo['idioma'],
                        'etiqueta': dialogo['etiqueta'],
                        'personaje': dialogo['personaje'],
                        'dialogo_original': dialogo['dialogo'],
                        'dialogo_traducido': traduccion,
                        'texto_completo_original': dialogo['texto_completo'],
                        'linea_vacia': dialogo['linea_vacia']
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
        """Traducción básica simulada mejorada"""
        # Diccionario de traducciones comunes expandido
        traducciones_comunes = {
            # Palabras básicas
            "hello": "hola", "goodbye": "adiós", "thank you": "gracias", "please": "por favor",
            "yes": "sí", "no": "no", "what": "qué", "how": "cómo", "where": "dónde",
            "when": "cuándo", "why": "por qué", "who": "quién",
            
            # Pronombres
            "i": "yo", "you": "tú", "he": "él", "she": "ella", "we": "nosotros", "they": "ellos",
            "me": "me", "him": "él", "her": "ella", "us": "nosotros", "them": "ellos",
            
            # Verbos comunes
            "am": "soy", "is": "es", "are": "son", "was": "era", "were": "eran",
            "will": "será", "can": "puede", "could": "podría", "would": "haría",
            "should": "debería", "may": "puede", "might": "podría",
            "do": "hacer", "does": "hace", "did": "hizo", "have": "tener", "has": "tiene",
            "had": "tenía", "go": "ir", "goes": "va", "went": "fue", "gone": "ido",
            "come": "venir", "comes": "viene", "came": "vino", "get": "obtener",
            "gets": "obtiene", "got": "obtuvo", "make": "hacer", "makes": "hace",
            "made": "hizo", "know": "saber", "knows": "sabe", "knew": "supo",
            "see": "ver", "sees": "ve", "saw": "vio", "seen": "visto",
            "think": "pensar", "thinks": "piensa", "thought": "pensó",
            "want": "querer", "wants": "quiere", "wanted": "quiso",
            "need": "necesitar", "needs": "necesita", "needed": "necesitó",
            
            # Adjetivos comunes
            "good": "bueno", "bad": "malo", "big": "grande", "small": "pequeño",
            "new": "nuevo", "old": "viejo", "young": "joven", "beautiful": "hermoso",
            "ugly": "feo", "happy": "feliz", "sad": "triste", "angry": "enojado",
            "tired": "cansado", "excited": "emocionado", "scared": "asustado",
            "surprised": "sorprendido", "confused": "confundido",
            
            # Adverbios
            "very": "muy", "really": "realmente", "quite": "bastante",
            "too": "demasiado", "also": "también", "only": "solo", "just": "solo",
            "still": "aún", "already": "ya", "never": "nunca", "always": "siempre",
            "sometimes": "a veces", "often": "a menudo", "usually": "usualmente",
            
            # Preposiciones
            "in": "en", "on": "en", "at": "en", "to": "a", "from": "de", "of": "de",
            "with": "con", "without": "sin", "by": "por", "for": "para",
            "about": "sobre", "against": "contra", "between": "entre",
            "among": "entre", "through": "a través de", "during": "durante",
            
            # Conjunciones
            "and": "y", "or": "o", "but": "pero", "because": "porque",
            "if": "si", "when": "cuando", "while": "mientras", "although": "aunque",
            "unless": "a menos que", "since": "desde", "until": "hasta",
            
            # Expresiones comunes
            "thank you": "gracias", "you're welcome": "de nada",
            "excuse me": "disculpe", "i'm sorry": "lo siento",
            "how are you": "cómo estás", "i'm fine": "estoy bien",
            "nice to meet you": "encantado de conocerte",
            "see you later": "hasta luego", "good morning": "buenos días",
            "good afternoon": "buenas tardes", "good night": "buenas noches",
            
            # Palabras específicas del contexto
            "sir": "señor", "madam": "señora", "miss": "señorita",
            "work": "trabajo", "job": "trabajo", "office": "oficina",
            "school": "escuela", "class": "clase", "student": "estudiante",
            "teacher": "profesor", "book": "libro", "study": "estudiar",
            "learn": "aprender", "understand": "entender", "know": "saber",
            "think": "pensar", "believe": "creer", "feel": "sentir",
            "love": "amar", "like": "gustar", "hate": "odiar",
            "want": "querer", "need": "necesitar", "hope": "esperar",
            "wish": "desear", "dream": "soñar", "imagine": "imaginar",
            
            # Expresiones de tiempo
            "today": "hoy", "yesterday": "ayer", "tomorrow": "mañana",
            "morning": "mañana", "afternoon": "tarde", "evening": "noche",
            "night": "noche", "week": "semana", "month": "mes", "year": "año",
            "time": "tiempo", "moment": "momento", "hour": "hora",
            "minute": "minuto", "second": "segundo",
            
            # Expresiones de lugar
            "here": "aquí", "there": "allí", "everywhere": "en todas partes",
            "nowhere": "en ninguna parte", "somewhere": "en algún lugar",
            "home": "casa", "house": "casa", "room": "habitación",
            "city": "ciudad", "town": "pueblo", "country": "país",
            "street": "calle", "road": "camino", "place": "lugar",
            
            # Expresiones de cantidad
            "many": "muchos", "few": "pocos", "some": "algunos",
            "all": "todos", "none": "ninguno", "each": "cada",
            "every": "cada", "any": "cualquier", "much": "mucho",
            "little": "poco", "more": "más", "less": "menos",
            "most": "la mayoría", "least": "el menos",
            
            # Expresiones de modo
            "well": "bien", "badly": "mal", "quickly": "rápidamente",
            "slowly": "lentamente", "easily": "fácilmente", "hard": "difícilmente",
            "together": "juntos", "alone": "solo", "early": "temprano",
            "late": "tarde", "soon": "pronto", "now": "ahora",
            "then": "entonces", "later": "más tarde", "before": "antes",
            "after": "después", "during": "durante", "while": "mientras",
            
            # Expresiones específicas del ejemplo
            "hmm": "hmm", "sigh": "suspiro", "looks like": "parece que",
            "snuck in": "se coló", "again": "de nuevo", "past month": "mes pasado",
            "super crazy": "super loco", "sometimes": "a veces", "wonder": "preguntarse",
            "things": "cosas", "would have been": "habría sido", "played out": "desarrollado",
            "differently": "diferentemente", "weird": "extraño", "little": "pequeña",
            "decision": "decisión", "change": "cambiar", "everything": "todo",
            "simple": "simple", "action": "acción", "turn": "voltear",
            "life": "vida", "completely": "completamente", "upside down": "al revés",
            "glance": "mirada", "fate": "destino", "honest": "honesto",
            "answer": "respuesta", "honestly": "honestamente", "putting": "poniendo",
            "too much": "demasiado", "plate": "plato", "work": "trabajo",
            "above average": "por encima del promedio", "classes": "clases",
            "coming up": "próximas", "handle": "manejar", "workload": "carga de trabajo",
            "due respect": "debido respeto", "manage": "manejar", "both": "ambos",
            "focus": "enfocar", "effectively": "efectivamente", "hard worker": "trabajador duro",
            "work ethic": "ética de trabajo", "long time": "mucho tiempo",
            "fail": "fallar", "doors": "puertas", "open": "abiertas",
            "semester": "semestre", "ends": "termina", "struggling": "luchando",
            "financially": "financieramente", "besides": "además", "face": "cara",
            "book": "libro", "school year": "año escolar", "started back up": "reanudó",
            "dad": "papá", "left": "dejó", "gradeschool": "escuela primaria",
            "relocate": "reubicar", "overseas": "extranjero", "promotion": "promoción",
            "reason": "razón", "stay": "quedarse", "new town": "nueva ciudad",
            "decided": "decidió", "move back": "regresar", "hometown": "ciudad natal",
            "despite": "a pesar de", "growing up": "crecer", "loner": "solitario",
            "interact": "interactuar", "people": "gente", "age": "edad",
            "moved out": "se mudó", "sad": "triste", "leave behind": "dejar atrás",
            "excited": "emocionado", "wealthy": "rico", "stand": "soportar",
            "thought": "pensamiento", "living off": "vivir de", "determined": "determinado",
            "make": "hacer", "income": "ingreso", "saved up": "ahorrado",
            "place": "lugar", "found": "encontró", "struggling": "luchando",
            "find": "encontrar", "time": "tiempo", "knowing": "conocer",
            "anybody": "nadie", "help": "ayudar", "cause": "causa",
            "single": "única", "interaction": "interacción", "rainy day": "día lluvioso",
            "office": "oficina", "turn": "voltear", "summer": "verano",
            "women": "mujeres", "ugly": "feo", "anything": "nada",
            "knew": "sabía", "say": "decir", "stupid": "estúpido",
            "wrong place": "lugar equivocado", "wrong time": "momento equivocado",
            "believe": "creer", "destiny": "destino", "caused": "causó",
            "hero": "héroe", "situation": "situación", "bigger": "más grande",
            "handle": "manejar", "much bigger": "mucho más grande"
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
        texto_mostrar += "=" * 60 + "\n\n"
        
        for i, dialogo in enumerate(self.dialogos_traducidos, 1):
            texto_mostrar += f"🔸 Traducción {i}:\n"
            texto_mostrar += f"📁 Archivo: {dialogo['archivo']}\n"
            texto_mostrar += f"📍 Línea: {dialogo['linea_original']} → {dialogo['linea_actual']}\n"
            texto_mostrar += f"🏷️ Etiqueta: {dialogo['etiqueta']}\n"
            if dialogo['personaje']:
                texto_mostrar += f"👤 Personaje: {dialogo['personaje']}\n"
            texto_mostrar += f"💬 Original: {dialogo['dialogo_original']}\n"
            texto_mostrar += f"🌍 Traducido: {dialogo['dialogo_traducido']}\n"
            texto_mostrar += f"📄 Línea original: {dialogo['texto_completo_original']}\n"
            texto_mostrar += "-" * 40 + "\n\n"
        
        self.texto_traducido.delete(1.0, tk.END)
        self.texto_traducido.insert(1.0, texto_mostrar)
        self.actualizar_estado(f"Traducidos {len(self.dialogos_traducidos)} diálogos")
    
    def guardar_traduccion(self):
        """Guarda la traducción en el archivo original"""
        if not self.dialogos_traducidos:
            messagebox.showwarning("Advertencia", "Primero traduce los diálogos")
            return
        
        try:
            # Leer archivo original
            with open(self.archivo_original, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            # Crear backup
            backup_path = self.archivo_original + ".backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lineas)
            
            # Reemplazar líneas vacías con traducciones
            lineas_modificadas = lineas.copy()
            
            for dialogo in self.dialogos_traducidos:
                linea_vacia = dialogo['linea_vacia'] - 1  # Convertir a índice
                if linea_vacia < len(lineas_modificadas):
                    # Crear línea de traducción
                    if dialogo['personaje']:
                        linea_traduccion = f'    {dialogo["personaje"]} "{dialogo["dialogo_traducido"]}"\n'
                    else:
                        linea_traduccion = f'    "{dialogo["dialogo_traducido"]}"\n'
                    
                    lineas_modificadas[linea_vacia] = linea_traduccion
            
            # Guardar archivo modificado
            with open(self.archivo_original, 'w', encoding='utf-8') as f:
                f.writelines(lineas_modificadas)
            
            # Guardar memoria
            self.guardar_memoria()
            
            messagebox.showinfo("Éxito", f"Traducción guardada en:\n{self.archivo_original}\n\nBackup creado en:\n{backup_path}")
            self.actualizar_estado(f"Traducción guardada: {os.path.basename(self.archivo_original)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
    
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
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas detalladas"""
        if not self.dialogos_extraidos:
            messagebox.showwarning("Advertencia", "Primero extrae los diálogos")
            return
        
        # Calcular estadísticas
        personajes = {}
        etiquetas = {}
        archivos = {}
        
        for dialogo in self.dialogos_extraidos:
            # Contar personajes
            personaje = dialogo['personaje'] or 'Sin personaje'
            personajes[personaje] = personajes.get(personaje, 0) + 1
            
            # Contar etiquetas
            etiqueta = dialogo['etiqueta']
            etiquetas[etiqueta] = etiquetas.get(etiqueta, 0) + 1
            
            # Contar archivos
            archivo = dialogo['archivo']
            archivos[archivo] = archivos.get(archivo, 0) + 1
        
        # Crear ventana de estadísticas
        ventana_stats = tk.Toplevel(self.root)
        ventana_stats.title("📊 Estadísticas Detalladas")
        ventana_stats.geometry("600x500")
        
        texto_stats = scrolledtext.ScrolledText(ventana_stats, wrap=tk.WORD)
        texto_stats.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        texto_mostrar = f"📊 ESTADÍSTICAS DETALLADAS\n"
        texto_mostrar += "=" * 40 + "\n\n"
        texto_mostrar += f"📈 Total de diálogos: {len(self.dialogos_extraidos)}\n"
        texto_mostrar += f"👥 Personajes únicos: {len(personajes)}\n"
        texto_mostrar += f"🏷️ Etiquetas únicas: {len(etiquetas)}\n"
        texto_mostrar += f"📁 Archivos únicos: {len(archivos)}\n\n"
        
        texto_mostrar += "👥 PERSONAJES MÁS FRECUENTES:\n"
        texto_mostrar += "-" * 30 + "\n"
        for personaje, count in sorted(personajes.items(), key=lambda x: x[1], reverse=True)[:10]:
            texto_mostrar += f"• {personaje}: {count} diálogos\n"
        
        texto_mostrar += "\n🏷️ ETIQUETAS MÁS FRECUENTES:\n"
        texto_mostrar += "-" * 30 + "\n"
        for etiqueta, count in sorted(etiquetas.items(), key=lambda x: x[1], reverse=True)[:10]:
            texto_mostrar += f"• {etiqueta}: {count} diálogos\n"
        
        texto_mostrar += "\n📁 ARCHIVOS:\n"
        texto_mostrar += "-" * 30 + "\n"
        for archivo, count in sorted(archivos.items(), key=lambda x: x[1], reverse=True):
            texto_mostrar += f"• {archivo}: {count} diálogos\n"
        
        texto_stats.insert(1.0, texto_mostrar)
    
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
    app = TraductorFormatoEspecifico()
    app.ejecutar() 
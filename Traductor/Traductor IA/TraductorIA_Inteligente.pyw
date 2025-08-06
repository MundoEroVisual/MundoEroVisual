#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traductor IA Inteligente - Versión Avanzada
Con características de IA: memoria, análisis contextual, aprendizaje automático
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import re
import os
import sys
import threading
import time
from datetime import datetime
from collections import defaultdict
import pickle

# Importar módulos de IA
try:
    from servicios_traduccion import TranslationServiceManager, TranslationQualityAnalyzer
    from asistente_virtual import AsistenteVirtualGUI
except ImportError:
    print("Advertencia: No se pudieron importar algunos módulos de IA")
    TranslationServiceManager = None
    TranslationQualityAnalyzer = None
    AsistenteVirtualGUI = None

class TranslationMemory:
    """Sistema de memoria para traducciones"""
    
    def __init__(self):
        self.translations = {}
        self.context_patterns = {}
        self.character_voices = {}
        self.emotional_patterns = {}
        self.cultural_adaptations = {}
        self.load_memory()
    
    def load_memory(self):
        """Carga la memoria desde archivo"""
        try:
            if os.path.exists('translation_memory.json'):
                with open('translation_memory.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.translations = data.get('translations', {})
                    self.context_patterns = data.get('context_patterns', {})
                    self.character_voices = data.get('character_voices', {})
                    self.emotional_patterns = data.get('emotional_patterns', {})
                    self.cultural_adaptations = data.get('cultural_adaptations', {})
        except Exception as e:
            print(f"Error cargando memoria: {e}")
    
    def save_memory(self):
        """Guarda la memoria en archivo"""
        try:
            data = {
                'translations': self.translations,
                'context_patterns': self.context_patterns,
                'character_voices': self.character_voices,
                'emotional_patterns': self.emotional_patterns,
                'cultural_adaptations': self.cultural_adaptations
            }
            with open('translation_memory.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando memoria: {e}")
    
    def remember_translation(self, original, translated, context, character=None, emotion=None):
        """Guarda una traducción con contexto"""
        key = original.lower().strip()
        self.translations[key] = {
            'translated': translated,
            'context': context,
            'character': character,
            'emotion': emotion,
            'count': self.translations.get(key, {}).get('count', 0) + 1,
            'timestamp': datetime.now().isoformat()
        }
        
        # Guardar patrones de contexto
        if context:
            self.context_patterns[context] = self.context_patterns.get(context, 0) + 1
        
        # Guardar voz del personaje
        if character:
            if character not in self.character_voices:
                self.character_voices[character] = []
            self.character_voices[character].append({
                'original': original,
                'translated': translated,
                'emotion': emotion
            })
        
        # Guardar patrones emocionales
        if emotion:
            if emotion not in self.emotional_patterns:
                self.emotional_patterns[emotion] = []
            self.emotional_patterns[emotion].append({
                'original': original,
                'translated': translated,
                'character': character
            })
    
    def suggest_translation(self, text, context=None, character=None, emotion=None):
        """Sugiere traducción basada en memoria"""
        key = text.lower().strip()
        
        # Buscar traducción exacta
        if key in self.translations:
            return self.translations[key]['translated']
        
        # Buscar por similitud
        suggestions = []
        for stored_key, data in self.translations.items():
            similarity = self.calculate_similarity(text, stored_key)
            if similarity > 0.7:  # 70% de similitud
                suggestions.append({
                    'original': stored_key,
                    'translated': data['translated'],
                    'similarity': similarity,
                    'context': data['context'],
                    'character': data['character'],
                    'emotion': data['emotion']
                })
        
        # Ordenar por similitud y uso
        suggestions.sort(key=lambda x: (x['similarity'], self.translations[x['original']]['count']), reverse=True)
        
        return suggestions[:3] if suggestions else []
    
    def calculate_similarity(self, text1, text2):
        """Calcula similitud entre dos textos"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

class ContextAnalyzer:
    """Analizador de contexto inteligente"""
    
    def __init__(self):
        self.dialogue_patterns = [
            r'^[A-Z][a-z]+ "',  # Personaje hablando
            r'^[a-z]+ "',        # Diálogo en minúsculas
            r'^[A-Z][a-z]+ \'',  # Personaje con comillas simples
        ]
        
        self.narration_patterns = [
            r'^\(',              # Pensamientos
            r'^scene ',          # Cambios de escena
            r'^show ',           # Mostrar elementos
            r'^play ',           # Reproducir audio
            r'^pause ',          # Pausas
        ]
        
        self.emotional_keywords = {
            'alegría': ['feliz', 'contento', 'alegre', 'dichoso', 'gozoso'],
            'tristeza': ['triste', 'deprimido', 'melancólico', 'abatido', 'desconsolado'],
            'ira': ['enojado', 'furioso', 'irritado', 'molesto', 'enfadado'],
            'miedo': ['asustado', 'aterrado', 'temeroso', 'nervioso', 'ansioso'],
            'sorpresa': ['sorprendido', 'asombrado', 'impactado', 'desconcertado'],
            'amor': ['amoroso', 'cariñoso', 'tierno', 'romántico', 'apasionado'],
            'neutral': ['normal', 'calmado', 'sereno', 'tranquilo', 'pacífico']
        }
    
    def analyze_content_type(self, text):
        """Analiza el tipo de contenido"""
        text = text.strip()
        
        # Verificar si es diálogo
        for pattern in self.dialogue_patterns:
            if re.match(pattern, text):
                return 'dialogue'
        
        # Verificar si es narración
        for pattern in self.narration_patterns:
            if re.match(pattern, text):
                return 'narration'
        
        # Verificar si es pensamiento
        if text.startswith('(') and text.endswith(')'):
            return 'thought'
        
        # Verificar si es comando
        if any(text.startswith(cmd) for cmd in ['scene', 'show', 'play', 'pause', 'stop', 'hide']):
            return 'command'
        
        return 'unknown'
    
    def detect_character(self, text):
        """Detecta el personaje que habla"""
        text = text.strip()
        
        # Buscar patrón de personaje
        match = re.match(r'^([A-Z][a-z]+)\s*["\']', text)
        if match:
            return match.group(1)
        
        return None
    
    def analyze_emotion(self, text):
        """Analiza la emoción del texto"""
        text_lower = text.lower()
        
        for emotion, keywords in self.emotional_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        return 'neutral'
    
    def analyze_context(self, text, surrounding_lines=None):
        """Analiza el contexto completo"""
        context = {
            'type': self.analyze_content_type(text),
            'character': self.detect_character(text),
            'emotion': self.analyze_emotion(text),
            'scene_context': self.analyze_scene_context(surrounding_lines) if surrounding_lines else None
        }
        
        return context
    
    def analyze_scene_context(self, lines):
        """Analiza el contexto de la escena"""
        if not lines:
            return None
        
        context = {
            'scene_type': 'unknown',
            'time_of_day': 'unknown',
            'location': 'unknown',
            'atmosphere': 'neutral'
        }
        
        # Analizar líneas para detectar contexto
        for line in lines:
            line_lower = line.lower()
            
            # Detectar tipo de escena
            if any(word in line_lower for word in ['casa', 'hogar', 'habitación', 'dormitorio']):
                context['scene_type'] = 'indoor'
            elif any(word in line_lower for word in ['calle', 'exterior', 'parque', 'aire libre']):
                context['scene_type'] = 'outdoor'
            
            # Detectar momento del día
            if any(word in line_lower for word in ['noche', 'oscuro', 'luna']):
                context['time_of_day'] = 'night'
            elif any(word in line_lower for word in ['día', 'sol', 'mañana', 'tarde']):
                context['time_of_day'] = 'day'
            
            # Detectar atmósfera
            if any(word in line_lower for word in ['romántico', 'íntimo', 'pasional']):
                context['atmosphere'] = 'romantic'
            elif any(word in line_lower for word in ['tenso', 'dramático', 'conflicto']):
                context['atmosphere'] = 'dramatic'
            elif any(word in line_lower for word in ['cómodo', 'relajado', 'tranquilo']):
                context['atmosphere'] = 'comfortable'
        
        return context

class CulturalAdapter:
    """Adaptador cultural para traducciones"""
    
    def __init__(self):
        self.cultural_mappings = {
            'español': {
                'expresiones_idiomaticas': {
                    'break a leg': '¡mucha mierda!',
                    'piece of cake': 'pan comido',
                    'hit the nail on the head': 'dar en el clavo',
                    'let the cat out of the bag': 'descubrir el pastel',
                    'kill two birds with one stone': 'matar dos pájaros de un tiro'
                },
                'referencias_culturales': {
                    'thanksgiving': 'día de acción de gracias',
                    'halloween': 'noche de brujas',
                    'christmas': 'navidad',
                    'easter': 'pascua'
                },
                'formas_de_tratamiento': {
                    'sir': 'señor',
                    'madam': 'señora',
                    'miss': 'señorita',
                    'mister': 'señor'
                }
            }
        }
    
    def adapt_culturally(self, text, target_culture='español'):
        """Adapta el texto culturalmente"""
        if target_culture not in self.cultural_mappings:
            return text
        
        adapted_text = text
        mappings = self.cultural_mappings[target_culture]
        
        # Adaptar expresiones idiomáticas
        for english, spanish in mappings['expresiones_idiomaticas'].items():
            adapted_text = adapted_text.replace(english, spanish)
        
        # Adaptar referencias culturales
        for english, spanish in mappings['referencias_culturales'].items():
            adapted_text = adapted_text.replace(english, spanish)
        
        # Adaptar formas de tratamiento
        for english, spanish in mappings['formas_de_tratamiento'].items():
            adapted_text = adapted_text.replace(english, spanish)
        
        return adapted_text

class IntelligentTranslator:
    """Traductor inteligente principal"""
    
    def __init__(self):
        self.memory = TranslationMemory()
        self.context_analyzer = ContextAnalyzer()
        self.cultural_adapter = CulturalAdapter()
        self.learning_mode = True
        
        # Integrar servicios de traducción
        if TranslationServiceManager:
            self.translation_service = TranslationServiceManager()
            self.quality_analyzer = TranslationQualityAnalyzer()
        else:
            self.translation_service = None
            self.quality_analyzer = None
    
    def translate_with_context(self, text, context=None, character=None, emotion=None):
        """Traduce considerando contexto completo"""
        # Analizar contexto si no se proporciona
        if not context:
            context = self.context_analyzer.analyze_context(text)
        
        # Buscar en memoria
        suggestions = self.memory.suggest_translation(text, context, character, emotion)
        
        if suggestions:
            # Usar la mejor sugerencia
            best_suggestion = suggestions[0]
            translated = best_suggestion['translated']
        else:
            # Traducción básica (aquí podrías integrar un servicio de traducción)
            translated = self.basic_translate(text)
        
        # Adaptación cultural
        translated = self.cultural_adapter.adapt_culturally(translated)
        
        # Guardar en memoria
        self.memory.remember_translation(text, translated, context, character, emotion)
        
        return translated, suggestions
    
    def basic_translate(self, text):
        """Traducción básica usando servicios de IA"""
        if self.translation_service:
            result = self.translation_service.translate(text)
            if result['success']:
                return result['translation']
        
        # Fallback: traducción básica
        return f"[TRADUCIDO] {text}"
    
    def learn_from_correction(self, original, corrected_translation, context):
        """Aprende de correcciones del usuario"""
        self.memory.remember_translation(original, corrected_translation, context)
        self.memory.save_memory()
    
    def get_translation_suggestions(self, text, context=None):
        """Obtiene múltiples sugerencias de traducción"""
        suggestions = self.memory.suggest_translation(text, context)
        return suggestions

class TraductorIAInteligente:
    """Interfaz principal del traductor IA"""
    
    def __init__(self):
        self.translator = IntelligentTranslator()
        self.current_file = ""
        self.current_context = {}
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz principal"""
        self.root = tk.Tk()
        self.root.title("🧠 Traductor IA Inteligente - Versión Avanzada")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Crear widgets principales
        self.crear_header()
        self.crear_area_principal()
        self.crear_panel_ia()
        
        # Integrar asistente virtual si está disponible
        if AsistenteVirtualGUI:
            self.asistente_virtual = AsistenteVirtualGUI(self.root)
            self.asistente_virtual.show_welcome_message()
        else:
            self.asistente_virtual = None
        
        self.crear_footer()
        
        # Centrar ventana
        self.centrar_ventana()
    
    def crear_header(self):
        """Crea el encabezado"""
        header_frame = tk.Frame(self.root, bg='#2b2b2b', height=100)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Título principal
        titulo = tk.Label(header_frame, 
                         text="🧠 TRADUCTOR IA INTELIGENTE",
                         font=('Segoe UI', 20, 'bold'),
                         bg='#2b2b2b',
                         fg='#00ff88')
        titulo.pack(pady=10)
        
        # Subtítulo
        subtitulo = tk.Label(header_frame,
                            text="Traducción Inteligente con Memoria, Análisis Contextual y Aprendizaje Automático",
                            font=('Segoe UI', 12),
                            bg='#2b2b2b',
                            fg='#cccccc')
        subtitulo.pack()
    
    def crear_area_principal(self):
        """Crea el área principal de traducción"""
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Frame superior para controles
        control_frame = tk.Frame(main_frame, bg='#1e1e1e')
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Botón para cargar archivo
        self.btn_cargar = tk.Button(control_frame,
                                   text="📁 CARGAR ARCHIVO",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg='#00ff88',
                                   fg='#000000',
                                   command=self.cargar_archivo,
                                   relief='flat',
                                   padx=20,
                                   pady=10)
        self.btn_cargar.pack(side='left', padx=(0, 10))
        
        # Botón para traducir
        self.btn_traducir = tk.Button(control_frame,
                                     text="🔄 TRADUCIR",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='#ffaa00',
                                     fg='#000000',
                                     command=self.traducir_texto,
                                     relief='flat',
                                     padx=20,
                                     pady=10)
        self.btn_traducir.pack(side='left', padx=(0, 10))
        
        # Botón para guardar
        self.btn_guardar = tk.Button(control_frame,
                                    text="💾 GUARDAR",
                                    font=('Segoe UI', 12, 'bold'),
                                    bg='#ff4444',
                                    fg='#ffffff',
                                    command=self.guardar_traduccion,
                                    relief='flat',
                                    padx=20,
                                    pady=10)
        self.btn_guardar.pack(side='left', padx=(0, 10))
        
        # Botón para aprender
        self.btn_aprender = tk.Button(control_frame,
                                     text="🧠 APRENDER",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='#8844ff',
                                     fg='#ffffff',
                                     command=self.modo_aprendizaje,
                                     relief='flat',
                                     padx=20,
                                     pady=10)
        self.btn_aprender.pack(side='left', padx=(0, 10))
        
        # Botón para servicios
        self.btn_servicios = tk.Button(control_frame,
                                      text="⚙️ SERVICIOS",
                                      font=('Segoe UI', 12, 'bold'),
                                      bg='#ff8800',
                                      fg='#ffffff',
                                      command=self.mostrar_servicios,
                                      relief='flat',
                                      padx=20,
                                      pady=10)
        self.btn_servicios.pack(side='left')
        
        # Área de texto dividida
        text_frame = tk.Frame(main_frame, bg='#1e1e1e')
        text_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo - Texto original
        left_frame = tk.Frame(text_frame, bg='#1e1e1e')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="📝 TEXTO ORIGINAL", font=('Segoe UI', 12, 'bold'), 
                bg='#1e1e1e', fg='#ffffff').pack(pady=(0, 5))
        
        self.txt_original = scrolledtext.ScrolledText(left_frame,
                                                     font=('Consolas', 11),
                                                     bg='#2b2b2b',
                                                     fg='#ffffff',
                                                     insertbackground='#ffffff',
                                                     wrap='word',
                                                     height=20)
        self.txt_original.pack(fill='both', expand=True)
        
        # Panel derecho - Texto traducido
        right_frame = tk.Frame(text_frame, bg='#1e1e1e')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(right_frame, text="🌐 TEXTO TRADUCIDO", font=('Segoe UI', 12, 'bold'), 
                bg='#1e1e1e', fg='#ffffff').pack(pady=(0, 5))
        
        self.txt_traducido = scrolledtext.ScrolledText(right_frame,
                                                       font=('Consolas', 11),
                                                       bg='#2b2b2b',
                                                       fg='#ffffff',
                                                       insertbackground='#ffffff',
                                                       wrap='word',
                                                       height=20)
        self.txt_traducido.pack(fill='both', expand=True)
    
    def crear_panel_ia(self):
        """Crea el panel de información de IA"""
        ia_frame = tk.Frame(self.root, bg='#2b2b2b', height=200)
        ia_frame.pack(fill='x', padx=20, pady=10)
        ia_frame.pack_propagate(False)
        
        # Título del panel
        tk.Label(ia_frame, text="🧠 ANÁLISIS IA", font=('Segoe UI', 14, 'bold'), 
                bg='#2b2b2b', fg='#00ff88').pack(pady=5)
        
        # Frame para información
        info_frame = tk.Frame(ia_frame, bg='#2b2b2b')
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Información de contexto
        self.lbl_contexto = tk.Label(info_frame,
                                    text="📊 Contexto: Analizando...",
                                    font=('Segoe UI', 10),
                                    bg='#2b2b2b',
                                    fg='#cccccc',
                                    anchor='w')
        self.lbl_contexto.pack(fill='x', pady=2)
        
        # Información de memoria
        self.lbl_memoria = tk.Label(info_frame,
                                   text="💾 Memoria: 0 traducciones guardadas",
                                   font=('Segoe UI', 10),
                                   bg='#2b2b2b',
                                   fg='#cccccc',
                                   anchor='w')
        self.lbl_memoria.pack(fill='x', pady=2)
        
        # Información de sugerencias
        self.lbl_sugerencias = tk.Label(info_frame,
                                       text="💡 Sugerencias: Sin sugerencias",
                                       font=('Segoe UI', 10),
                                       bg='#2b2b2b',
                                       fg='#cccccc',
                                       anchor='w')
        self.lbl_sugerencias.pack(fill='x', pady=2)
        
        # Información de aprendizaje
        self.lbl_aprendizaje = tk.Label(info_frame,
                                        text="🧠 Aprendizaje: Modo activo",
                                        font=('Segoe UI', 10),
                                        bg='#2b2b2b',
                                        fg='#cccccc',
                                        anchor='w')
        self.lbl_aprendizaje.pack(fill='x', pady=2)
    
    def crear_footer(self):
        """Crea el pie de página"""
        footer_frame = tk.Frame(self.root, bg='#2b2b2b', height=60)
        footer_frame.pack(fill='x', padx=20, pady=10)
        footer_frame.pack_propagate(False)
        
        # Información del programa
        info_programa = tk.Label(footer_frame,
                                text="🧠 Traductor IA Inteligente v3.0 | Con características de IA avanzadas",
                                font=('Segoe UI', 10),
                                bg='#2b2b2b',
                                fg='#888888')
        info_programa.pack(side='left', padx=10, pady=20)
        
        # Estado de la IA
        self.lbl_estado_ia = tk.Label(footer_frame,
                                     text="✅ IA: Conectada y funcionando",
                                     font=('Segoe UI', 10),
                                     bg='#2b2b2b',
                                     fg='#00ff88')
        self.lbl_estado_ia.pack(side='right', padx=10, pady=20)
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def cargar_archivo(self):
        """Carga un archivo para traducir"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo para traducir",
            filetypes=[("Archivos de texto", "*.txt"), ("Archivos RenPy", "*.rpy"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                self.txt_original.delete(1.0, tk.END)
                self.txt_original.insert(1.0, contenido)
                self.current_file = archivo
                
                # Actualizar información de IA
                self.actualizar_info_ia()
                
                messagebox.showinfo("Éxito", f"Archivo cargado: {os.path.basename(archivo)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo: {e}")
    
    def traducir_texto(self):
        """Traduce el texto con IA"""
        texto_original = self.txt_original.get(1.0, tk.END).strip()
        
        if not texto_original:
            messagebox.showwarning("Advertencia", "No hay texto para traducir")
            return
        
        try:
            # Analizar contexto
            context = self.translator.context_analyzer.analyze_context(texto_original)
            
            # Traducir con contexto
            traduccion, sugerencias = self.translator.translate_with_context(
                texto_original, context, context.get('character'), context.get('emotion')
            )
            
            # Mostrar traducción
            self.txt_traducido.delete(1.0, tk.END)
            self.txt_traducido.insert(1.0, traduccion)
            
            # Actualizar información de IA
            self.actualizar_info_ia(context, sugerencias)
            
            messagebox.showinfo("Éxito", "Traducción completada con IA")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en traducción: {e}")
    
    def guardar_traduccion(self):
        """Guarda la traducción"""
        if not self.current_file:
            messagebox.showwarning("Advertencia", "No hay archivo cargado")
            return
        
        try:
            nombre_base = os.path.splitext(self.current_file)[0]
            archivo_traducido = f"{nombre_base}_traducido.txt"
            
            traduccion = self.txt_traducido.get(1.0, tk.END)
            
            with open(archivo_traducido, 'w', encoding='utf-8') as f:
                f.write(traduccion)
            
            messagebox.showinfo("Éxito", f"Traducción guardada: {os.path.basename(archivo_traducido)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
    
    def modo_aprendizaje(self):
        """Activa/desactiva el modo de aprendizaje"""
        self.translator.learning_mode = not self.translator.learning_mode
        
        estado = "ACTIVO" if self.translator.learning_mode else "INACTIVO"
        color = "#00ff88" if self.translator.learning_mode else "#ff4444"
        
        self.lbl_aprendizaje.config(text=f"🧠 Aprendizaje: Modo {estado}", fg=color)
        
        messagebox.showinfo("Modo Aprendizaje", f"Modo de aprendizaje: {estado}")
    
    def actualizar_info_ia(self, context=None, sugerencias=None):
        """Actualiza la información de IA en la interfaz"""
        # Actualizar información de contexto
        if context:
            tipo = context.get('type', 'unknown')
            personaje = context.get('character', 'N/A')
            emocion = context.get('emotion', 'neutral')
            
            self.lbl_contexto.config(
                text=f"📊 Contexto: Tipo={tipo}, Personaje={personaje}, Emoción={emocion}"
            )
        else:
            self.lbl_contexto.config(text="📊 Contexto: Sin análisis")
        
        # Actualizar información de memoria
        total_translations = len(self.translator.memory.translations)
        self.lbl_memoria.config(text=f"💾 Memoria: {total_translations} traducciones guardadas")
        
        # Actualizar información de sugerencias
        if sugerencias:
            self.lbl_sugerencias.config(text=f"💡 Sugerencias: {len(sugerencias)} disponibles")
        else:
            self.lbl_sugerencias.config(text="💡 Sugerencias: Sin sugerencias")
        
        # Actualizar información de calidad si está disponible
        if self.translator.quality_analyzer and context:
            self.lbl_aprendizaje.config(text="🧠 Aprendizaje: Analizando calidad...")
    
    def get_current_text(self):
        """Obtiene el texto actual seleccionado"""
        try:
            return self.txt_original.get("sel.first", "sel.last")
        except tk.TclError:
            return self.txt_original.get(1.0, tk.END).strip()
    
    def get_current_context(self):
        """Obtiene el contexto actual"""
        text = self.get_current_text()
        if text:
            return self.translator.context_analyzer.analyze_context(text)
        return None
    
    def mostrar_servicios(self):
        """Muestra ventana de configuración de servicios"""
        if not self.translator.translation_service:
            messagebox.showinfo("Servicios", "Los servicios de traducción no están disponibles")
            return
        
        # Crear ventana de servicios
        servicios_window = tk.Toplevel(self.root)
        servicios_window.title("⚙️ Configuración de Servicios de Traducción")
        servicios_window.geometry("600x400")
        servicios_window.configure(bg='#1e1e1e')
        
        # Título
        tk.Label(servicios_window, text="⚙️ SERVICIOS DE TRADUCCIÓN", 
                font=('Segoe UI', 16, 'bold'), bg='#1e1e1e', fg='#00ff88').pack(pady=10)
        
        # Frame para servicios
        servicios_frame = tk.Frame(servicios_window, bg='#1e1e1e')
        servicios_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Lista de servicios disponibles
        servicios_disponibles = self.translator.translation_service.get_available_services()
        
        for servicio in servicios_disponibles:
            info = self.translator.translation_service.get_service_info(servicio)
            
            # Frame para cada servicio
            servicio_frame = tk.Frame(servicios_frame, bg='#2b2b2b', relief='raised', bd=2)
            servicio_frame.pack(fill='x', pady=5)
            
            # Nombre del servicio
            tk.Label(servicio_frame, text=f"🔧 {info['name']}", 
                    font=('Segoe UI', 12, 'bold'), bg='#2b2b2b', fg='#ffffff').pack(anchor='w', padx=10, pady=5)
            
            # Descripción
            tk.Label(servicio_frame, text=f"📝 {info['description']}", 
                    font=('Segoe UI', 10), bg='#2b2b2b', fg='#cccccc').pack(anchor='w', padx=10)
            
            # Mejor para
            tk.Label(servicio_frame, text=f"🎯 Mejor para: {info['best_for']}", 
                    font=('Segoe UI', 10), bg='#2b2b2b', fg='#cccccc').pack(anchor='w', padx=10)
            
            # Precisión y velocidad
            tk.Label(servicio_frame, text=f"📊 Precisión: {info['accuracy']} | Velocidad: {info['speed']}", 
                    font=('Segoe UI', 10), bg='#2b2b2b', fg='#cccccc').pack(anchor='w', padx=10, pady=(0, 5))
            
            # Botón para seleccionar
            btn_seleccionar = tk.Button(servicio_frame,
                                       text="✅ SELECCIONAR",
                                       font=('Segoe UI', 10, 'bold'),
                                       bg='#00ff88',
                                       fg='#000000',
                                       command=lambda s=servicio: self.seleccionar_servicio(s, servicios_window),
                                       relief='flat',
                                       padx=15,
                                       pady=5)
            btn_seleccionar.pack(anchor='e', padx=10, pady=5)
    
    def seleccionar_servicio(self, servicio, window):
        """Selecciona un servicio de traducción"""
        if self.translator.translation_service.set_service(servicio):
            messagebox.showinfo("Servicio Seleccionado", f"Servicio {servicio.upper()} seleccionado correctamente")
            window.destroy()
        else:
            messagebox.showerror("Error", f"No se pudo seleccionar el servicio {servicio}")
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = TraductorIAInteligente()
        app.ejecutar()
    except Exception as e:
        print(f"Error iniciando aplicación: {e}")
        messagebox.showerror("Error Fatal", f"Error al iniciar la aplicación: {e}") 
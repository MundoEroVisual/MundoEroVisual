#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asistente Virtual Inteligente - Ayuda contextual y sugerencias
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

class AsistenteVirtual:
    """Asistente virtual inteligente para traducción"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.translation_tips = self.load_translation_tips()
        self.context_help = self.load_context_help()
        self.load_preferences()
    
    def load_translation_tips(self) -> Dict:
        """Carga consejos de traducción"""
        return {
            'dialogue': [
                "💡 Mantén el tono natural del diálogo",
                "💡 Preserva las emociones del personaje",
                "💡 Adapta las expresiones coloquiales",
                "💡 Considera el contexto de la conversación"
            ],
            'narration': [
                "💡 Mantén la fluidez narrativa",
                "💡 Preserva el estilo del autor",
                "💡 Adapta las descripciones culturalmente",
                "💡 Mantén la coherencia temporal"
            ],
            'thought': [
                "💡 Usa el estilo indirecto apropiado",
                "💡 Mantén la voz interior del personaje",
                "💡 Preserva la intimidad del pensamiento",
                "💡 Adapta las reflexiones culturalmente"
            ],
            'command': [
                "💡 Mantén la sintaxis de RenPy",
                "💡 No traduzcas comandos técnicos",
                "💡 Preserva los nombres de archivos",
                "💡 Mantén la estructura del código"
            ]
        }
    
    def load_context_help(self) -> Dict:
        """Carga ayuda contextual"""
        return {
            'romantic': [
                "💕 Contexto romántico detectado",
                "💕 Usa lenguaje más íntimo y cariñoso",
                "💕 Adapta las expresiones de amor culturalmente",
                "💕 Mantén la pasión y el romanticismo"
            ],
            'dramatic': [
                "🎭 Contexto dramático detectado",
                "🎭 Usa lenguaje más intenso y emocional",
                "🎭 Preserva la tensión dramática",
                "🎭 Mantén el impacto emocional"
            ],
            'comfortable': [
                "😌 Contexto cómodo detectado",
                "😌 Usa lenguaje relajado y natural",
                "😌 Mantén la atmósfera tranquila",
                "😌 Preserva la sensación de confort"
            ],
            'formal': [
                "👔 Contexto formal detectado",
                "👔 Usa lenguaje más respetuoso y profesional",
                "👔 Mantén la formalidad apropiada",
                "👔 Adapta las formas de tratamiento"
            ]
        }
    
    def load_preferences(self):
        """Carga preferencias del usuario"""
        try:
            with open('user_preferences.json', 'r', encoding='utf-8') as f:
                self.user_preferences = json.load(f)
        except:
            self.user_preferences = {
                'translation_style': 'natural',
                'formality_level': 'medium',
                'cultural_adaptation': True,
                'show_tips': True,
                'auto_suggest': True
            }
    
    def save_preferences(self):
        """Guarda preferencias del usuario"""
        try:
            with open('user_preferences.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando preferencias: {e}")
    
    def analyze_text_for_help(self, text: str, context: Dict = None) -> List[str]:
        """Analiza el texto y genera ayuda contextual"""
        help_suggestions = []
        
        # Analizar tipo de contenido
        content_type = context.get('type', 'unknown') if context else 'unknown'
        
        # Agregar consejos específicos del tipo de contenido
        if content_type in self.translation_tips:
            help_suggestions.extend(self.translation_tips[content_type])
        
        # Analizar contexto emocional
        emotion = context.get('emotion', 'neutral') if context else 'neutral'
        if emotion != 'neutral':
            help_suggestions.append(f"😊 Emoción detectada: {emotion}")
        
        # Analizar contexto de escena
        scene_context = context.get('scene_context', {}) if context else {}
        if scene_context:
            atmosphere = scene_context.get('atmosphere', 'neutral')
            if atmosphere in self.context_help:
                help_suggestions.extend(self.context_help[atmosphere])
        
        # Análisis específico del texto
        text_analysis = self.analyze_text_specifics(text)
        help_suggestions.extend(text_analysis)
        
        return help_suggestions
    
    def analyze_text_specifics(self, text: str) -> List[str]:
        """Analiza aspectos específicos del texto"""
        suggestions = []
        
        # Detectar expresiones idiomáticas
        idioms = self.detect_idioms(text)
        if idioms:
            suggestions.append(f"🔤 Expresiones idiomáticas detectadas: {', '.join(idioms)}")
        
        # Detectar términos técnicos
        technical_terms = self.detect_technical_terms(text)
        if technical_terms:
            suggestions.append(f"⚙️ Términos técnicos: {', '.join(technical_terms)}")
        
        # Detectar nombres propios
        proper_nouns = self.detect_proper_nouns(text)
        if proper_nouns:
            suggestions.append(f"📛 Nombres propios: {', '.join(proper_nouns)}")
        
        # Detectar referencias culturales
        cultural_refs = self.detect_cultural_references(text)
        if cultural_refs:
            suggestions.append(f"🌍 Referencias culturales: {', '.join(cultural_refs)}")
        
        return suggestions
    
    def detect_idioms(self, text: str) -> List[str]:
        """Detecta expresiones idiomáticas"""
        idioms = [
            'break a leg', 'piece of cake', 'hit the nail on the head',
            'let the cat out of the bag', 'kill two birds with one stone',
            'pull someone\'s leg', 'get out of hand', 'hit the sack',
            'on the ball', 'under the weather'
        ]
        
        found_idioms = []
        text_lower = text.lower()
        
        for idiom in idioms:
            if idiom in text_lower:
                found_idioms.append(idiom)
        
        return found_idioms
    
    def detect_technical_terms(self, text: str) -> List[str]:
        """Detecta términos técnicos"""
        technical_terms = [
            'scene', 'show', 'hide', 'play', 'stop', 'pause',
            'with', 'at', 'truecenter', 'dissolve', 'fade',
            'character', 'define', 'label', 'jump', 'return'
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in technical_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def detect_proper_nouns(self, text: str) -> List[str]:
        """Detecta nombres propios"""
        # Patrón básico para nombres propios (mayúscula seguida de minúsculas)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Filtrar palabras comunes
        common_words = ['The', 'And', 'But', 'For', 'With', 'From', 'This', 'That']
        filtered_nouns = [noun for noun in proper_nouns if noun not in common_words]
        
        return filtered_nouns[:5]  # Limitar a 5 resultados
    
    def detect_cultural_references(self, text: str) -> List[str]:
        """Detecta referencias culturales"""
        cultural_refs = [
            'thanksgiving', 'halloween', 'christmas', 'easter',
            'valentine\'s day', 'new year', 'birthday',
            'sir', 'madam', 'miss', 'mister'
        ]
        
        found_refs = []
        text_lower = text.lower()
        
        for ref in cultural_refs:
            if ref in text_lower:
                found_refs.append(ref)
        
        return found_refs
    
    def get_translation_suggestions(self, text: str, context: Dict = None) -> List[str]:
        """Genera sugerencias de traducción"""
        suggestions = []
        
        # Sugerencias basadas en el tipo de contenido
        content_type = context.get('type', 'unknown') if context else 'unknown'
        
        if content_type == 'dialogue':
            suggestions.extend([
                "💬 Considera el tono de voz del personaje",
                "💬 Adapta las expresiones coloquiales",
                "💬 Mantén la naturalidad del diálogo"
            ])
        elif content_type == 'narration':
            suggestions.extend([
                "📖 Mantén el estilo narrativo",
                "📖 Preserva la atmósfera descrita",
                "📖 Adapta las descripciones culturalmente"
            ])
        elif content_type == 'thought':
            suggestions.extend([
                "💭 Usa el estilo indirecto apropiado",
                "💭 Mantén la intimidad del pensamiento",
                "💭 Preserva la voz interior"
            ])
        
        # Sugerencias basadas en emociones
        emotion = context.get('emotion', 'neutral') if context else 'neutral'
        if emotion != 'neutral':
            suggestions.append(f"😊 Adapta el lenguaje para expresar {emotion}")
        
        return suggestions
    
    def provide_contextual_help(self, text: str, context: Dict = None) -> Dict:
        """Proporciona ayuda contextual completa"""
        help_data = {
            'tips': self.analyze_text_for_help(text, context),
            'suggestions': self.get_translation_suggestions(text, context),
            'context_info': self.get_context_info(context),
            'quality_tips': self.get_quality_tips(text, context)
        }
        
        return help_data
    
    def get_context_info(self, context: Dict = None) -> Dict:
        """Obtiene información del contexto"""
        if not context:
            return {'message': 'Sin contexto disponible'}
        
        info = {
            'content_type': context.get('type', 'unknown'),
            'character': context.get('character', 'N/A'),
            'emotion': context.get('emotion', 'neutral'),
            'scene_context': context.get('scene_context', {})
        }
        
        return info
    
    def get_quality_tips(self, text: str, context: Dict = None) -> List[str]:
        """Obtiene consejos de calidad"""
        tips = []
        
        # Consejos generales de calidad
        tips.append("✨ Revisa la fluidez natural del texto")
        tips.append("✨ Verifica que mantenga el significado original")
        tips.append("✨ Asegúrate de que sea culturalmente apropiado")
        tips.append("✨ Confirma que preserve el tono y estilo")
        
        # Consejos específicos según el contexto
        if context and context.get('type') == 'dialogue':
            tips.append("💬 Verifica que suene natural en español")
        
        if context and context.get('type') == 'command':
            tips.append("⚙️ No traduzcas comandos técnicos de RenPy")
        
        return tips
    
    def log_interaction(self, user_input: str, response: str, context: Dict = None):
        """Registra interacción con el usuario"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': response,
            'context': context
        }
        
        self.conversation_history.append(interaction)
        
        # Mantener solo las últimas 100 interacciones
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def get_conversation_summary(self) -> Dict:
        """Obtiene resumen de la conversación"""
        if not self.conversation_history:
            return {'message': 'Sin historial de conversación'}
        
        total_interactions = len(self.conversation_history)
        recent_interactions = len([i for i in self.conversation_history 
                                if (datetime.now() - datetime.fromisoformat(i['timestamp'])).days < 1])
        
        return {
            'total_interactions': total_interactions,
            'recent_interactions': recent_interactions,
            'last_interaction': self.conversation_history[-1]['timestamp'] if self.conversation_history else None
        }

class AsistenteVirtualGUI:
    """Interfaz gráfica del asistente virtual"""
    
    def __init__(self, parent):
        self.parent = parent
        self.assistant = AsistenteVirtual()
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets del asistente"""
        # Frame principal del asistente
        self.frame = tk.Frame(self.parent, bg='#2b2b2b', relief='raised', bd=2)
        self.frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Título del asistente
        title_label = tk.Label(self.frame, 
                              text="🤖 ASISTENTE VIRTUAL IA",
                              font=('Segoe UI', 14, 'bold'),
                              bg='#2b2b2b',
                              fg='#00ff88')
        title_label.pack(pady=5)
        
        # Área de texto para el asistente
        self.assistant_text = tk.Text(self.frame,
                                     height=8,
                                     font=('Segoe UI', 10),
                                     bg='#1e1e1e',
                                     fg='#ffffff',
                                     wrap='word',
                                     state='disabled')
        self.assistant_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame para botones
        button_frame = tk.Frame(self.frame, bg='#2b2b2b')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        # Botón para ayuda contextual
        self.btn_help = tk.Button(button_frame,
                                 text="💡 AYUDA CONTEXTUAL",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg='#8844ff',
                                 fg='#ffffff',
                                 command=self.show_contextual_help,
                                 relief='flat',
                                 padx=15,
                                 pady=5)
        self.btn_help.pack(side='left', padx=(0, 5))
        
        # Botón para consejos
        self.btn_tips = tk.Button(button_frame,
                                 text="✨ CONSEJOS",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg='#ffaa00',
                                 fg='#000000',
                                 command=self.show_tips,
                                 relief='flat',
                                 padx=15,
                                 pady=5)
        self.btn_tips.pack(side='left', padx=(0, 5))
        
        # Botón para sugerencias
        self.btn_suggestions = tk.Button(button_frame,
                                        text="💭 SUGERENCIAS",
                                        font=('Segoe UI', 10, 'bold'),
                                        bg='#00ff88',
                                        fg='#000000',
                                        command=self.show_suggestions,
                                        relief='flat',
                                        padx=15,
                                        pady=5)
        self.btn_suggestions.pack(side='left')
    
    def update_assistant_text(self, text: str):
        """Actualiza el texto del asistente"""
        self.assistant_text.config(state='normal')
        self.assistant_text.delete(1.0, tk.END)
        self.assistant_text.insert(1.0, text)
        self.assistant_text.config(state='disabled')
        self.assistant_text.see(tk.END)
    
    def show_contextual_help(self):
        """Muestra ayuda contextual"""
        # Obtener texto actual del traductor
        current_text = self.parent.get_current_text()
        current_context = self.parent.get_current_context()
        
        if not current_text:
            self.update_assistant_text("🤖 No hay texto seleccionado para analizar.\n\nPor favor, selecciona un texto para obtener ayuda contextual.")
            return
        
        # Obtener ayuda contextual
        help_data = self.assistant.provide_contextual_help(current_text, current_context)
        
        # Formatear respuesta
        response = "🤖 ANÁLISIS CONTEXTUAL:\n\n"
        
        if help_data['tips']:
            response += "💡 CONSEJOS:\n"
            for tip in help_data['tips']:
                response += f"  • {tip}\n"
            response += "\n"
        
        if help_data['suggestions']:
            response += "💭 SUGERENCIAS:\n"
            for suggestion in help_data['suggestions']:
                response += f"  • {suggestion}\n"
            response += "\n"
        
        if help_data['quality_tips']:
            response += "✨ CONSEJOS DE CALIDAD:\n"
            for tip in help_data['quality_tips']:
                response += f"  • {tip}\n"
        
        self.update_assistant_text(response)
        
        # Registrar interacción
        self.assistant.log_interaction("Ayuda contextual solicitada", response, current_context)
    
    def show_tips(self):
        """Muestra consejos generales"""
        tips = [
            "💡 CONSEJOS GENERALES DE TRADUCCIÓN:",
            "",
            "🎯 MANTÉN LA NATURALIDAD:",
            "  • El texto debe sonar natural en español",
            "  • Evita traducciones literales",
            "  • Adapta las expresiones culturalmente",
            "",
            "🎭 PRESERVA EL TONO:",
            "  • Mantén las emociones del original",
            "  • Conserva el estilo del autor",
            "  • Adapta el registro apropiado",
            "",
            "🌍 ADAPTACIÓN CULTURAL:",
            "  • Considera las diferencias culturales",
            "  • Adapta referencias específicas",
            "  • Mantén la coherencia cultural",
            "",
            "✨ CALIDAD:",
            "  • Revisa la fluidez del texto",
            "  • Verifica la precisión del significado",
            "  • Asegúrate de que sea apropiado"
        ]
        
        response = "\n".join(tips)
        self.update_assistant_text(response)
        
        # Registrar interacción
        self.assistant.log_interaction("Consejos solicitados", response)
    
    def show_suggestions(self):
        """Muestra sugerencias de traducción"""
        current_text = self.parent.get_current_text()
        current_context = self.parent.get_current_context()
        
        if not current_text:
            self.update_assistant_text("🤖 No hay texto seleccionado para sugerencias.\n\nPor favor, selecciona un texto para obtener sugerencias de traducción.")
            return
        
        # Obtener sugerencias
        suggestions = self.assistant.get_translation_suggestions(current_text, current_context)
        
        response = "🤖 SUGERENCIAS DE TRADUCCIÓN:\n\n"
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                response += f"{i}. {suggestion}\n"
        else:
            response += "No hay sugerencias específicas para este texto.\n"
            response += "Considera usar las herramientas de análisis contextual."
        
        self.update_assistant_text(response)
        
        # Registrar interacción
        self.assistant.log_interaction("Sugerencias solicitadas", response, current_context)
    
    def show_welcome_message(self):
        """Muestra mensaje de bienvenida"""
        welcome = """🤖 ¡Hola! Soy tu Asistente Virtual IA.

Estoy aquí para ayudarte con tus traducciones:

💡 AYUDA CONTEXTUAL - Analiza el texto y proporciona consejos específicos
✨ CONSEJOS - Muestra consejos generales de traducción  
💭 SUGERENCIAS - Ofrece sugerencias para mejorar la traducción

¡Selecciona un texto y usa los botones para obtener ayuda!"""
        
        self.update_assistant_text(welcome) 
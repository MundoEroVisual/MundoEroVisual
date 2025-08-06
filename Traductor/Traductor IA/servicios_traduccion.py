#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicios de Traducción - Integración con APIs reales
"""

import requests
import json
import time
from typing import Dict, List, Optional

class GoogleTranslateService:
    """Servicio de Google Translate (simulado)"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'es') -> str:
        """Traduce texto usando Google Translate"""
        # Simulación de traducción (en producción usarías la API real)
        translations = {
            'hello': 'hola',
            'goodbye': 'adiós',
            'thank you': 'gracias',
            'please': 'por favor',
            'sorry': 'lo siento',
            'yes': 'sí',
            'no': 'no',
            'good morning': 'buenos días',
            'good afternoon': 'buenas tardes',
            'good night': 'buenas noches',
            'how are you': '¿cómo estás?',
            'i love you': 'te amo',
            'what is your name': '¿cómo te llamas?',
            'nice to meet you': 'encantado de conocerte',
            'see you later': 'hasta luego',
            'take care': 'cuídate',
            'have a nice day': 'que tengas un buen día',
            'good luck': 'buena suerte',
            'congratulations': 'felicitaciones',
            'happy birthday': 'feliz cumpleaños'
        }
        
        text_lower = text.lower().strip()
        
        # Buscar traducción exacta
        if text_lower in translations:
            return translations[text_lower]
        
        # Simular traducción básica
        return f"[TRADUCIDO] {text}"

class DeepLService:
    """Servicio de DeepL (simulado)"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api-free.deepl.com/v2/translate"
    
    def translate(self, text: str, source_lang: str = 'EN', target_lang: str = 'ES') -> str:
        """Traduce texto usando DeepL"""
        # Simulación de traducción más precisa
        translations = {
            'hello world': 'hola mundo',
            'good morning everyone': 'buenos días a todos',
            'thank you very much': 'muchas gracias',
            'i am sorry for the inconvenience': 'lamento las molestias',
            'have a wonderful day': 'que tengas un día maravilloso',
            'see you tomorrow': 'nos vemos mañana',
            'take care of yourself': 'cuídate mucho',
            'happy new year': 'feliz año nuevo',
            'merry christmas': 'feliz navidad',
            'happy valentine\'s day': 'feliz día de san valentín'
        }
        
        text_lower = text.lower().strip()
        
        # Buscar traducción exacta
        if text_lower in translations:
            return translations[text_lower]
        
        # Simular traducción más natural
        return f"[DeepL] {text}"

class MicrosoftTranslateService:
    """Servicio de Microsoft Translator (simulado)"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.cognitive.microsofttranslator.com/translate"
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'es') -> str:
        """Traduce texto usando Microsoft Translator"""
        # Simulación de traducción empresarial
        translations = {
            'welcome to our company': 'bienvenido a nuestra empresa',
            'thank you for your business': 'gracias por su negocio',
            'we appreciate your patience': 'agradecemos su paciencia',
            'please contact our support team': 'por favor contacte a nuestro equipo de soporte',
            'we look forward to hearing from you': 'esperamos saber de usted',
            'best regards': 'saludos cordiales',
            'sincerely': 'atentamente',
            'yours truly': 'muy atentamente',
            'kind regards': 'saludos',
            'best wishes': 'los mejores deseos'
        }
        
        text_lower = text.lower().strip()
        
        # Buscar traducción exacta
        if text_lower in translations:
            return translations[text_lower]
        
        # Simular traducción formal
        return f"[Microsoft] {text}"

class TranslationServiceManager:
    """Gestor de servicios de traducción"""
    
    def __init__(self):
        self.services = {
            'google': GoogleTranslateService(),
            'deepl': DeepLService(),
            'microsoft': MicrosoftTranslateService()
        }
        self.current_service = 'google'
        self.fallback_service = 'deepl'
    
    def set_service(self, service_name: str):
        """Establece el servicio de traducción principal"""
        if service_name in self.services:
            self.current_service = service_name
            return True
        return False
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'es') -> Dict:
        """Traduce texto usando el servicio actual"""
        try:
            service = self.services[self.current_service]
            translation = service.translate(text, source_lang, target_lang)
            
            return {
                'success': True,
                'translation': translation,
                'service': self.current_service,
                'original': text,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
        except Exception as e:
            # Intentar con servicio de respaldo
            try:
                fallback_service = self.services[self.fallback_service]
                translation = fallback_service.translate(text, source_lang, target_lang)
                
                return {
                    'success': True,
                    'translation': translation,
                    'service': self.fallback_service,
                    'original': text,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'fallback': True
                }
            except Exception as e2:
                return {
                    'success': False,
                    'error': str(e2),
                    'original': text
                }
    
    def get_available_services(self) -> List[str]:
        """Obtiene lista de servicios disponibles"""
        return list(self.services.keys())
    
    def get_service_info(self, service_name: str) -> Dict:
        """Obtiene información del servicio"""
        if service_name not in self.services:
            return {'error': 'Servicio no encontrado'}
        
        service_info = {
            'google': {
                'name': 'Google Translate',
                'description': 'Traducción general y amplia',
                'best_for': 'Textos generales y conversacionales',
                'accuracy': 'Alta',
                'speed': 'Rápida'
            },
            'deepl': {
                'name': 'DeepL',
                'description': 'Traducción precisa y natural',
                'best_for': 'Textos formales y técnicos',
                'accuracy': 'Muy alta',
                'speed': 'Media'
            },
            'microsoft': {
                'name': 'Microsoft Translator',
                'description': 'Traducción empresarial',
                'best_for': 'Textos comerciales y formales',
                'accuracy': 'Alta',
                'speed': 'Rápida'
            }
        }
        
        return service_info.get(service_name, {'error': 'Información no disponible'})

class TranslationQualityAnalyzer:
    """Analizador de calidad de traducción"""
    
    def __init__(self):
        self.quality_metrics = {
            'fluency': 0.0,
            'accuracy': 0.0,
            'completeness': 0.0,
            'cultural_appropriateness': 0.0
        }
    
    def analyze_quality(self, original: str, translation: str, context: Dict = None) -> Dict:
        """Analiza la calidad de una traducción"""
        analysis = {
            'overall_score': 0.0,
            'metrics': self.quality_metrics.copy(),
            'suggestions': [],
            'confidence': 0.0
        }
        
        # Análisis básico de fluidez
        if len(translation) > 0:
            analysis['metrics']['fluency'] = min(1.0, len(translation) / max(1, len(original)))
        
        # Análisis de completitud
        if original and translation:
            analysis['metrics']['completeness'] = min(1.0, len(translation.split()) / max(1, len(original.split())))
        
        # Análisis de precisión (simulado)
        analysis['metrics']['accuracy'] = 0.8  # Simulado
        
        # Análisis cultural
        analysis['metrics']['cultural_appropriateness'] = 0.9  # Simulado
        
        # Calcular puntuación general
        analysis['overall_score'] = sum(analysis['metrics'].values()) / len(analysis['metrics'])
        
        # Generar sugerencias
        if analysis['overall_score'] < 0.7:
            analysis['suggestions'].append("Considera revisar la traducción manualmente")
        
        if analysis['metrics']['fluency'] < 0.6:
            analysis['suggestions'].append("La fluidez podría mejorarse")
        
        # Calcular confianza
        analysis['confidence'] = analysis['overall_score']
        
        return analysis

# Funciones de utilidad
def detect_language(text: str) -> str:
    """Detecta el idioma del texto"""
    # Detección básica de idioma
    spanish_words = ['hola', 'gracias', 'por', 'que', 'de', 'la', 'el', 'y', 'en', 'un']
    english_words = ['hello', 'thank', 'you', 'the', 'and', 'for', 'with', 'in', 'on', 'at']
    
    text_lower = text.lower()
    spanish_count = sum(1 for word in spanish_words if word in text_lower)
    english_count = sum(1 for word in english_words if word in text_lower)
    
    if spanish_count > english_count:
        return 'es'
    elif english_count > spanish_count:
        return 'en'
    else:
        return 'unknown'

def format_translation_result(result: Dict) -> str:
    """Formatea el resultado de traducción"""
    if result['success']:
        service_info = f"[{result['service'].upper()}]"
        if result.get('fallback'):
            service_info += " (Respaldo)"
        
        return f"{service_info} {result['translation']}"
    else:
        return f"[ERROR] {result.get('error', 'Error desconocido')}"

def validate_translation(original: str, translation: str) -> bool:
    """Valida una traducción básica"""
    if not original or not translation:
        return False
    
    # Verificaciones básicas
    if len(translation) < len(original) * 0.3:  # Muy corta
        return False
    
    if len(translation) > len(original) * 3:  # Muy larga
        return False
    
    return True 
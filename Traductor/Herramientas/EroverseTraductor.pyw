import sys
import os
import re
import requests
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QMessageBox, QComboBox, QGroupBox, QFrame,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
import random
import string


class ExtractorThread(QThread):
    progreso = pyqtSignal(int)
    log = pyqtSignal(str)
    terminado = pyqtSignal(bool, str)

    def __init__(self, carpeta_entrada, directorio_salida, tipo_archivo):
        super().__init__()
        self.carpeta_entrada = carpeta_entrada
        self.directorio_salida = directorio_salida
        self.tipo_archivo = tipo_archivo

    def extraer_rpa(self, archivo):
        try:
            unrpa_path = os.path.join(os.path.dirname(__file__), "unrpa-2.3.0", "unrpa")
            if os.path.exists(unrpa_path):
                cmd = [sys.executable, "-m", "unrpa", "-mp", self.directorio_salida, archivo]
            else:
                cmd = ["unrpa", "-mp", self.directorio_salida, archivo]
            
            self.log.emit(f"🔧 Extrayendo: {os.path.basename(archivo)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log.emit(f"✅ {os.path.basename(archivo)} extraído correctamente")
                return True
            else:
                self.log.emit(f"❌ Error al extraer {os.path.basename(archivo)}: {result.stderr}")
                return False
        except Exception as e:
            self.log.emit(f"❌ Excepción al extraer {os.path.basename(archivo)}: {e}")
            return False

    def extraer_rpyc(self, archivo):
        try:
            unrpyc_path = os.path.join(os.path.dirname(__file__), "unrpyc-master", "unrpyc.py")
            if os.path.exists(unrpyc_path):
                cmd = [sys.executable, unrpyc_path, archivo]
            else:
                cmd = ["unrpyc", archivo]
            
            self.log.emit(f"🔧 Descompilando: {os.path.basename(archivo)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log.emit(f"✅ {os.path.basename(archivo)} descompilado correctamente")
                return True
            else:
                self.log.emit(f"❌ Error al descompilar {os.path.basename(archivo)}: {result.stderr}")
                return False
        except Exception as e:
            self.log.emit(f"❌ Excepción al descompilar {os.path.basename(archivo)}: {e}")
            return False

    def run(self):
        self.progreso.emit(10)
        self.log.emit(f"🚀 Iniciando procesamiento de carpeta: {self.carpeta_entrada}")
        
        # Buscar todos los archivos del tipo especificado en la carpeta
        archivos_encontrados = []
        extension = ".rpa" if self.tipo_archivo == "RPA" else ".rpyc"
        
        for archivo in os.listdir(self.carpeta_entrada):
            if archivo.lower().endswith(extension):
                ruta_completa = os.path.join(self.carpeta_entrada, archivo)
                if os.path.isfile(ruta_completa):
                    archivos_encontrados.append(ruta_completa)
        
        if not archivos_encontrados:
            self.log.emit(f"❌ No se encontraron archivos {extension} en la carpeta")
            self.terminado.emit(False, "")
            return
        
        self.log.emit(f"📁 Encontrados {len(archivos_encontrados)} archivos {extension}")
        
        # Procesar cada archivo
        exitosos = 0
        total_archivos = len(archivos_encontrados)
        
        for i, archivo in enumerate(archivos_encontrados):
            self.progreso.emit(10 + int(80 * i / total_archivos))
            
            if self.tipo_archivo == "RPA":
                if self.extraer_rpa(archivo):
                    exitosos += 1
            elif self.tipo_archivo == "RPYC":
                if self.extraer_rpyc(archivo):
                    exitosos += 1
        
        self.progreso.emit(100)
        
        if exitosos > 0:
            self.log.emit(f"✅ Procesamiento completado: {exitosos}/{total_archivos} archivos exitosos")
            self.log.emit(f"📂 Ubicación: {self.directorio_salida}")
            self.terminado.emit(True, self.directorio_salida)
        else:
            self.log.emit("❌ No se pudo procesar ningún archivo")
            self.terminado.emit(False, "")


class TraductorThread(QThread):
    progreso = pyqtSignal(int)
    log = pyqtSignal(str)
    terminado = pyqtSignal(bool)
    
    # Contador global de traducciones
    contador_traducciones = 0
    limite_diario = 800  # Límite conservador para API gratuita
    
    # Sistema de múltiples APIs (APIs gratuitas verificadas y funcionando)
    apis_disponibles = [
        {
            "nombre": "GoogleTranslate",
            "url": "https://translate.googleapis.com/translate_a/single",
            "limite": 5000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LingvaTranslate1",
            "url": "https://lingva.ml/api/v1/en/es/",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LingvaTranslate2",
            "url": "https://lingva.lunar.icu/api/v1/en/es/",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "MyMemory",
            "url": "https://api.mymemory.translated.net/get",
            "limite": 800,
            "contador": 0,
            "activa": True
        }
    ]
    
    api_actual = 0  # Índice de la API actual
    ultimo_dia = None  # Para detectar cambio de día

    def __init__(self, archivo_entrada, archivo_salida, idioma_origen="en", idioma_destino="es"):
        super().__init__()
        self.archivo_entrada = archivo_entrada
        self.archivo_salida = archivo_salida
        self.idioma_origen = idioma_origen
        self.idioma_destino = idioma_destino
        self.verificar_cambio_dia()
        self.test_api_availability()  # Probar disponibilidad de APIs al inicio
        self.pausado = False
        self.terminar = False

    def pausar(self):
        """Pausa la traducción"""
        self.pausado = True
        self.log.emit("⏸️ Traducción pausada...")

    def reanudar(self):
        """Reanuda la traducción"""
        self.pausado = False
        self.log.emit("▶️ Traducción reanudada...")

    def terminar_traduccion(self):
        """Termina la traducción de forma controlada"""
        self.terminar = True
        self.log.emit("🛑 Terminando traducción...")

    def verificar_cambio_dia(self):
        """Verifica si es un nuevo día y resetea los contadores"""
        import datetime
        hoy = datetime.date.today()
        
        if TraductorThread.ultimo_dia != hoy:
            if TraductorThread.ultimo_dia is not None:
                self.log.emit(f"🔄 Nuevo día detectado: {hoy}. Reseteando contadores...")
            
            # Resetear todos los contadores
            TraductorThread.contador_traducciones = 0
            for api in TraductorThread.apis_disponibles:
                api["contador"] = 0
                api["activa"] = True
            
            TraductorThread.ultimo_dia = hoy
            self.log.emit(f"✅ Contadores reseteados. Todas las APIs disponibles.")
            self.log.emit(f"📊 Límites diarios:")
            for api in TraductorThread.apis_disponibles:
                self.log.emit(f"   • {api['nombre']}: {api['limite']} traducciones")
        else:
            self.log.emit(f"📅 Día actual: {hoy}")
            self.log.emit(f"📊 Contadores actuales:")
            for api in TraductorThread.apis_disponibles:
                if api["contador"] > 0:
                    self.log.emit(f"   • {api['nombre']}: {api['contador']}/{api['limite']}")
    
    def test_api_availability(self):
        """Testea la disponibilidad de las APIs más importantes"""
        self.log.emit("🔍 Probando disponibilidad de APIs...")
        
        # APIs más confiables para probar primero
        test_apis = [
            {"nombre": "MyMemory", "url": "https://api.mymemory.translated.net/get"},
            {"nombre": "GoogleTranslate", "url": "https://translate.googleapis.com/translate_a/single"},
            {"nombre": "LibreTranslate1", "url": "https://libretranslate.de/translate"},
            {"nombre": "LibreTranslate2", "url": "https://translate.argosopentech.com/translate"}
        ]
        
        apis_disponibles = []
        
        for api in test_apis:
            try:
                if api["nombre"] == "MyMemory":
                    response = requests.get(api["url"], params={"q": "test", "langpair": "en|es"}, timeout=5)
                elif api["nombre"] == "GoogleTranslate":
                    response = requests.get(api["url"], params={"client": "gtx", "sl": "en", "tl": "es", "dt": "t", "q": "test"}, timeout=5)
                else:
                    response = requests.post(api["url"], json={"q": "test", "source": "en", "target": "es"}, timeout=5)
                
                if response.status_code == 200:
                    apis_disponibles.append(api["nombre"])
                    self.log.emit(f"✅ {api['nombre']}: Disponible")
                else:
                    self.log.emit(f"⚠️ {api['nombre']}: HTTP {response.status_code}")
            except Exception as e:
                self.log.emit(f"❌ {api['nombre']}: {str(e)[:50]}...")
        
        if apis_disponibles:
            self.log.emit(f"🎯 APIs disponibles: {', '.join(apis_disponibles)}")
        else:
            self.log.emit("⚠️ No se detectaron APIs disponibles. Verificando conexión a internet...")
        
        return len(apis_disponibles) > 0

    def cambiar_api(self):
        """Cambia a la siguiente API disponible"""
        intentos = 0
        max_intentos = len(self.apis_disponibles) * 2  # Evitar bucle infinito
        
        while intentos < max_intentos:
            intentos += 1
            siguiente = (self.api_actual + 1) % len(self.apis_disponibles)
            
            if self.apis_disponibles[siguiente]["activa"] and self.apis_disponibles[siguiente]["contador"] < self.apis_disponibles[siguiente]["limite"]:
                self.api_actual = siguiente
                api = self.apis_disponibles[siguiente]
                self.log.emit(f"🔄 Cambiando a API: {api['nombre']} ({api['limite'] - api['contador']} traducciones disponibles)")
                return True
            else:
                # Si la API está agotada o inactiva, marcar como agotada para evitar intentos futuros
                if self.apis_disponibles[siguiente]["contador"] >= self.apis_disponibles[siguiente]["limite"]:
                    self.log.emit(f"⚠️ {self.apis_disponibles[siguiente]['nombre']} agotada, saltando...")
                self.api_actual = siguiente
        
        self.log.emit(f"❌ No se encontraron APIs disponibles después de {max_intentos} intentos")
        return False

    def traducir_con_api(self, texto, api_info):
        """Traduce usando la API especificada"""
        if api_info["nombre"] == "MyMemory":
            return self.traducir_mymemory(texto)
        elif api_info["nombre"] == "GoogleTranslate":
            return self.traducir_google(texto)
        elif api_info["nombre"].startswith("LingvaTranslate"):
            return self.traducir_lingva(texto, api_info)
        return texto

    def traducir_mymemory(self, texto):
        """Traduce usando MyMemory API"""
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": texto,
            "langpair": f"{self.idioma_origen}|{self.idioma_destino}"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    traduccion = data["responseData"]["translatedText"]
                    self.log.emit(f"✅ MyMemory: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ MyMemory error: {data.get('responseDetails', 'Error desconocido')}")
            elif response.status_code == 429:
                self.log.emit(f"⚠️ MyMemory: Error 429 - Límite alcanzado")
                # Marcar esta API como agotada
                self.apis_disponibles[0]["contador"] = self.apis_disponibles[0]["limite"]
                return None  # Indicar que debe cambiar de API
            else:
                self.log.emit(f"⚠️ MyMemory HTTP error: {response.status_code}")
            return texto
        except Exception as e:
            self.log.emit(f"❌ MyMemory exception: {e}")
            return texto

    def traducir_google(self, texto):
        """Traduce usando Google Translate API"""
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": self.idioma_origen,
            "tl": self.idioma_destino,
            "dt": "t",
            "q": texto
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and len(data[0]) > 0:
                    traduccion = data[0][0][0]
                    self.log.emit(f"✅ Google: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ Google: Respuesta vacía para '{texto}'")
            elif response.status_code == 429:
                self.log.emit(f"⚠️ Google: Error 429 - Límite alcanzado")
                # Marcar esta API como agotada
                self.apis_disponibles[1]["contador"] = self.apis_disponibles[1]["limite"]
                return None  # Indicar que debe cambiar de API
            else:
                self.log.emit(f"⚠️ Google HTTP error: {response.status_code}")
            return texto
        except Exception as e:
            self.log.emit(f"❌ Google exception: {e}")
            return texto

    def traducir_libretranslate(self, texto, url):
        """Traduce usando LibreTranslate API"""
        data = {
            "q": texto,
            "source": self.idioma_origen,
            "target": self.idioma_destino
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)  # Reducido de 30 a 10 segundos
            if response.status_code == 200:
                data = response.json()
                traduccion = data.get("translatedText", texto)
                if traduccion != texto:
                    self.log.emit(f"✅ LibreTranslate: '{texto}' → '{traduccion}'")
                else:
                    self.log.emit(f"⚠️ LibreTranslate: No se pudo traducir '{texto}'")
                return traduccion
            elif response.status_code == 429:
                self.log.emit(f"⚠️ LibreTranslate: Error 429 - Límite alcanzado")
                return None  # Indicar que debe cambiar de API
            else:
                self.log.emit(f"⚠️ LibreTranslate HTTP error: {response.status_code}")
            return texto
        except requests.exceptions.Timeout:
            self.log.emit(f"⏰ LibreTranslate: Timeout - API no responde")
            return None  # Cambiar de API
        except requests.exceptions.ConnectionError:
            self.log.emit(f"🌐 LibreTranslate: Error de conexión - API no disponible")
            return None  # Cambiar de API
        except Exception as e:
            self.log.emit(f"❌ LibreTranslate exception: {e}")
            return None  # Cambiar de API en caso de cualquier error

    def traducir_yandex(self, texto):
        """Traduce usando Yandex API (gratuito)"""
        url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
        params = {
            "key": "trnsl.1.1.20231201T000000Z.0000000000000000",  # Key pública de ejemplo
            "text": texto,
            "lang": f"{self.idioma_origen}-{self.idioma_destino}"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "text" in data and data["text"]:
                    traduccion = data["text"][0]
                    if traduccion != texto:
                        self.log.emit(f"✅ Yandex: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ Yandex: No se pudo traducir '{texto}'")
            elif response.status_code == 429:
                self.log.emit(f"⚠️ Yandex: Error 429 - Límite alcanzado")
                return None
            else:
                self.log.emit(f"⚠️ Yandex HTTP error: {response.status_code}")
            return texto
        except requests.exceptions.Timeout:
            self.log.emit(f"⏰ Yandex: Timeout - API no responde")
            return None
        except requests.exceptions.ConnectionError:
            self.log.emit(f"🌐 Yandex: Error de conexión - API no disponible")
            return None
        except Exception as e:
            self.log.emit(f"❌ Yandex exception: {e}")
            return None

    def traducir_bing(self, texto):
        """Traduce usando Bing Translator API (gratuito)"""
        url = "https://api.cognitive.microsofttranslator.com/translate"
        headers = {
            "Ocp-Apim-Subscription-Key": "free",  # Versión gratuita
            "Content-Type": "application/json",
            "X-ClientTraceId": "00000000-0000-0000-0000-000000000000"
        }
        data = [{"text": texto}]
        params = {
            "api-version": "3.0",
            "from": self.idioma_origen,
            "to": self.idioma_destino
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and "translations" in data[0]:
                    traduccion = data[0]["translations"][0]["text"]
                    if traduccion != texto:
                        self.log.emit(f"✅ Bing: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ Bing: No se pudo traducir '{texto}'")
            elif response.status_code == 429:
                self.log.emit(f"⚠️ Bing: Error 429 - Límite alcanzado")
                return None
            else:
                self.log.emit(f"⚠️ Bing HTTP error: {response.status_code}")
            return texto
        except requests.exceptions.Timeout:
            self.log.emit(f"⏰ Bing: Timeout - API no responde")
            return None
        except requests.exceptions.ConnectionError:
            self.log.emit(f"🌐 Bing: Error de conexión - API no disponible")
            return None
        except Exception as e:
            self.log.emit(f"❌ Bing exception: {e}")
            return None

    def traducir_deepl(self, texto):
        """Traduce usando DeepL Free API"""
        url = "https://api-free.deepl.com/v2/translate"
        headers = {
            "Authorization": "DeepL-Auth-Key free",  # Versión gratuita
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "text": texto,
            "source_lang": self.idioma_origen.upper(),
            "target_lang": self.idioma_destino.upper()
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "translations" in data and data["translations"]:
                    traduccion = data["translations"][0]["text"]
                    if traduccion != texto:
                        self.log.emit(f"✅ DeepL: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ DeepL: No se pudo traducir '{texto}'")
            elif response.status_code == 429:
                self.log.emit(f"⚠️ DeepL: Error 429 - Límite alcanzado")
                return None
            else:
                self.log.emit(f"⚠️ DeepL HTTP error: {response.status_code}")
            return texto
        except requests.exceptions.Timeout:
            self.log.emit(f"⏰ DeepL: Timeout - API no responde")
            return None
        except requests.exceptions.ConnectionError:
            self.log.emit(f"🌐 DeepL: Error de conexión - API no disponible")
            return None
        except Exception as e:
            self.log.emit(f"❌ DeepL exception: {e}")
            return None

    def traducir_apertium(self, texto):
        """Traduce usando Apertium API (gratuito)"""
        url = "https://apertium.org/apy/translate"
        data = {
            "langpair": f"{self.idioma_origen}|{self.idioma_destino}",
            "q": texto
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "responseData" in data and "translatedText" in data["responseData"]:
                    traduccion = data["responseData"]["translatedText"]
                    if traduccion != texto:
                        self.log.emit(f"✅ Apertium: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ Apertium: No se pudo traducir '{texto}'")
            elif response.status_code == 429:
                self.log.emit(f"⚠️ Apertium: Error 429 - Límite alcanzado")
                return None
            else:
                self.log.emit(f"⚠️ Apertium HTTP error: {response.status_code}")
            return texto
        except requests.exceptions.Timeout:
            self.log.emit(f"⏰ Apertium: Timeout - API no responde")
            return None
        except requests.exceptions.ConnectionError:
            self.log.emit(f"🌐 Apertium: Error de conexión - API no disponible")
            return None
        except Exception as e:
            self.log.emit(f"❌ Apertium exception: {e}")
            return None

    def traducir_lingva(self, texto, api_info):
        """Traduce usando Lingva Translate API"""
        # Lingva usa un formato diferente - GET request con el texto en la URL
        texto_encoded = requests.utils.quote(texto)
        url = f"{api_info['url']}{texto_encoded}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "translation" in data:
                    traduccion = data["translation"]
                    if traduccion != texto:
                        self.log.emit(f"✅ {api_info['nombre']}: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ {api_info['nombre']}: No se pudo traducir '{texto}'")
            elif response.status_code == 429:
                self.log.emit(f"⚠️ {api_info['nombre']}: Error 429 - Límite alcanzado")
                return None
            else:
                self.log.emit(f"⚠️ {api_info['nombre']} HTTP error: {response.status_code}")
            return texto
        except requests.exceptions.Timeout:
            self.log.emit(f"⏰ {api_info['nombre']}: Timeout - API no responde")
            return None
        except requests.exceptions.ConnectionError:
            self.log.emit(f"🌐 {api_info['nombre']}: Error de conexión - API no disponible")
            return None
        except Exception as e:
            self.log.emit(f"❌ {api_info['nombre']} exception: {e}")
            return None

    def traducir_texto(self, texto):
        # Lista de palabras que NO deben traducirse
        palabras_no_traducir = {
            'who', 'what', 'namebox', 'vertical', 'horizontal',
            'small', 'medium', 'large', 'tiny', 'huge',
            'prefix', 'suffix', 'hover', 'idle', 'selected', 'insensitive'
        }
        
        # Si es una palabra técnica, no traducir
        if texto.lower().strip() in palabras_no_traducir:
            return texto
        
        import time
        time.sleep(1)  # Pausa entre traducciones
        
        # Intentar con todas las APIs disponibles
        for intento_api in range(len(self.apis_disponibles)):
            api_actual = self.apis_disponibles[self.api_actual]
            
            # Verificar si la API actual está disponible
            if api_actual["contador"] >= api_actual["limite"]:
                self.log.emit(f"⚠️ Límite alcanzado en {api_actual['nombre']}. Cambiando API...")
                if not self.cambiar_api():
                    self.log.emit(f"❌ Todas las APIs están agotadas.")
                    return texto
                api_actual = self.apis_disponibles[self.api_actual]
            
            # Traducir con la API actual
            traduccion = self.traducir_con_api(texto, api_actual)
            
            # Si la traducción fue exitosa (no es None)
            if traduccion is not None and traduccion != texto:
                # Incrementar contador de la API actual
                api_actual["contador"] += 1
                TraductorThread.contador_traducciones += 1
                
                self.log.emit(f"📊 {api_actual['nombre']}: {api_actual['contador']}/{api_actual['limite']}")
                
                # Verificar que la traducción no sea muy diferente del original
                if len(traduccion) > len(texto) * 3:
                    self.log.emit(f"⚠️ Traducción sospechosa, manteniendo original: '{texto}'")
                    return texto
                
                return traduccion
            elif traduccion is None:
                # La API indicó que debe cambiar
                self.log.emit(f"🔄 Cambiando API debido a error...")
                if not self.cambiar_api():
                    self.log.emit(f"❌ Todas las APIs están agotadas.")
                    return texto
                continue
            else:
                # La traducción falló, intentar con la siguiente API
                self.log.emit(f"⚠️ {api_actual['nombre']} falló, intentando siguiente API...")
                if not self.cambiar_api():
                    self.log.emit(f"❌ Todas las APIs están agotadas.")
                    return texto
        
        return texto  # Si llegamos aquí, mantener el texto original

    def run(self):
        try:
            # Patrones mejorados para capturar todo el texto entre comillas
            patron_dialogo = re.compile(r'^(\s*[a-zA-Z0-9_]+\s+)(["\'])(.*?)\2(\s*)$', re.DOTALL)
            patron_linea_comillas = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)$', re.DOTALL)
            patron_style_prefix = re.compile(r'^(\s*style_prefix\s+)(["\'])(.*?)\2(\s*)$', re.DOTALL)
        
        # NUEVOS PATRONES PARA EL FORMATO ESPECÍFICO DE TRADUCCIÓN
        patron_formato_especifico = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$', re.DOTALL)
        patron_linea_vacia = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*""\s*$', re.DOTALL)
        patron_etiqueta_traduccion = re.compile(r'^\s*#\s*game/([^:]+):(\d+)\s*$', re.DOTALL)
        patron_translate = re.compile(r'^\s*translate\s+(\w+)\s+(\w+):\s*$', re.DOTALL)
        
        # PATRONES MEJORADOS PARA EL FORMATO ESPECÍFICO DE TRADUCCIÓN
        patron_comentario_traduccion = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$', re.DOTALL)
        patron_linea_vacia_traduccion = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*""\s*$', re.DOTALL)
        patron_bloque_traduccion = re.compile(r'^\s*translate\s+(\w+)\s+(\w+):\s*$', re.DOTALL)
        
        # Nuevos patrones para textos de traducción de Ren'Py
        patron_traduccion = re.compile(r'textbutton\s+_\s*\(\s*["\'](.*?)["\']\s*\)', re.DOTALL)
        patron_traduccion_simple = re.compile(r'_\s*\(\s*["\'](.*?)["\']\s*\)', re.DOTALL)
        
        # Patrones mejorados para capturar líneas con comillas mal formateadas
        patron_dialogo_mal_formateado = re.compile(r'^(\s*[a-zA-Z0-9_]+)(["\'])(.*?)\2(\s*)$', re.DOTALL)
        patron_comillas_mal_formateadas = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)(["\'])(.*?)\5(\s*)$', re.DOTALL)
        patron_comillas_sueltas = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)$', re.DOTALL)
        
        # Patrón para capturar líneas con texto mezclado y comillas mal formateadas
        patron_texto_mezclado = re.compile(r'^(\s*)(.*?)(["\'])(.*?)\3(\s*)$', re.DOTALL)
        
        # Patrón específico para líneas con comillas mal formateadas como: s"texto" "texto2"
        patron_comillas_mal_formateadas_especifico = re.compile(r'^(\s*[a-zA-Z0-9_]+)(["\'])(.*?)\2(\s*)(["\'])(.*?)\5(\s*)$', re.DOTALL)
        
        # Patrones adicionales para líneas complejas
        patron_linea_con_texto_y_comillas = re.compile(r'^(\s*)(.*?)(["\'])(.*?)\3(\s*)(["\'])(.*?)\6(\s*)$', re.DOTALL)
        patron_linea_con_personaje_y_texto = re.compile(r'^(\s*[a-zA-Z0-9_]+)(\s*)(["\'])(.*?)\3(\s*)$', re.DOTALL)
        patron_linea_solo_texto = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)$', re.DOTALL)
        
        # Patrón para líneas con texto mezclado con comandos de Ren'Py
        patron_texto_con_comando = re.compile(r'^(\s*)(.*?)(["\'])(.*?)\3(\s*)(scene|show|hide|play|stop|pause|label|jump|call|return|with|at|as|zorder|behind|onlayer|transform|style|screen)(\s+)(.*?)$', re.DOTALL)
        
        # Patrón para líneas con texto seguido de comandos de Ren'Py en la misma línea
        patron_texto_seguido_comando = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)(scene|show|hide|play|stop|pause|label|jump|call|return|with|at|as|zorder|behind|onlayer|transform|style|screen)(\s+)(.*?)$', re.DOTALL)
        
        # NUEVOS PATRONES PARA CAPTURAR TEXTOS NARRATIVOS Y OPCIONES DE MENÚ
        patron_texto_narrativo = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)$', re.DOTALL)  # Líneas que solo contienen texto entre comillas
        patron_opcion_menu = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*):(\s*)$', re.DOTALL)  # Opciones de menú con dos puntos
        patron_opcion_menu_sin_dos_puntos = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)$', re.DOTALL)  # Opciones de menú sin dos puntos
        patron_texto_con_variables = re.compile(r'^(\s*)(["\'])(.*?\[[^\]]+\].*?)\2(\s*)$', re.DOTALL)  # Texto con variables como [fmc_name]
        patron_texto_centrado = re.compile(r'^(\s*centered\s+)(["\'])(.*?)\2(\s*)$', re.DOTALL)  # Texto centrado
        patron_texto_con_formato = re.compile(r'^(\s*)(["\'])(.*?\{[^}]+\}.*?)\2(\s*)$', re.DOTALL)  # Texto con formato como {b}texto{/b}
        
        # PATRÓN GENERAL PARA CAPTURAR CUALQUIER TEXTO EN INGLÉS QUE NO HAYA SIDO DETECTADO
        patron_texto_general = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)$', re.DOTALL)  # Cualquier texto entre comillas
        
        # PATRONES ADICIONALES PARA CAPTURAR CASOS ESPECÍFICOS NO TRADUCIDOS
        patron_texto_narrativo_ingles = re.compile(r'^(\s*)(["\'])([A-Z][a-z].*[a-z].*)\2(\s*)$', re.DOTALL)  # Texto narrativo que empieza con mayúscula
        patron_dialogo_ingles = re.compile(r'^(\s*)(\w+)\s+["\']([A-Z][a-z].*[a-z].*)["\'](\s*)$', re.DOTALL)  # Diálogo en inglés
        patron_input_prompt = re.compile(r'renpy\.input\("([A-Z][a-z].*[a-z].*)"', re.DOTALL)  # Prompts de input
        patron_notification = re.compile(r'renpy\.notify\("([A-Z][a-z].*[a-z].*)"', re.DOTALL)  # Notificaciones
        patron_texto_con_verbo_ingles = re.compile(r'^(\s*)(["\'])(.*\b(you|he|she|it|we|they|I|am|is|are|was|were|have|has|had|do|does|did|will|would|could|should|can|may|might)\b.*)\2(\s*)$', re.DOTALL)  # Texto con verbos en inglés
        
        # NUEVOS PATRONES BASADOS EN NUESTRO ANÁLISIS DE ejemplo.rpy
        patron_texto_con_variables_renpy = re.compile(r'^(\s*)(["\'])(.*?\[[^\]]+\].*?)\2(\s*)$', re.DOTALL)  # Texto con variables como [fmc_name]
        patron_texto_con_formato_renpy = re.compile(r'^(\s*)(["\'])(.*?\{[^}]+\}.*?)\2(\s*)$', re.DOTALL)  # Texto con formato como {b}texto{/b}
        patron_texto_centrado_ingles = re.compile(r'^(\s*centered\s+)(["\'])(.*?)\2(\s*)$', re.DOTALL)  # Texto centrado en inglés
        patron_texto_con_url = re.compile(r'^(\s*)(["\'])(.*?(?:https?://|www\.).*?)\2(\s*)$', re.DOTALL)  # Texto con URLs
        patron_texto_con_numeros = re.compile(r'^(\s*)(["\'])(.*?\d+.*?)\2(\s*)$', re.DOTALL)  # Texto con números
        patron_texto_con_euros = re.compile(r'^(\s*)(["\'])(.*?€.*?)\2(\s*)$', re.DOTALL)  # Texto con símbolos de euro
        patron_texto_con_newline = re.compile(r'^(\s*)(["\'])(.*?\\n.*?)\2(\s*)$', re.DOTALL)  # Texto con saltos de línea
        
        lineas_traducidas = []

        # Elementos que NO se deben traducir
        elementos_no_traducir = (
            # Archivos y rutas
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ttf", ".otf", ".woff",
            "gui/", "images/", "audio/", "music/", "sounds/",
            # Variables y códigos
            "[", "]", "{", "}", "config.", "gui.", "renpy.",
            # Códigos de color
            "#", "rgb(", "rgba(",
            # Comandos y funciones
            "define", "init", "transform", "style", "screen",
            # Combinaciones de teclas
            "Shift+", "Ctrl+", "Alt+", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            # Otros elementos técnicos
            "prefix", "suffix", "hover", "idle", "selected", "insensitive"
        )

        estilos_protegidos = (
            "subtitle", "title", "skip_triangle", "default", "button", "button_text",
            "choice_button", "choice_button_text", "quick_button", "quick_button_text",
            "navigation_button", "narrador", "texto", "menu", "style", "screen"
        )

        def debe_traducir(texto):
            """Verifica si el texto debe ser traducido con detección mejorada"""
            texto_lower = texto.lower()
            texto_strip = texto.strip()
            
            # No traducir si es muy corto (menos de 2 caracteres)
            if len(texto_strip) < 2:
                return False
            
            # No traducir si contiene elementos técnicos
            for elemento in elementos_no_traducir:
                if elemento in texto_lower:
                    return False
            
            # No traducir si contiene solo números, símbolos o caracteres especiales
            texto_limpio = texto_strip.replace(" ", "").replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace(":", "").replace(";", "").replace("-", "").replace("_", "").replace("'", "").replace('"', "")
            if texto_limpio.isdigit() or not any(c.isalpha() for c in texto_strip):
                return False
            
            # No traducir si contiene caracteres especiales de programación (pero ser más permisivo)
            caracteres_prohibidos = "{}[]()<>$@#%^&*+=|\\"
            if any(char in texto for char in caracteres_prohibidos):
                # Si contiene caracteres prohibidos, verificar si parece ser código
                if texto_strip.startswith(("$", "[", "{", "config.", "gui.", "renpy.")):
                    return False
                # Si contiene muchos caracteres especiales pero también texto, podría ser diálogo
                if len([c for c in texto if c in caracteres_prohibidos]) > len(texto) * 0.3:
                    return False
            
            # No traducir si es solo un nombre de archivo o ruta
            if "/" in texto_strip or "\\" in texto_strip or texto_strip.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ttf", ".otf")):
                return False
            
            # No traducir si es muy corto y parece ser un identificador
            if len(texto_strip) <= 3 and texto_strip.isupper():
                return False
            
            # Verificar que contenga al menos una palabra real (no solo símbolos)
            palabras = texto_strip.split()
            palabras_reales = [p for p in palabras if any(c.isalpha() for c in p) and len(p) > 1]
            
            if not palabras_reales:
                return False
            
            # Ser más permisivo con diálogos que contienen caracteres especiales comunes
            # como comillas, puntos, comas, etc.
            if any(c in texto for c in '"\'.!?,;:-'):
                # Si contiene caracteres de puntuación comunes en diálogos, verificar que tenga texto real
                texto_sin_puntuacion = texto.replace('"', '').replace("'", '').replace('.', '').replace(',', '').replace('!', '').replace('?', '').replace(':', '').replace(';', '').replace('-', '')
                if any(c.isalpha() for c in texto_sin_puntuacion) and len(texto_sin_puntuacion.strip()) > 2:
                    return True
            
            return True

        def debe_traducir_mejorado(texto):
            """Versión mejorada que detecta más tipos de texto para traducir basada en nuestro análisis"""
            texto_strip = texto.strip()
            
            # No traducir si es muy corto (menos de 2 caracteres)
            if len(texto_strip) < 2:
                return False
            
            # No traducir elementos técnicos específicos
            elementos_tecnicos = {
                'who', 'what', 'namebox', 'vertical', 'horizontal', 'small', 'medium', 'large', 
                'tiny', 'huge', 'prefix', 'suffix', 'hover', 'idle', 'selected', 'insensitive',
                'define', 'init', 'transform', 'style', 'screen', 'label', 'jump', 'call',
                'scene', 'show', 'hide', 'play', 'stop', 'pause', 'with', 'at', 'as',
                'centered', 'text', 'image', 'audio', 'music', 'sound', 'voice'
            }
            
            if texto_strip.lower() in elementos_tecnicos:
                return False
            
            # No traducir rutas de archivos
            if any(ext in texto_strip.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ttf', '.otf', '.mp3', '.wav', '.ogg']):
                return False
            
            # No traducir si contiene solo símbolos técnicos
            caracteres_tecnicos = "{}[]()<>$@#%^&*+=|\\"
            if all(c in caracteres_tecnicos or c.isspace() for c in texto_strip):
                return False
            
            # Verificar que contenga al menos una palabra con letras
            palabras = texto_strip.split()
            palabras_con_letras = [p for p in palabras if any(c.isalpha() for c in p)]
            
            if not palabras_con_letras:
                return False
            
            # MEJORA 1: Ser más permisivo con textos que contienen variables como [fmc_name], [mmc_name]
            if '[' in texto_strip and ']' in texto_strip:
                # Si contiene variables, verificar que tenga texto real además de las variables
                texto_sin_variables = re.sub(r'\[[^\]]+\]', '', texto_strip)
                if any(c.isalpha() for c in texto_sin_variables) and len(texto_sin_variables.strip()) > 2:
                    return True
            
            # MEJORA 2: Permitir traducción de textos cortos que son claramente diálogo
            palabras_cortas_dialogo = {
                'yes', 'no', 'sure', 'okay', 'thanks', 'sorry', 'hi', 'hello', 'bye', 'thanks',
                'yeah', 'yep', 'nope', 'maybe', 'please', 'please', 'excuse', 'pardon'
            }
            if texto_strip.lower() in palabras_cortas_dialogo:
                return True
            
            # MEJORA 3: Detectar texto narrativo en inglés (líneas que empiezan con mayúscula)
            if texto_strip and texto_strip[0].isupper():
                # Verificar si contiene palabras típicas del inglés
                palabras_ingles = {
                    'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 
                    'up', 'down', 'out', 'off', 'over', 'under', 'through', 'during', 'before', 'after', 
                    'while', 'since', 'until', 'because', 'although', 'though', 'unless', 'if', 'when', 
                    'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'this', 'that', 
                    'these', 'those', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
                    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 
                    'very', 'can', 'will', 'just', 'don', 'should', 'now', 'then', 'here', 'there',
                    'you', 'he', 'she', 'it', 'we', 'they', 'I', 'am', 'is', 'are', 'was', 'were',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                    'can', 'may', 'might', 'must', 'shall', 'being', 'been', 'be', 'get', 'gets',
                    'got', 'getting', 'go', 'goes', 'went', 'going', 'gone', 'come', 'comes', 'came',
                    'coming', 'see', 'sees', 'saw', 'seeing', 'seen', 'look', 'looks', 'looked',
                    'looking', 'feel', 'feels', 'felt', 'feeling', 'think', 'thinks', 'thought',
                    'thinking', 'know', 'knows', 'knew', 'knowing', 'known', 'want', 'wants', 'wanted',
                    'wanting', 'need', 'needs', 'needed', 'needing', 'like', 'likes', 'liked', 'liking',
                    'love', 'loves', 'loved', 'loving', 'hate', 'hates', 'hated', 'hating', 'say',
                    'says', 'said', 'saying', 'tell', 'tells', 'told', 'telling', 'ask', 'asks',
                    'asked', 'asking', 'give', 'gives', 'gave', 'giving', 'given', 'take', 'takes',
                    'took', 'taking', 'taken', 'make', 'makes', 'made', 'making', 'let', 'lets',
                    'letting', 'put', 'puts', 'putting', 'bring', 'brings', 'brought', 'bringing',
                    'find', 'finds', 'found', 'finding', 'keep', 'keeps', 'kept', 'keeping',
                    'hold', 'holds', 'held', 'holding', 'leave', 'leaves', 'left', 'leaving',
                    'turn', 'turns', 'turned', 'turning', 'move', 'moves', 'moved', 'moving',
                    'walk', 'walks', 'walked', 'walking', 'run', 'runs', 'ran', 'running',
                    'sit', 'sits', 'sat', 'sitting', 'stand', 'stands', 'stood', 'standing',
                    'lie', 'lies', 'lay', 'lying', 'laying', 'sleep', 'sleeps', 'slept', 'sleeping',
                    'wake', 'wakes', 'woke', 'waking', 'woken', 'eat', 'eats', 'ate', 'eating',
                    'eaten', 'drink', 'drinks', 'drank', 'drinking', 'drunk', 'wear', 'wears',
                    'wore', 'wearing', 'worn', 'open', 'opens', 'opened', 'opening', 'close',
                    'closes', 'closed', 'closing', 'start', 'starts', 'started', 'starting',
                    'stop', 'stops', 'stopped', 'stopping', 'begin', 'begins', 'began', 'beginning',
                    'begun', 'end', 'ends', 'ended', 'ending', 'finish', 'finishes', 'finished',
                    'finishing', 'try', 'tries', 'tried', 'trying', 'help', 'helps', 'helped',
                    'helping', 'work', 'works', 'worked', 'working', 'play', 'plays', 'played',
                    'playing', 'read', 'reads', 'read', 'reading', 'write', 'writes', 'wrote',
                    'writing', 'written', 'draw', 'draws', 'drew', 'drawing', 'drawn', 'paint',
                    'paints', 'painted', 'painting', 'sing', 'sings', 'sang', 'singing', 'sung',
                    'dance', 'dances', 'danced', 'dancing', 'laugh', 'laughs', 'laughed', 'laughing',
                    'smile', 'smiles', 'smiled', 'smiling', 'cry', 'cries', 'cried', 'crying',
                    'shout', 'shouts', 'shouted', 'shouting', 'whisper', 'whispers', 'whispered',
                    'whispering', 'talk', 'talks', 'talked', 'talking', 'speak', 'speaks', 'spoke',
                    'speaking', 'spoken', 'listen', 'listens', 'listened', 'listening', 'hear',
                    'hears', 'heard', 'hearing', 'watch', 'watches', 'watched', 'watching', 'see',
                    'sees', 'saw', 'seeing', 'seen', 'look', 'looks', 'looked', 'looking', 'stare',
                    'stares', 'stared', 'staring', 'glance', 'glances', 'glanced', 'glancing',
                    'touch', 'touches', 'touched', 'touching', 'hold', 'holds', 'held', 'holding',
                    'grab', 'grabs', 'grabbed', 'grabbing', 'pull', 'pulls', 'pulled', 'pulling',
                    'push', 'pushes', 'pushed', 'pushing', 'lift', 'lifts', 'lifted', 'lifting',
                    'carry', 'carries', 'carried', 'carrying', 'drop', 'drops', 'dropped', 'dropping',
                    'throw', 'throws', 'threw', 'throwing', 'thrown', 'catch', 'catches', 'caught',
                    'catching', 'hit', 'hits', 'hit', 'hitting', 'kick', 'kicks', 'kicked', 'kicking',
                    'punch', 'punches', 'punched', 'punching', 'fight', 'fights', 'fought', 'fighting',
                    'kill', 'kills', 'killed', 'killing', 'die', 'dies', 'died', 'dying', 'dead',
                    'alive', 'live', 'lives', 'lived', 'living', 'born', 'birth', 'grow', 'grows',
                    'grew', 'growing', 'grown', 'old', 'young', 'new', 'fresh', 'clean', 'dirty',
                    'big', 'small', 'large', 'tiny', 'huge', 'enormous', 'giant', 'massive',
                    'heavy', 'light', 'strong', 'weak', 'fast', 'slow', 'quick', 'rapid', 'swift',
                    'hot', 'cold', 'warm', 'cool', 'soft', 'hard', 'smooth', 'rough', 'sharp',
                    'blunt', 'bright', 'dark', 'light', 'heavy', 'empty', 'full', 'half', 'quarter',
                    'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
                    'first', 'second', 'last', 'next', 'previous', 'current', 'present', 'past',
                    'future', 'now', 'then', 'today', 'yesterday', 'tomorrow', 'morning', 'afternoon',
                    'evening', 'night', 'day', 'week', 'month', 'year', 'time', 'hour', 'minute',
                    'second', 'moment', 'instant', 'while', 'during', 'before', 'after', 'since',
                    'until', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose',
                    'this', 'that', 'these', 'those', 'here', 'there', 'everywhere', 'nowhere',
                    'somewhere', 'anywhere', 'inside', 'outside', 'above', 'below', 'under', 'over',
                    'behind', 'in front', 'beside', 'next to', 'near', 'far', 'close', 'distant',
                    'away', 'toward', 'towards', 'into', 'onto', 'upon', 'within', 'without',
                    'against', 'among', 'between', 'through', 'across', 'around', 'along', 'beyond',
                    'past', 'beneath', 'underneath', 'besides', 'except', 'including', 'concerning',
                    'regarding', 'about', 'above', 'below', 'under', 'over', 'behind', 'in front',
                    'beside', 'next to', 'near', 'far', 'close', 'distant', 'away', 'toward',
                    'towards', 'into', 'onto', 'upon', 'within', 'without', 'against', 'among',
                    'between', 'through', 'across', 'around', 'along', 'beyond', 'past', 'beneath',
                    'underneath', 'besides', 'except', 'including', 'concerning', 'regarding'
                }
                palabras_texto = set(texto_strip.lower().split())
                if palabras_texto.intersection(palabras_ingles):
                    return True
            
            # MEJORA 4: Detectar frases completas en inglés con verbos comunes
            if len(texto_strip) > 5 and any(palabra.isalpha() for palabra in texto_strip.split()):
                # Verificar si parece ser una frase en inglés con verbos comunes
                verbos_ingles = {
                    'you', 'he', 'she', 'it', 'we', 'they', 'I', 'am', 'is', 'are', 'was', 'were',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                    'can', 'may', 'might', 'must', 'shall', 'being', 'been', 'be', 'get', 'gets',
                    'got', 'getting', 'go', 'goes', 'went', 'going', 'gone', 'come', 'comes', 'came',
                    'coming', 'see', 'sees', 'saw', 'seeing', 'seen', 'look', 'looks', 'looked',
                    'looking', 'feel', 'feels', 'felt', 'feeling', 'think', 'thinks', 'thought',
                    'thinking', 'know', 'knows', 'knew', 'knowing', 'known', 'want', 'wants', 'wanted',
                    'wanting', 'need', 'needs', 'needed', 'needing', 'like', 'likes', 'liked', 'liking',
                    'love', 'loves', 'loved', 'loving', 'hate', 'hates', 'hated', 'hating', 'say',
                    'says', 'said', 'saying', 'tell', 'tells', 'told', 'telling', 'ask', 'asks',
                    'asked', 'asking', 'give', 'gives', 'gave', 'giving', 'given', 'take', 'takes',
                    'took', 'taking', 'taken', 'make', 'makes', 'made', 'making', 'let', 'lets',
                    'letting', 'put', 'puts', 'putting', 'bring', 'brings', 'brought', 'bringing',
                    'find', 'finds', 'found', 'finding', 'keep', 'keeps', 'kept', 'keeping',
                    'hold', 'holds', 'held', 'holding', 'leave', 'leaves', 'left', 'leaving',
                    'turn', 'turns', 'turned', 'turning', 'move', 'moves', 'moved', 'moving',
                    'walk', 'walks', 'walked', 'walking', 'run', 'runs', 'ran', 'running',
                    'sit', 'sits', 'sat', 'sitting', 'stand', 'stands', 'stood', 'standing',
                    'lie', 'lies', 'lay', 'lying', 'laying', 'sleep', 'sleeps', 'slept', 'sleeping',
                    'wake', 'wakes', 'woke', 'waking', 'woken', 'eat', 'eats', 'ate', 'eating',
                    'eaten', 'drink', 'drinks', 'drank', 'drinking', 'drunk', 'wear', 'wears',
                    'wore', 'wearing', 'worn', 'open', 'opens', 'opened', 'opening', 'close',
                    'closes', 'closed', 'closing', 'start', 'starts', 'started', 'starting',
                    'stop', 'stops', 'stopped', 'stopping', 'begin', 'begins', 'began', 'beginning',
                    'begun', 'end', 'ends', 'ended', 'ending', 'finish', 'finishes', 'finished',
                    'finishing', 'try', 'tries', 'tried', 'trying', 'help', 'helps', 'helped',
                    'helping', 'work', 'works', 'worked', 'working', 'play', 'plays', 'played',
                    'playing', 'read', 'reads', 'read', 'reading', 'write', 'writes', 'wrote',
                    'writing', 'written', 'draw', 'draws', 'drew', 'drawing', 'drawn', 'paint',
                    'paints', 'painted', 'painting', 'sing', 'sings', 'sang', 'singing', 'sung',
                    'dance', 'dances', 'danced', 'dancing', 'laugh', 'laughs', 'laughed', 'laughing',
                    'smile', 'smiles', 'smiled', 'smiling', 'cry', 'cries', 'cried', 'crying',
                    'shout', 'shouts', 'shouted', 'shouting', 'whisper', 'whispers', 'whispered',
                    'whispering', 'talk', 'talks', 'talked', 'talking', 'speak', 'speaks', 'spoke',
                    'speaking', 'spoken', 'listen', 'listens', 'listened', 'listening', 'hear',
                    'hears', 'heard', 'hearing', 'watch', 'watches', 'watched', 'watching', 'see',
                    'sees', 'saw', 'seeing', 'seen', 'look', 'looks', 'looked', 'looking', 'stare',
                    'stares', 'stared', 'staring', 'glance', 'glances', 'glanced', 'glancing',
                    'touch', 'touches', 'touched', 'touching', 'hold', 'holds', 'held', 'holding',
                    'grab', 'grabs', 'grabbed', 'grabbing', 'pull', 'pulls', 'pulled', 'pulling',
                    'push', 'pushes', 'pushed', 'pushing', 'lift', 'lifts', 'lifted', 'lifting',
                    'carry', 'carries', 'carried', 'carrying', 'drop', 'drops', 'dropped', 'dropping',
                    'throw', 'throws', 'threw', 'throwing', 'thrown', 'catch', 'catches', 'caught',
                    'catching', 'hit', 'hits', 'hit', 'hitting', 'kick', 'kicks', 'kicked', 'kicking',
                    'punch', 'punches', 'punched', 'punching', 'fight', 'fights', 'fought', 'fighting',
                    'kill', 'kills', 'killed', 'killing', 'die', 'dies', 'died', 'dying', 'dead',
                    'alive', 'live', 'lives', 'lived', 'living', 'born', 'birth', 'grow', 'grows',
                    'grew', 'growing', 'grown', 'old', 'young', 'new', 'fresh', 'clean', 'dirty',
                    'big', 'small', 'large', 'tiny', 'huge', 'enormous', 'giant', 'massive',
                    'heavy', 'light', 'strong', 'weak', 'fast', 'slow', 'quick', 'rapid', 'swift',
                    'hot', 'cold', 'warm', 'cool', 'soft', 'hard', 'smooth', 'rough', 'sharp',
                    'blunt', 'bright', 'dark', 'light', 'heavy', 'empty', 'full', 'half', 'quarter',
                    'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
                    'first', 'second', 'last', 'next', 'previous', 'current', 'present', 'past',
                    'future', 'now', 'then', 'today', 'yesterday', 'tomorrow', 'morning', 'afternoon',
                    'evening', 'night', 'day', 'week', 'month', 'year', 'time', 'hour', 'minute',
                    'second', 'moment', 'instant', 'while', 'during', 'before', 'after', 'since',
                    'until', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose',
                    'this', 'that', 'these', 'those', 'here', 'there', 'everywhere', 'nowhere',
                    'somewhere', 'anywhere', 'inside', 'outside', 'above', 'below', 'under', 'over',
                    'behind', 'in front', 'beside', 'next to', 'near', 'far', 'close', 'distant',
                    'away', 'toward', 'towards', 'into', 'onto', 'upon', 'within', 'without',
                    'against', 'among', 'between', 'through', 'across', 'around', 'along', 'beyond',
                    'past', 'beneath', 'underneath', 'besides', 'except', 'including', 'concerning',
                    'regarding', 'about', 'above', 'below', 'under', 'over', 'behind', 'in front',
                    'beside', 'next to', 'near', 'far', 'close', 'distant', 'away', 'toward',
                    'towards', 'into', 'onto', 'upon', 'within', 'without', 'against', 'among',
                    'between', 'through', 'across', 'around', 'along', 'beyond', 'past', 'beneath',
                    'underneath', 'besides', 'except', 'including', 'concerning', 'regarding'
                }
                if any(verbo in texto_strip.lower() for verbo in verbos_ingles):
                    return True
            
            # MEJORA 5: Detectar textos con formato especial como {b}texto{/b}
            if '{' in texto_strip and '}' in texto_strip:
                # Si contiene formato, verificar que tenga texto real además del formato
                texto_sin_formato = re.sub(r'\{[^}]+\}', '', texto_strip)
                if any(c.isalpha() for c in texto_sin_formato) and len(texto_sin_formato.strip()) > 2:
                    return True
            
            # MEJORA 6: Detectar textos con URLs o enlaces
            if 'http' in texto_strip.lower() or 'www' in texto_strip.lower():
                # Si contiene URL, verificar que tenga texto descriptivo además de la URL
                texto_sin_url = re.sub(r'https?://[^\s]+', '', texto_strip)
                if any(c.isalpha() for c in texto_sin_url) and len(texto_sin_url.strip()) > 5:
                    return True
            
            # MEJORA 7: Detectar textos con números pero que también contienen palabras
            if any(c.isdigit() for c in texto_strip) and any(c.isalpha() for c in texto_strip):
                # Si contiene números y letras, verificar que tenga suficiente texto
                texto_solo_letras = ''.join(c for c in texto_strip if c.isalpha() or c.isspace())
                if len(texto_solo_letras.strip()) > 3:
                    return True
            
            # Verificar que tenga contenido traducible
            texto_sin_puntuacion = re.sub(r'[^\w\s]', '', texto_strip)
            if any(c.isalpha() for c in texto_sin_puntuacion) and len(texto_sin_puntuacion.strip()) > 2:
                return True
            
            return False

        try:
            with open(self.archivo_entrada, "r", encoding="utf-8") as f_in:
                lineas = f_in.readlines()
        except Exception as e:
            self.log.emit(f"❌ Error al leer archivo: {e}")
            self.terminado.emit(False)
            return
        
        # Corregir errores de sintaxis automáticamente
        self.log.emit("🔧 Verificando y corrigiendo errores de sintaxis...")
        lineas, errores_corregidos = self.corregir_sintaxis_renpy(lineas)
        
        # Procesar bloques de traducción específicos
        self.log.emit("🎯 Procesando bloques de traducción específicos...")
        lineas, bloques_traducidos = self.procesar_bloques_traduccion(lineas)
        
        # Detectar y traducir formato específico con comentarios y líneas vacías
        self.log.emit("🔍 Detectando formato específico de traducción...")
        lineas, formato_especifico_traducido = self.detectar_y_traducir_formato_especifico(lineas)

        total = len(lineas)
        lineas_traducidas_count = 0
        traducciones_usadas = 0
        lineas_omitidas = 0
        tiempo_inicio = time.time()

        # Verificar cuántas traducciones quedan
        traducciones_disponibles = TraductorThread.limite_diario - TraductorThread.contador_traducciones
        self.log.emit(f"📊 Traducciones disponibles: {traducciones_disponibles}")
        self.log.emit(f"📁 Archivo: {os.path.basename(self.archivo_entrada)}")
        self.log.emit(f"📏 Total de líneas: {total}")

        for idx, linea in enumerate(lineas):
            # Verificar si se debe terminar
            if self.terminar:
                self.log.emit("🛑 Traducción terminada por el usuario.")
                break
                
            # Esperar si está pausado
            while self.pausado and not self.terminar:
                time.sleep(0.5)
                
            linea_strip = linea.strip()
            traducida = linea

            contiene_estilo_protegido = any(
                f'"{estilo}"' in linea or f"'{estilo}'" in linea for estilo in estilos_protegidos
            )

            if (
                not linea_strip or
                linea_strip.startswith("#") or
                linea_strip.split()[0] in estilos_protegidos or
                linea_strip.startswith(("define ", "init ", "$", "screen ", "style ", "transform ")) or
                re.match(r'^\s*text\s+[\'"]-\s*[\'"]\s+en\s+retard_blink', linea_strip) or
                contiene_estilo_protegido
            ):
                pass
            elif patron_style_prefix.match(linea):
                pass
            elif patron_traduccion.search(linea):
                # Buscar todos los matches en la línea
                traducida = linea
                for match in patron_traduccion.finditer(linea):
                    texto = match.group(1)
                    if texto.strip() and debe_traducir(texto):
                        # Verificar si quedan traducciones
                        if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                            self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                            break
                        
                        texto_trad = self.traducir_texto(texto)
                        traducida = traducida.replace(f'_("{texto}")', f'_("{texto_trad}")')
                        lineas_traducidas_count += 1
                        traducciones_usadas += 1
                        self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")
            elif patron_traduccion_simple.search(linea):
                # Buscar todos los matches en la línea
                traducida = linea
                for match in patron_traduccion_simple.finditer(linea):
                    texto = match.group(1)
                    if texto.strip() and debe_traducir(texto):
                        # Verificar si quedan traducciones
                        if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                            self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                            break
                        
                        texto_trad = self.traducir_texto(texto)
                        traducida = traducida.replace(f'_("{texto}")', f'_("{texto_trad}")')
                        lineas_traducidas_count += 1
                        traducciones_usadas += 1
                        self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")
            elif patron_dialogo.match(linea):
                m = patron_dialogo.match(linea)
                prefix = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{prefix}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")
            elif patron_linea_comillas.match(linea):
                m = patron_linea_comillas.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")
            elif patron_dialogo_mal_formateado.match(linea):
                # Capturar líneas como: s"texto" o j"texto" (sin espacio después del personaje)
                m = patron_dialogo_mal_formateado.match(linea)
                personaje = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{personaje}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (mal formateado): '{texto}' → '{texto_trad}'")
            elif patron_comillas_mal_formateadas.match(linea):
                # Capturar líneas como: "texto1" "texto2"
                m = patron_comillas_mal_formateadas.match(linea)
                indent = m.group(1)
                texto1 = m.group(3)
                texto2 = m.group(6)
                suffix = m.group(7)
                
                traducida = linea
                if texto1.strip() and debe_traducir(texto1):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto1_trad = self.traducir_texto(texto1)
                    traducida = traducida.replace(f'"{texto1}"', f'"{texto1_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comillas múltiples 1): '{texto1}' → '{texto1_trad}'")
                
                if texto2.strip() and debe_traducir(texto2):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto2_trad = self.traducir_texto(texto2)
                    traducida = traducida.replace(f'"{texto2}"', f'"{texto2_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comillas múltiples 2): '{texto2}' → '{texto2_trad}'")
            elif patron_comillas_sueltas.match(linea):
                # Capturar líneas que solo contienen texto entre comillas
                m = patron_comillas_sueltas.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comillas sueltas): '{texto}' → '{texto_trad}'")
            elif patron_texto_mezclado.match(linea):
                # Capturar líneas con texto mezclado y comillas mal formateadas
                m = patron_texto_mezclado.match(linea)
                indent = m.group(1)
                texto_antes = m.group(2)
                texto_entre_comillas = m.group(4)
                suffix = m.group(5)
                
                traducida = linea
                if texto_entre_comillas.strip() and debe_traducir(texto_entre_comillas):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto_entre_comillas)
                    # Reemplazar solo el texto entre comillas
                    traducida = traducida.replace(f'"{texto_entre_comillas}"', f'"{texto_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto mezclado): '{texto_entre_comillas}' → '{texto_trad}'")
            elif patron_comillas_mal_formateadas_especifico.match(linea):
                # Capturar líneas como: s"texto" "texto2"
                m = patron_comillas_mal_formateadas_especifico.match(linea)
                personaje = m.group(1)
                texto1 = m.group(3)
                texto2 = m.group(6)
                suffix = m.group(7)
                
                traducida = linea
                if texto1.strip() and debe_traducir(texto1):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto1_trad = self.traducir_texto(texto1)
                    traducida = traducida.replace(f'"{texto1}"', f'"{texto1_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comillas múltiples específico 1): '{texto1}' → '{texto1_trad}'")
                
                if texto2.strip() and debe_traducir(texto2):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto2_trad = self.traducir_texto(texto2)
                    traducida = traducida.replace(f'"{texto2}"', f'"{texto2_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comillas múltiples específico 2): '{texto2}' → '{texto2_trad}'")
            elif patron_linea_con_texto_y_comillas.match(linea):
                # Capturar líneas como: "texto" "texto2"
                m = patron_linea_con_texto_y_comillas.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                texto2 = m.group(6)
                suffix = m.group(7)
                
                traducida = linea
                if texto.strip() and debe_traducir(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = traducida.replace(f'"{texto}"', f'"{texto_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comillas dobles): '{texto}' → '{texto_trad}'")
                
                if texto2.strip() and debe_traducir(texto2):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto2_trad = self.traducir_texto(texto2)
                    traducida = traducida.replace(f'"{texto2}"', f'"{texto2_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comillas dobles): '{texto2}' → '{texto2_trad}'")
            elif patron_linea_con_personaje_y_texto.match(linea):
                # Capturar líneas como: personaje "texto"
                m = patron_linea_con_personaje_y_texto.match(linea)
                personaje = m.group(1)
                texto = m.group(4)
                suffix = m.group(5)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{personaje}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (personaje y texto): '{texto}' → '{texto_trad}'")
            elif patron_texto_narrativo.match(linea):
                # Capturar líneas que solo contienen texto narrativo entre comillas
                m = patron_texto_narrativo.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto narrativo): '{texto}' → '{texto_trad}'")
            elif patron_opcion_menu.match(linea):
                # Capturar opciones de menú como: "Sure.":
                m = patron_opcion_menu.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4) + m.group(5)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (opción menú): '{texto}' → '{texto_trad}'")
            elif patron_opcion_menu_sin_dos_puntos.match(linea):
                # Capturar opciones de menú sin dos puntos y agregarlos automáticamente
                m = patron_opcion_menu_sin_dos_puntos.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                
                # Verificar si la siguiente línea es un bloque (indicando que es una opción de menú)
                if idx < len(lineas) - 1:
                    siguiente_linea = lineas[idx + 1].strip()
                    if siguiente_linea and not siguiente_linea.startswith(('"', 'menu', 'label', 'scene', 'show', 'hide', 'pause', 'jump', 'call', 'return')):
                        # Es una opción de menú que necesita dos puntos
                        if texto.strip() and debe_traducir_mejorado(texto):
                            # Verificar si quedan traducciones
                            if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                                self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                                break
                            
                            texto_trad = self.traducir_texto(texto)
                            traducida = f'{indent}"{texto_trad}"{suffix}:\n'
                            lineas_traducidas_count += 1
                            traducciones_usadas += 1
                            self.log.emit(f"🔄 Traduciendo (opción menú corregida): '{texto}' → '{texto_trad}'")
                        else:
                            # Solo agregar los dos puntos sin traducir
                            traducida = f'{indent}"{texto}"{suffix}:\n'
                            self.log.emit(f"🔧 Línea {idx + 1}: Agregados dos puntos a opción de menú")
            elif patron_texto_con_variables.match(linea):
                # Capturar texto que contiene variables como [fmc_name]
                m = patron_texto_con_variables.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con variables): '{texto}' → '{texto_trad}'")
            elif patron_texto_centrado.match(linea):
                # Capturar texto centrado como: centered "texto"
                m = patron_texto_centrado.match(linea)
                prefix = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{prefix}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto centrado): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_formato.match(linea):
                # Capturar texto con formato como {b}texto{/b}
                m = patron_texto_con_formato.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con formato): '{texto}' → '{texto_trad}'")
            elif patron_texto_general.match(linea):
                # Capturar cualquier texto entre comillas que no haya sido detectado por otros patrones
                m = patron_texto_general.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto general): '{texto}' → '{texto_trad}'")
                if texto.strip() and debe_traducir(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{personaje}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (personaje y texto): '{texto}' → '{texto_trad}'")
            elif patron_linea_solo_texto.match(linea):
                # Capturar líneas que solo contienen texto entre comillas
                m = patron_linea_solo_texto.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (solo texto): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_comando.match(linea):
                # Capturar líneas con texto mezclado con comandos de Ren'Py
                m = patron_texto_con_comando.match(linea)
                indent = m.group(1)
                texto_antes = m.group(2)
                texto_entre_comillas = m.group(4)
                comando = m.group(6)
                texto_despues = m.group(7)
                
                traducida = linea
                if texto_entre_comillas.strip() and debe_traducir(texto_entre_comillas):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto_entre_comillas)
                    # Reemplazar solo el texto entre comillas
                    traducida = traducida.replace(f'"{texto_entre_comillas}"', f'"{texto_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con comando): '{texto_entre_comillas}' → '{texto_trad}'")
            elif patron_texto_seguido_comando.match(linea):
                # Capturar líneas con texto seguido de comandos de Ren'Py en la misma línea
                m = patron_texto_seguido_comando.match(linea)
                indent = m.group(1)
                texto_entre_comillas = m.group(3)
                comando = m.group(5)
                texto_despues = m.group(6)
                
                traducida = linea
                if texto_entre_comillas.strip() and debe_traducir(texto_entre_comillas):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto_entre_comillas)
                    # Reemplazar solo el texto entre comillas
                    traducida = traducida.replace(f'"{texto_entre_comillas}"', f'"{texto_trad}"')
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto seguido de comando): '{texto_entre_comillas}' → '{texto_trad}'")
            elif patron_texto_narrativo_ingles.match(linea):
                # Capturar texto narrativo en inglés que empieza con mayúscula
                m = patron_texto_narrativo_ingles.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto narrativo inglés): '{texto}' → '{texto_trad}'")
            elif patron_dialogo_ingles.match(linea):
                # Capturar diálogo en inglés
                m = patron_dialogo_ingles.match(linea)
                indent = m.group(1)
                personaje = m.group(2)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}{personaje} "{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (diálogo inglés): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_verbo_ingles.match(linea):
                # Capturar texto que contiene verbos en inglés
                m = patron_texto_con_verbo_ingles.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    # Verificar si quedan traducciones
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con verbo inglés): '{texto}' → '{texto_trad}'")
            elif 'renpy.input(' in linea:
                # Capturar prompts de input como: renpy.input("Please enter his name.", default = "Jason")
                match = patron_input_prompt.search(linea)
                if match:
                    texto = match.group(1)
                    if texto.strip() and debe_traducir_mejorado(texto):
                        # Verificar si quedan traducciones
                        if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                            self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                            break
                        
                        texto_trad = self.traducir_texto(texto)
                        traducida = linea.replace(f'"{texto}"', f'"{texto_trad}"')
                        lineas_traducidas_count += 1
                        traducciones_usadas += 1
                        self.log.emit(f"🔄 Traduciendo (prompt input): '{texto}' → '{texto_trad}'")
            elif 'renpy.notify(' in linea:
                # Capturar notificaciones como: renpy.notify("Corruption +1")
                match = patron_notification.search(linea)
                if match:
                    texto = match.group(1)
                    if texto.strip() and debe_traducir_mejorado(texto):
                        # Verificar si quedan traducciones
                        if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                            self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                            break
                        
                        texto_trad = self.traducir_texto(texto)
                        traducida = linea.replace(f'"{texto}"', f'"{texto_trad}"')
                        lineas_traducidas_count += 1
                        traducciones_usadas += 1
                        self.log.emit(f"🔄 Traduciendo (notificación): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_variables_renpy.match(linea):
                # Capturar texto con variables como [fmc_name]
                m = patron_texto_con_variables_renpy.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con variables): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_formato_renpy.match(linea):
                # Capturar texto con formato como {b}texto{/b}
                m = patron_texto_con_formato_renpy.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con formato): '{texto}' → '{texto_trad}'")
            elif patron_texto_centrado_ingles.match(linea):
                # Capturar texto centrado en inglés
                m = patron_texto_centrado_ingles.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto centrado): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_url.match(linea):
                # Capturar texto con URLs
                m = patron_texto_con_url.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con URL): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_numeros.match(linea):
                # Capturar texto con números
                m = patron_texto_con_numeros.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con números): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_euros.match(linea):
                # Capturar texto con símbolos de euro
                m = patron_texto_con_euros.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con euros): '{texto}' → '{texto_trad}'")
            elif patron_texto_con_newline.match(linea):
                # Capturar texto con saltos de línea
                m = patron_texto_con_newline.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip() and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (texto con saltos): '{texto}' → '{texto_trad}'")
            
            # NUEVA LÓGICA PARA EL FORMATO ESPECÍFICO DE TRADUCCIÓN
            elif patron_formato_especifico.match(linea):
                # Capturar comentarios con diálogos del formato específico
                m = patron_formato_especifico.match(linea)
                personaje = m.group(1).strip()
                texto = m.group(2).strip()
                
                if texto and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'    # {personaje} "{texto_trad}"\n'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (formato específico): '{texto}' → '{texto_trad}'")
                    
                    # Buscar la línea vacía correspondiente y reemplazarla
                    if idx + 1 < len(lineas):
                        siguiente_linea = lineas[idx + 1].strip()
                        if patron_linea_vacia.match(siguiente_linea):
                            # Reemplazar la línea vacía con la traducción
                            match_vacia = patron_linea_vacia.match(siguiente_linea)
                            personaje_vacio = match_vacia.group(1)
                            lineas[idx + 1] = f'    {personaje_vacio} "{texto_trad}"\n'
                            self.log.emit(f"✅ Línea vacía reemplazada con traducción")
            
            elif patron_linea_vacia.match(linea):
                # Capturar líneas vacías del formato específico
                m = patron_linea_vacia.match(linea)
                personaje = m.group(1)
                
                # Buscar el comentario correspondiente en la línea anterior
                if idx > 0:
                    linea_anterior = lineas[idx - 1].strip()
                    match_comentario = patron_formato_especifico.match(linea_anterior)
                    if match_comentario:
                        texto_original = match_comentario.group(2).strip()
                        if texto_original and debe_traducir_mejorado(texto_original):
                            if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                                self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                                break
                            
                            texto_trad = self.traducir_texto(texto_original)
                            traducida = f'    {personaje} "{texto_trad}"\n'
                            lineas_traducidas_count += 1
                            traducciones_usadas += 1
                            self.log.emit(f"🔄 Traduciendo (línea vacía): '{texto_original}' → '{texto_trad}'")
            
            # LÓGICA MEJORADA PARA EL FORMATO ESPECÍFICO DE TRADUCCIÓN
            elif patron_comentario_traduccion.match(linea):
                # Capturar comentarios con diálogos del formato específico
                m = patron_comentario_traduccion.match(linea)
                personaje = m.group(1).strip()
                texto = m.group(2).strip()
                
                if texto and debe_traducir_mejorado(texto):
                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                        self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                        break
                    
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'    # {personaje} "{texto_trad}"\n'
                    lineas_traducidas_count += 1
                    traducciones_usadas += 1
                    self.log.emit(f"🔄 Traduciendo (comentario): '{texto}' → '{texto_trad}'")
                    
                    # Buscar la línea vacía correspondiente y reemplazarla
                    if idx + 1 < len(lineas):
                        siguiente_linea = lineas[idx + 1].strip()
                        if patron_linea_vacia_traduccion.match(siguiente_linea):
                            # Reemplazar la línea vacía con la traducción
                            match_vacia = patron_linea_vacia_traduccion.match(siguiente_linea)
                            personaje_vacio = match_vacia.group(1)
                            lineas[idx + 1] = f'    {personaje_vacio} "{texto_trad}"\n'
                            self.log.emit(f"✅ Línea vacía reemplazada con traducción")
            
            elif patron_linea_vacia_traduccion.match(linea):
                # Capturar líneas vacías del formato específico
                m = patron_linea_vacia_traduccion.match(linea)
                personaje = m.group(1)
                
                # Buscar el comentario correspondiente en la línea anterior
                if idx > 0:
                    linea_anterior = lineas[idx - 1].strip()
                    match_comentario = patron_comentario_traduccion.match(linea_anterior)
                    if match_comentario:
                        texto_original = match_comentario.group(2).strip()
                        if texto_original and debe_traducir_mejorado(texto_original):
                            if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                                self.log.emit(f"⚠️ Límite alcanzado en línea {idx + 1}. Guardando progreso...")
                                break
                            
                            texto_trad = self.traducir_texto(texto_original)
                            traducida = f'    {personaje} "{texto_trad}"\n'
                            lineas_traducidas_count += 1
                            traducciones_usadas += 1
                            self.log.emit(f"🔄 Traduciendo (línea vacía): '{texto_original}' → '{texto_trad}'")

            lineas_traducidas.append(traducida)
            self.progreso.emit(int((idx + 1) * 100 / total))

        try:
            # Guardar directamente el archivo traducido
            with open(self.archivo_salida, "w", encoding="utf-8") as f_out:
                f_out.writelines(lineas_traducidas)
            
            # Estadísticas finales
            tiempo_total = time.time() - tiempo_inicio
            velocidad = lineas_traducidas_count / tiempo_total if tiempo_total > 0 else 0
            
            self.log.emit(f"✅ Traducción completada: {self.archivo_salida}")
            self.log.emit(f"📊 Estadísticas finales:")
            self.log.emit(f"   • Líneas procesadas: {total}")
            self.log.emit(f"   • Líneas traducidas: {lineas_traducidas_count}")
            self.log.emit(f"   • Líneas omitidas: {total - lineas_traducidas_count}")
            self.log.emit(f"   • Traducciones usadas: {traducciones_usadas}")
            self.log.emit(f"   • Tiempo total: {tiempo_total:.1f} segundos")
            self.log.emit(f"   • Velocidad: {velocidad:.1f} líneas/segundo")
            self.log.emit(f"   • Traducciones restantes: {TraductorThread.limite_diario - TraductorThread.contador_traducciones}")
            
            if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                self.log.emit(f"⚠️ Límite diario alcanzado. Continúa mañana con el resto del archivo.")
            
            self.terminado.emit(True)
        except Exception as e:
            self.log.emit(f"❌ Error al guardar archivo: {e}")
            self.terminado.emit(False)
        except Exception as e:
            self.log.emit(f"❌ Error crítico en traducción: {e}")
            self.terminado.emit(False)

    def mostrar_estadisticas_apis(self):
        """Muestra estadísticas de uso de todas las APIs"""
        self.log.emit(f"📊 Estadísticas de APIs (4 APIs gratuitas verificadas y funcionando):")
        total_traducciones = 0
        apis_activas = 0
        apis_agotadas = 0
        
        for api in self.apis_disponibles:
            if api["activa"]:
                self.log.emit(f"   ✅ {api['nombre']}: {api['contador']}/{api['limite']}")
                total_traducciones += api['contador']
                apis_activas += 1
            else:
                self.log.emit(f"   ❌ {api['nombre']}: Agotada")
                apis_agotadas += 1
        
        self.log.emit(f"📈 Resumen:")
        self.log.emit(f"   • APIs activas: {apis_activas}")
        self.log.emit(f"   • APIs agotadas: {apis_agotadas}")
        self.log.emit(f"   • Total de traducciones: {total_traducciones}")
        self.log.emit(f"   • Capacidad total: ~7,800 traducciones")
        self.log.emit(f"   • Capacidad restante: ~{7_800 - total_traducciones}")

    def corregir_sintaxis_renpy(self, lineas):
        """Corrige automáticamente errores de sintaxis de Ren'Py"""
        lineas_corregidas = []
        errores_corregidos = 0
        
        # Patrones para detectar errores comunes
        patron_opcion_menu = re.compile(r'^(\s*)"([^"]+)"(\s*)$')
        patron_label = re.compile(r'^(\s*label\s+\w+)(\s*)$')
        patron_menu = re.compile(r'^(\s*menu)(\s*)$')
        
        for i, linea in enumerate(lineas):
            linea_strip = linea.strip()
            linea_corregida = linea
            
            # Corregir opciones de menú sin dos puntos
            match = patron_opcion_menu.match(linea_strip)
            if match and not linea_strip.endswith(':'):
                # Verificar si la siguiente línea es un bloque (tiene indentación)
                if i + 1 < len(lineas):
                    siguiente_linea = lineas[i + 1].strip()
                    if siguiente_linea and not siguiente_linea.startswith(('"', 'menu', 'label', 'scene', 'show', 'hide', 'pause', 'jump', 'call', 'return')):
                        # Es una opción de menú que necesita dos puntos
                        linea_corregida = linea.rstrip() + ':\n'
                        errores_corregidos += 1
                        self.log.emit(f"🔧 Línea {i+1}: Corregido opción de menú sin dos puntos")
            
            # Corregir labels sin dos puntos
            match = patron_label.match(linea_strip)
            if match and not linea_strip.endswith(':'):
                linea_corregida = linea.rstrip() + ':\n'
                errores_corregidos += 1
                self.log.emit(f"🔧 Línea {i+1}: Corregido label sin dos puntos")
            
            # Corregir menús sin dos puntos
            match = patron_menu.match(linea_strip)
            if match and not linea_strip.endswith(':'):
                linea_corregida = linea.rstrip() + ':\n'
                errores_corregidos += 1
                self.log.emit(f"🔧 Línea {i+1}: Corregido menú sin dos puntos")
            
            lineas_corregidas.append(linea_corregida)
        
        if errores_corregidos > 0:
            self.log.emit(f"✅ Corregidos {errores_corregidos} errores de sintaxis automáticamente")
        
        return lineas_corregidas, errores_corregidos

    def procesar_bloques_traduccion(self, lineas):
        """Procesa bloques de traducción específicos de Ren'Py"""
        lineas_procesadas = []
        bloques_traducidos = 0
        
        # Patrones para bloques de traducción
        patron_bloque_inicio = re.compile(r'^\s*translate\s+(\w+)\s+(\w+):\s*$')
        patron_comentario_original = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
        patron_linea_vacia = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*""\s*$')
        
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            linea_strip = linea.strip()
            
            # Detectar inicio de bloque de traducción
            match_bloque = patron_bloque_inicio.match(linea_strip)
            if match_bloque:
                self.log.emit(f"🎯 Detectado bloque de traducción: {match_bloque.group(1)} {match_bloque.group(2)}")
                lineas_procesadas.append(linea)
                i += 1
                
                # Procesar el contenido del bloque
                while i < len(lineas):
                    linea_actual = lineas[i]
                    linea_actual_strip = linea_actual.strip()
                    
                    # Si encontramos otro bloque o label, terminar
                    if (linea_actual_strip.startswith('translate ') or 
                        linea_actual_strip.startswith('label ') or
                        (linea_actual_strip and not linea_actual_strip.startswith(('#', '    ', '\t')))):
                        break
                    
                    # Detectar comentario con texto original
                    match_comentario = patron_comentario_original.match(linea_actual_strip)
                    if match_comentario:
                        personaje = match_comentario.group(1)
                        texto_original = match_comentario.group(2)
                        
                        # Verificar si la siguiente línea es una línea vacía
                        if i + 1 < len(lineas):
                            siguiente_linea = lineas[i + 1].strip()
                            match_vacia = patron_linea_vacia.match(siguiente_linea)
                            
                            if match_vacia and match_vacia.group(1) == personaje:
                                # Traducir el texto original
                                if texto_original and self.debe_traducir_mejorado(texto_original):
                                    if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                                        self.log.emit(f"⚠️ Límite alcanzado. Guardando progreso...")
                                        break
                                    
                                    texto_trad = self.traducir_texto(texto_original)
                                    
                                    # Mantener el comentario original
                                    lineas_procesadas.append(linea_actual)
                                    
                                    # Reemplazar la línea vacía con la traducción
                                    linea_traducida = f'    {personaje} "{texto_trad}"\n'
                                    lineas_procesadas.append(linea_traducida)
                                    
                                    bloques_traducidos += 1
                                    self.log.emit(f"🔄 Traducido bloque: '{texto_original}' → '{texto_trad}'")
                                    
                                    i += 2  # Saltar la línea vacía
                                    continue
                        
                        # Si no hay línea vacía correspondiente, mantener como está
                        lineas_procesadas.append(linea_actual)
                    else:
                        # Mantener otras líneas como están
                        lineas_procesadas.append(linea_actual)
                    
                    i += 1
            else:
                # Mantener líneas que no son bloques de traducción
                lineas_procesadas.append(linea)
                i += 1
        
        if bloques_traducidos > 0:
            self.log.emit(f"✅ Procesados {bloques_traducidos} bloques de traducción")
        
        return lineas_procesadas, bloques_traducidos

    def detectar_y_traducir_formato_especifico(self, lineas):
        """Detecta y traduce el formato específico de Ren'Py con comentarios y líneas vacías"""
        lineas_procesadas = []
        traducciones_realizadas = 0
        
        # Patrones para el formato específico
        patron_comentario_original = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
        patron_linea_vacia = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*""\s*$')
        
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            linea_strip = linea.strip()
            
            # Detectar comentario con texto original
            match_comentario = patron_comentario_original.match(linea_strip)
            if match_comentario:
                personaje = match_comentario.group(1)
                texto_original = match_comentario.group(2)
                
                # Verificar si la siguiente línea es una línea vacía del mismo personaje
                if i + 1 < len(lineas):
                    siguiente_linea = lineas[i + 1].strip()
                    match_vacia = patron_linea_vacia.match(siguiente_linea)
                    
                    if match_vacia and match_vacia.group(1) == personaje:
                        # Traducir el texto original
                        if texto_original and self.debe_traducir_mejorado(texto_original):
                            if TraductorThread.contador_traducciones >= TraductorThread.limite_diario:
                                self.log.emit(f"⚠️ Límite alcanzado. Guardando progreso...")
                                break
                            
                            texto_trad = self.traducir_texto(texto_original)
                            
                            # Mantener el comentario original
                            lineas_procesadas.append(linea)
                            
                            # Reemplazar la línea vacía con la traducción
                            linea_traducida = f'    {personaje} "{texto_trad}"\n'
                            lineas_procesadas.append(linea_traducida)
                            
                            traducciones_realizadas += 1
                            self.log.emit(f"🔄 Traducido formato específico: '{texto_original}' → '{texto_trad}'")
                            
                            i += 2  # Saltar la línea vacía
                            continue
                
                # Si no hay línea vacía correspondiente, mantener como está
                lineas_procesadas.append(linea)
            else:
                # Mantener otras líneas como están
                lineas_procesadas.append(linea)
            
            i += 1
        
        if traducciones_realizadas > 0:
            self.log.emit(f"✅ Realizadas {traducciones_realizadas} traducciones en formato específico")
        
        return lineas_procesadas, traducciones_realizadas

    def convertir_a_formato_especifico(self, lineas):
        """Convierte diálogos normales al formato específico con comentarios y líneas vacías"""
        lineas_procesadas = []
        conversiones_realizadas = 0
        
        # Patrones para detectar diálogos normales
        patron_dialogo_normal = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
        
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            linea_strip = linea.strip()
            
            # Detectar diálogo normal
            match_dialogo = patron_dialogo_normal.match(linea_strip)
            if match_dialogo:
                personaje = match_dialogo.group(1)
                texto = match_dialogo.group(2)
                
                                            # Solo convertir si el texto está en inglés y es traducible
                            if texto and self.debe_traducir_mejorado(texto):
                                # Crear comentario con texto original
                                comentario_original = f'    # {personaje} "{texto}"\n'
                                linea_vacia = f'    {personaje} ""\n'
                    
                    lineas_procesadas.append(comentario_original)
                    lineas_procesadas.append(linea_vacia)
                    
                    conversiones_realizadas += 1
                    self.log.emit(f"🔄 Convertido a formato específico: {personaje} - '{texto}'")
                else:
                    # Mantener diálogo como está si no es traducible
                    lineas_procesadas.append(linea)
            else:
                # Mantener otras líneas como están
                lineas_procesadas.append(linea)
            
            i += 1
        
        if conversiones_realizadas > 0:
            self.log.emit(f"✅ Convertidos {conversiones_realizadas} diálogos al formato específico")
        
        return lineas_procesadas, conversiones_realizadas


class ConfiguracionTraductor:
    """Configuración centralizada para el traductor"""
    
    # Límites de APIs (4 APIs gratuitas verificadas y funcionando)
    LIMITES_APIS = {
        "GoogleTranslate": 5000,
        "LingvaTranslate1": 1000,
        "LingvaTranslate2": 1000,
        "MyMemory": 800
    }
    
    # URLs de APIs principales
    URLS_APIS = {
        "GoogleTranslate": "https://translate.googleapis.com/translate_a/single",
        "LingvaTranslate1": "https://lingva.ml/api/v1/en/es/",
        "LingvaTranslate2": "https://lingva.lunar.icu/api/v1/en/es/",
        "MyMemory": "https://api.mymemory.translated.net/get"
    }
    
    # Pausa entre traducciones
    PAUSA_ENTRE_TRADUCCIONES = 1.0
    
    # Elementos que NO se deben traducir
    ELEMENTOS_NO_TRADUCIR = (
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ttf", ".otf", ".woff",
        "gui/", "images/", "audio/", "music/", "sounds/",
        "[", "]", "{", "}", "config.", "gui.", "renpy.",
        "#", "rgb(", "rgba(",
        "define", "init", "transform", "style", "screen",
        "Shift+", "Ctrl+", "Alt+", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        "prefix", "suffix", "hover", "idle", "selected", "insensitive"
    )
    
    # Estilos protegidos
    ESTILOS_PROTEGIDOS = (
        "subtitle", "title", "skip_triangle", "default", "button", "button_text",
        "choice_button", "choice_button_text", "quick_button", "quick_button_text",
        "navigation_button", "narrador", "texto", "menu", "style", "screen"
    )





class TraductorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Traductor y Extractor - Archivos Ren'Py")
        self.setMinimumSize(900, 650)
        self.resize(1000, 750)
        self.setStyleSheet(self.estilo_moderno())
        self.init_ui()
        self.traductor_thread = None
        self.extractor_thread = None

    def estilo_moderno(self):
        return """
        QWidget { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460); 
            color: #e94560; 
            font-family: 'Segoe UI'; 
            font-size: 10pt;
        }
        QLabel { 
            font-weight: bold; 
            color: #f7f7f7;
            font-size: 10pt;
        }
        QLineEdit, QTextEdit {
            background: #222; 
            color: #ffffff; 
            border: 1px solid #444;
            border-radius: 6px; 
            font-size: 10pt; 
            padding: 4px 8px;
            selection-background-color: #533483;
        }
        QComboBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #f4d03f, stop:1 #f39c12);
            color: #000000; 
            font-weight: bold; 
            border-radius: 6px; 
            padding: 6px 12px;
            font-size: 10pt; 
            border: none; 
            margin: 2px;
            min-height: 32px;
            min-width: 80px;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #000000;
            margin-right: 5px;
        }
        QComboBox:focus {
            border: 2px solid #f4d03f;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #f7dc6f, stop:1 #f4d03f);
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #f4d03f;
            background: #1a1a2e;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #f4d03f, stop:1 #f39c12);
            color: #000000; 
            font-weight: bold; 
            border-radius: 6px; 
            padding: 8px 14px;
            font-size: 10pt; 
            border: none; 
            margin: 2px;
            min-height: 32px;
            min-width: 110px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #f7dc6f, stop:1 #f4d03f);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #f39c12, stop:1 #e67e22);
        }
        QPushButton:disabled { 
            background: #2d3748; 
            color: #718096; 
            border: 1px solid #4a5568;
        }
        QProgressBar {
            background: #1e1e1e; 
            color: #ffffff; 
            border: 1px solid #333; 
            border-radius: 5px;
            text-align: center; 
            font-weight: bold;
            font-size: 10pt;
            min-height: 25px;
            padding: 2px;
        }
        QProgressBar::chunk {
            background-color: #f4d03f;
            border-radius: 3px;
        }
        QGroupBox {
            font-weight: bold; 
            border: 2px solid #533483; 
            border-radius: 10px;
            margin-top: 8px; 
            padding-top: 10px;
            padding-bottom: 10px;
            padding-left: 8px;
            padding-right: 8px;
            background: rgba(26, 26, 46, 0.7);
            color: #f7f7f7;
            font-size: 10pt;
            min-height: 130px;
        }
        QGroupBox::title { 
            subcontrol-origin: margin; 
            left: 10px; 
            padding: 0 8px 0 8px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #533483, stop:1 #e94560);
            border-radius: 6px;
            color: #ffffff;
        }
        QScrollBar:vertical {
            background: #16213e;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #533483;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #e94560;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título principal
        titulo = QLabel("🛠️ Traductor y Extractor - Archivos Ren'Py")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #FFD700;
                margin-bottom: 10px;
            }
        """)
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Grupo de extracción
        grupo_extraccion = QGroupBox("📦 Extracción de Archivos RPA/RPYC")
        grupo_extraccion.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                min-height: 120px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        layout_extraccion = QVBoxLayout()
        
        # Seleccionar carpeta de entrada
        hlayout_entrada = QHBoxLayout()
        hlayout_entrada.setSpacing(10)
        hlayout_entrada.setContentsMargins(0, 0, 0, 0)
        
        self.label_entrada = QLabel("Carpeta a extraer:")
        self.label_entrada.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.label_entrada.setMinimumWidth(120)
        hlayout_entrada.addWidget(self.label_entrada)
        
        self.entrada_edit = QLineEdit()
        self.entrada_edit.setPlaceholderText("Selecciona la carpeta con archivos RPA/RPYC...")
        self.entrada_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
                background-color: #3C3C3C;
            }
        """)
        hlayout_entrada.addWidget(self.entrada_edit)
        
        self.btn_entrada = QPushButton("📁 Seleccionar")
        self.btn_entrada.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_entrada.clicked.connect(self.seleccionar_archivo_extraccion)
        hlayout_entrada.addWidget(self.btn_entrada)
        layout_extraccion.addLayout(hlayout_entrada)

        # Seleccionar directorio de salida
        hlayout_salida = QHBoxLayout()
        hlayout_salida.setSpacing(10)
        hlayout_salida.setContentsMargins(0, 0, 0, 0)
        
        self.label_salida = QLabel("Carpeta de destino:")
        self.label_salida.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.label_salida.setMinimumWidth(120)
        hlayout_salida.addWidget(self.label_salida)
        
        self.salida_edit = QLineEdit()
        self.salida_edit.setPlaceholderText("Selecciona donde guardar los archivos extraídos...")
        self.salida_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
                background-color: #3C3C3C;
            }
        """)
        hlayout_salida.addWidget(self.salida_edit)
        
        self.btn_salida = QPushButton("📁 Seleccionar")
        self.btn_salida.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_salida.clicked.connect(self.seleccionar_directorio_extraccion)
        hlayout_salida.addWidget(self.btn_salida)
        layout_extraccion.addLayout(hlayout_salida)

        # Botón de extracción
        self.btn_extraer = QPushButton("🔧 Extraer / Descompilar archivo")
        self.btn_extraer.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_extraer.clicked.connect(self.iniciar_extraccion)
        layout_extraccion.addWidget(self.btn_extraer, alignment=Qt.AlignCenter)
        
        grupo_extraccion.setLayout(layout_extraccion)
        main_layout.addWidget(grupo_extraccion)

        # Grupo de traducción
        grupo_traduccion = QGroupBox("🌐 Traducción de Archivos RPY")
        grupo_traduccion.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                min-height: 200px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        layout_traduccion = QVBoxLayout()

        # Selección de idiomas
        hlayout_idiomas = QHBoxLayout()
        hlayout_idiomas.setSpacing(10)
        hlayout_idiomas.setContentsMargins(0, 0, 0, 0)
        
        self.label_origen = QLabel("Idioma de origen:")
        self.label_origen.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.label_origen.setMinimumWidth(120)
        hlayout_idiomas.addWidget(self.label_origen)
        
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ru"])
        self.combo_origen.setCurrentText("en")
        self.combo_origen.setStyleSheet("""
            QComboBox {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
                min-width: 80px;
            }
            QComboBox:focus {
                border: 2px solid #FFD700;
                background-color: #3C3C3C;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFD700;
                margin-right: 5px;
            }
        """)
        hlayout_idiomas.addWidget(self.combo_origen)
        
        self.label_destino = QLabel("Idioma de destino:")
        self.label_destino.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.label_destino.setMinimumWidth(120)
        hlayout_idiomas.addWidget(self.label_destino)
        
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh", "ru"])
        self.combo_destino.setCurrentText("es")
        self.combo_destino.setStyleSheet("""
            QComboBox {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
                min-width: 80px;
            }
            QComboBox:focus {
                border: 2px solid #FFD700;
                background-color: #3C3C3C;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFD700;
                margin-right: 5px;
            }
        """)
        hlayout_idiomas.addWidget(self.combo_destino)
        layout_traduccion.addLayout(hlayout_idiomas)

        # Selección de archivos
        hlayout_archivos = QHBoxLayout()
        hlayout_archivos.setSpacing(10)
        hlayout_archivos.setContentsMargins(0, 0, 0, 0)
        
        self.label_archivo_entrada = QLabel("Archivo de entrada:")
        self.label_archivo_entrada.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.label_archivo_entrada.setMinimumWidth(120)
        hlayout_archivos.addWidget(self.label_archivo_entrada)
        
        self.archivo_entrada_edit = QLineEdit()
        self.archivo_entrada_edit.setPlaceholderText("Selecciona el archivo RPY a traducir...")
        self.archivo_entrada_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
                background-color: #3C3C3C;
            }
        """)
        hlayout_archivos.addWidget(self.archivo_entrada_edit)
        
        self.btn_archivo_entrada = QPushButton("📁 Seleccionar")
        self.btn_archivo_entrada.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_archivo_entrada.clicked.connect(self.seleccionar_entrada)
        hlayout_archivos.addWidget(self.btn_archivo_entrada)
        layout_traduccion.addLayout(hlayout_archivos)

        hlayout_archivo_salida = QHBoxLayout()
        hlayout_archivo_salida.setSpacing(10)
        hlayout_archivo_salida.setContentsMargins(0, 0, 0, 0)
        
        self.label_archivo_salida = QLabel("Archivo de salida:")
        self.label_archivo_salida.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.label_archivo_salida.setMinimumWidth(120)
        hlayout_archivo_salida.addWidget(self.label_archivo_salida)
        
        self.archivo_salida_edit = QLineEdit()
        self.archivo_salida_edit.setPlaceholderText("Archivo traducido se guardará aquí...")
        self.archivo_salida_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
                background-color: #3C3C3C;
            }
        """)
        hlayout_archivo_salida.addWidget(self.archivo_salida_edit)
        
        self.btn_archivo_salida = QPushButton("📁 Seleccionar")
        self.btn_archivo_salida.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_archivo_salida.clicked.connect(self.seleccionar_salida)
        hlayout_archivo_salida.addWidget(self.btn_archivo_salida)
        layout_traduccion.addLayout(hlayout_archivo_salida)

        # Botones de traducción
        hlayout_botones = QHBoxLayout()
        hlayout_botones.setSpacing(10)
        hlayout_botones.setContentsMargins(0, 0, 0, 0)
        
        self.btn_traducir = QPushButton("🌐 Traducir archivo")
        self.btn_traducir.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_traducir.clicked.connect(self.iniciar_traduccion)
        hlayout_botones.addWidget(self.btn_traducir)
        
        self.btn_pausar = QPushButton("⏸️ Pausar")
        self.btn_pausar.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_pausar.clicked.connect(self.pausar_traduccion)
        self.btn_pausar.setEnabled(False)
        hlayout_botones.addWidget(self.btn_pausar)
        
        self.btn_estructura = QPushButton("🏗️ Crear Estructura")
        self.btn_estructura.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_estructura.clicked.connect(self.crear_estructura_traduccion)
        hlayout_botones.addWidget(self.btn_estructura)
        
        self.btn_formato_especifico = QPushButton("🎯 Formato Específico")
        self.btn_formato_especifico.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_formato_especifico.clicked.connect(self.convertir_a_formato_especifico_archivo)
        hlayout_botones.addWidget(self.btn_formato_especifico)
        
        self.btn_limpiar = QPushButton("🧹 Limpiar registro")
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_limpiar.clicked.connect(self.limpiar_log)
        hlayout_botones.addWidget(self.btn_limpiar)
        
        self.btn_estadisticas = QPushButton("📊 Estadísticas APIs")
        self.btn_estadisticas.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #DAA520;
                color: #000000;
            }
        """)
        self.btn_estadisticas.clicked.connect(self.mostrar_estadisticas_apis)
        hlayout_botones.addWidget(self.btn_estadisticas)
        
        layout_traduccion.addLayout(hlayout_botones)
        
        grupo_traduccion.setLayout(layout_traduccion)
        main_layout.addWidget(grupo_traduccion)



        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)

        # Área de log
        label_log = QLabel("📋 Registro de operaciones:")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(120)
        self.log_area.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 8pt;")
        main_layout.addWidget(label_log)
        main_layout.addWidget(self.log_area)

        # Botones de acción
        hlayout_botones = QHBoxLayout()
        hlayout_botones.setSpacing(8)
        hlayout_botones.setAlignment(Qt.AlignVCenter)
        hlayout_botones.setContentsMargins(0, 4, 0, 4)
        
        self.btn_abrir = QPushButton("📂 Abrir archivo traducido")
        self.btn_abrir.setFixedHeight(32)
        self.btn_abrir.setMinimumWidth(180)
        self.btn_abrir.clicked.connect(self.abrir_archivo_salida)
        self.btn_abrir.setEnabled(False)
        
        btn_limpiar = QPushButton("🧹 Limpiar registro")
        btn_limpiar.setFixedHeight(32)
        btn_limpiar.setMinimumWidth(140)
        btn_limpiar.clicked.connect(self.limpiar_log)
        
        self.btn_estructura = QPushButton("🏗️ Crear Estructura")
        self.btn_estructura.setFixedHeight(32)
        self.btn_estructura.setMinimumWidth(160)
        self.btn_estructura.clicked.connect(self.crear_estructura_traduccion)
        
        hlayout_botones.addWidget(self.btn_abrir)
        hlayout_botones.addWidget(btn_limpiar)
        hlayout_botones.addWidget(self.btn_estructura)
        hlayout_botones.addStretch(1)
        
        main_layout.addLayout(hlayout_botones)

        self.setLayout(main_layout)

    def seleccionar_archivo_extraccion(self):
        dirname = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de entrada")
        if dirname:
            self.entrada_edit.setText(dirname)

    def seleccionar_directorio_extraccion(self):
        dirname = QFileDialog.getExistingDirectory(self, "Seleccionar directorio de salida")
        if dirname:
            self.salida_edit.setText(dirname)

    def seleccionar_entrada(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo .rpy", "", "Archivos Ren'Py (*.rpy);;Todos los archivos (*)")
        if fname:
            self.archivo_entrada_edit.setText(fname)
            base_name = os.path.splitext(fname)[0]
            self.archivo_salida_edit.setText(f"{base_name}_traducido.rpy")
            self.verificar_archivo_salida()

    def seleccionar_salida(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Guardar archivo traducido", "", "Archivos Ren'Py (*.rpy);;Todos los archivos (*)")
        if fname:
            self.archivo_salida_edit.setText(fname)
            self.verificar_archivo_salida()

    def iniciar_extraccion(self):
        carpeta_entrada = self.entrada_edit.text().strip()
        directorio_salida = self.salida_edit.text().strip()
        
        if not carpeta_entrada or not os.path.isdir(carpeta_entrada):
            QMessageBox.warning(self, "Error", "Selecciona una carpeta válida para extraer.")
            return
        if not directorio_salida:
            QMessageBox.warning(self, "Error", "Selecciona un directorio de salida válido.")
            return

        # Verificar qué tipos de archivos hay en la carpeta
        archivos_rpa = []
        archivos_rpyc = []
        
        for archivo in os.listdir(carpeta_entrada):
            if archivo.lower().endswith('.rpa'):
                archivos_rpa.append(archivo)
            elif archivo.lower().endswith('.rpyc'):
                archivos_rpyc.append(archivo)
        
        # Determinar el tipo de archivo a procesar
        if archivos_rpa and archivos_rpyc:
            # Si hay ambos tipos, preguntar al usuario
            respuesta = QMessageBox.question(
                self, 
                "Tipo de archivo", 
                f"Se encontraron {len(archivos_rpa)} archivos RPA y {len(archivos_rpyc)} archivos RPYC.\n\n¿Qué tipo quieres procesar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if respuesta == QMessageBox.Yes:
                tipo_archivo = "RPA"
                self.log_area.append(f"📁 Procesando {len(archivos_rpa)} archivos RPA...")
            else:
                tipo_archivo = "RPYC"
                self.log_area.append(f"📁 Procesando {len(archivos_rpyc)} archivos RPYC...")
        elif archivos_rpa:
            tipo_archivo = "RPA"
            self.log_area.append(f"📁 Procesando {len(archivos_rpa)} archivos RPA...")
        elif archivos_rpyc:
            tipo_archivo = "RPYC"
            self.log_area.append(f"📁 Procesando {len(archivos_rpyc)} archivos RPYC...")
        else:
            QMessageBox.warning(self, "Error", "No se encontraron archivos .rpa o .rpyc en la carpeta seleccionada.")
            return

        self.btn_extraer.setEnabled(False)
        self.actualizar_progreso(0, "Iniciando extracción...")
        self.log_area.append(f"🚀 Iniciando extracción de {tipo_archivo}...")
        
        self.extractor_thread = ExtractorThread(carpeta_entrada, directorio_salida, tipo_archivo)
        self.extractor_thread.progreso.connect(lambda x: self.actualizar_progreso(x, "Extrayendo..."))
        self.extractor_thread.log.connect(self.log_area.append)
        self.extractor_thread.terminado.connect(self.extraccion_terminada)
        self.extractor_thread.start()

    def extraccion_terminada(self, exito, directorio):
        self.btn_extraer.setEnabled(True)
        if exito:
            self.actualizar_progreso(100, "Extracción completada")
            QMessageBox.information(self, "Éxito", f"Extracción completada en:\n{directorio}")
            if QMessageBox.question(self, "Abrir directorio", "¿Quieres abrir el directorio de salida?") == QMessageBox.Yes:
                os.startfile(directorio)
        else:
            self.actualizar_progreso(0, "Error en extracción")
            QMessageBox.critical(self, "Error", "Ocurrió un error durante la extracción.")

    def iniciar_traduccion(self):
        """Inicia el proceso de traducción"""
        try:
            if not self.archivo_entrada_edit.text() or not self.archivo_salida_edit.text():
                QMessageBox.warning(self, "Error", "Por favor selecciona archivo de entrada y salida.")
                return

            if not os.path.exists(self.archivo_entrada_edit.text()):
                QMessageBox.warning(self, "Error", "El archivo de entrada no existe.")
                return

            # Crear directorio de salida si no existe
            directorio_salida = os.path.dirname(self.archivo_salida_edit.text())
            if directorio_salida and not os.path.exists(directorio_salida):
                os.makedirs(directorio_salida)

            self.btn_traducir.setEnabled(False)
            self.btn_pausar.setEnabled(True)
            self.btn_pausar.setText("⏸️ Pausar")

            self.traductor_thread = TraductorThread(
                self.archivo_entrada_edit.text(),
                self.archivo_salida_edit.text(),
                self.combo_origen.currentText(),
                self.combo_destino.currentText()
            )

            self.traductor_thread.progreso.connect(self.actualizar_progreso)
            self.traductor_thread.log.connect(self.log_area.append)
            self.traductor_thread.terminado.connect(self.traduccion_terminada)

            self.traductor_thread.start()
            self.log_area.append("🌐 Iniciando traducción...")
            
        except Exception as e:
            self.log_area.append(f"❌ Error al iniciar traducción: {e}")
            QMessageBox.critical(self, "Error", f"Error al iniciar traducción: {e}")
            self.btn_traducir.setEnabled(True)
            self.btn_pausar.setEnabled(False)

    def traduccion_terminada(self, exito):
        self.btn_traducir.setEnabled(True)
        if exito:
            self.actualizar_progreso(100, "Traducción completada")
            self.btn_abrir.setEnabled(True)
            QMessageBox.information(self, "Listo", "¡Traducción finalizada!")
        else:
            self.actualizar_progreso(0, "Error en traducción")
            QMessageBox.critical(self, "Error", "Ocurrió un error durante la traducción.")

    def abrir_archivo_salida(self):
        archivo = self.archivo_salida_edit.text().strip()
        if archivo and os.path.isfile(archivo):
            os.startfile(archivo)
        else:
            QMessageBox.warning(self, "Error", "El archivo de salida no existe o no se ha especificado.")

    def limpiar_log(self):
        self.log_area.clear()

    def mostrar_estadisticas_apis(self):
        """Muestra estadísticas de uso de todas las APIs"""
        self.log.emit(f"📊 Estadísticas de APIs (4 APIs gratuitas verificadas y funcionando):")
        total_traducciones = 0
        apis_activas = 0
        apis_agotadas = 0
        
        for api in self.apis_disponibles:
            if api["activa"]:
                self.log.emit(f"   ✅ {api['nombre']}: {api['contador']}/{api['limite']}")
                total_traducciones += api['contador']
                apis_activas += 1
            else:
                self.log.emit(f"   ❌ {api['nombre']}: Agotada")
                apis_agotadas += 1
        
        self.log.emit(f"📈 Resumen:")
        self.log.emit(f"   • APIs activas: {apis_activas}")
        self.log.emit(f"   • APIs agotadas: {apis_agotadas}")
        self.log.emit(f"   • Total de traducciones: {total_traducciones}")
        self.log.emit(f"   • Capacidad total: ~7,800 traducciones")
        self.log.emit(f"   • Capacidad restante: ~{7_800 - total_traducciones}")

    def crear_estructura_traduccion(self):
        """Crea una estructura de traducción profesional para Ren'Py."""
        # Obtener el directorio del archivo de entrada
        archivo_entrada = self.archivo_entrada_edit.text().strip()
        if not archivo_entrada or not os.path.isfile(archivo_entrada):
            QMessageBox.warning(self, "Error", "Selecciona un archivo de entrada válido para crear la estructura.")
            return

        directorio_juego = os.path.dirname(archivo_entrada)
        nombre_traduccion = "Eroverse"  # Nombre por defecto

        try:
            # Crear directorio de traducción
            tl_dir = os.path.join(directorio_juego, "tl", nombre_traduccion)
            os.makedirs(tl_dir, exist_ok=True)
            self.log_area.append(f"📁 Creado directorio: {tl_dir}")

            # Crear archivo force_translation.rpy
            force_translation_content = f'''init -999 python:
    old_change_language = renpy.change_language
    def change_language(lang, force=False):
        old_change_language("{nombre_traduccion}",force=False)
    renpy.change_language = change_language
'''
            force_file = os.path.join(directorio_juego, "force_translation.rpy")
            with open(force_file, 'w', encoding='utf-8') as f:
                f.write(force_translation_content)
            self.log_area.append(f"✅ Creado: force_translation.rpy")

            # Crear archivo config_language.rpy
            define_language_content = f'''init python:
   config.language = "{nombre_traduccion}"
   config.default_language = "{nombre_traduccion}"
'''
            define_file = os.path.join(directorio_juego, "config_language.rpy")
            with open(define_file, 'w', encoding='utf-8') as f:
                f.write(define_language_content)
            self.log_area.append(f"✅ Creado: config_language.rpy")

            # Crear archivo strings.rpy
            strings_content = f'''translate {nombre_traduccion} strings:

    # Aquí irán las traducciones de strings
    # Ejemplo:
    # old "MENU"
    # new "MENÚ"
'''
            strings_file = os.path.join(tl_dir, "strings.rpy")
            with open(strings_file, 'w', encoding='utf-8') as f:
                f.write(strings_content)
            self.log_area.append(f"✅ Creado: strings.rpy")

            # Crear archivo dialogue.rpy
            dialogue_content = f'''translate {nombre_traduccion} dialogue:

    # Aquí irán las traducciones de diálogos
    # Ejemplo:
    # old "Hello, how are you?"
    # new "Hola, ¿cómo estás?"
'''
            dialogue_file = os.path.join(tl_dir, "dialogue.rpy")
            with open(dialogue_file, 'w', encoding='utf-8') as f:
                f.write(dialogue_content)
            self.log_area.append(f"✅ Creado: dialogue.rpy")

            # Crear archivo replaceText.rpy básico
            replace_content = f'''init python:
    # Sistema de reemplazo de texto para {nombre_traduccion}
    # Aquí puedes añadir reemplazos automáticos de texto
    
    def replace_text_eroverse(text):
        # Reemplazos automáticos
        replacements = {{
            "Hello": "Hola",
            "Goodbye": "Adiós",
            # Añade más reemplazos aquí
        }}
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
'''
            replace_file = os.path.join(tl_dir, "replaceText.rpy")
            with open(replace_file, 'w', encoding='utf-8') as f:
                f.write(replace_content)
            self.log_area.append(f"✅ Creado: replaceText.rpy")

            QMessageBox.information(self, "Éxito", f"Estructura de traducción creada en:\n{directorio_juego}")
            if QMessageBox.question(self, "Abrir directorio", "¿Quieres abrir el directorio de la estructura?") == QMessageBox.Yes:
                os.startfile(directorio_juego)

        except Exception as e:
            self.log_area.append(f"❌ Error al crear estructura: {e}")
            QMessageBox.critical(self, "Error", f"Ocurrió un error durante la creación de la estructura: {e}")

    def convertir_a_formato_especifico_archivo(self):
        """Convierte un archivo al formato específico de traducción con comentarios y líneas vacías"""
        archivo_entrada = self.archivo_entrada_edit.text().strip()
        if not archivo_entrada or not os.path.isfile(archivo_entrada):
            QMessageBox.warning(self, "Error", "Selecciona un archivo de entrada válido.")
            return

        # Crear nombre de archivo de salida
        nombre_base = os.path.splitext(archivo_entrada)[0]
        archivo_salida = f"{nombre_base}_formato_especifico.rpy"

        try:
            # Leer archivo
            with open(archivo_entrada, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            self.log_area.append(f"🎯 Procesando archivo: {os.path.basename(archivo_entrada)}")
            self.log_area.append(f"📝 Convirtiendo diálogos al formato específico...")

            # Crear thread para el procesamiento
            class FormatoEspecificoThread(QThread):
                progreso = pyqtSignal(int)
                log = pyqtSignal(str)
                terminado = pyqtSignal(bool)

                def __init__(self, lineas, archivo_salida):
                    super().__init__()
                    self.lineas = lineas
                    self.archivo_salida = archivo_salida

                def run(self):
                    try:
                        # Usar la función de conversión
                        lineas_procesadas, conversiones = self.convertir_a_formato_especifico(self.lineas)
                        
                        # Guardar archivo
                        with open(self.archivo_salida, "w", encoding="utf-8") as f:
                            f.writelines(lineas_procesadas)
                        
                        self.log.emit(f"✅ Archivo convertido: {os.path.basename(self.archivo_salida)}")
                        self.log.emit(f"📊 Conversiones realizadas: {conversiones}")
                        self.terminado.emit(True)
                        
                    except Exception as e:
                        self.log.emit(f"❌ Error: {e}")
                        self.terminado.emit(False)

                def convertir_a_formato_especifico(self, lineas):
                    """Convierte diálogos normales al formato específico con comentarios y líneas vacías"""
                    lineas_procesadas = []
                    conversiones_realizadas = 0
                    
                    # Patrones para detectar diálogos normales
                    patron_dialogo_normal = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
                    
                    i = 0
                    while i < len(lineas):
                        linea = lineas[i]
                        linea_strip = linea.strip()
                        
                        # Detectar diálogo normal
                        match_dialogo = patron_dialogo_normal.match(linea_strip)
                        if match_dialogo:
                            personaje = match_dialogo.group(1)
                            texto = match_dialogo.group(2)
                            
                            # Solo convertir si el texto está en inglés y es traducible
                            if texto and self.debe_traducir_mejorado(texto):
                                # Crear comentario con texto original
                                comentario_original = f'    # {personaje} "{texto}"\n'
                                linea_vacia = f'    {personaje} ""\n'
                                
                                lineas_procesadas.append(comentario_original)
                                lineas_procesadas.append(linea_vacia)
                                
                                conversiones_realizadas += 1
                                self.log.emit(f"🔄 Convertido: {personaje} - '{texto}'")
                            else:
                                # Mantener diálogo como está si no es traducible
                                lineas_procesadas.append(linea)
                        else:
                            # Mantener otras líneas como están
                            lineas_procesadas.append(linea)
                        
                        i += 1
                    
                    return lineas_procesadas, conversiones_realizadas

                def debe_traducir_mejorado(self, texto):
                    """Versión simplificada de debe_traducir_mejorado para el thread"""
                    texto_strip = texto.strip()
                    
                    if len(texto_strip) < 2:
                        return False
                    
                    # Verificar que contenga al menos una palabra con letras
                    palabras = texto_strip.split()
                    palabras_con_letras = [p for p in palabras if any(c.isalpha() for c in p)]
                    
                    if not palabras_con_letras:
                        return False
                    
                    # Detectar texto en inglés
                    palabras_ingles = {
                        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
                        'you', 'he', 'she', 'it', 'we', 'they', 'I', 'am', 'is', 'are', 'was', 'were',
                        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                        'can', 'may', 'might', 'must', 'shall', 'being', 'been', 'be'
                    }
                    
                    palabras_texto = set(texto_strip.lower().split())
                    if palabras_texto.intersection(palabras_ingles):
                        return True
                    
                    return False

            # Crear y ejecutar thread
            self.formato_thread = FormatoEspecificoThread(lineas, archivo_salida)
            self.formato_thread.progreso.connect(self.actualizar_progreso)
            self.formato_thread.log.connect(self.log_area.append)
            self.formato_thread.terminado.connect(self.formato_especifico_completado)
            self.formato_thread.start()

        except Exception as e:
            self.log_area.append(f"❌ Error al procesar archivo: {e}")
            QMessageBox.critical(self, "Error", f"Ocurrió un error durante el procesamiento: {e}")

    def formato_especifico_completado(self, exitoso):
        """Maneja la finalización del procesamiento de formato específico"""
        if exitoso:
            QMessageBox.information(self, "Éxito", "Archivo convertido al formato específico exitosamente.")
        else:
            QMessageBox.critical(self, "Error", "Ocurrió un error durante la conversión.")

    def actualizar_progreso(self, valor, texto=""):
        """Actualiza la barra de progreso con valor y texto de estado"""
        self.progress.setValue(valor)
        if valor == 0 and not texto:
            self.progress.setFormat("Esperando archivo...")
        elif texto:
            self.progress.setFormat(f"{texto} - {valor}%")
        else:
            self.progress.setFormat(f"En progreso... - {valor}%")

    def verificar_archivo_salida(self):
        """Verifica si el archivo de salida existe y habilita/deshabilita el botón"""
        archivo = self.archivo_salida_edit.text().strip()
        if archivo and os.path.isfile(archivo):
            self.btn_abrir.setEnabled(True)
        else:
            self.btn_abrir.setEnabled(False)

    def pausar_traduccion(self):
        """Pausa o reanuda la traducción"""
        if hasattr(self, 'traductor_thread') and self.traductor_thread.isRunning():
            if self.btn_pausar.text() == "⏸️ Pausar":
                self.traductor_thread.pausar()
                self.btn_pausar.setText("▶️ Reanudar")
                self.log_area.append("⏸️ Traducción pausada...")
            else:
                self.traductor_thread.reanudar()
                self.btn_pausar.setText("⏸️ Pausar")
                self.log_area.append("▶️ Traducción reanudada...")

    def verificar_cambio_dia(self):
        """Verifica si es un nuevo día y resetea los contadores"""
        import datetime
        hoy = datetime.date.today()
        
        if TraductorThread.ultimo_dia != hoy:
            if TraductorThread.ultimo_dia is not None:
                self.log.emit(f"🔄 Nuevo día detectado: {hoy}. Reseteando contadores...")
            
            # Resetear todos los contadores
            TraductorThread.contador_traducciones = 0
            for api in TraductorThread.apis_disponibles:
                api["contador"] = 0
                api["activa"] = True
            
            TraductorThread.ultimo_dia = hoy
            self.log.emit(f"✅ Contadores reseteados. Todas las APIs disponibles.")
            self.log.emit(f"📊 Límites diarios:")
            for api in TraductorThread.apis_disponibles:
                self.log.emit(f"   • {api['nombre']}: {api['limite']} traducciones")
        else:
            self.log.emit(f"📅 Día actual: {hoy}")
            self.log.emit(f"📊 Contadores actuales:")
            for api in TraductorThread.apis_disponibles:
                if api["contador"] > 0:
                    self.log.emit(f"   • {api['nombre']}: {api['contador']}/{api['limite']}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TraductorGUI()
    gui.show()
    sys.exit(app.exec_()) 
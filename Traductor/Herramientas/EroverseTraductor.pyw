#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import glob

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
    
    def __init__(self, archivo_entrada, archivo_salida, idioma_origen="en", idioma_destino="es"):
        super().__init__()
        self.archivo_entrada = archivo_entrada
        self.archivo_salida = archivo_salida
        self.idioma_origen = idioma_origen
        self.idioma_destino = idioma_destino

    def debe_traducir(self, texto):
        """Verifica si el texto debe ser traducido"""
        texto_strip = texto.strip()
        
        if len(texto_strip) < 2:
            return False
        
        # Verificar que contenga al menos una palabra con letras
        palabras = texto_strip.split()
        palabras_con_letras = [p for p in palabras if any(c.isalpha() for c in p)]
        
        if not palabras_con_letras:
            return False
        
        # Detectar texto en inglés (más permisivo)
        palabras_ingles = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
            'you', 'he', 'she', 'it', 'we', 'they', 'I', 'am', 'is', 'are', 'was', 'were',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'shall', 'being', 'been', 'be',
            'thanks', 'playing', 'hope', 'enjoyed', 'liked', 'game', 'please', 'consider',
            'supporting', 'checking', 'other', 'upcoming', 'shorts', 'coming', 'soon',
            'until', 'next', 'time', 'bye', 'crossing', 'fate', 'visual', 'novel', 'adventure',
            'start', 'load', 'settings', 'quit', 'gary', 'keller'
        }
        
        # Convertir a minúsculas y limpiar puntuación
        texto_limpio = re.sub(r'[^\w\s]', '', texto_strip.lower())
        palabras_texto = set(texto_limpio.split())
        
        # Si contiene palabras en inglés, traducir
        if palabras_texto.intersection(palabras_ingles):
            return True
        
        # Si contiene caracteres ASCII (probablemente inglés), traducir
        if any(ord(c) < 128 for c in texto_strip if c.isalpha()):
            return True
        
        return False

    def traducir_texto(self, texto):
        """Traduce usando múltiples APIs como respaldo"""
        
        # API 1: MyMemory (Principal)
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": texto,
                "langpair": f"{self.idioma_origen}|{self.idioma_destino}"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    traduccion = data["responseData"]["translatedText"]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (MyMemory): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error MyMemory: {e}")

        # API 2: Google Translate (Respaldo 1)
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={self.idioma_origen}&tl={self.idioma_destino}&dt=t&q={texto}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and len(data[0]) > 0:
                    traduccion = data[0][0][0]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (Google): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error Google: {e}")

        # API 3: LibreTranslate (Respaldo 2)
        try:
            url = "https://libretranslate.com/translate"
            data = {
                "q": texto,
                "source": self.idioma_origen,
                "target": self.idioma_destino
            }
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("translatedText"):
                    traduccion = data["translatedText"]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (LibreTranslate): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error LibreTranslate: {e}")

        # API 4: LingvaTranslate (Respaldo 3)
        try:
            url = f"https://lingva.ml/api/v1/{self.idioma_origen}/{self.idioma_destino}/{texto}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("translation"):
                    traduccion = data["translation"]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (Lingva): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error LingvaTranslate: {e}")

        # API 5: Yandex Translate (Respaldo 4)
        try:
            url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
            params = {
                "key": "trnsl.1.1.20231201T000000Z.free",  # Clave gratuita
                "text": texto,
                "lang": f"{self.idioma_origen}-{self.idioma_destino}"
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("text") and len(data["text"]) > 0:
                    traduccion = data["text"][0]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (Yandex): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error Yandex: {e}")

        # API 6: Microsoft Translator (Respaldo 5)
        try:
            url = "https://api.cognitive.microsofttranslator.com/translate"
            params = {
                "api-version": "3.0",
                "from": self.idioma_origen,
                "to": self.idioma_destino
            }
            headers = {
                "Content-Type": "application/json",
                "X-ClientTraceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            }
            body = [{"text": texto}]
            response = requests.post(url, params=params, headers=headers, json=body, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and len(data[0]["translations"]) > 0:
                    traduccion = data[0]["translations"][0]["text"]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (Microsoft): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error Microsoft: {e}")

        # API 7: Apertium (Respaldo 6)
        try:
            url = f"https://apertium.org/apy/translate"
            params = {
                "langpair": f"{self.idioma_origen}|{self.idioma_destino}",
                "q": texto
            }
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseData", {}).get("translatedText"):
                    traduccion = data["responseData"]["translatedText"]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (Apertium): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error Apertium: {e}")

        # API 8: MyMemory (Respaldo alternativo)
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": texto,
                "langpair": f"{self.idioma_destino}|{self.idioma_origen}"  # Inverso
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    traduccion = data["responseData"]["translatedText"]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (MyMemory Inverso): '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error MyMemory Inverso: {e}")

        self.log.emit(f"❌ No se pudo traducir: '{texto[:30]}...'")
        return texto

    def run(self):
        try:
            self.log.emit("🚀 Iniciando traducción...")
            
            # Leer archivo
            with open(self.archivo_entrada, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            
            self.log.emit(f"📁 Archivo leído: {len(lineas)} líneas")
            
            lineas_traducidas = []
            traducciones_realizadas = 0
            
            # Patrones para detectar diálogos
            patron_dialogo = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
            patron_comentario = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
            patron_linea_vacia = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*""\s*$')
            
            # Patrón mejorado para comentarios con texto original
            patron_comentario_mejorado = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
            # Patrón para comentarios sin personaje (como # "Thanks for playing!")
            patron_comentario_sin_personaje = re.compile(r'^\s*#\s*"([^"]*)"\s*$')
            
            # Patrones para detectar bloques translate y strings
            patron_bloque_translate = re.compile(r'^\s*translate\s+(\w+)\s+(\w+):\s*$')
            patron_old_string = re.compile(r'^\s*old\s*"([^"]*)"\s*$')
            patron_new_string = re.compile(r'^\s*new\s*""\s*$')
            patron_string_vacio = re.compile(r'^\s*"([^"]*)"\s*$')
            
            i = 0
            while i < len(lineas):
                try:
                    linea = lineas[i]
                    linea_strip = linea.strip()
                    
                    # Debug: mostrar cada línea procesada
                    if linea_strip and not linea_strip.startswith('#'):
                        self.log.emit(f"🔍 Procesando línea: '{linea_strip[:50]}...'")
                    
                    # Detectar comentario con texto original
                    match_comentario = patron_comentario_mejorado.match(linea_strip)
                    if match_comentario:
                        personaje = match_comentario.group(1)
                        texto_original = match_comentario.group(2)
                        
                        self.log.emit(f"🔍 Detectado comentario: {personaje} = '{texto_original}'")
                        
                        # Verificar si la siguiente línea es una línea vacía del mismo personaje
                        if i + 1 < len(lineas):
                            siguiente_linea = lineas[i + 1].strip()
                            match_vacia = patron_linea_vacia.match(siguiente_linea)
                            
                            if match_vacia and match_vacia.group(1) == personaje:
                                self.log.emit(f"🔍 Línea vacía encontrada para: {personaje}")
                                
                                # Traducir el texto original
                                self.log.emit(f"🔍 Verificando si traducir: '{texto_original}'")
                                if texto_original and self.debe_traducir(texto_original):
                                    texto_trad = self.traducir_texto(texto_original)
                                    
                                    # Mantener el comentario original
                                    lineas_traducidas.append(linea)
                                    
                                    # Reemplazar la línea vacía con la traducción
                                    linea_traducida = f'    {personaje} "{texto_trad}"\n'
                                    lineas_traducidas.append(linea_traducida)
                                    
                                    traducciones_realizadas += 1
                                    self.log.emit(f"🔄 Traducido formato específico: '{texto_original}' → '{texto_trad}'")
                                    
                                    i += 2  # Saltar la línea vacía
                                    continue
                                else:
                                    self.log.emit(f"⚠️ No se debe traducir: '{texto_original}'")
                                    lineas_traducidas.append(linea)
                                    i += 1
                                    continue
                            else:
                                self.log.emit(f"⚠️ No se encontró línea vacía para: {personaje}")
                                lineas_traducidas.append(linea)
                                i += 1
                                continue
                        else:
                            self.log.emit(f"⚠️ No hay siguiente línea para comentario")
                            lineas_traducidas.append(linea)
                            i += 1
                            continue
                        
                        # Si no hay línea vacía correspondiente, mantener como está
                        lineas_traducidas.append(linea)
                        i += 1
                        continue
                
                # Detectar comentario sin personaje (como # "Thanks for playing!")
                match_comentario_sin_personaje = patron_comentario_sin_personaje.match(linea_strip)
                if match_comentario_sin_personaje:
                    texto_original = match_comentario_sin_personaje.group(1)
                    
                    self.log.emit(f"🔍 Detectado comentario sin personaje: '{texto_original}'")
                    
                    # Verificar si la siguiente línea es una línea vacía
                    if i + 1 < len(lineas):
                        siguiente_linea = lineas[i + 1].strip()
                        match_vacia = patron_string_vacio.match(siguiente_linea)
                        
                        if match_vacia and match_vacia.group(1) == '':
                            self.log.emit(f"🔍 Línea vacía encontrada para comentario sin personaje")
                            
                            # Traducir el texto original
                            self.log.emit(f"🔍 Verificando si traducir: '{texto_original}'")
                            if texto_original and self.debe_traducir(texto_original):
                                texto_trad = self.traducir_texto(texto_original)
                                
                                # Mantener el comentario original
                                lineas_traducidas.append(linea)
                                
                                # Reemplazar la línea vacía con la traducción
                                linea_traducida = f'    "{texto_trad}"\n'
                                lineas_traducidas.append(linea_traducida)
                                
                                traducciones_realizadas += 1
                                self.log.emit(f"🔄 Traducido comentario sin personaje: '{texto_original}' → '{texto_trad}'")
                                
                                i += 2  # Saltar la línea vacía
                                continue
                            else:
                                self.log.emit(f"⚠️ No se debe traducir: '{texto_original}'")
                                lineas_traducidas.append(linea)
                                i += 1
                                continue
                        else:
                            self.log.emit(f"⚠️ No se encontró línea vacía para comentario sin personaje")
                            lineas_traducidas.append(linea)
                            i += 1
                            continue
                    else:
                        self.log.emit(f"⚠️ No hay siguiente línea para comentario sin personaje")
                        lineas_traducidas.append(linea)
                        i += 1
                        continue
                    
                    # Si no hay línea vacía correspondiente, mantener como está
                    lineas_traducidas.append(linea)
                    i += 1
                    continue
                else:
                    # Detectar bloques translate
                    match_translate = patron_bloque_translate.match(linea_strip)
                    if match_translate:
                        lineas_traducidas.append(linea)
                        self.log.emit(f"🔍 Detectado bloque translate: {match_translate.group(1)} {match_translate.group(2)}")
                        continue
                    
                    # Detectar old/new strings
                    match_old = patron_old_string.match(linea_strip)
                    if match_old:
                        texto_original = match_old.group(1)
                        lineas_traducidas.append(linea)
                        
                        # Verificar si la siguiente línea es "new """
                        if i + 1 < len(lineas):
                            siguiente_linea = lineas[i + 1].strip()
                            match_new = patron_new_string.match(siguiente_linea)
                            
                            if match_new:
                                # Traducir el texto original
                                self.log.emit(f"🔍 Verificando si traducir string: '{texto_original}'")
                                if texto_original and self.debe_traducir(texto_original):
                                    texto_trad = self.traducir_texto(texto_original)
                                    
                                    # Reemplazar la línea "new "" con la traducción
                                    linea_traducida = f'    new "{texto_trad}"\n'
                                    lineas_traducidas.append(linea_traducida)
                                    
                                    traducciones_realizadas += 1
                                    self.log.emit(f"🔄 Traducido string: '{texto_original}' → '{texto_trad}'")
                                    
                                    i += 1  # Saltar la línea "new"
                                    continue
                                else:
                                    lineas_traducidas.append(lineas[i + 1])
                                    i += 1
                                    continue
                        continue
                    
                    # Detectar strings vacíos (como "Thanks for playing!")
                    match_string_vacio = patron_string_vacio.match(linea_strip)
                    if match_string_vacio:
                        texto_original = match_string_vacio.group(1)
                        
                        if texto_original and self.debe_traducir(texto_original):
                            texto_trad = self.traducir_texto(texto_original)
                            linea_traducida = f'    "{texto_trad}"\n'
                            lineas_traducidas.append(linea_traducida)
                            traducciones_realizadas += 1
                            self.log.emit(f"🔄 Traducido string vacío: '{texto_original}' → '{texto_trad}'")
                        else:
                            lineas_traducidas.append(linea)
                        continue
                    
                    # Detectar diálogo normal
                    match_dialogo = patron_dialogo.match(linea_strip)
                    if match_dialogo:
                        personaje = match_dialogo.group(1)
                        texto = match_dialogo.group(2)
                        
                        if texto and self.debe_traducir(texto):
                            texto_trad = self.traducir_texto(texto)
                            linea_traducida = f'    {personaje} "{texto_trad}"\n'
                            lineas_traducidas.append(linea_traducida)
                            traducciones_realizadas += 1
                        else:
                            lineas_traducidas.append(linea)
                    else:
                        lineas_traducidas.append(linea)
                    
                    i += 1
                    self.progreso.emit(int((i + 1) * 100 / len(lineas)))
                    
                except Exception as e:
                    self.log.emit(f"❌ Error procesando línea {i}: {e}")
                    lineas_traducidas.append(linea)
                    i += 1
                    continue
            
            # Guardar archivo
            with open(self.archivo_salida, "w", encoding="utf-8") as f:
                f.writelines(lineas_traducidas)
            
            self.log.emit(f"✅ Traducción completada: {traducciones_realizadas} traducciones")
            self.terminado.emit(True)
            
        except Exception as e:
            self.log.emit(f"❌ Error crítico: {e}")
            self.terminado.emit(False)

class TraductorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Traductor Ren'Py - Versión Corregida")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grupo de extracción
        grupo_extraccion = QGroupBox("📦 Extracción de Archivos")
        layout_extraccion = QVBoxLayout()
        
        # Carpeta de entrada para extracción
        hlayout_carpeta_entrada = QHBoxLayout()
        self.carpeta_entrada_edit = QLineEdit()
        self.carpeta_entrada_edit.setPlaceholderText("Carpeta con archivos RPA/RPYC")
        btn_carpeta_entrada = QPushButton("📁 Seleccionar")
        btn_carpeta_entrada.clicked.connect(self.seleccionar_carpeta_entrada)
        hlayout_carpeta_entrada.addWidget(QLabel("Carpeta de entrada:"))
        hlayout_carpeta_entrada.addWidget(self.carpeta_entrada_edit)
        hlayout_carpeta_entrada.addWidget(btn_carpeta_entrada)
        layout_extraccion.addLayout(hlayout_carpeta_entrada)
        
        # Carpeta de salida para extracción
        hlayout_carpeta_salida = QHBoxLayout()
        self.carpeta_salida_edit = QLineEdit()
        self.carpeta_salida_edit.setPlaceholderText("Carpeta de salida para archivos extraídos")
        btn_carpeta_salida = QPushButton("📁 Seleccionar")
        btn_carpeta_salida.clicked.connect(self.seleccionar_carpeta_salida)
        hlayout_carpeta_salida.addWidget(QLabel("Carpeta de salida:"))
        hlayout_carpeta_salida.addWidget(self.carpeta_salida_edit)
        hlayout_carpeta_salida.addWidget(btn_carpeta_salida)
        layout_extraccion.addLayout(hlayout_carpeta_salida)
        
        # Tipo de archivo
        hlayout_tipo = QHBoxLayout()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["RPA", "RPYC"])
        hlayout_tipo.addWidget(QLabel("Tipo de archivo:"))
        hlayout_tipo.addWidget(self.combo_tipo)
        layout_extraccion.addLayout(hlayout_tipo)
        
        # Botón de extracción
        self.btn_extraer = QPushButton("📦 Extraer Archivos")
        self.btn_extraer.clicked.connect(self.iniciar_extraccion)
        layout_extraccion.addWidget(self.btn_extraer)
        
        grupo_extraccion.setLayout(layout_extraccion)
        layout.addWidget(grupo_extraccion)
        
        # Grupo de archivos para traducción
        grupo_archivos = QGroupBox("📁 Archivos para Traducción")
        layout_archivos = QVBoxLayout()
        
        # Archivo de entrada
        hlayout_entrada = QHBoxLayout()
        self.archivo_entrada_edit = QLineEdit()
        self.archivo_entrada_edit.setPlaceholderText("Archivo de entrada (.rpy)")
        btn_entrada = QPushButton("📁 Seleccionar")
        btn_entrada.clicked.connect(self.seleccionar_entrada)
        hlayout_entrada.addWidget(QLabel("Archivo de entrada:"))
        hlayout_entrada.addWidget(self.archivo_entrada_edit)
        hlayout_entrada.addWidget(btn_entrada)
        layout_archivos.addLayout(hlayout_entrada)
        
        # Archivo de salida
        hlayout_salida = QHBoxLayout()
        self.archivo_salida_edit = QLineEdit()
        self.archivo_salida_edit.setPlaceholderText("Archivo de salida (.rpy)")
        btn_salida = QPushButton("📁 Seleccionar")
        btn_salida.clicked.connect(self.seleccionar_salida)
        hlayout_salida.addWidget(QLabel("Archivo de salida:"))
        hlayout_salida.addWidget(self.archivo_salida_edit)
        hlayout_salida.addWidget(btn_salida)
        layout_archivos.addLayout(hlayout_salida)
        
        grupo_archivos.setLayout(layout_archivos)
        layout.addWidget(grupo_archivos)
        
        # Grupo de idiomas
        grupo_idiomas = QGroupBox("🌐 Idiomas")
        layout_idiomas = QHBoxLayout()
        
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(["en", "es", "fr", "de", "it", "pt"])
        self.combo_origen.setCurrentText("en")
        
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt"])
        self.combo_destino.setCurrentText("es")
        
        layout_idiomas.addWidget(QLabel("Idioma origen:"))
        layout_idiomas.addWidget(self.combo_origen)
        layout_idiomas.addWidget(QLabel("Idioma destino:"))
        layout_idiomas.addWidget(self.combo_destino)
        
        grupo_idiomas.setLayout(layout_idiomas)
        layout.addWidget(grupo_idiomas)
        
        # Botones
        hlayout_botones = QHBoxLayout()
        
        self.btn_traducir = QPushButton("🚀 Traducir")
        self.btn_traducir.clicked.connect(self.iniciar_traduccion)
        hlayout_botones.addWidget(self.btn_traducir)
        
        self.btn_limpiar = QPushButton("🧹 Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_log)
        hlayout_botones.addWidget(self.btn_limpiar)
        
        layout.addLayout(hlayout_botones)
        
        # Barra de progreso
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        self.setLayout(layout)

    def seleccionar_carpeta_entrada(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta con archivos RPA/RPYC")
        if carpeta:
            self.carpeta_entrada_edit.setText(carpeta)

    def seleccionar_carpeta_salida(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if carpeta:
            self.carpeta_salida_edit.setText(carpeta)

    def seleccionar_entrada(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de entrada", "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.archivo_entrada_edit.setText(archivo)
            # Auto-generar archivo de salida
            nombre_base = os.path.splitext(archivo)[0]
            self.archivo_salida_edit.setText(f"{nombre_base}_traducido.rpy")

    def seleccionar_salida(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar archivo de salida", "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.archivo_salida_edit.setText(archivo)

    def iniciar_extraccion(self):
        try:
            if not self.carpeta_entrada_edit.text() or not self.carpeta_salida_edit.text():
                QMessageBox.warning(self, "Error", "Selecciona carpeta de entrada y salida.")
                return

            if not os.path.exists(self.carpeta_entrada_edit.text()):
                QMessageBox.warning(self, "Error", "La carpeta de entrada no existe.")
                return

            # Crear directorio de salida si no existe
            if not os.path.exists(self.carpeta_salida_edit.text()):
                os.makedirs(self.carpeta_salida_edit.text())

            self.btn_extraer.setEnabled(False)
            self.progress.setValue(0)

            self.extractor_thread = ExtractorThread(
                self.carpeta_entrada_edit.text(),
                self.carpeta_salida_edit.text(),
                self.combo_tipo.currentText()
            )

            self.extractor_thread.progreso.connect(self.progress.setValue)
            self.extractor_thread.log.connect(self.log_area.append)
            self.extractor_thread.terminado.connect(self.extraccion_terminada)

            self.extractor_thread.start()
            self.log_area.append("📦 Iniciando extracción...")
            
        except Exception as e:
            self.log_area.append(f"❌ Error al iniciar extracción: {e}")
            QMessageBox.critical(self, "Error", f"Error al iniciar extracción: {e}")
            self.btn_extraer.setEnabled(True)

    def extraccion_terminada(self, exito, directorio):
        self.btn_extraer.setEnabled(True)
        if exito:
            self.progress.setValue(100)
            QMessageBox.information(self, "Éxito", f"¡Extracción completada!\nArchivos extraídos en: {directorio}")
        else:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error", "Error en la extracción.")

    def iniciar_traduccion(self):
        try:
            if not self.archivo_entrada_edit.text() or not self.archivo_salida_edit.text():
                QMessageBox.warning(self, "Error", "Selecciona archivo de entrada y salida.")
                return

            if not os.path.exists(self.archivo_entrada_edit.text()):
                QMessageBox.warning(self, "Error", "El archivo de entrada no existe.")
                return

            # Crear directorio de salida si no existe
            directorio_salida = os.path.dirname(self.archivo_salida_edit.text())
            if directorio_salida and not os.path.exists(directorio_salida):
                os.makedirs(directorio_salida)

            self.btn_traducir.setEnabled(False)
            self.progress.setValue(0)

            self.traductor_thread = TraductorThread(
                self.archivo_entrada_edit.text(),
                self.archivo_salida_edit.text(),
                self.combo_origen.currentText(),
                self.combo_destino.currentText()
            )

            self.traductor_thread.progreso.connect(self.progress.setValue)
            self.traductor_thread.log.connect(self.log_area.append)
            self.traductor_thread.terminado.connect(self.traduccion_terminada)

            self.traductor_thread.start()
            self.log_area.append("🌐 Iniciando traducción...")
            
        except Exception as e:
            self.log_area.append(f"❌ Error al iniciar traducción: {e}")
            QMessageBox.critical(self, "Error", f"Error al iniciar traducción: {e}")
            self.btn_traducir.setEnabled(True)

    def traduccion_terminada(self, exito):
        self.btn_traducir.setEnabled(True)
        if exito:
            self.progress.setValue(100)
            QMessageBox.information(self, "Éxito", "¡Traducción completada!")
        else:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error", "Error en la traducción.")

    def limpiar_log(self):
        self.log_area.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TraductorGUI()
    gui.show()
    sys.exit(app.exec_()) 
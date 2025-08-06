#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import requests
import subprocess
import glob
import time
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QMessageBox, QComboBox, QGroupBox, QFrame,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage

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
        """Traduce usando múltiples APIs con fallback"""
        apis = [
            # MyMemory API
            {
                "name": "MyMemory",
                "url": "https://api.mymemory.translated.net/get",
                "params": lambda t: {"q": t, "langpair": f"{self.idioma_origen}|{self.idioma_destino}"},
                "extract": lambda r: r.json().get("responseData", {}).get("translatedText")
            },
            # Google Translate API (simulado)
            {
                "name": "Google Translate",
                "url": "https://translate.googleapis.com/translate_a/single",
                "params": lambda t: {"client": "gtx", "sl": self.idioma_origen, "tl": self.idioma_destino, "dt": "t", "q": t},
                "extract": lambda r: r.json()[0][0][0] if r.json() and r.json()[0] else None
            },
            # LibreTranslate API
            {
                "name": "LibreTranslate",
                "url": "https://libretranslate.de/translate",
                "params": lambda t: {"q": t, "source": self.idioma_origen, "target": self.idioma_destino},
                "extract": lambda r: r.json().get("translatedText")
            },
            # LingvaTranslate API
            {
                "name": "LingvaTranslate",
                "url": f"https://lingva.ml/api/v1/{self.idioma_origen}/{self.idioma_destino}/{requests.utils.quote(texto)}",
                "params": lambda t: {},
                "extract": lambda r: r.json().get("translation")
            },
            # Yandex Translate API
            {
                "name": "Yandex",
                "url": "https://translate.yandex.net/api/v1.5/tr.json/translate",
                "params": lambda t: {"key": "trnsl.1.1.20200101T000000Z.1234567890abcdef", "text": t, "lang": f"{self.idioma_origen}-{self.idioma_destino}"},
                "extract": lambda r: r.json().get("text", [None])[0]
            },
            # Microsoft Translator API
            {
                "name": "Microsoft",
                "url": "https://api.cognitive.microsofttranslator.com/translate",
                "params": lambda t: {"api-version": "3.0", "from": self.idioma_origen, "to": self.idioma_destino},
                "headers": {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "your_key_here"},
                "data": lambda t: [{"text": t}],
                "extract": lambda r: r.json()[0]["translations"][0]["text"]
            },
            # Apertium API
            {
                "name": "Apertium",
                "url": "https://apertium.org/apy/translate",
                "params": lambda t: {"langpair": f"{self.idioma_origen}|{self.idioma_destino}", "q": t},
                "extract": lambda r: r.json().get("responseData", {}).get("translatedText")
            }
        ]
        
        for api in apis:
            try:
                if api["name"] == "Microsoft":
                    # Microsoft requiere POST con JSON
                    response = requests.post(
                        api["url"],
                        params=api["params"](texto),
                        headers=api.get("headers", {}),
                        json=api["data"](texto),
                        timeout=5
                    )
                else:
                    # Otros APIs usan GET
                    response = requests.get(
                        api["url"],
                        params=api["params"](texto),
                        timeout=5
                    )
                
                if response.status_code == 200:
                    traduccion = api["extract"](response)
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido con {api['name']}: '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
                        
            except Exception as e:
                self.log.emit(f"⚠️ Error con {api['name']}: {e}")
                continue
        
        self.log.emit(f"❌ No se pudo traducir: '{texto[:30]}...'")
        return texto

    def run(self):
        try:
            self.log.emit("🚀 Iniciando traducción...")
            
            # Leer archivo
            with open(self.archivo_entrada, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            
            self.log.emit(f"📁 Archivo leído: {len(lineas)} líneas")
            
            # PRIMERA PASADA: Eliminar líneas "new "" vacías
            lineas_limpias = []
            i = 0
            while i < len(lineas):
                linea = lineas[i]
                linea_strip = linea.strip()
                
                # Detectar línea "new "" y eliminarla
                if re.match(r'^\s*new\s*""\s*$', linea_strip):
                    self.log.emit(f"🗑️ Eliminando línea vacía: {linea_strip}")
                    i += 1
                    continue
                
                lineas_limpias.append(linea)
                i += 1
            
            self.log.emit(f"🧹 Archivo limpiado: {len(lineas_limpias)} líneas")
            
            lineas_traducidas = []
            traducciones_realizadas = 0
            
            # Patrones para detectar diferentes tipos de líneas
            patron_dialogo = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
            patron_comentario = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$')
            patron_linea_vacia = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*""\s*$')
            patron_old_string = re.compile(r'^\s*old\s*"([^"]*)"\s*$')
            patron_new_string = re.compile(r'^\s*new\s*""\s*$')
            patron_comentario_sin_personaje = re.compile(r'^\s*#\s*"([^"]*)"\s*$')
            patron_string_vacio = re.compile(r'^\s*"([^"]*)"\s*$')
            
            i = 0
            while i < len(lineas_limpias):
                try:
                    linea = lineas_limpias[i]
                    linea_strip = linea.strip()
                    
                    # Detectar comentario con texto original
                    match_comentario = patron_comentario.match(linea_strip)
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
                                if texto_original and self.debe_traducir(texto_original):
                                    texto_trad = self.traducir_texto(texto_original)
                                    
                                    # Mantener el comentario original
                                    lineas_traducidas.append(linea)
                                    
                                    # Reemplazar la línea vacía con la traducción
                                    # Mantener etiquetas de texto en minúsculas
                                    texto_trad_limpio = texto_trad.replace('{I}', '{i}').replace('{/I}', '{/i}')
                                    linea_traducida = f'    {personaje} "{texto_trad_limpio}"\n'
                                    lineas_traducidas.append(linea_traducida)
                                    
                                    traducciones_realizadas += 1
                                    self.log.emit(f"🔄 Traducido formato específico: '{texto_original}' → '{texto_trad}'")
                                    
                                    i += 2  # Saltar la línea vacía
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
                                if texto_original and self.debe_traducir(texto_original):
                                    texto_trad = self.traducir_texto(texto_original)
                                    
                                    # Mantener el comentario original
                                    lineas_traducidas.append(linea)
                                    
                                    # Reemplazar la línea vacía con la traducción
                                    # Mantener etiquetas de texto en minúsculas
                                    texto_trad_limpio = texto_trad.replace('{I}', '{i}').replace('{/I}', '{/i}')
                                    linea_traducida = f'    "{texto_trad_limpio}"\n'
                                    lineas_traducidas.append(linea_traducida)
                                    
                                    traducciones_realizadas += 1
                                    self.log.emit(f"🔄 Traducido comentario sin personaje: '{texto_original}' → '{texto_trad}'")
                                    
                                    i += 2  # Saltar la línea vacía
                                    continue
                        
                        # Si no hay línea vacía correspondiente, mantener como está
                        lineas_traducidas.append(linea)
                        i += 1
                        continue
                    
                    # Detectar old/new strings
                    match_old = patron_old_string.match(linea_strip)
                    if match_old:
                        texto_original = match_old.group(1)
                        lineas_traducidas.append(linea)  # Agregar línea 'old'
                        
                        # Traducir el texto original
                        if texto_original and self.debe_traducir(texto_original):
                            texto_trad = self.traducir_texto(texto_original)
                            
                            # AGREGAR la línea "new" con la traducción (SIN líneas vacías)
                            # Mantener etiquetas de texto en minúsculas
                            texto_trad_limpio = texto_trad.replace('{I}', '{i}').replace('{/I}', '{/i}')
                            linea_traducida = f'    new "{texto_trad_limpio}"\n'
                            lineas_traducidas.append(linea_traducida)
                            
                            traducciones_realizadas += 1
                            self.log.emit(f"🔄 Traducido string: '{texto_original}' → '{texto_trad}'")
                        else:
                            # Si no se debe traducir, agregar línea "new" vacía
                            linea_vacia = f'    new ""\n'
                            lineas_traducidas.append(linea_vacia)
                        
                        i += 1
                        continue
                    
                    # Detectar strings vacíos (como "Thanks for playing!")
                    match_string_vacio = patron_string_vacio.match(linea_strip)
                    if match_string_vacio:
                        texto_original = match_string_vacio.group(1)
                        
                        if texto_original and self.debe_traducir(texto_original):
                            texto_trad = self.traducir_texto(texto_original)
                            # Mantener etiquetas de texto en minúsculas
                            texto_trad_limpio = texto_trad.replace('{I}', '{i}').replace('{/I}', '{/i}')
                            linea_traducida = f'    "{texto_trad_limpio}"\n'
                            lineas_traducidas.append(linea_traducida)
                            traducciones_realizadas += 1
                            self.log.emit(f"🔄 Traducido string vacío: '{texto_original}' → '{texto_trad}'")
                        else:
                            lineas_traducidas.append(linea)
                        i += 1
                        continue
                    
                    # Detectar diálogo normal
                    match_dialogo = patron_dialogo.match(linea_strip)
                    if match_dialogo:
                        personaje = match_dialogo.group(1)
                        texto = match_dialogo.group(2)
                        
                        if texto and self.debe_traducir(texto):
                            texto_trad = self.traducir_texto(texto)
                            # Mantener etiquetas de texto en minúsculas
                            texto_trad_limpio = texto_trad.replace('{I}', '{i}').replace('{/I}', '{/i}')
                            linea_traducida = f'    {personaje} "{texto_trad_limpio}"\n'
                            lineas_traducidas.append(linea_traducida)
                            traducciones_realizadas += 1
                        else:
                            lineas_traducidas.append(linea)
                    else:
                        lineas_traducidas.append(linea)
                    
                    i += 1
                    self.progreso.emit(int((i + 1) * 100 / len(lineas_limpias)))
                    
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

class ExtractorThread(QThread):
    progreso = pyqtSignal(int)
    log = pyqtSignal(str)
    terminado = pyqtSignal(bool)

    def __init__(self, archivo_entrada, carpeta_salida, tipo_archivo):
        super().__init__()
        self.archivo_entrada = archivo_entrada
        self.carpeta_salida = carpeta_salida
        self.tipo_archivo = tipo_archivo

    def run(self):
        try:
            self.log.emit(f"🚀 Iniciando extracción de {self.tipo_archivo}...")
            
            if self.tipo_archivo == "RPA":
                # Extraer archivo RPA usando unrpa
                comando = [
                    sys.executable, "-m", "unrpa", 
                    "-p", self.carpeta_salida,
                    self.archivo_entrada
                ]
            else:  # RPYC
                # Extraer archivo RPYC usando unrpyc
                comando = [
                    sys.executable, "unrpyc.py",
                    self.archivo_entrada,
                    "-o", self.carpeta_salida
                ]
            
            self.log.emit(f"🔧 Ejecutando: {' '.join(comando)}")
            
            proceso = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitorear progreso
            while True:
                salida = proceso.stdout.readline()
                if salida == '' and proceso.poll() is not None:
                    break
                if salida:
                    self.log.emit(f"📝 {salida.strip()}")
                    self.progreso.emit(50)  # Progreso simulado
            
            codigo_salida = proceso.poll()
            
            if codigo_salida == 0:
                self.log.emit(f"✅ Extracción completada exitosamente")
                self.terminado.emit(True)
            else:
                error = proceso.stderr.read()
                self.log.emit(f"❌ Error en extracción: {error}")
                self.terminado.emit(False)
                
        except Exception as e:
            self.log.emit(f"❌ Error crítico: {e}")
            self.terminado.emit(False)

class TraductorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Traductor Ren'Py - Versión Completa")
        self.setMinimumSize(1000, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grupo de extracción
        grupo_extraccion = QGroupBox("📦 Extracción de Archivos")
        layout_extraccion = QVBoxLayout()
        
        # Archivo RPA/RPYC de entrada
        hlayout_extraccion_entrada = QHBoxLayout()
        self.archivo_extraccion_edit = QLineEdit()
        self.archivo_extraccion_edit.setPlaceholderText("Archivo .rpa o .rpyc a extraer")
        btn_extraccion_entrada = QPushButton("📁 Seleccionar")
        btn_extraccion_entrada.clicked.connect(self.seleccionar_archivo_extraccion)
        hlayout_extraccion_entrada.addWidget(QLabel("Archivo a extraer:"))
        hlayout_extraccion_entrada.addWidget(self.archivo_extraccion_edit)
        hlayout_extraccion_entrada.addWidget(btn_extraccion_entrada)
        layout_extraccion.addLayout(hlayout_extraccion_entrada)
        
        # Carpeta de salida para extracción
        hlayout_extraccion_salida = QHBoxLayout()
        self.carpeta_extraccion_edit = QLineEdit()
        self.carpeta_extraccion_edit.setPlaceholderText("Carpeta donde extraer")
        btn_extraccion_salida = QPushButton("📁 Seleccionar")
        btn_extraccion_salida.clicked.connect(self.seleccionar_carpeta_extraccion)
        hlayout_extraccion_salida.addWidget(QLabel("Carpeta de salida:"))
        hlayout_extraccion_salida.addWidget(self.carpeta_extraccion_edit)
        hlayout_extraccion_salida.addWidget(btn_extraccion_salida)
        layout_extraccion.addLayout(hlayout_extraccion_salida)
        
        # Botones de extracción
        hlayout_botones_extraccion = QHBoxLayout()
        self.btn_extraer_rpa = QPushButton("📦 Extraer RPA")
        self.btn_extraer_rpa.clicked.connect(self.iniciar_extraccion_rpa)
        self.btn_extraer_rpyc = QPushButton("📦 Extraer RPYC")
        self.btn_extraer_rpyc.clicked.connect(self.iniciar_extraccion_rpyc)
        hlayout_botones_extraccion.addWidget(self.btn_extraer_rpa)
        hlayout_botones_extraccion.addWidget(self.btn_extraer_rpyc)
        layout_extraccion.addLayout(hlayout_botones_extraccion)
        
        grupo_extraccion.setLayout(layout_extraccion)
        layout.addWidget(grupo_extraccion)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Grupo de traducción
        grupo_traduccion = QGroupBox("🌐 Traducción de Archivos")
        layout_traduccion = QVBoxLayout()
        
        # Archivo de entrada
        hlayout_entrada = QHBoxLayout()
        self.archivo_entrada_edit = QLineEdit()
        self.archivo_entrada_edit.setPlaceholderText("Archivo .rpy a traducir")
        btn_entrada = QPushButton("📁 Seleccionar")
        btn_entrada.clicked.connect(self.seleccionar_archivo_entrada)
        hlayout_entrada.addWidget(QLabel("Archivo de entrada:"))
        hlayout_entrada.addWidget(self.archivo_entrada_edit)
        hlayout_entrada.addWidget(btn_entrada)
        layout_traduccion.addLayout(hlayout_entrada)
        
        # Archivo de salida
        hlayout_salida = QHBoxLayout()
        self.archivo_salida_edit = QLineEdit()
        self.archivo_salida_edit.setPlaceholderText("Archivo .rpy traducido")
        btn_salida = QPushButton("📁 Seleccionar")
        btn_salida.clicked.connect(self.seleccionar_archivo_salida)
        hlayout_salida.addWidget(QLabel("Archivo de salida:"))
        hlayout_salida.addWidget(self.archivo_salida_edit)
        hlayout_salida.addWidget(btn_salida)
        layout_traduccion.addLayout(hlayout_salida)
        
        # Idiomas
        hlayout_idiomas = QHBoxLayout()
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(["en", "es", "fr", "de", "it", "pt"])
        self.combo_origen.setCurrentText("en")
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt"])
        self.combo_destino.setCurrentText("es")
        hlayout_idiomas.addWidget(QLabel("Idioma origen:"))
        hlayout_idiomas.addWidget(self.combo_origen)
        hlayout_idiomas.addWidget(QLabel("Idioma destino:"))
        hlayout_idiomas.addWidget(self.combo_destino)
        layout_traduccion.addLayout(hlayout_idiomas)
        
        # Botón traducir
        self.btn_traducir = QPushButton("🚀 Traducir")
        self.btn_traducir.clicked.connect(self.iniciar_traduccion)
        layout_traduccion.addWidget(self.btn_traducir)
        
        grupo_traduccion.setLayout(layout_traduccion)
        layout.addWidget(grupo_traduccion)
        
        # Barra de progreso
        self.progreso_bar = QProgressBar()
        layout.addWidget(self.progreso_bar)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)

    def seleccionar_archivo_extraccion(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar archivo a extraer", 
            "", 
            "Archivos Ren'Py (*.rpa *.rpyc);;Archivos RPA (*.rpa);;Archivos RPYC (*.rpyc)"
        )
        if archivo:
            self.archivo_extraccion_edit.setText(archivo)

    def seleccionar_carpeta_extraccion(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if carpeta:
            self.carpeta_extraccion_edit.setText(carpeta)

    def seleccionar_archivo_entrada(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo .rpy", "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.archivo_entrada_edit.setText(archivo)

    def seleccionar_archivo_salida(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar archivo traducido", "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.archivo_salida_edit.setText(archivo)

    def iniciar_extraccion_rpa(self):
        archivo = self.archivo_extraccion_edit.text()
        carpeta = self.carpeta_extraccion_edit.text()
        
        if not archivo or not carpeta:
            QMessageBox.warning(self, "Error", "Por favor selecciona archivo y carpeta de salida")
            return
        
        if not os.path.exists(archivo):
            QMessageBox.warning(self, "Error", "El archivo de entrada no existe")
            return
        
        self.btn_extraer_rpa.setEnabled(False)
        self.btn_extraer_rpyc.setEnabled(False)
        self.progreso_bar.setValue(0)
        self.log_text.clear()
        
        self.extractor_thread = ExtractorThread(archivo, carpeta, "RPA")
        self.extractor_thread.progreso.connect(self.progreso_bar.setValue)
        self.extractor_thread.log.connect(self.log_text.append)
        self.extractor_thread.terminado.connect(self.extraccion_terminada)
        
        self.extractor_thread.start()

    def iniciar_extraccion_rpyc(self):
        archivo = self.archivo_extraccion_edit.text()
        carpeta = self.carpeta_extraccion_edit.text()
        
        if not archivo or not carpeta:
            QMessageBox.warning(self, "Error", "Por favor selecciona archivo y carpeta de salida")
            return
        
        if not os.path.exists(archivo):
            QMessageBox.warning(self, "Error", "El archivo de entrada no existe")
            return
        
        self.btn_extraer_rpa.setEnabled(False)
        self.btn_extraer_rpyc.setEnabled(False)
        self.progreso_bar.setValue(0)
        self.log_text.clear()
        
        self.extractor_thread = ExtractorThread(archivo, carpeta, "RPYC")
        self.extractor_thread.progreso.connect(self.progreso_bar.setValue)
        self.extractor_thread.log.connect(self.log_text.append)
        self.extractor_thread.terminado.connect(self.extraccion_terminada)
        
        self.extractor_thread.start()

    def extraccion_terminada(self, exitoso):
        self.btn_extraer_rpa.setEnabled(True)
        self.btn_extraer_rpyc.setEnabled(True)
        if exitoso:
            QMessageBox.information(self, "Éxito", "Extracción completada correctamente")
        else:
            QMessageBox.warning(self, "Error", "Error durante la extracción")

    def iniciar_traduccion(self):
        archivo_entrada = self.archivo_entrada_edit.text()
        archivo_salida = self.archivo_salida_edit.text()
        
        if not archivo_entrada or not archivo_salida:
            QMessageBox.warning(self, "Error", "Por favor selecciona archivo de entrada y salida")
            return
        
        if not os.path.exists(archivo_entrada):
            QMessageBox.warning(self, "Error", "El archivo de entrada no existe")
            return
        
        self.btn_traducir.setEnabled(False)
        self.progreso_bar.setValue(0)
        self.log_text.clear()
        
        self.thread = TraductorThread(
            archivo_entrada,
            archivo_salida,
            self.combo_origen.currentText(),
            self.combo_destino.currentText()
        )
        
        self.thread.progreso.connect(self.progreso_bar.setValue)
        self.thread.log.connect(self.log_text.append)
        self.thread.terminado.connect(self.traduccion_terminada)
        
        self.thread.start()

    def traduccion_terminada(self, exitoso):
        self.btn_traducir.setEnabled(True)
        if exitoso:
            QMessageBox.information(self, "Éxito", "Traducción completada correctamente")
        else:
            QMessageBox.warning(self, "Error", "Error durante la traducción")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = TraductorGUI()
    ventana.show()
    sys.exit(app.exec_()) 
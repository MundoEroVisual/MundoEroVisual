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

    def traducir_texto(self, texto):
        """Traduce usando MyMemory API"""
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": texto,
            "langpair": f"{self.idioma_origen}|{self.idioma_destino}"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    traduccion = data["responseData"]["translatedText"]
                    self.log.emit(f"✅ Traducido: '{texto}' → '{traduccion}'")
                    return traduccion
                else:
                    self.log.emit(f"⚠️ Error en traducción: {data.get('responseDetails', 'Error desconocido')}")
            else:
                self.log.emit(f"⚠️ HTTP error: {response.status_code}")
            return texto
        except Exception as e:
            self.log.emit(f"❌ Error de traducción: {e}")
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
            
            i = 0
            while i < len(lineas):
                linea = lineas[i]
                linea_strip = linea.strip()
                
                # Detectar comentario con texto original
                match_comentario = patron_comentario.match(linea_strip)
                if match_comentario:
                    personaje = match_comentario.group(1)
                    texto_original = match_comentario.group(2)
                    
                    # Verificar si la siguiente línea es una línea vacía del mismo personaje
                    if i + 1 < len(lineas):
                        siguiente_linea = lineas[i + 1].strip()
                        match_vacia = patron_linea_vacia.match(siguiente_linea)
                        
                        if match_vacia and match_vacia.group(1) == personaje:
                            # Traducir el texto original
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
                    
                    # Si no hay línea vacía correspondiente, mantener como está
                    lineas_traducidas.append(linea)
                else:
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
                            time.sleep(1)  # Pausa entre traducciones
                        else:
                            lineas_traducidas.append(linea)
                    else:
                        lineas_traducidas.append(linea)
                
                i += 1
                self.progreso.emit(int((i + 1) * 100 / len(lineas)))
            
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
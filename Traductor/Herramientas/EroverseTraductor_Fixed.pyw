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
        """Traduce usando MyMemory API"""
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
                        self.log.emit(f"✅ Traducido: '{texto[:30]}...' → '{traduccion[:30]}...'")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error traducción: {e}")
        
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
            patron_old_string = re.compile(r'^\s*old\s*"([^"]*)"\s*$')
            patron_new_string = re.compile(r'^\s*new\s*""\s*$')
            
            # Patrones para comentarios sin personaje y strings vacíos
            patron_comentario_sin_personaje = re.compile(r'^\s*#\s*"([^"]*)"\s*$')
            patron_string_vacio = re.compile(r'^\s*"([^"]*)"\s*$')
            
            i = 0
            while i < len(lineas):
                try:
                    linea = lineas[i]
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
                                    linea_traducida = f'    {personaje} "{texto_trad}"\n'
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
                                    linea_traducida = f'    "{texto_trad}"\n'
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
                        
                        # Verificar si la siguiente línea es "new """
                        if i + 1 < len(lineas):
                            siguiente_linea = lineas[i + 1].strip()
                            match_new = patron_new_string.match(siguiente_linea)
                            
                            if match_new:
                                # Traducir el texto original
                                if texto_original and self.debe_traducir(texto_original):
                                    texto_trad = self.traducir_texto(texto_original)
                                    
                                    # REEMPLAZAR la línea "new "" con la traducción
                                    linea_traducida = f'    new "{texto_trad}"\n'
                                    lineas_traducidas.append(linea_traducida)
                                    
                                    traducciones_realizadas += 1
                                    self.log.emit(f"🔄 Traducido string: '{texto_original}' → '{texto_trad}'")
                                    
                                    i += 1  # Saltar la línea "new" original (NO agregarla)
                                    continue
                                else:
                                    # Si no se debe traducir, mantener la línea "new" original
                                    lineas_traducidas.append(lineas[i + 1])
                                    i += 1
                                    continue
                        
                        # Si no hay línea "new" correspondiente, mantener como está
                        i += 1
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

    def seleccionar_archivo_entrada(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo .rpy", "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.archivo_entrada_edit.setText(archivo)

    def seleccionar_archivo_salida(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar archivo traducido", "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.archivo_salida_edit.setText(archivo)

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
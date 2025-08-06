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

class TraductorThread(QThread):
    progreso = pyqtSignal(int)
    log = pyqtSignal(str)
    terminado = pyqtSignal(bool, str)

    def __init__(self, archivo_entrada, archivo_salida, idioma_origen, idioma_destino):
        super().__init__()
        self.archivo_entrada = archivo_entrada
        self.archivo_salida = archivo_salida
        self.idioma_origen = idioma_origen
        self.idioma_destino = idioma_destino

    def debe_traducir_mejorado(self, texto):
        """Determina si un texto debe ser traducido"""
        if not texto or len(texto.strip()) < 3:
            return False
        
        # No traducir nombres de variables, etiquetas, etc.
        patrones_excluir = [
            r'^[a-zA-Z_][a-zA-Z0-9_]*$',  # Variables
            r'^[A-Z_]+$',  # Constantes
            r'^[a-z_]+$',  # Funciones
            r'^[0-9]+$',  # Números
            r'^[^a-zA-Z]*$',  # Solo símbolos
            r'^[a-zA-Z]+_[a-zA-Z]+$',  # Nombres con guión bajo
        ]
        
        for patron in patrones_excluir:
            if re.match(patron, texto.strip()):
                return False
        
        return True

    def traducir_texto(self, texto, idioma_origen, idioma_destino):
        """Traduce texto usando múltiples APIs"""
        if not self.debe_traducir_mejorado(texto):
            return texto
        
        # API 1: MyMemory
        try:
            url = f"https://api.mymemory.translated.net/get?q={texto}&langpair={idioma_origen}|{idioma_destino}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('responseStatus') == 200:
                    traduccion = data['responseData']['translatedText']
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido: {texto[:50]}...")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error MyMemory: {e}")

        # API 2: Google Translate (fallback)
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={idioma_origen}&tl={idioma_destino}&dt=t&q={texto}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and len(data[0]) > 0:
                    traduccion = data[0][0][0]
                    if traduccion and traduccion != texto:
                        self.log.emit(f"✅ Traducido (Google): {texto[:50]}...")
                        return traduccion
        except Exception as e:
            self.log.emit(f"⚠️ Error Google: {e}")

        return texto

    def run(self):
        try:
            self.progreso.emit(10)
            self.log.emit("📖 Leyendo archivo...")
            
            with open(self.archivo_entrada, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            self.progreso.emit(20)
            self.log.emit(f"📄 Archivo leído: {len(lineas)} líneas")
            
            lineas_traducidas = []
            total_lineas = len(lineas)
            
            for i, linea in enumerate(lineas):
                self.progreso.emit(20 + int(60 * i / total_lineas))
                
                # Buscar diálogos para traducir
                patron_dialogo = r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*"([^"]*)"'
                match = re.match(patron_dialogo, linea)
                
                if match:
                    espacios, personaje, texto = match.groups()
                    if self.debe_traducir_mejorado(texto):
                        texto_traducido = self.traducir_texto(texto, self.idioma_origen, self.idioma_destino)
                        linea_traducida = f'{espacios}{personaje} "{texto_traducido}"\n'
                        lineas_traducidas.append(linea_traducida)
                    else:
                        lineas_traducidas.append(linea)
                else:
                    lineas_traducidas.append(linea)
            
            self.progreso.emit(80)
            self.log.emit("💾 Guardando archivo traducido...")
            
            with open(self.archivo_salida, 'w', encoding='utf-8') as f:
                f.writelines(lineas_traducidas)
            
            self.progreso.emit(100)
            self.log.emit("✅ Traducción completada exitosamente")
            self.terminado.emit(True, self.archivo_salida)
            
        except Exception as e:
            self.log.emit(f"❌ Error durante la traducción: {e}")
            self.terminado.emit(False, str(e))

class TraductorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grupo de archivos
        grupo_archivos = QGroupBox("📁 Archivos")
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
        
        # Idioma origen
        layout_idiomas.addWidget(QLabel("Idioma origen:"))
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(["en", "es", "fr", "de", "it", "pt"])
        self.combo_origen.setCurrentText("en")
        layout_idiomas.addWidget(self.combo_origen)
        
        # Idioma destino
        layout_idiomas.addWidget(QLabel("Idioma destino:"))
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt"])
        self.combo_destino.setCurrentText("es")
        layout_idiomas.addWidget(self.combo_destino)
        
        grupo_idiomas.setLayout(layout_idiomas)
        layout.addWidget(grupo_idiomas)
        
        # Barra de progreso
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Botón de traducción
        self.btn_traducir = QPushButton("🚀 Traducir")
        self.btn_traducir.clicked.connect(self.iniciar_traduccion)
        layout.addWidget(self.btn_traducir)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(200)
        layout.addWidget(self.log_area)
        
        self.setLayout(layout)

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

    def traduccion_terminada(self, exito, archivo_salida):
        self.btn_traducir.setEnabled(True)
        if exito:
            self.progress.setValue(100)
            QMessageBox.information(self, "Éxito", f"¡Traducción completada!\nArchivo guardado en: {archivo_salida}")
        else:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error", f"Error en la traducción: {archivo_salida}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Traductor Ren'Py")
    
    window = TraductorGUI()
    window.setWindowTitle("Traductor Ren'Py")
    window.resize(600, 500)
    window.show()
    
    sys.exit(app.exec_()) 
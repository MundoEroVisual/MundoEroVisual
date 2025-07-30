import sys
import os
import re
import requests
import subprocess
import zipfile
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QMessageBox, QComboBox, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class ExtractorThread(QThread):
    progreso = pyqtSignal(int)
    log = pyqtSignal(str)
    terminado = pyqtSignal(bool, str)

    def __init__(self, archivo_entrada, directorio_salida, tipo_archivo):
        super().__init__()
        self.archivo_entrada = archivo_entrada
        self.directorio_salida = directorio_salida
        self.tipo_archivo = tipo_archivo

    def extraer_rpa(self):
        try:
            # Usar unrpa si está disponible
            unrpa_path = os.path.join(os.path.dirname(__file__), "unrpa-2.3.0", "unrpa")
            if os.path.exists(unrpa_path):
                cmd = [sys.executable, "-m", "unrpa", "-mp", self.directorio_salida, self.archivo_entrada]
            else:
                # Fallback: intentar con unrpa instalado globalmente
                cmd = ["unrpa", "-mp", self.directorio_salida, self.archivo_entrada]
            
            self.log.emit(f"🔧 Ejecutando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log.emit("✅ Archivo RPA extraído correctamente")
                return True
            else:
                self.log.emit(f"❌ Error al extraer RPA: {result.stderr}")
                return False
        except Exception as e:
            self.log.emit(f"❌ Excepción al extraer RPA: {e}")
            return False

    def extraer_rpyc(self):
        try:
            # Usar unrpyc si está disponible
            unrpyc_path = os.path.join(os.path.dirname(__file__), "unrpyc-master", "unrpyc.py")
            if os.path.exists(unrpyc_path):
                cmd = [sys.executable, unrpyc_path, self.archivo_entrada]
            else:
                # Fallback: intentar con unrpyc instalado globalmente
                cmd = ["unrpyc", self.archivo_entrada]
            
            self.log.emit(f"🔧 Ejecutando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log.emit("✅ Archivo RPYC decompilado correctamente")
                return True
            else:
                self.log.emit(f"❌ Error al decompilar RPYC: {result.stderr}")
                return False
        except Exception as e:
            self.log.emit(f"❌ Excepción al decompilar RPYC: {e}")
            return False

    def run(self):
        self.progreso.emit(10)
        self.log.emit(f"🚀 Iniciando extracción de {self.tipo_archivo}")
        
        if self.tipo_archivo == "RPA":
            exito = self.extraer_rpa()
        elif self.tipo_archivo == "RPYC":
            exito = self.extraer_rpyc()
        else:
            self.log.emit("❌ Tipo de archivo no soportado")
            exito = False
        
        self.progreso.emit(100)
        
        if exito:
            self.log.emit(f"✅ Extracción completada en: {self.directorio_salida}")
            self.terminado.emit(True, self.directorio_salida)
        else:
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

    def traducir_texto(self, texto):
        # Usar MyMemory API (gratuita, sin registro)
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": texto,
            "langpair": f"{self.idioma_origen}|{self.idioma_destino}"
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    return data["responseData"]["translatedText"]
                else:
                    self.log.emit(f"⚠️ Error en traducción: {data.get('responseDetails', 'Error desconocido')}")
                    return texto
            else:
                self.log.emit(f"⚠️ Error HTTP: {response.status_code}")
                return texto
        except Exception as e:
            self.log.emit(f"❌ Excepción al traducir: {e}")
            return texto

    def run(self):
        # Patrones mejorados para mantener sangría
        patron_dialogo = re.compile(r'^(\s*[a-zA-Z0-9_]+\s+)(["\'])(.+?)\2(\s*)$')
        patron_linea_comillas = re.compile(r'^(\s*)(["\'])(.+?)\2(\s*)$')
        patron_style_prefix = re.compile(r'^(\s*style_prefix\s+)(["\'])(.+?)\2(\s*)$')
        lineas_traducidas = []

        estilos_protegidos = (
            "subtitle", "title", "skip_triangle", "default", "button", "button_text",
            "choice_button", "choice_button_text", "quick_button", "quick_button_text",
            "navigation_button", "narrador", "texto", "menu", "style", "screen"
        )

        try:
            with open(self.archivo_entrada, "r", encoding="utf-8") as f_in:
                lineas = f_in.readlines()
        except Exception as e:
            self.log.emit(f"❌ Error al leer archivo: {e}")
            self.terminado.emit(False)
            return

        total = len(lineas)
        lineas_traducidas_count = 0

        for idx, linea in enumerate(lineas):
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
                pass  # Saltar líneas técnicas
            elif patron_style_prefix.match(linea):
                pass  # Mantener style_prefix intacto
            elif patron_dialogo.match(linea):
                m = patron_dialogo.match(linea)
                prefix = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)  # Mantener espacios finales
                if texto.strip():  # Solo traducir si hay texto
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{prefix}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")
            elif patron_linea_comillas.match(linea):
                m = patron_linea_comillas.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)  # Mantener espacios finales
                if texto.strip():  # Solo traducir si hay texto
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")

            lineas_traducidas.append(traducida)
            self.progreso.emit(int((idx + 1) * 100 / total))

        try:
            with open(self.archivo_salida, "w", encoding="utf-8") as f_out:
                f_out.writelines(lineas_traducidas)
            self.log.emit(f"✅ Traducción completada: {self.archivo_salida}")
            self.log.emit(f"📊 Total de líneas traducidas: {lineas_traducidas_count}")
            self.terminado.emit(True)
        except Exception as e:
            self.log.emit(f"❌ Error al guardar archivo: {e}")
            self.terminado.emit(False)


class TraductorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traductor Mejorado - Archivos Ren'Py")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        self.resize(1000, 800)
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
            font-size: 11pt;
        }
        QLineEdit, QTextEdit, QComboBox {
            background: #16213e; 
            color: #e94560; 
            border: 2px solid #533483;
            border-radius: 10px; 
            font-size: 10pt; 
            padding: 8px 12px;
            selection-background-color: #533483;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #e94560;
            background: #1a1a2e;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #e94560, stop:1 #c44569);
            color: #ffffff; 
            font-weight: bold; 
            border-radius: 12px; 
            padding: 12px 20px;
            font-size: 11pt; 
            border: none; 
            margin: 6px 4px;
            min-height: 40px;
            min-width: 100px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #f0544f, stop:1 #e94560);
            transform: scale(1.05);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #c44569, stop:1 #a83271);
        }
        QPushButton:disabled { 
            background: #2d3748; 
            color: #718096; 
            border: 1px solid #4a5568;
        }
        QProgressBar {
            background: #16213e; 
            color: #e94560; 
            border: 2px solid #533483; 
            border-radius: 12px;
            text-align: center; 
            font-weight: bold;
            font-size: 10pt;
            min-height: 25px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #e94560, stop:1 #c44569);
            border-radius: 10px;
        }
        QGroupBox {
            font-weight: bold; 
            border: 3px solid #533483; 
            border-radius: 15px;
            margin-top: 10px; 
            padding-top: 10px;
            padding-bottom: 10px;
            padding-left: 8px;
            padding-right: 8px;
            background: rgba(26, 26, 46, 0.7);
            color: #f7f7f7;
            font-size: 11pt;
            min-height: 150px;
        }
        QGroupBox::title { 
            subcontrol-origin: margin; 
            left: 15px; 
            padding: 0 10px 0 10px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #533483, stop:1 #e94560);
            border-radius: 8px;
            color: #ffffff;
        }
        QCheckBox { 
            spacing: 10px; 
            color: #f7f7f7;
            font-size: 10pt;
        }
        QCheckBox::indicator { 
            width: 20px; 
            height: 20px; 
            border: 2px solid #533483;
            border-radius: 4px;
            background: #16213e;
        }
        QCheckBox::indicator:checked {
            background: #e94560;
            border: 2px solid #e94560;
        }
        QScrollBar:vertical {
            background: #16213e;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #533483;
            border-radius: 6px;
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
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("🎮 Traductor Mejorado - Archivos Ren'Py")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont('Segoe UI', 18, QFont.Bold))
        titulo.setStyleSheet("color: #e94560; margin: 6px; padding: 6px;")
        layout.addWidget(titulo)

        # Grupo de Extracción
        grupo_extraccion = QGroupBox("🔧 Extracción de Archivos RPA/RPYC")
        layout_extraccion = QVBoxLayout()

        # Selección de archivo para extracción
        hlayout_extraccion = QHBoxLayout()
        hlayout_extraccion.setSpacing(8)
        hlayout_extraccion.setContentsMargins(6, 8, 6, 8)
        
        self.input_extraccion = QLineEdit()
        self.input_extraccion.setPlaceholderText("Selecciona archivo .rpa o .rpyc...")
        btn_extraccion = QPushButton("📁 Seleccionar archivo...")
        btn_extraccion.setMinimumWidth(150)
        btn_extraccion.setMinimumHeight(35)
        btn_extraccion.clicked.connect(self.seleccionar_archivo_extraccion)
        
        hlayout_extraccion.addWidget(QLabel("Archivo a extraer:"))
        hlayout_extraccion.addWidget(self.input_extraccion, 1)  # Stretch factor
        hlayout_extraccion.addWidget(btn_extraccion)
        layout_extraccion.addLayout(hlayout_extraccion)

        # Directorio de salida para extracción
        hlayout_directorio = QHBoxLayout()
        hlayout_directorio.setSpacing(8)
        hlayout_directorio.setContentsMargins(6, 8, 6, 8)
        
        self.output_directorio = QLineEdit()
        self.output_directorio.setPlaceholderText("Directorio de salida...")
        btn_directorio = QPushButton("📂 Seleccionar directorio...")
        btn_directorio.setMinimumWidth(150)
        btn_directorio.setMinimumHeight(35)
        btn_directorio.clicked.connect(self.seleccionar_directorio_extraccion)
        
        hlayout_directorio.addWidget(QLabel("Directorio de salida:"))
        hlayout_directorio.addWidget(self.output_directorio, 1)  # Stretch factor
        hlayout_directorio.addWidget(btn_directorio)
        layout_extraccion.addLayout(hlayout_directorio)

        # Botón de extracción
        self.btn_extraer = QPushButton("🔧 Extraer/Decompilar archivo")
        self.btn_extraer.setMinimumHeight(40)
        self.btn_extraer.setMinimumWidth(180)
        self.btn_extraer.clicked.connect(self.iniciar_extraccion)
        layout_extraccion.addWidget(self.btn_extraer)
        
        # Agregar espacio vertical después del botón
        layout_extraccion.addStretch(1)

        grupo_extraccion.setLayout(layout_extraccion)
        layout.addWidget(grupo_extraccion)

        # Grupo de Traducción
        grupo_traduccion = QGroupBox("🌐 Traducción de Archivos RPY")
        layout_traduccion = QVBoxLayout()

        # Configuración de idiomas
        hlayout_lang = QHBoxLayout()
        hlayout_lang.setSpacing(10)
        hlayout_lang.setContentsMargins(6, 10, 6, 10)
        
        hlayout_lang.addWidget(QLabel("🌍 Idioma origen:"))
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(["en", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.combo_origen.setCurrentText("en")
        self.combo_origen.setMinimumWidth(80)
        self.combo_origen.setMinimumHeight(30)
        hlayout_lang.addWidget(self.combo_origen)
        
        hlayout_lang.addStretch(1)  # Espacio flexible
        
        hlayout_lang.addWidget(QLabel("🎯 Idioma destino:"))
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.combo_destino.setCurrentText("es")
        self.combo_destino.setMinimumWidth(80)
        self.combo_destino.setMinimumHeight(30)
        hlayout_lang.addWidget(self.combo_destino)
        layout_traduccion.addLayout(hlayout_lang)

        # Archivos de traducción
        hlayout1 = QHBoxLayout()
        hlayout1.setSpacing(8)
        hlayout1.setContentsMargins(6, 8, 6, 8)
        
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Archivo .rpy a traducir...")
        btn_input = QPushButton("📄 Seleccionar archivo...")
        btn_input.setMinimumWidth(150)
        btn_input.setMinimumHeight(35)
        btn_input.clicked.connect(self.seleccionar_entrada)
        
        hlayout1.addWidget(QLabel("Archivo de entrada:"))
        hlayout1.addWidget(self.input_edit, 1)  # Stretch factor
        hlayout1.addWidget(btn_input)
        layout_traduccion.addLayout(hlayout1)

        hlayout2 = QHBoxLayout()
        hlayout2.setSpacing(8)
        hlayout2.setContentsMargins(6, 8, 6, 8)
        
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Archivo traducido...")
        btn_output = QPushButton("💾 Guardar como...")
        btn_output.setMinimumWidth(150)
        btn_output.setMinimumHeight(35)
        btn_output.clicked.connect(self.seleccionar_salida)
        
        hlayout2.addWidget(QLabel("Archivo de salida:"))
        hlayout2.addWidget(self.output_edit, 1)  # Stretch factor
        hlayout2.addWidget(btn_output)
        layout_traduccion.addLayout(hlayout2)

        # Botón de traducción
        self.btn_traducir = QPushButton("🌐 Traducir archivo")
        self.btn_traducir.setMinimumHeight(40)
        self.btn_traducir.setMinimumWidth(180)
        self.btn_traducir.clicked.connect(self.iniciar_traduccion)
        layout_traduccion.addWidget(self.btn_traducir)
        
        # Agregar espacio vertical después del botón
        layout_traduccion.addStretch(1)

        grupo_traduccion.setLayout(layout_traduccion)
        layout.addWidget(grupo_traduccion)

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(200)
        self.log_area.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 8pt;")
        layout.addWidget(QLabel("📋 Log de operaciones:"))
        layout.addWidget(self.log_area)

        # Botones de acción
        hlayout_botones = QHBoxLayout()
        hlayout_botones.setSpacing(10)
        hlayout_botones.setContentsMargins(6, 10, 6, 10)
        
        self.btn_abrir = QPushButton("📂 Abrir archivo traducido")
        self.btn_abrir.setEnabled(False)
        self.btn_abrir.setMinimumWidth(160)
        self.btn_abrir.setMinimumHeight(35)
        self.btn_abrir.clicked.connect(self.abrir_archivo_salida)
        hlayout_botones.addWidget(self.btn_abrir)

        hlayout_botones.addStretch(1)  # Espacio flexible

        self.btn_limpiar = QPushButton("🧹 Limpiar log")
        self.btn_limpiar.setMinimumWidth(120)
        self.btn_limpiar.setMinimumHeight(35)
        self.btn_limpiar.clicked.connect(self.limpiar_log)
        hlayout_botones.addWidget(self.btn_limpiar)
        layout.addLayout(hlayout_botones)

        self.setLayout(layout)

    def seleccionar_archivo_extraccion(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", 
            "Archivos Ren'Py (*.rpa *.rpyc);;Archivos RPA (*.rpa);;Archivos RPYC (*.rpyc);;Todos los archivos (*)"
        )
        if fname:
            self.input_extraccion.setText(fname)
            # Detectar tipo de archivo
            if fname.lower().endswith('.rpa'):
                self.log_area.append("📦 Archivo RPA detectado")
            elif fname.lower().endswith('.rpyc'):
                self.log_area.append("📄 Archivo RPYC detectado")

    def seleccionar_directorio_extraccion(self):
        dirname = QFileDialog.getExistingDirectory(self, "Seleccionar directorio de salida")
        if dirname:
            self.output_directorio.setText(dirname)

    def seleccionar_entrada(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo .rpy", "", "Archivos Ren'Py (*.rpy);;Todos los archivos (*)")
        if fname:
            self.input_edit.setText(fname)
            # Generar nombre de salida automáticamente
            base_name = os.path.splitext(fname)[0]
            self.output_edit.setText(f"{base_name}_traducido.rpy")

    def seleccionar_salida(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Guardar archivo traducido", "", "Archivos Ren'Py (*.rpy);;Todos los archivos (*)")
        if fname:
            self.output_edit.setText(fname)

    def iniciar_extraccion(self):
        archivo_entrada = self.input_extraccion.text().strip()
        directorio_salida = self.output_directorio.text().strip()
        
        if not archivo_entrada or not os.path.isfile(archivo_entrada):
            QMessageBox.warning(self, "Error", "Selecciona un archivo válido para extraer.")
            return
        if not directorio_salida:
            QMessageBox.warning(self, "Error", "Selecciona un directorio de salida válido.")
            return

        # Determinar tipo de archivo
        if archivo_entrada.lower().endswith('.rpa'):
            tipo_archivo = "RPA"
        elif archivo_entrada.lower().endswith('.rpyc'):
            tipo_archivo = "RPYC"
        else:
            QMessageBox.warning(self, "Error", "Solo se soportan archivos .rpa y .rpyc")
            return

        self.btn_extraer.setEnabled(False)
        self.progress.setValue(0)
        self.log_area.append(f"🚀 Iniciando extracción de {tipo_archivo}...")
        
        self.extractor_thread = ExtractorThread(archivo_entrada, directorio_salida, tipo_archivo)
        self.extractor_thread.progreso.connect(self.progress.setValue)
        self.extractor_thread.log.connect(self.log_area.append)
        self.extractor_thread.terminado.connect(self.extraccion_terminada)
        self.extractor_thread.start()

    def extraccion_terminada(self, exito, directorio):
        self.btn_extraer.setEnabled(True)
        if exito:
            QMessageBox.information(self, "Éxito", f"Extracción completada en:\n{directorio}")
            # Opcional: abrir el directorio
            if QMessageBox.question(self, "Abrir directorio", "¿Quieres abrir el directorio de salida?") == QMessageBox.Yes:
                os.startfile(directorio)
        else:
            QMessageBox.critical(self, "Error", "Ocurrió un error durante la extracción.")

    def iniciar_traduccion(self):
        archivo_entrada = self.input_edit.text().strip()
        archivo_salida = self.output_edit.text().strip()
        
        if not archivo_entrada or not os.path.isfile(archivo_entrada):
            QMessageBox.warning(self, "Error", "Selecciona un archivo de entrada válido.")
            return
        if not archivo_salida:
            QMessageBox.warning(self, "Error", "Selecciona un archivo de salida válido.")
            return
            
        self.btn_traducir.setEnabled(False)
        self.btn_abrir.setEnabled(False)
        self.progress.setValue(0)
        self.log_area.append("🌐 Iniciando traducción...")
        
        idioma_origen = self.combo_origen.currentText()
        idioma_destino = self.combo_destino.currentText()
        
        self.traductor_thread = TraductorThread(
            archivo_entrada, 
            archivo_salida, 
            idioma_origen, 
            idioma_destino
        )
        self.traductor_thread.progreso.connect(self.progress.setValue)
        self.traductor_thread.log.connect(self.log_area.append)
        self.traductor_thread.terminado.connect(self.traduccion_terminada)
        self.traductor_thread.start()

    def traduccion_terminada(self, exito):
        self.btn_traducir.setEnabled(True)
        if exito:
            self.btn_abrir.setEnabled(True)
            QMessageBox.information(self, "Listo", "¡Traducción finalizada!")
        else:
            QMessageBox.critical(self, "Error", "Ocurrió un error durante la traducción.")

    def abrir_archivo_salida(self):
        archivo = self.output_edit.text().strip()
        if archivo and os.path.isfile(archivo):
            os.startfile(archivo)

    def limpiar_log(self):
        self.log_area.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TraductorGUI()
    gui.show()
    sys.exit(app.exec_()) 
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
            unrpa_path = os.path.join(os.path.dirname(__file__), "unrpa-2.3.0", "unrpa")
            if os.path.exists(unrpa_path):
                cmd = [sys.executable, "-m", "unrpa", "-mp", self.directorio_salida, self.archivo_entrada]
            else:
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
            unrpyc_path = os.path.join(os.path.dirname(__file__), "unrpyc-master", "unrpyc.py")
            if os.path.exists(unrpyc_path):
                cmd = [sys.executable, unrpyc_path, self.archivo_entrada]
            else:
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
                pass
            elif patron_style_prefix.match(linea):
                pass
            elif patron_dialogo.match(linea):
                m = patron_dialogo.match(linea)
                prefix = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip():
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{prefix}"{texto_trad}"{suffix}'
                    lineas_traducidas_count += 1
                    self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")
            elif patron_linea_comillas.match(linea):
                m = patron_linea_comillas.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                suffix = m.group(4)
                if texto.strip():
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
        self.setWindowTitle("🛠️ Traductor y Extractor - Archivos Ren'Py")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
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
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Título
        titulo = QLabel("🛠️ Traductor y Extractor - Archivos Ren'Py")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont('Segoe UI', 12, QFont.Bold))
        titulo.setStyleSheet("color: #e94560; margin: 3px; padding: 3px;")
        main_layout.addWidget(titulo)

        # Grupo de Extracción
        grupo_extraccion = QGroupBox("📦 Extracción de Archivos RPA/RPYC")
        layout_extraccion = QVBoxLayout()
        layout_extraccion.setSpacing(8)

        # Archivo a extraer
        hlayout_archivo = QHBoxLayout()
        hlayout_archivo.setSpacing(8)
        hlayout_archivo.setAlignment(Qt.AlignVCenter)
        hlayout_archivo.setContentsMargins(0, 4, 0, 4)
        
        label_archivo = QLabel("Seleccionar archivo a extraer:")
        self.input_extraccion = QLineEdit()
        self.input_extraccion.setPlaceholderText("Selecciona archivo .rpa o .rpyc...")
        self.input_extraccion.setFixedHeight(32)
        btn_extraccion = QPushButton("📁 Seleccionar archivo...")
        btn_extraccion.setMinimumWidth(150)
        btn_extraccion.setFixedHeight(32)
        btn_extraccion.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        btn_extraccion.clicked.connect(self.seleccionar_archivo_extraccion)
        
        hlayout_archivo.addWidget(label_archivo)
        hlayout_archivo.addWidget(self.input_extraccion, 1)
        hlayout_archivo.addWidget(btn_extraccion)
        layout_extraccion.addLayout(hlayout_archivo)

        # Directorio de salida
        hlayout_directorio = QHBoxLayout()
        hlayout_directorio.setSpacing(8)
        hlayout_directorio.setAlignment(Qt.AlignVCenter)
        hlayout_directorio.setContentsMargins(0, 4, 0, 4)
        
        label_directorio = QLabel("Directorio de salida:")
        self.output_directorio = QLineEdit()
        self.output_directorio.setPlaceholderText("Directorio de salida...")
        self.output_directorio.setFixedHeight(32)
        btn_directorio = QPushButton("📂 Seleccionar directorio...")
        btn_directorio.setMinimumWidth(150)
        btn_directorio.setFixedHeight(32)
        btn_directorio.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        btn_directorio.clicked.connect(self.seleccionar_directorio_extraccion)
        
        hlayout_directorio.addWidget(label_directorio)
        hlayout_directorio.addWidget(self.output_directorio, 1)
        hlayout_directorio.addWidget(btn_directorio)
        layout_extraccion.addLayout(hlayout_directorio)

        # Botón de extracción
        self.btn_extraer = QPushButton("🔧 Extraer / Descompilar archivo")
        self.btn_extraer.setFixedHeight(32)
        self.btn_extraer.setMinimumWidth(180)
        self.btn_extraer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_extraer.clicked.connect(self.iniciar_extraccion)
        layout_extraccion.addWidget(self.btn_extraer)
        
        # Agregar espacio después del botón
        layout_extraccion.addStretch(1)

        grupo_extraccion.setLayout(layout_extraccion)
        main_layout.addWidget(grupo_extraccion)

        # Grupo de Traducción
        grupo_traduccion = QGroupBox("🌐 Traducción de Archivos RPY")
        layout_traduccion = QVBoxLayout()
        layout_traduccion.setSpacing(8)

        # Configuración de idiomas
        hlayout_idiomas = QHBoxLayout()
        hlayout_idiomas.setSpacing(10)
        hlayout_idiomas.setAlignment(Qt.AlignVCenter)
        hlayout_idiomas.setContentsMargins(0, 4, 0, 4)
        
        label_origen = QLabel("🌍 Idioma de origen:")
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(["en", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.combo_origen.setCurrentText("en")
        self.combo_origen.setMinimumWidth(70)
        self.combo_origen.setFixedHeight(32)
        self.combo_origen.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        label_destino = QLabel("🎯 Idioma de destino:")
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.combo_destino.setCurrentText("es")
        self.combo_destino.setMinimumWidth(70)
        self.combo_destino.setFixedHeight(32)
        self.combo_destino.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        hlayout_idiomas.addWidget(label_origen)
        hlayout_idiomas.addWidget(self.combo_origen)
        hlayout_idiomas.addStretch(1)
        hlayout_idiomas.addWidget(label_destino)
        hlayout_idiomas.addWidget(self.combo_destino)
        layout_traduccion.addLayout(hlayout_idiomas)

        # Archivo de entrada
        hlayout_entrada = QHBoxLayout()
        hlayout_entrada.setSpacing(8)
        hlayout_entrada.setAlignment(Qt.AlignVCenter)
        hlayout_entrada.setContentsMargins(0, 4, 0, 4)
        
        label_entrada = QLabel("Archivo de entrada:")
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Archivo .rpy a traducir...")
        self.input_edit.setFixedHeight(32)
        btn_input = QPushButton("📄 Seleccionar archivo...")
        btn_input.setMinimumWidth(140)
        btn_input.setFixedHeight(32)
        btn_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        btn_input.clicked.connect(self.seleccionar_entrada)
        
        hlayout_entrada.addWidget(label_entrada)
        hlayout_entrada.addWidget(self.input_edit, 1)
        hlayout_entrada.addWidget(btn_input)
        layout_traduccion.addLayout(hlayout_entrada)

        # Archivo de salida
        hlayout_salida = QHBoxLayout()
        hlayout_salida.setSpacing(8)
        hlayout_salida.setAlignment(Qt.AlignVCenter)
        hlayout_salida.setContentsMargins(0, 4, 0, 4)
        
        label_salida = QLabel("Archivo de salida:")
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Archivo traducido...")
        self.output_edit.setFixedHeight(32)
        self.output_edit.textChanged.connect(self.verificar_archivo_salida)
        btn_output = QPushButton("💾 Guardar como...")
        btn_output.setMinimumWidth(140)
        btn_output.setFixedHeight(32)
        btn_output.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        btn_output.clicked.connect(self.seleccionar_salida)
        
        hlayout_salida.addWidget(label_salida)
        hlayout_salida.addWidget(self.output_edit, 1)
        hlayout_salida.addWidget(btn_output)
        layout_traduccion.addLayout(hlayout_salida)

        # Botón de traducción
        self.btn_traducir = QPushButton("🌐 Traducir archivo")
        self.btn_traducir.setFixedHeight(32)
        self.btn_traducir.setMinimumWidth(180)
        self.btn_traducir.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_traducir.clicked.connect(self.iniciar_traduccion)
        layout_traduccion.addWidget(self.btn_traducir)
        
        # Agregar espacio después del botón
        layout_traduccion.addStretch(1)

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
        hlayout_botones.setSpacing(10)
        hlayout_botones.setAlignment(Qt.AlignVCenter)
        
        self.btn_abrir = QPushButton("📂 Abrir archivo traducido")
        self.btn_abrir.setEnabled(False)
        self.btn_abrir.setMinimumWidth(150)
        self.btn_abrir.setFixedHeight(32)
        self.btn_abrir.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_abrir.clicked.connect(self.abrir_archivo_salida)
        
        self.btn_limpiar = QPushButton("🧹 Limpiar registro")
        self.btn_limpiar.setMinimumWidth(120)
        self.btn_limpiar.setFixedHeight(32)
        self.btn_limpiar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_limpiar.clicked.connect(self.limpiar_log)
        
        hlayout_botones.addWidget(self.btn_abrir)
        hlayout_botones.addStretch(1)
        hlayout_botones.addWidget(self.btn_limpiar)
        
        main_layout.addLayout(hlayout_botones)

        self.setLayout(main_layout)

    def seleccionar_archivo_extraccion(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", 
            "Archivos Ren'Py (*.rpa *.rpyc);;Archivos RPA (*.rpa);;Archivos RPYC (*.rpyc);;Todos los archivos (*)"
        )
        if fname:
            self.input_extraccion.setText(fname)
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
            base_name = os.path.splitext(fname)[0]
            self.output_edit.setText(f"{base_name}_traducido.rpy")
            self.verificar_archivo_salida()

    def seleccionar_salida(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Guardar archivo traducido", "", "Archivos Ren'Py (*.rpy);;Todos los archivos (*)")
        if fname:
            self.output_edit.setText(fname)
            self.verificar_archivo_salida()

    def iniciar_extraccion(self):
        archivo_entrada = self.input_extraccion.text().strip()
        directorio_salida = self.output_directorio.text().strip()
        
        if not archivo_entrada or not os.path.isfile(archivo_entrada):
            QMessageBox.warning(self, "Error", "Selecciona un archivo válido para extraer.")
            return
        if not directorio_salida:
            QMessageBox.warning(self, "Error", "Selecciona un directorio de salida válido.")
            return

        if archivo_entrada.lower().endswith('.rpa'):
            tipo_archivo = "RPA"
        elif archivo_entrada.lower().endswith('.rpyc'):
            tipo_archivo = "RPYC"
        else:
            QMessageBox.warning(self, "Error", "Solo se soportan archivos .rpa y .rpyc")
            return

        self.btn_extraer.setEnabled(False)
        self.actualizar_progreso(0, "Iniciando extracción...")
        self.log_area.append(f"🚀 Iniciando extracción de {tipo_archivo}...")
        
        self.extractor_thread = ExtractorThread(archivo_entrada, directorio_salida, tipo_archivo)
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
        self.actualizar_progreso(0, "Iniciando traducción...")
        self.log_area.append("🌐 Iniciando traducción...")
        
        idioma_origen = self.combo_origen.currentText()
        idioma_destino = self.combo_destino.currentText()
        
        self.traductor_thread = TraductorThread(
            archivo_entrada, 
            archivo_salida, 
            idioma_origen, 
            idioma_destino
        )
        self.traductor_thread.progreso.connect(lambda x: self.actualizar_progreso(x, "Traduciendo..."))
        self.traductor_thread.log.connect(self.log_area.append)
        self.traductor_thread.terminado.connect(self.traduccion_terminada)
        self.traductor_thread.start()

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
        archivo = self.output_edit.text().strip()
        if archivo and os.path.isfile(archivo):
            os.startfile(archivo)
        else:
            QMessageBox.warning(self, "Error", "El archivo de salida no existe o no se ha especificado.")

    def limpiar_log(self):
        self.log_area.clear()

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
        archivo = self.output_edit.text().strip()
        if archivo and os.path.isfile(archivo):
            self.btn_abrir.setEnabled(True)
        else:
            self.btn_abrir.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TraductorGUI()
    gui.show()
    sys.exit(app.exec_()) 
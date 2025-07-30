import sys
import os
import re
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


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
        patron_dialogo = re.compile(r'^(\s*[a-zA-Z0-9_]+\s+)(["\'])(.+?)\2\s*$')
        patron_linea_comillas = re.compile(r'^(\s*)(["\'])(.+?)\2\s*$')
        patron_style_prefix = re.compile(r'^(\s*style_prefix\s+)(["\'])(.+?)\2\s*$')
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
                if texto.strip():  # Solo traducir si hay texto
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{prefix}"{texto_trad}"\n'
                    lineas_traducidas_count += 1
                    self.log.emit(f"🔄 Traduciendo: '{texto}' → '{texto_trad}'")
            elif patron_linea_comillas.match(linea):
                m = patron_linea_comillas.match(linea)
                indent = m.group(1)
                texto = m.group(3)
                if texto.strip():  # Solo traducir si hay texto
                    texto_trad = self.traducir_texto(texto)
                    traducida = f'{indent}"{texto_trad}"\n'
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
        self.setWindowTitle("Traductor de archivos .rpy (API Externa)")
        self.setMinimumWidth(700)
        self.setStyleSheet(self.estilo_moderno())
        self.init_ui()
        self.traductor_thread = None

    def estilo_moderno(self):
        return """
        QWidget { background-color: #111; color: #FFD700; font-family: 'Segoe UI'; }
        QLabel { font-weight: bold; }
        QLineEdit, QTextEdit, QComboBox {
            background: #181818; color: #FFD700; border: 1.5px solid #FFD700;
            border-radius: 7px; font-size: 1.08em; padding: 6px 10px;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:1 #B8860B);
            color: #111; font-weight: bold; border-radius: 8px; padding: 8px 18px;
            font-size: 1.08em; border: none; margin: 4px 0;
        }
        QPushButton:disabled { background: #444; color: #888; }
        QProgressBar {
            background: #222; color: #FFD700; border: 1.5px solid #FFD700; border-radius: 8px;
            text-align: center; font-weight: bold;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:1 #B8860B);
            border-radius: 8px;
        }
        """

    def init_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Traductor de archivos .rpy (API Externa)")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont('Segoe UI', 18, QFont.Bold))
        layout.addWidget(titulo)

        # Configuración de idiomas
        hlayout_lang = QHBoxLayout()
        hlayout_lang.addWidget(QLabel("Idioma origen:"))
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(["en", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.combo_origen.setCurrentText("en")
        hlayout_lang.addWidget(self.combo_origen)
        
        hlayout_lang.addWidget(QLabel("Idioma destino:"))
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh"])
        self.combo_destino.setCurrentText("es")
        hlayout_lang.addWidget(self.combo_destino)
        layout.addLayout(hlayout_lang)

        hlayout1 = QHBoxLayout()
        self.input_edit = QLineEdit()
        btn_input = QPushButton("Seleccionar archivo...")
        btn_input.clicked.connect(self.seleccionar_entrada)
        hlayout1.addWidget(QLabel("Archivo de entrada:"))
        hlayout1.addWidget(self.input_edit)
        hlayout1.addWidget(btn_input)
        layout.addLayout(hlayout1)

        hlayout2 = QHBoxLayout()
        self.output_edit = QLineEdit()
        btn_output = QPushButton("Guardar como...")
        btn_output.clicked.connect(self.seleccionar_salida)
        hlayout2.addWidget(QLabel("Archivo de salida:"))
        hlayout2.addWidget(self.output_edit)
        hlayout2.addWidget(btn_output)
        layout.addLayout(hlayout2)

        self.btn_traducir = QPushButton("Traducir archivo")
        self.btn_traducir.clicked.connect(self.iniciar_traduccion)
        layout.addWidget(self.btn_traducir)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(150)
        layout.addWidget(QLabel("Log de traducción:"))
        layout.addWidget(self.log_area)

        self.btn_abrir = QPushButton("Abrir archivo traducido")
        self.btn_abrir.setEnabled(False)
        self.btn_abrir.clicked.connect(self.abrir_archivo_salida)
        layout.addWidget(self.btn_abrir)

        self.setLayout(layout)

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
        self.log_area.clear()
        
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TraductorGUI()
    gui.show()
    sys.exit(app.exec_()) 
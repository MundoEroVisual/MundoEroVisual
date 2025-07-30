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
import time
import datetime


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
    
    # Sistema de múltiples APIs (110 APIs totales)
    apis_disponibles = [
        {
            "nombre": "MyMemory",
            "url": "https://api.mymemory.translated.net/get",
            "limite": 800,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "GoogleTranslate",
            "url": "https://translate.googleapis.com/translate_a/single",
            "limite": 5000,
            "contador": 0,
            "activa": True
        },
        # LibreTranslate Instancias (1-50)
        {
            "nombre": "LibreTranslate1",
            "url": "https://libretranslate.de/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate2",
            "url": "https://translate.argosopentech.com/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate3",
            "url": "https://translate.fortytwo-it.com/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate4",
            "url": "https://translate.terraprint.co/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate5",
            "url": "https://translate.mentality.rip/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate6",
            "url": "https://translate.parvusvir.top/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate7",
            "url": "https://translate.vincentvandijck.com/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate8",
            "url": "https://translate.leptons.xyz/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate9",
            "url": "https://translate.eldreel.com/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate10",
            "url": "https://translate.liberama.org/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate11",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate12",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate13",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate14",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate15",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate16",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate17",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate18",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate19",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate20",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate21",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate22",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate23",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate24",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate25",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate26",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate27",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate28",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate29",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate30",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate31",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate32",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate33",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate34",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate35",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate36",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate37",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate38",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate39",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate40",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate41",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate42",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate43",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate44",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate45",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate46",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate47",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate48",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate49",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "LibreTranslate50",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        # APIs Alternativas Gratuitas
        {
            "nombre": "Yandex",
            "url": "https://translate.yandex.net/api/v1.5/tr.json/translate",
            "limite": 10000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "BingTranslate",
            "url": "https://api.cognitive.microsofttranslator.com/translate",
            "limite": 2000000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "DeepL",
            "url": "https://api-free.deepl.com/v2/translate",
            "limite": 500000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "Apertium",
            "url": "https://apertium.org/apy/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI",
            "url": "https://translate-api.vercel.app/api/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "FreeTranslate",
            "url": "https://translate.fortytwo-it.com/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateService",
            "url": "https://translate.terraprint.co/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI2",
            "url": "https://translate.mentality.rip/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI3",
            "url": "https://translate.parvusvir.top/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI4",
            "url": "https://translate.vincentvandijck.com/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI5",
            "url": "https://translate.leptons.xyz/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI6",
            "url": "https://translate.eldreel.com/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI7",
            "url": "https://translate.liberama.org/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI8",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI9",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI10",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI11",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI12",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI13",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI14",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI15",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI16",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI17",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI18",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI19",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI20",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI21",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI22",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI23",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI24",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI25",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI26",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI27",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI28",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI29",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI30",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI31",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI32",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI33",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI34",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI35",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI36",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI37",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI38",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI39",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI40",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI41",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI42",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI43",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI44",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI45",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI46",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI47",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI48",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI49",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI50",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI51",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI52",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI53",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI54",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI55",
            "url": "https://translate.lingva.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI56",
            "url": "https://translate.lingva.dev/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI57",
            "url": "https://translate.lingva.art/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI58",
            "url": "https://translate.lingva.poetry.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI59",
            "url": "https://translate.lingva.lunar.icu/translate",
            "limite": 1000,
            "contador": 0,
            "activa": True
        },
        {
            "nombre": "TranslateAPI60",
            "url": "https://translate.lingva.ml/translate",
            "limite": 1000,
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

    def cambiar_api(self):
        """Cambia a la siguiente API disponible"""
        for i in range(len(self.apis_disponibles)):
            siguiente = (self.api_actual + i + 1) % len(self.apis_disponibles)
            if self.apis_disponibles[siguiente]["activa"] and self.apis_disponibles[siguiente]["contador"] < self.apis_disponibles[siguiente]["limite"]:
                self.api_actual = siguiente
                api = self.apis_disponibles[siguiente]
                self.log.emit(f"🔄 Cambiando a API: {api['nombre']} ({api['limite'] - api['contador']} traducciones disponibles)")
                return True
        return False

    def traducir_con_api(self, texto, api_info):
        """Traduce usando la API especificada"""
        if api_info["nombre"] == "MyMemory":
            return self.traducir_mymemory(texto)
        elif api_info["nombre"] == "GoogleTranslate":
            return self.traducir_google(texto)
        elif api_info["nombre"].startswith("LibreTranslate") or api_info["nombre"].startswith("TranslateAPI"):
            return self.traducir_libretranslate(texto, api_info["url"])
        elif api_info["nombre"] == "Yandex":
            return self.traducir_yandex(texto)
        elif api_info["nombre"] == "BingTranslate":
            return self.traducir_bing(texto)
        elif api_info["nombre"] == "DeepL":
            return self.traducir_deepl(texto)
        elif api_info["nombre"] == "Apertium":
            return self.traducir_apertium(texto)
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
            response = requests.post(url, json=data, timeout=30)
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
        except Exception as e:
            self.log.emit(f"❌ LibreTranslate exception: {e}")
            return texto

    def traducir_yandex(self, texto):
        """Traduce usando Yandex API (requiere key)"""
        # Yandex requiere API key, así que por ahora devolvemos el texto original
        self.log.emit(f"⚠️ Yandex: Requiere API key, manteniendo original: '{texto}'")
        return texto

    def traducir_bing(self, texto):
        """Traduce usando Bing Translator API (requiere key)"""
        # Bing requiere API key, así que por ahora devolvemos el texto original
        self.log.emit(f"⚠️ Bing: Requiere API key, manteniendo original: '{texto}'")
        return texto

    def traducir_deepl(self, texto):
        """Traduce usando DeepL API (requiere key)"""
        # DeepL requiere API key, así que por ahora devolvemos el texto original
        self.log.emit(f"⚠️ DeepL: Requiere API key, manteniendo original: '{texto}'")
        return texto

    def traducir_apertium(self, texto):
        # Apertium no requiere API key, así que simplemente devolvemos el texto original
        self.log.emit(f"⚠️ Apertium: No se requiere API key, manteniendo original: '{texto}'")
        return texto

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
        # Patrones mejorados para capturar todo el texto entre comillas
        patron_dialogo = re.compile(r'^(\s*[a-zA-Z0-9_]+\s+)(["\'])(.*?)\2(\s*)$', re.DOTALL)
        patron_linea_comillas = re.compile(r'^(\s*)(["\'])(.*?)\2(\s*)$', re.DOTALL)
        patron_style_prefix = re.compile(r'^(\s*style_prefix\s+)(["\'])(.*?)\2(\s*)$', re.DOTALL)
        
        # Nuevos patrones para textos de traducción de Ren'Py
        patron_traduccion = re.compile(r'textbutton\s+_\s*\(\s*["\'](.*?)["\']\s*\)', re.DOTALL)
        patron_traduccion_simple = re.compile(r'_\s*\(\s*["\'](.*?)["\']\s*\)', re.DOTALL)
        
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
            
            # No traducir si contiene caracteres especiales de programación
            if any(char in texto for char in "{}[]()<>$@#%^&*+=|\\"):
                return False
            
            # No traducir si parece ser código o variable
            if texto_strip.startswith(("$", "[", "{", "config.", "gui.", "renpy.")):
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
            
            return True

        try:
            with open(self.archivo_entrada, "r", encoding="utf-8") as f_in:
                lineas = f_in.readlines()
        except Exception as e:
            self.log.emit(f"❌ Error al leer archivo: {e}")
            self.terminado.emit(False)
            return

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

    def mostrar_estadisticas_apis(self):
        """Muestra estadísticas de uso de todas las APIs"""
        self.log.emit(f"📊 Estadísticas de APIs (110 APIs totales):")
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
        self.log.emit(f"   • Capacidad restante: ~{apis_activas * 1000 - total_traducciones}")


class ConfiguracionTraductor:
    """Configuración centralizada para el traductor"""
    
    # Límites de APIs (110 APIs totales)
    LIMITES_APIS = {
        "MyMemory": 800,
        "GoogleTranslate": 5000,
        "Yandex": 10000,
        "BingTranslate": 2000000,
        "DeepL": 500000,
        "Apertium": 1000
    }
    
    # URLs de APIs principales
    URLS_APIS = {
        "MyMemory": "https://api.mymemory.translated.net/get",
        "GoogleTranslate": "https://translate.googleapis.com/translate_a/single",
        "Yandex": "https://translate.yandex.net/api/v1.5/tr.json/translate",
        "BingTranslate": "https://api.cognitive.microsofttranslator.com/translate",
        "DeepL": "https://api-free.deepl.com/v2/translate",
        "Apertium": "https://apertium.org/apy/translate"
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
        self.combo_origen.addItems(["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"])
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
        self.combo_destino.addItems(["es", "en", "fr", "de", "it", "pt", "ja", "ko", "zh"])
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

        if carpeta_entrada.lower().endswith('.rpa'):
            tipo_archivo = "RPA"
        elif carpeta_entrada.lower().endswith('.rpyc'):
            tipo_archivo = "RPYC"
        else:
            QMessageBox.warning(self, "Error", "Solo se soportan carpetas con archivos .rpa y .rpyc")
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
        """Muestra estadísticas de todas las APIs en el log"""
        if hasattr(self, 'traductor_thread') and self.traductor_thread:
            self.traductor_thread.mostrar_estadisticas_apis()
        else:
            self.log_area.append("⚠️ No hay traducción activa para mostrar estadísticas")

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
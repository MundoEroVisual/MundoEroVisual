#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para organizar automáticamente los archivos del proyecto
"""

import os
import shutil
import glob

def organizar_archivos():
    """Organiza los archivos en carpetas apropiadas"""
    
    # Definir las carpetas y sus archivos correspondientes
    carpetas = {
        "Traductor IA": [
            "TraductorIA_Inteligente.pyw",
            "servicios_traduccion.py", 
            "asistente_virtual.py"
        ],
        "Documentacion": [
            "INSTRUCCIONES_TRADUCTOR_IA.md",
            "README*.md",
            "*.md"
        ],
        "Herramientas": [
            "EroverseTraductor.py",
            "*.pyw",
            "*.py"
        ],
        "Archivos Antiguos": [
            "Corrector*.pyw",
            "test_*.py",
            "ejemplo*.py",
            "script*.rpy"
        ]
    }
    
    # Crear carpetas si no existen
    for carpeta in carpetas.keys():
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            print(f"✅ Carpeta creada: {carpeta}")
    
    # Mover archivos
    for carpeta, patrones in carpetas.items():
        for patron in patrones:
            archivos = glob.glob(patron)
            for archivo in archivos:
                if os.path.isfile(archivo):
                    try:
                        destino = os.path.join(carpeta, archivo)
                        if not os.path.exists(destino):
                            shutil.move(archivo, destino)
                            print(f"📁 Movido: {archivo} → {carpeta}/")
                        else:
                            print(f"⚠️ Ya existe: {destino}")
                    except Exception as e:
                        print(f"❌ Error moviendo {archivo}: {e}")
    
    # Limpiar archivos innecesarios
    archivos_a_eliminar = [
        "CorrectorRenPy_Simple.pyw",
        "CorrectorRenPy_Mejorado.pyw", 
        "test_error_exacto.rpy",
        "test_error_exacto.py",
        "ejemplo.rpy",
        "ejemploo.py"
    ]
    
    for archivo in archivos_a_eliminar:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                print(f"🗑️ Eliminado: {archivo}")
            except Exception as e:
                print(f"❌ Error eliminando {archivo}: {e}")
    
    print("\n🎉 Organización completada!")

if __name__ == "__main__":
    organizar_archivos() 
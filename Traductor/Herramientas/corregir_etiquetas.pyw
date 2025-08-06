#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os

def corregir_etiquetas_texto(archivo_entrada, archivo_salida=None):
    """
    Corrige las etiquetas de texto incorrectas en archivos Ren'Py
    - Convierte {I} a {i}
    - Convierte {/I} a {/i}
    - Corrige etiquetas mal cerradas
    """
    
    if archivo_salida is None:
        archivo_salida = archivo_entrada
    
    try:
        # Leer archivo
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print(f"📁 Archivo leído: {archivo_entrada}")
        print(f"📊 Tamaño: {len(contenido)} caracteres")
        
        # Contadores para estadísticas
        correcciones_realizadas = 0
        lineas_procesadas = 0
        
        # Dividir en líneas para procesar
        lineas = contenido.split('\n')
        lineas_corregidas = []
        
        for i, linea in enumerate(lineas):
            linea_original = linea
            linea_corregida = linea
            
            # Corregir etiquetas de texto
            # {I} -> {i}
            if '{I}' in linea:
                linea_corregida = linea_corregida.replace('{I}', '{i}')
                correcciones_realizadas += 1
                print(f"🔧 Línea {i+1}: {I} -> {i}")
            
            # {/I} -> {/i}
            if '{/I}' in linea:
                linea_corregida = linea_corregida.replace('{/I}', '{/i}')
                correcciones_realizadas += 1
                print(f"🔧 Línea {i+1}: {/I} -> {/i}")
            
            # Corregir etiquetas mal cerradas (sin /)
            # Buscar patrones como {i}texto{/i} pero con errores
            patron_etiqueta_mal_cerrada = r'\{i\}([^{]*?)\{i\}'
            coincidencias = re.finditer(patron_etiqueta_mal_cerrada, linea_corregida)
            for match in coincidencias:
                texto_entre_etiquetas = match.group(1)
                # Reemplazar la segunda {i} con {/i}
                linea_corregida = linea_corregida.replace(
                    f'{{i}}{texto_entre_etiquetas}{{i}}',
                    f'{{i}}{texto_entre_etiquetas}{{/i}}'
                )
                correcciones_realizadas += 1
                print(f"🔧 Línea {i+1}: Corregida etiqueta mal cerrada")
            
            # Corregir etiquetas que empiezan con mayúscula pero terminan con minúscula
            patron_inconsistente = r'\{I\}([^{]*?)\{/i\}'
            coincidencias = re.finditer(patron_inconsistente, linea_corregida)
            for match in coincidencias:
                texto_entre_etiquetas = match.group(1)
                linea_corregida = linea_corregida.replace(
                    f'{{I}}{texto_entre_etiquetas}{{/i}}',
                    f'{{i}}{texto_entre_etiquetas}{{/i}}'
                )
                correcciones_realizadas += 1
                print(f"🔧 Línea {i+1}: Corregida inconsistencia de etiquetas")
            
            # Corregir etiquetas que empiezan con minúscula pero terminan con mayúscula
            patron_inconsistente2 = r'\{i\}([^{]*?)\{/I\}'
            coincidencias = re.finditer(patron_inconsistente2, linea_corregida)
            for match in coincidencias:
                texto_entre_etiquetas = match.group(1)
                linea_corregida = linea_corregida.replace(
                    f'{{i}}{texto_entre_etiquetas}{{/I}}',
                    f'{{i}}{texto_entre_etiquetas}{{/i}}'
                )
                correcciones_realizadas += 1
                print(f"🔧 Línea {i+1}: Corregida inconsistencia de etiquetas")
            
            lineas_corregidas.append(linea_corregida)
            lineas_procesadas += 1
        
        # Unir las líneas corregidas
        contenido_corregido = '\n'.join(lineas_corregidas)
        
        # Guardar archivo corregido
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)
        
        print(f"\n✅ Corrección completada:")
        print(f"📊 Líneas procesadas: {lineas_procesadas}")
        print(f"🔧 Correcciones realizadas: {correcciones_realizadas}")
        print(f"💾 Archivo guardado: {archivo_salida}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🛠️  Corrector de Etiquetas de Texto Ren'Py")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Uso: python corregir_etiquetas.py <archivo_entrada> [archivo_salida]")
        print("\nEjemplos:")
        print("  python corregir_etiquetas.py script.rpy")
        print("  python corregir_etiquetas.py script.rpy script_corregido.rpy")
        return
    
    archivo_entrada = sys.argv[1]
    archivo_salida = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(archivo_entrada):
        print(f"❌ Error: El archivo '{archivo_entrada}' no existe")
        return
    
    print(f"🎯 Archivo a corregir: {archivo_entrada}")
    if archivo_salida:
        print(f"💾 Archivo de salida: {archivo_salida}")
    else:
        print(f"💾 Se sobrescribirá el archivo original")
    
    print("\n🚀 Iniciando corrección...")
    print("-" * 50)
    
    exito = corregir_etiquetas_texto(archivo_entrada, archivo_salida)
    
    if exito:
        print("\n🎉 ¡Corrección completada exitosamente!")
    else:
        print("\n❌ Error durante la corrección")

if __name__ == "__main__":
    main() 
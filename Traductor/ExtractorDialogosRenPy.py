#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor Especializado para Diálogos RenPy
Extrae diálogos en el formato específico de novelas visuales
"""

import re
import os
import json
from datetime import datetime

class ExtractorDialogosRenPy:
    def __init__(self):
        self.dialogos_extraidos = []
        self.estadisticas = {
            'archivos_procesados': 0,
            'dialogos_totales': 0,
            'personajes_unicos': set(),
            'archivos_info': []
        }
    
    def extraer_del_archivo(self, ruta_archivo):
        """Extrae diálogos de un archivo específico"""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except UnicodeDecodeError:
            # Intentar con otras codificaciones
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(ruta_archivo, 'r', encoding=encoding) as f:
                        contenido = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"❌ No se pudo leer: {ruta_archivo}")
                return []
        
        return self.extraer_dialogos_del_contenido(contenido, ruta_archivo)
    
    def extraer_dialogos_del_contenido(self, contenido, nombre_archivo):
        """Extrae diálogos del contenido del archivo"""
        dialogos = []
        lineas = contenido.split('\n')
        
        # Patrones específicos para RenPy
        patrones = [
            # Patrón: Personaje "Diálogo"
            (r'^\s*([^"]+)\s*"([^"]*)"', 'personaje_dialogo'),
            # Patrón: Solo "Diálogo"
            (r'^\s*"([^"]*)"', 'solo_dialogo'),
            # Patrón: translate SpanishHz etiqueta:
            (r'^\s*translate\s+SpanishHz\s+(\w+):\s*$', 'etiqueta_traduccion'),
            # Patrón: Comentario con diálogo
            (r'^\s*#\s*([^"]+)\s*"([^"]*)"', 'comentario_dialogo'),
            # Patrón: Comentario solo diálogo
            (r'^\s*#\s*"([^"]*)"', 'comentario_solo_dialogo'),
        ]
        
        etiqueta_actual = ""
        personaje_actual = ""
        
        for i, linea in enumerate(lineas):
            linea_numero = i + 1
            
            # Buscar etiquetas de traducción
            for patron, tipo in patrones:
                match = re.match(patron, linea)
                if match:
                    if tipo == 'etiqueta_traduccion':
                        etiqueta_actual = match.group(1)
                        continue
                    elif tipo == 'personaje_dialogo':
                        personaje = match.group(1).strip()
                        dialogo = match.group(2).strip()
                        if dialogo:
                            dialogos.append({
                                'archivo': nombre_archivo,
                                'linea': linea_numero,
                                'etiqueta': etiqueta_actual,
                                'personaje': personaje,
                                'dialogo': dialogo,
                                'tipo': 'personaje_dialogo',
                                'texto_completo': linea.strip()
                            })
                            self.estadisticas['personajes_unicos'].add(personaje)
                            break
                    elif tipo == 'solo_dialogo':
                        dialogo = match.group(1).strip()
                        if dialogo:
                            dialogos.append({
                                'archivo': nombre_archivo,
                                'linea': linea_numero,
                                'etiqueta': etiqueta_actual,
                                'personaje': personaje_actual,
                                'dialogo': dialogo,
                                'tipo': 'solo_dialogo',
                                'texto_completo': linea.strip()
                            })
                            break
                    elif tipo == 'comentario_dialogo':
                        personaje = match.group(1).strip()
                        dialogo = match.group(2).strip()
                        if dialogo:
                            dialogos.append({
                                'archivo': nombre_archivo,
                                'linea': linea_numero,
                                'etiqueta': etiqueta_actual,
                                'personaje': personaje,
                                'dialogo': dialogo,
                                'tipo': 'comentario_dialogo',
                                'texto_completo': linea.strip()
                            })
                            self.estadisticas['personajes_unicos'].add(personaje)
                            break
                    elif tipo == 'comentario_solo_dialogo':
                        dialogo = match.group(1).strip()
                        if dialogo:
                            dialogos.append({
                                'archivo': nombre_archivo,
                                'linea': linea_numero,
                                'etiqueta': etiqueta_actual,
                                'personaje': personaje_actual,
                                'dialogo': dialogo,
                                'tipo': 'comentario_solo_dialogo',
                                'texto_completo': linea.strip()
                            })
                            break
        
        return dialogos
    
    def procesar_directorio(self, directorio):
        """Procesa todos los archivos .rpy en un directorio"""
        dialogos_totales = []
        
        for root, dirs, files in os.walk(directorio):
            for file in files:
                if file.endswith('.rpy'):
                    ruta_completa = os.path.join(root, file)
                    print(f"🔍 Procesando: {file}")
                    
                    dialogos_archivo = self.extraer_del_archivo(ruta_completa)
                    
                    if dialogos_archivo:
                        dialogos_totales.extend(dialogos_archivo)
                        self.estadisticas['archivos_info'].append({
                            'archivo': file,
                            'dialogos': len(dialogos_archivo),
                            'ruta': ruta_completa
                        })
                        self.estadisticas['archivos_procesados'] += 1
                        self.estadisticas['dialogos_totales'] += len(dialogos_archivo)
        
        return dialogos_totales
    
    def generar_reporte(self, dialogos):
        """Genera un reporte detallado de los diálogos extraídos"""
        reporte = {
            'fecha': datetime.now().isoformat(),
            'estadisticas': {
                'archivos_procesados': self.estadisticas['archivos_procesados'],
                'dialogos_totales': self.estadisticas['dialogos_totales'],
                'personajes_unicos': len(self.estadisticas['personajes_unicos']),
                'personajes': list(self.estadisticas['personajes_unicos'])
            },
            'archivos': self.estadisticas['archivos_info'],
            'dialogos': dialogos
        }
        
        return reporte
    
    def guardar_reporte(self, reporte, archivo_salida):
        """Guarda el reporte en formato JSON"""
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)
    
    def generar_formato_traduccion(self, dialogos):
        """Genera el formato específico para traducción"""
        formato_traduccion = []
        
        # Agrupar por archivo
        archivos = {}
        for dialogo in dialogos:
            archivo = dialogo['archivo']
            if archivo not in archivos:
                archivos[archivo] = []
            archivos[archivo].append(dialogo)
        
        # Generar formato para cada archivo
        for archivo, dialogos_archivo in archivos.items():
            formato_traduccion.append(f"# ARQUIVO: {archivo} DIALOGOS: {len(dialogos_archivo)}")
            formato_traduccion.append("")
            
            for dialogo in dialogos_archivo:
                # Línea de etiqueta
                if dialogo['etiqueta']:
                    formato_traduccion.append(f"# {archivo}:{dialogo['linea']}")
                    formato_traduccion.append(f"translate SpanishHz {dialogo['etiqueta']}:")
                    formato_traduccion.append("")
                
                # Línea de comentario original
                if dialogo['personaje']:
                    formato_traduccion.append(f"#   {dialogo['personaje']} \"{dialogo['dialogo']}\"")
                else:
                    formato_traduccion.append(f"#   \"{dialogo['dialogo']}\"")
                
                # Línea de traducción (vacía para completar)
                if dialogo['personaje']:
                    formato_traduccion.append(f"    {dialogo['personaje']} \"[TRADUCIR: {dialogo['dialogo']}]\"")
                else:
                    formato_traduccion.append(f"    \"[TRADUCIR: {dialogo['dialogo']}]\"")
                
                formato_traduccion.append("")
        
        return '\n'.join(formato_traduccion)

def main():
    """Función principal de ejemplo"""
    extractor = ExtractorDialogosRenPy()
    
    # Ejemplo de uso
    print("🎭 Extractor de Diálogos RenPy")
    print("=" * 40)
    
    # Procesar directorio actual
    directorio = "."
    print(f"🔍 Procesando directorio: {directorio}")
    
    dialogos = extractor.procesar_directorio(directorio)
    
    if dialogos:
        print(f"\n✅ Extraídos {len(dialogos)} diálogos de {extractor.estadisticas['archivos_procesados']} archivos")
        
        # Generar reporte
        reporte = extractor.generar_reporte(dialogos)
        extractor.guardar_reporte(reporte, 'reporte_dialogos.json')
        print("📊 Reporte guardado en: reporte_dialogos.json")
        
        # Generar formato de traducción
        formato_traduccion = extractor.generar_formato_traduccion(dialogos)
        with open('dialogos_para_traducir.txt', 'w', encoding='utf-8') as f:
            f.write(formato_traduccion)
        print("📝 Formato de traducción guardado en: dialogos_para_traducir.txt")
        
        # Mostrar estadísticas
        print(f"\n📈 Estadísticas:")
        print(f"   • Archivos procesados: {extractor.estadisticas['archivos_procesados']}")
        print(f"   • Diálogos totales: {extractor.estadisticas['dialogos_totales']}")
        print(f"   • Personajes únicos: {len(extractor.estadisticas['personajes_unicos'])}")
        
        if extractor.estadisticas['personajes_unicos']:
            print(f"   • Personajes: {', '.join(sorted(extractor.estadisticas['personajes_unicos']))}")
    
    else:
        print("❌ No se encontraron diálogos para extraer")

if __name__ == "__main__":
    main() 
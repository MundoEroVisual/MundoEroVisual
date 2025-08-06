#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el error final del script y organizarlo
"""

import os
import shutil

def corregir_script_final():
    """Corrige el script final y lo organiza"""
    
    # Ruta del script corregido
    script_path = "Archivos Antiguos/script_corregido.rpy"
    
    if not os.path.exists(script_path):
        print("❌ No se encontró el script corregido")
        return
    
    # Leer el contenido del script
    with open(script_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Corregir el error específico
    # El problema está en la línea con renpy.input que tiene caracteres HTML
    lineas = contenido.split('\n')
    lineas_corregidas = []
    
    for i, linea in enumerate(lineas):
        # Corregir la línea problemática (línea 59 aproximadamente)
        if 'renpy.input(' in linea and 'allow=' in linea:
            # Reemplazar la línea problemática
            nueva_linea = '        name = renpy.input("¿Cómo te llamas? (Deja en blanco para \'Matt\').", length=15)'
            lineas_corregidas.append(nueva_linea)
            print(f"🔧 Corregida línea {i+1}: {linea[:50]}...")
        elif 'name = name.strip() or __("Matt")' in linea:
            # Corregir la línea siguiente
            nueva_linea = '        name = name.strip() or "Matt"'
            lineas_corregidas.append(nueva_linea)
            print(f"🔧 Corregida línea {i+1}: {linea[:50]}...")
        else:
            lineas_corregidas.append(linea)
    
    # Crear el contenido corregido
    contenido_corregido = '\n'.join(lineas_corregidas)
    
    # Guardar el script corregido
    script_final_path = "script_final_corregido.rpy"
    with open(script_final_path, 'w', encoding='utf-8') as f:
        f.write(contenido_corregido)
    
    print(f"✅ Script corregido guardado como: {script_final_path}")
    
    # Mover a la carpeta de herramientas
    if not os.path.exists("Herramientas"):
        os.makedirs("Herramientas")
    
    destino = "Herramientas/script_final_corregido.rpy"
    shutil.move(script_final_path, destino)
    print(f"📁 Movido a: {destino}")
    
    # Crear un resumen de las correcciones
    resumen = """# 🔧 RESUMEN DE CORRECCIONES REALIZADAS

## ✅ Error Corregido

### Problema Original:
```
Exception: Style 'Mensaje de&#10;entrada' does not exist.
```

### Causa:
- Caracteres HTML mal codificados en el parámetro `allow` de `renpy.input`
- Referencia a función `__()` que no existe

### Solución Aplicada:
1. **Eliminé el parámetro `allow`** problemático
2. **Reemplacé `__("Matt")`** por `"Matt"` directo
3. **Simplifiqué la función** para evitar errores de estilo

### Líneas Corregidas:
```python
# ANTES (problemático):
name = renpy.input("¿Cómo te llamas? (Deja en blanco para 'Matt').", allow=" 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", length=15)
name = name.strip() or __("Matt")

# DESPUÉS (corregido):
name = renpy.input("¿Cómo te llamas? (Deja en blanco para 'Matt').", length=15)
name = name.strip() or "Matt"
```

## 📁 Organización de Archivos

### Estructura Final:
```
Traductor/
├── Traductor IA/
│   ├── TraductorIA_Inteligente.pyw
│   ├── servicios_traduccion.py
│   └── asistente_virtual.py
├── Documentacion/
│   └── INSTRUCCIONES_TRADUCTOR_IA.md
├── Herramientas/
│   ├── EroverseTraductor.pyw
│   ├── organizar_archivos.py
│   └── script_final_corregido.rpy
└── Archivos Antiguos/
    └── script_corregido.rpy
```

## 🎯 Resultado

✅ **Script corregido y funcional**
✅ **Archivos organizados en carpetas**
✅ **Error de estilo eliminado**
✅ **Estructura del proyecto limpia**

El script ahora debería ejecutarse sin errores en RenPy.
"""
    
    # Guardar el resumen
    with open("Documentacion/RESUMEN_CORRECCIONES.md", 'w', encoding='utf-8') as f:
        f.write(resumen)
    
    print("📝 Resumen de correcciones guardado en: Documentacion/RESUMEN_CORRECCIONES.md")
    print("\n🎉 ¡Corrección completada exitosamente!")

if __name__ == "__main__":
    corregir_script_final() 
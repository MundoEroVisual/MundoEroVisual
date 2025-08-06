# 🎭 INSTRUCCIONES - TRADUCTOR DE NOVELAS VISUALES

## 🚀 **Descripción General**

El **Traductor de Novelas Visuales** es una herramienta especializada para extraer, traducir y reinsertar solo los diálogos de novelas visuales RenPy, manteniendo el formato original y la estructura del juego.

### 🎯 **Características Principales**

#### **1. Extracción Inteligente de Diálogos**
- **Detección automática**: Identifica patrones de diálogos en archivos .rpy
- **Preservación de contexto**: Mantiene información de personajes y etiquetas
- **Múltiples formatos**: Soporta diferentes estilos de diálogos
- **Estadísticas detalladas**: Reporta cantidad de diálogos y personajes

#### **2. Traducción con Memoria**
- **Aprendizaje continuo**: Recuerda traducciones previas
- **Consistencia**: Mantiene términos uniformes
- **Contexto de personajes**: Preserva voces y estilos
- **Optimización**: Mejora con cada uso

#### **3. Reinserción Automática**
- **Formato preservado**: Mantiene la estructura original
- **Líneas exactas**: Reemplaza solo los diálogos
- **Backup automático**: Crea copias de seguridad
- **Validación**: Verifica la integridad del archivo

## 📋 **Instrucciones de Uso**

### **Método 1: Traductor GUI Completo**

#### **1. Iniciar la Aplicación**
```bash
python TraductorNovelasVisuales.pyw
```

#### **2. Cargar Archivo**
1. **Haz clic en "📁 CARGAR ARCHIVO"**
2. **Selecciona el archivo .rpy** de la novela visual
3. **El contenido aparecerá** en el panel izquierdo

#### **3. Extraer Diálogos**
1. **Haz clic en "🔍 EXTRAER DIÁLOGOS"**
2. **La aplicación analizará** el archivo automáticamente
3. **Se mostrarán los diálogos** extraídos en el panel derecho
4. **Verás estadísticas** de personajes y cantidad de diálogos

#### **4. Traducir Diálogos**
1. **Haz clic en "🔄 TRADUCIR"**
2. **La IA traducirá** automáticamente todos los diálogos
3. **Se aplicará la memoria** de traducciones previas
4. **Los resultados aparecerán** en el panel derecho

#### **5. Guardar Traducción**
1. **Haz clic en "💾 GUARDAR"**
2. **Selecciona la ubicación** para el archivo traducido
3. **Se guardará** con el formato original preservado

#### **6. Gestionar Memoria**
1. **Haz clic en "🧠 MEMORIA"**
2. **Revisa las traducciones** guardadas
3. **Aprende de correcciones** manuales

### **Método 2: Extractor Especializado**

#### **1. Ejecutar Extractor**
```bash
python ExtractorDialogosRenPy.py
```

#### **2. Procesar Directorio**
- **El script procesará** todos los archivos .rpy del directorio
- **Generará reportes** detallados de diálogos
- **Creará archivos** de formato para traducción

#### **3. Archivos Generados**
- **`reporte_dialogos.json`**: Reporte completo en formato JSON
- **`dialogos_para_traducir.txt`**: Formato específico para traducción manual

## 🎯 **Formatos Soportados**

### **Patrones de Diálogos Detectados**

#### **1. Diálogo con Personaje**
```renpy
Felicia "What am I going to do? Sigh.."
mc "Hey you did your best, it's alright"
```

#### **2. Diálogo Solo**
```renpy
"Pronto se le mostrará un selector de colores."
"Elegiste el color [chosen_color]."
```

#### **3. Etiquetas de Traducción**
```renpy
translate SpanishHz intro_169ef2b6:
translate SpanishHz intro_d33d5b55:
```

#### **4. Comentarios con Diálogos**
```renpy
#   Felicia "What am I going to do? Sigh.."
#   mc "Hey you did your best, it's alright"
```

## 📊 **Estadísticas y Reportes**

### **Información Proporcionada**

#### **Estadísticas Generales**
- **Archivos procesados**: Número total de archivos .rpy
- **Diálogos totales**: Cantidad de diálogos extraídos
- **Personajes únicos**: Lista de personajes encontrados
- **Tiempo de procesamiento**: Duración del análisis

#### **Reporte por Archivo**
```json
{
  "archivo": "episodes.rpy",
  "dialogos": 1045,
  "ruta": "./game/episodes.rpy"
}
```

#### **Información de Diálogo**
```json
{
  "archivo": "episodes.rpy",
  "linea": 54,
  "etiqueta": "intro_169ef2b6",
  "personaje": "Felicia",
  "dialogo": "What am I going to do? Sigh..",
  "tipo": "personaje_dialogo",
  "texto_completo": "Felicia \"What am I going to do? Sigh..\""
}
```

## 🔧 **Configuración Avanzada**

### **Archivos de Configuración**

#### **memoria_traducciones.json**
```json
{
  "hello": "hola",
  "goodbye": "adiós",
  "thank you": "gracias",
  "please": "por favor"
}
```

#### **Personalización de Patrones**
```python
# Agregar nuevos patrones en ExtractorDialogosRenPy.py
patrones = [
    (r'^\s*([^"]+)\s*"([^"]*)"', 'personaje_dialogo'),
    (r'^\s*"([^"]*)"', 'solo_dialogo'),
    # Agregar tu patrón personalizado aquí
]
```

### **Opciones de Traducción**

#### **Servicios de Traducción**
- **Traducción básica**: Diccionario de palabras comunes
- **Memoria inteligente**: Aprendizaje de traducciones previas
- **Contexto de personajes**: Preservación de voces únicas
- **Consistencia terminológica**: Términos uniformes

## 🎭 **Casos de Uso Específicos**

### **Para Novelas Visuales Completas**

#### **1. Procesamiento por Episodios**
```bash
# Procesar solo archivos de episodios
python ExtractorDialogosRenPy.py --archivos "episodes.rpy,chapter1.rpy"
```

#### **2. Traducción por Personajes**
- **Filtrar por personaje**: Traducir solo diálogos de personajes específicos
- **Mantener voces**: Preservar el estilo de habla de cada personaje
- **Contexto emocional**: Considerar el estado emocional del personaje

#### **3. Traducción por Escenas**
- **Agrupar por etiqueta**: Traducir escenas completas
- **Mantener coherencia**: Preservar la narrativa
- **Contexto de ubicación**: Adaptar según el entorno

### **Para Archivos de Ejemplo**

#### **Formato de Entrada**
```renpy
# game/episodes.rpy:54
translate SpanishHz intro_169ef2b6:

#   Felicia "What am I going to do? Sigh.."
    Felicia "¿Qué voy a hacer? Suspiro..."

# game/episodes.rpy:55
translate SpanishHz intro_d33d5b55:

#   mc "Hey you did your best, it's alright I still got selected right?"
    mc "Oye, hiciste lo mejor que pudiste, está bien, aún así me seleccionaron, ¿verdad?"
```

#### **Formato de Salida**
```renpy
# game/episodes.rpy:54
translate SpanishHz intro_169ef2b6:

#   Felicia "What am I going to do? Sigh.."
    Felicia "¿Qué voy a hacer? Suspiro..."

# game/episodes.rpy:55
translate SpanishHz intro_d33d5b55:

#   mc "Hey you did your best, it's alright I still got selected right?"
    mc "Oye, hiciste lo mejor que pudiste, está bien, aún así me seleccionaron, ¿verdad?"
```

## 🚨 **Solución de Problemas**

### **Problemas Comunes**

#### **No se detectan diálogos**
- **Verificar formato**: Asegúrate de que los diálogos usen comillas dobles
- **Revisar codificación**: El archivo debe estar en UTF-8
- **Comprobar patrones**: Los diálogos deben seguir los patrones soportados

#### **Traducción incorrecta**
- **Revisar memoria**: Verifica las traducciones guardadas
- **Corregir manualmente**: Edita las traducciones incorrectas
- **Reiniciar memoria**: Borra `memoria_traducciones.json` si es necesario

#### **Archivo corrupto**
- **Crear backup**: Siempre haz copias de seguridad
- **Verificar permisos**: Asegúrate de tener permisos de escritura
- **Revisar sintaxis**: Valida que el archivo .rpy sea válido

### **Logs y Debugging**

#### **Archivos de Log**
- **`reporte_dialogos.json`**: Información detallada de extracción
- **`memoria_traducciones.json`**: Traducciones guardadas
- **`dialogos_para_traducir.txt`**: Formato para traducción manual

#### **Información de Debug**
- **Estadísticas**: Número de archivos y diálogos procesados
- **Personajes**: Lista de personajes únicos encontrados
- **Errores**: Problemas durante el procesamiento

## 🔮 **Características Futuras**

### **Próximas Mejoras**

1. **Integración con APIs reales**: Google Translate, DeepL
2. **Análisis de contexto**: Detección de emociones y situaciones
3. **Traducción en tiempo real**: Mientras escribes
4. **Soporte para más idiomas**: Múltiples pares de idiomas
5. **Interfaz web**: Versión online del traductor
6. **Colaboración**: Compartir traducciones entre usuarios
7. **Análisis de calidad**: Métricas de calidad automáticas
8. **Aprendizaje profundo**: Redes neuronales para traducción

### **Expansiones Planificadas**

1. **Traducción de audio**: Reconocimiento de voz
2. **Traducción de imágenes**: OCR y traducción
3. **Traducción de video**: Subtítulos automáticos
4. **API pública**: Para desarrolladores
5. **Plugins**: Extensiones personalizables

## 📞 **Soporte**

### **Contacto**
- **Problemas técnicos**: Revisa la documentación
- **Sugerencias**: Usa el sistema de reportes
- **Bugs**: Reporta con logs detallados

### **Recursos Adicionales**
- **Documentación**: Archivos README
- **Ejemplos**: Archivos de prueba incluidos
- **Comunidad**: Foros de desarrollo

---

## 🎉 **¡Disfruta tu Traductor de Novelas Visuales!**

Con estas herramientas especializadas, tienes todo lo necesario para traducir novelas visuales de manera eficiente y profesional. ¡Explora todas las funciones y descubre cómo simplificar tu proceso de traducción! 
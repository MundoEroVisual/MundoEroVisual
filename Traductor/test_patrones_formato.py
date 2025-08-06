import re

# Patrones del traductor
patron_formato_especifico = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*"([^"]*)"\s*$', re.DOTALL)
patron_linea_vacia = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*""\s*$', re.DOTALL)

# Líneas de prueba
lineas_prueba = [
    '    # m "({i}*sigh* Looks like she snuck in again.{/i})"',
    '    m ""',
    '    # s "Hello world"',
    '    s ""',
    '    # n "Some narrative text"',
    '    n ""'
]

print("=== PRUEBA DE PATRONES ===")
for i, linea in enumerate(lineas_prueba):
    print(f"\nLínea {i+1}: '{linea}'")
    
    # Probar patrón de formato específico
    match_formato = patron_formato_especifico.match(linea)
    if match_formato:
        personaje = match_formato.group(1)
        texto = match_formato.group(2)
        print(f"  ✅ Formato específico detectado:")
        print(f"     Personaje: '{personaje}'")
        print(f"     Texto: '{texto}'")
    else:
        print(f"  ❌ No coincide con formato específico")
    
    # Probar patrón de línea vacía
    match_vacia = patron_linea_vacia.match(linea)
    if match_vacia:
        personaje = match_vacia.group(1)
        print(f"  ✅ Línea vacía detectada:")
        print(f"     Personaje: '{personaje}'")
    else:
        print(f"  ❌ No es línea vacía")

print("\n=== SIMULACIÓN DE TRADUCCIÓN ===")
for i in range(0, len(lineas_prueba), 2):
    if i + 1 < len(lineas_prueba):
        linea_comentario = lineas_prueba[i]
        linea_vacia = lineas_prueba[i + 1]
        
        match_comentario = patron_formato_especifico.match(linea_comentario)
        match_vacia = patron_linea_vacia.match(linea_vacia)
        
        if match_comentario and match_vacia:
            personaje_comentario = match_comentario.group(1)
            texto_original = match_comentario.group(2)
            personaje_vacio = match_vacia.group(1)
            
            print(f"\n📝 Par detectado:")
            print(f"   Comentario: {linea_comentario}")
            print(f"   Línea vacía: {linea_vacia}")
            print(f"   Personaje: '{personaje_comentario}' -> '{personaje_vacio}'")
            print(f"   Texto a traducir: '{texto_original}'")
            
            # Simular traducción
            texto_trad = texto_original.replace("sigh", "suspiro").replace("Looks like she snuck in again", "Parece que se coló de nuevo")
            linea_traducida = f'    {personaje_vacio} "{texto_trad}"'
            print(f"   Traducción: {linea_traducida}") 
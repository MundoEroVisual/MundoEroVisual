# Proyecto Web de Novelas

Este proyecto es una plataforma para gestionar y mostrar novelas visuales. Permite a los administradores subir nuevas novelas y generar páginas HTML para cada novela y por género.

## Estructura del Proyecto

- **data/**: Contiene el archivo `novelas.json` donde se almacenan las novelas en formato JSON.
- **imagenes/**: Carpeta destinada a almacenar las imágenes de las novelas.
- **public/**: Contiene las páginas HTML públicas, incluyendo `admin.html` para la administración y `index.html` para la visualización de novelas.
- **scripts/**: Incluye scripts de Node.js:
  - `subirNovela.js`: Procesa y guarda las novelas subidas por el administrador.
  - `generarPaginas.js`: Genera subpáginas HTML y páginas por género a partir de las novelas.
- **package.json**: Archivo de configuración del proyecto que incluye las dependencias necesarias.

## Instalación

1. Clona el repositorio en tu máquina local.
2. Navega a la carpeta del proyecto.
3. Ejecuta `npm install` para instalar las dependencias.

## Uso

- Accede a `admin.html` para subir nuevas novelas.
- Las novelas se almacenarán en `novelas.json` y se generarán automáticamente las páginas correspondientes.
- Visita `index.html` para ver las novelas disponibles.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.
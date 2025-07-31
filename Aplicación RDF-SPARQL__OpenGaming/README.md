# OpenGaming - Recomendador de Videojuegos

Una aplicación web que permite encontrar videojuegos basándose en preferencias del usuario, utilizando consultas SPARQL a DBpedia.



## Archivos

### index.html
- Contiene la estructura HTML completa de la aplicación
- Formulario de preferencias con múltiples filtros
- Secciones para mostrar resultados y consultas SPARQL
- Enlaces a dependencias externas (Tailwind CSS, Google Fonts)

### styles.css
- Estilos personalizados para el tema gamer
- Efectos visuales como texto neón y hover effects
- Personalización de scrollbar
- Variables de color y fuentes temáticas

### script.js
- Manejo del formulario y eventos
- Construcción de consultas SPARQL dinámicas
- Comunicación con la API de DBpedia
- Renderizado de resultados en tarjetas

## Características

- **Filtros de búsqueda**: Género, plataforma, año, desarrollador, publicadora, modo de juego
- **Interfaz responsive**: Adaptable a diferentes tamaños de pantalla
- **Tema gamer**: Colores neón y efectos visuales
- **Debugging**: Visualización de consultas SPARQL generadas
- **Manejo de errores**: Mensajes informativos para diferentes escenarios

## Tecnologías Utilizadas

- HTML5
- CSS3 (con Tailwind CSS)
- JavaScript ES6+
- SPARQL (consultas a DBpedia)
- Google Fonts (Press Start 2P, Russo One)

## Instalación

1. Clona o descarga los archivos
2. Asegúrate de que todos los archivos estén en el mismo directorio
3. Abre `index.html` en un navegador web
4. ¡La aplicación estará lista para usar!

## Uso

1. Selecciona tus preferencias en el formulario
2. Haz clic en "Buscar Juegos"
3. Revisa los resultados mostrados en tarjetas
4. Haz clic en cualquier juego para ver más detalles en DBpedia

## Notas Técnicas

- La aplicación realiza consultas SPARQL a `https://dbpedia.org/sparql`
- Las consultas están limitadas a 10 resultados para optimizar rendimiento
- Se incluye funcionalidad de debugging para visualizar las consultas generadas
- Manejo de imágenes con fallback a placeholders cuando no están disponibles

## Autor

Jean Alejo
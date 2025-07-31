# Conversor Genérico CSV a RDF

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![RDF](https://img.shields.io/badge/RDF-Turtle%20%7C%20XML%20%7C%20N--Triples-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

Una herramienta intuitiva para convertir datos tabulares (CSV) en grafos de conocimiento RDF con mapeo inteligente y detección automática de contexto.

[Características](#características) •
[Instalación](#instalación) •
[Uso Rápido](#uso-rápido) •
[Ejemplos](#ejemplos) •
[Documentación](#documentación)

</div>

---

## 🚀 Características

- **🧠 Mapeo Inteligente**: Detección automática de contexto (académico/general) y generación de mapeos YAML
- **🎯 Interfaz Intuitiva**: GUI desarrollada con Tkinter, fácil de usar para usuarios no técnicos
- **🔄 Conversión Robusta**: Manejo inteligente de valores multivaluados y relaciones complejas
- **📊 Múltiples Formatos**: Exportación en Turtle, RDF/XML y N-Triples
- **⚡ Proceso en Tiempo Real**: Barra de progreso y logs detallados durante la conversión


## 📋 Requisitos del Sistema

- Python 3.8 o superior
- Librerías Python (ver `requirements.txt`)

## 🔧 Instalación

### Opción 1: Clonar el repositorio

```bash
git clone hhttps://github.com/Jgalejo/RACR_Proyectos_Finales.git
cd  Alejo_Jean__Conversion_RDF
pip install -r requirements.txt
```

### Opción 2: Instalación manual de dependencias

```bash
pip install pandas rdflib pyyaml tkinter
```

### Dependencias principales

```
pandas >= 1.3.0      # Manipulación de datos CSV
rdflib >= 6.0.0      # Creación y manejo de grafos RDF
PyYAML >= 5.4.0      # Procesamiento de archivos de configuración
tkinter              # Interfaz gráfica (incluido en Python)
```

## 🚀 Uso Rápido

### Ejecutar la aplicación

```bash
python Script_conversion.py
```

### Flujo básico de trabajo

1. **📁 Cargar CSV**: Selecciona tu archivo de datos tabulares
2. **⚙️ Configurar Mapeo**: Genera automáticamente o carga un archivo YAML de mapeo
3. **👀 Previsualizar**: Revisa la estructura de datos detectada
4. **🔄 Convertir**: Ejecuta la transformación CSV → RDF
5. **💾 Exportar**: Guarda tu grafo RDF en el formato deseado


## ⚙️ Configuración Avanzada

### Archivo de Mapeo YAML

El sistema puede generar automáticamente archivos de configuración, pero también puedes crear mapeos personalizados:

```yaml
base_uri: 'http://example.org/data/'
namespaces:
  ex: 'http://example.org/data/'
  schema: 'http://schema.org/'
  foaf: 'http://xmlns.com/foaf/0.1/'

subject:
  class: 'schema:Thing'
  primary_key: 'id'
  uri_template: 'resource/{value}'

properties:
  name:
    predicate: 'schema:name'
    type: 'literal'
  
  authors:
    predicate: 'schema:author'
    type: 'relation'
    separator: ';'
    target:
      uri_template: 'person/{value}'
      class: 'foaf:Person'
      properties:
        - predicate: 'foaf:name'
          type: 'literal'
          source: 'self'
```

### Tipos de Propiedades Soportadas

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `literal` | Valores de texto simples | Títulos, descripciones, fechas |
| `uri` | Referencias a recursos web | URLs, identificadores DOI |
| `relation` | Relaciones con otras entidades | Autores, categorías, organizaciones |

## 🧠 Detección Inteligente de Contexto

El sistema analiza automáticamente las columnas de tu CSV para determinar el contexto más apropiado:

### Contexto Académico 📚
**Detectado cuando encuentra:** DOI, Abstract, Journal, Publication, Volume, etc.

**Vocabularios utilizados:**
- Dublin Core (DC/DCTERMS)
- BIBO (Bibliographic Ontology)


### Contexto General 🌐
**Para cualquier otro tipo de datos**

**Vocabularios utilizados:**
- Schema.org
- FOAF (Friend of a Friend)

## 🔍 Funcionalidades Avanzadas

### Manejo de Valores Multivaluados
```csv
Authors,Author IDs
"John Doe;Jane Smith;Bob Wilson","123;456;789"
```

El sistema correlaciona automáticamente los valores usando separadores (`;` por defecto).

### Validación y Manejo de Errores
- ✅ Validación de formato CSV y YAML
- ✅ Detección de claves primarias vacías
- ✅ Manejo de URIs malformadas
- ✅ Logs detallados para depuración

### Formatos de Salida
- **Turtle (.ttl)**: Formato compacto y legible
- **RDF/XML (.rdf)**: Estándar W3C
- **N-Triples (.nt)**: Formato simple línea por línea



## 🐛 Reportar Problemas

Si encuentras algún bug o tienes sugerencias:

1. Revisa que no exista ya un issue similar
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducirlo
   - Archivos de ejemplo (CSV/YAML) si es relevante
   - Logs de error completos

## 📈 Casos de Uso

- **🎓 Académico**: Conversión de bibliografías y publicaciones científicas
- **🏢 Empresarial**: Transformación de catálogos de productos y datos corporativos
- **🏛️ Institucional**: Migración de datos de bibliotecas y archivos
- **🔬 Investigación**: Creación de knowledge bases para proyectos de IA



## 👨‍💻 Autor

Desarrollado como parte del proyecto de la asignatura **"Representación Avanzada del Conocimiento y Razonamiento"**.

---

<div align="center">

**¿Te ha resultado útil? ⭐ Dale una estrella al repositorio**

[Reportar Bug](../../issues) •
[Solicitar Feature](../../issues) •
[Documentación](docs/documentation.md)

</div>
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD
import uuid
import threading
import yaml
import re
import traceback

class YAMLEditorWindow:
    """Ventana independiente para editar archivos YAML de mapeo."""
    
    def __init__(self, parent, yaml_path=None, yaml_content=None):
        self.parent = parent
        self.yaml_path = yaml_path
        self.window = tk.Toplevel(parent.root)
        self.window.title("Editor de Mapeo YAML")
        self.window.geometry("800x600")
        self.window.transient(parent.root)
        self.window.grab_set()
        
        # Variables
        self.modified = False
        
        self.create_widgets()
        
        # Cargar contenido inicial
        if yaml_content:
            self.load_yaml_content(yaml_content)
        elif yaml_path:
            self.load_yaml_from_file(yaml_path)
            
        # Vincular eventos para detectar cambios
        self.yaml_editor.bind('<Key>', self.on_content_changed)
        self.yaml_editor.bind('<Button-1>', self.on_content_changed)
        
        # Protocolo de cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de herramientas
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Guardar", command=self.save_yaml).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Guardar Como...", command=self.save_yaml_as).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Validar YAML", command=self.validate_yaml).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Aplicar Cambios", command=self.apply_changes).pack(side=tk.RIGHT, padx=5)
        
        # Información del archivo
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.file_label = ttk.Label(info_frame, text="Archivo: Nuevo mapeo")
        self.file_label.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(info_frame, text="", foreground="green")
        self.status_label.pack(side=tk.RIGHT)
        
        # Editor de texto
        editor_frame = ttk.LabelFrame(main_frame, text="Contenido YAML", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.yaml_editor = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.NONE, 
            font=('Consolas', 10),
            tabs=('2c',)  # Tabulación de 2 espacios
        )
        self.yaml_editor.pack(fill=tk.BOTH, expand=True)
        
        # Área de validación
        validation_frame = ttk.LabelFrame(main_frame, text="Validación", padding=5)
        validation_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.validation_text = scrolledtext.ScrolledText(
            validation_frame, 
            height=4, 
            state='disabled',
            font=('Consolas', 9)
        )
        self.validation_text.pack(fill=tk.BOTH, expand=True)
        
    def load_yaml_from_file(self, file_path):
        """Carga contenido YAML desde un archivo."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.yaml_editor.delete(1.0, tk.END)
            self.yaml_editor.insert(1.0, content)
            self.yaml_path = file_path
            self.file_label.config(text=f"Archivo: {file_path}")
            self.modified = False
            self.update_title()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")
            
    def load_yaml_content(self, yaml_data):
        """Carga contenido YAML desde un diccionario."""
        try:
            yaml_content = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
            self.yaml_editor.delete(1.0, tk.END)
            self.yaml_editor.insert(1.0, yaml_content)
            self.modified = False
            self.update_title()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el contenido YAML:\n{e}")
            
    def on_content_changed(self, event=None):
        """Maneja cambios en el contenido del editor."""
        if not self.modified:
            self.modified = True
            self.update_title()
            
    def update_title(self):
        """Actualiza el título de la ventana según el estado de modificación."""
        title = "Editor de Mapeo YAML"
        if self.yaml_path:
            title += f" - {self.yaml_path.split('/')[-1]}"
        if self.modified:
            title += " *"
        self.window.title(title)
        
    def validate_yaml(self):
        """Valida la sintaxis del YAML y la estructura del mapeo."""
        content = self.yaml_editor.get(1.0, tk.END)
        
        self.validation_text.config(state='normal')
        self.validation_text.delete(1.0, tk.END)
        
        try:
            # Validar sintaxis YAML
            yaml_data = yaml.safe_load(content)
            
            # Validar estructura del mapeo
            errors = []
            if not isinstance(yaml_data, dict):
                errors.append("El archivo debe contener un objeto YAML válido")
            else:
                if 'base_uri' not in yaml_data:
                    errors.append("Falta el campo requerido 'base_uri'")
                if 'subject' not in yaml_data:
                    errors.append("Falta el campo requerido 'subject'")
                elif not isinstance(yaml_data['subject'], dict):
                    errors.append("El campo 'subject' debe ser un objeto")
                else:
                    if 'primary_key' not in yaml_data['subject']:
                        errors.append("Falta 'primary_key' en la configuración del sujeto")
                    if 'uri_template' not in yaml_data['subject']:
                        errors.append("Falta 'uri_template' en la configuración del sujeto")
                        
                if 'properties' in yaml_data and not isinstance(yaml_data['properties'], dict):
                    errors.append("El campo 'properties' debe ser un objeto")
                    
            if errors:
                self.validation_text.insert(tk.END, "❌ ERRORES DE VALIDACIÓN:\n")
                for error in errors:
                    self.validation_text.insert(tk.END, f"  • {error}\n")
                self.status_label.config(text="❌ Inválido", foreground="red")
            else:
                self.validation_text.insert(tk.END, "✅ YAML válido y estructura correcta")
                self.status_label.config(text="✅ Válido", foreground="green")
                
        except yaml.YAMLError as e:
            self.validation_text.insert(tk.END, f"❌ ERROR DE SINTAXIS YAML:\n{e}")
            self.status_label.config(text="❌ Sintaxis inválida", foreground="red")
        except Exception as e:
            self.validation_text.insert(tk.END, f"❌ ERROR INESPERADO:\n{e}")
            self.status_label.config(text="❌ Error", foreground="red")
            
        self.validation_text.config(state='disabled')
        
    def save_yaml(self):
        """Guarda el archivo YAML actual."""
        if not self.yaml_path:
            self.save_yaml_as()
            return
            
        try:
            content = self.yaml_editor.get(1.0, tk.END)
            with open(self.yaml_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.modified = False
            self.update_title()
            self.status_label.config(text="✅ Guardado", foreground="green")
            messagebox.showinfo("Éxito", "Archivo guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
            
    def save_yaml_as(self):
        """Guarda el archivo YAML con un nuevo nombre."""
        file_path = filedialog.asksaveasfilename(
            title="Guardar archivo YAML",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("YAML files", "*.yml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.yaml_editor.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.yaml_path = file_path
                self.file_label.config(text=f"Archivo: {file_path}")
                self.modified = False
                self.update_title()
                self.status_label.config(text="✅ Guardado", foreground="green")
                messagebox.showinfo("Éxito", "Archivo guardado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
                
    def apply_changes(self):
        """Aplica los cambios al archivo de mapeo en la aplicación principal."""
        try:
            content = self.yaml_editor.get(1.0, tk.END)
            yaml_data = yaml.safe_load(content)
            
            # Validar estructura básica
            if 'base_uri' not in yaml_data or 'subject' not in yaml_data:
                messagebox.showerror("Error", "El mapeo debe contener 'base_uri' y 'subject'.")
                return
                
            # Aplicar a la aplicación principal
            self.parent.mapping_data = yaml_data
            if self.yaml_path:
                self.parent.mapping_path.set(self.yaml_path)
            
            self.parent.log("Mapeo YAML actualizado desde el editor.")
            messagebox.showinfo("Éxito", "Cambios aplicados correctamente al mapeo.")
            
        except yaml.YAMLError as e:
            messagebox.showerror("Error de YAML", f"El contenido no es un YAML válido:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron aplicar los cambios:\n{e}")
            
    def on_closing(self):
        """Maneja el cierre de la ventana."""
        if self.modified:
            result = messagebox.askyesnocancel(
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de cerrar?"
            )
            if result is True:  # Sí
                self.save_yaml()
                if self.modified:  # Si aún está modificado, el guardado falló
                    return
            elif result is None:  # Cancelar
                return
                
        self.window.destroy()


class RDFConverterApp:
    """
    Una aplicación de escritorio para convertir archivos CSV a RDF utilizando
    un sistema de mapeo genérico basado en un archivo de configuración YAML.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor Genérico CSV a RDF")
        self.root.geometry("900x750")
        
        # Variables de estado
        self.df = None
        self.mapping_data = None
        self.graph = Graph()
        self.conversion_thread = None
        self.stop_conversion = False
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Sección de carga de archivos ---
        load_frame = ttk.Frame(main_frame)
        load_frame.pack(fill=tk.X, pady=5)

        # Carga de CSV
        csv_frame = ttk.LabelFrame(load_frame, text="1. Cargar Archivo CSV", padding=10)
        csv_frame.pack(fill=tk.X, pady=5)
        
        self.csv_path = tk.StringVar()
        ttk.Entry(csv_frame, textvariable=self.csv_path, width=70).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(csv_frame, text="Examinar CSV", command=self.load_csv).pack(side=tk.LEFT, padx=5)
        
        # Carga de Mapeo - MODIFICADO para incluir botón de editar
        mapping_frame = ttk.LabelFrame(load_frame, text="2. Cargar, Generar o Editar Mapeo (YAML)", padding=10)
        mapping_frame.pack(fill=tk.X, pady=5)

        self.mapping_path = tk.StringVar()
        ttk.Entry(mapping_frame, textvariable=self.mapping_path, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(mapping_frame, text="Examinar YAML", command=self.load_mapping).pack(side=tk.LEFT, padx=2)
        ttk.Button(mapping_frame, text="Generar Mapeo", command=self.generate_mapping).pack(side=tk.LEFT, padx=2)
        ttk.Button(mapping_frame, text="Editar YAML", command=self.edit_mapping).pack(side=tk.LEFT, padx=2)

        # --- Previsualización de Datos ---
        data_frame = ttk.LabelFrame(main_frame, text="Previsualización de Datos CSV", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.data_table = ttk.Treeview(data_frame)
        self.data_table.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_table.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_table.configure(yscrollcommand=vsb.set)
        
        # --- Proceso y Logs ---
        log_frame = ttk.LabelFrame(main_frame, text="Proceso de Conversión", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        self.progress = ttk.Progressbar(log_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # --- Botones de Control ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Iniciar Conversión", command=self.start_conversion).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Detener", command=self.stop_process).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Guardar RDF", command=self.save_rdf).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Limpiar Logs", command=self.clear_logs).pack(side=tk.RIGHT, padx=5)
    
    def edit_mapping(self):
        """Abre el editor YAML para el mapeo actual o crea uno nuevo."""
        if self.mapping_data is not None:
            # Editar mapeo existente
            yaml_path = self.mapping_path.get() if self.mapping_path.get() else None
            editor = YAMLEditorWindow(self, yaml_path=yaml_path, yaml_content=self.mapping_data)
        else:
            # Crear nuevo mapeo
            if self.df is not None:
                # Si hay CSV cargado, generar mapeo base
                suggested_mapping = self._guess_mapping_from_df()
                editor = YAMLEditorWindow(self, yaml_content=suggested_mapping)
                self.log("Editor YAML abierto con mapeo sugerido basado en el CSV actual.")
            else:
                # Mapeo completamente vacío
                empty_mapping = {
                    'base_uri': 'http://example.org/data/',
                    'namespaces': {
                        'ex': 'http://example.org/data/',
                        'schema': 'http://schema.org/',
                        'foaf': 'http://xmlns.com/foaf/0.1/',
                        'xsd': 'http://www.w3.org/2001/XMLSchema#'
                    },
                    'subject': {
                        'class': 'schema:Thing',
                        'primary_key': 'id',
                        'uri_template': 'resource/{value}'
                    },
                    'properties': {}
                }
                editor = YAMLEditorWindow(self, yaml_content=empty_mapping)
                self.log("Editor YAML abierto con mapeo vacío.")
    
    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path: return
        
        self.csv_path.set(path)
        try:
            self.df = pd.read_csv(path)
            self.show_data_preview()
            self.log("Archivo CSV cargado exitosamente.")
            self.log(f"Filas detectadas: {len(self.df)}")
            self.log(f"Columnas: {', '.join(self.df.columns)}")
        except Exception as e:
            messagebox.showerror("Error al Cargar CSV", f"No se pudo cargar el archivo:\n{e}")

    def load_mapping(self):
        path = self.mapping_path.get()
        if not path:
            path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml;*.yml"), ("All files", "*.*")])
        if not path: return

        self.mapping_path.set(path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.mapping_data = yaml.safe_load(f)
            self.log("Archivo de mapeo YAML cargado exitosamente.")
            if 'base_uri' not in self.mapping_data or 'subject' not in self.mapping_data:
                raise ValueError("El archivo de mapeo debe contener 'base_uri' y 'subject'.")
            self.log("Mapeo validado: OK.")
        except Exception as e:
            self.mapping_data = None
            messagebox.showerror("Error al Cargar Mapeo", f"No se pudo cargar o parsear el archivo YAML:\n{e}")

    def generate_mapping(self):
        if self.df is None:
            messagebox.showwarning("Advertencia", "Cargue primero un archivo CSV para poder generar un mapeo.")
            return

        try:
            suggested_mapping = self._guess_mapping_from_df()
            path = filedialog.asksaveasfilename(
                title="Guardar archivo de mapeo generado",
                defaultextension=".yaml",
                filetypes=[("YAML files", "*.yaml;*.yml")]
            )
            if not path: return

            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(suggested_mapping, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            self.log(f"Mapeo sugerido guardado en: {path}")
            self.mapping_path.set(path)
            self.load_mapping()

        except Exception as e:
            messagebox.showerror("Error al Generar Mapeo", f"No se pudo generar el archivo de mapeo:\n{e}")
            self.log(f"ERROR: No se pudo generar el mapeo. {e}")
        
    def _detect_csv_context(self, cols):
        """Detecta si el CSV es de naturaleza académica o general."""
        cols_lower = {c.lower().replace(' ', '').replace('_', '') for c in cols}
        academic_kws = {'doi', 'abstract', 'sourcetitle', 'publication', 'journal', 'volume', 'issue', 'citedby', 'authorkeywords', 'authorsid'}
        academic_score = len(cols_lower.intersection(academic_kws))
        
        if academic_score >= 3:
            self.log("Contexto detectado: Académico (se usarán vocabularios DC, DCTERMS, FOAF).")
            return 'academic'
            
        self.log("Contexto detectado: General (se usará Schema.org y FOAF).")
        return 'general'

    def _guess_mapping_from_df(self):
        """
        Genera un mapeo inteligente basado en el contexto detectado del CSV.
        """
        self.log("Iniciando generación de mapeo inteligente...")
        cols = self.df.columns
        context = self._detect_csv_context(cols)

        mapping = {
            'base_uri': 'http://example.org/data/',
            'namespaces': {
                'ex': 'http://example.org/data/',
                'schema': 'http://schema.org/',
                'foaf': 'http://xmlns.com/foaf/0.1/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'dcterms': 'http://purl.org/dc/terms/',
                'bibo': 'http://purl.org/ontology/bibo/',
                'xsd': 'http://www.w3.org/2001/XMLSchema#'
            },
            'subject': {},
            'properties': {}
        }

        mapping['subject']['class'] = 'bibo:AcademicArticle' if context == 'academic' else 'schema:Thing'

        pk_candidates = ['id', 'doi', 'title', 'name', 'identifier']
        pk_col_lower = next((c for c in pk_candidates if c in (col.lower() for col in cols)), cols[0].lower())
        pk_col = next(c for c in cols if c.lower() == pk_col_lower)

        mapping['subject']['primary_key'] = pk_col
        mapping['subject']['uri_template'] = f"resource/{self._sanitize_for_uri(pk_col)}/{{value}}"
        self.log(f"Clave primaria sugerida: '{pk_col}'")
        
        processed_cols = set()

        for col in cols:
            if col in processed_cols: continue
            col_lower = col.lower()
            prop = {}
            
            if 'author' in col_lower and 'id' not in col_lower and 'keyword' not in col_lower:
                prop = {
                    'predicate': 'dc:creator' if context == 'academic' else 'schema:author',
                    'type': 'relation', 'separator': ';',
                    'target': {
                        'uri_template': 'person/{value}', 'class': 'foaf:Person',
                        'properties': [{'predicate': 'foaf:name', 'type': 'literal', 'source': 'self'}]
                    }
                }
                id_col_candidate = next((c for c in cols if 'author' in c.lower() and 'id' in c.lower()), None)
                if id_col_candidate:
                    prop['target']['properties'].append({'predicate': 'dc:identifier', 'type': 'literal', 'source': id_col_candidate})
                    self.log(f"Relación de persona encontrada: '{col}' -> '{id_col_candidate}' (usando FOAF)")
                    processed_cols.add(id_col_candidate)
            
            elif col_lower in ['id', 'identifier']:
                prop = {'predicate': 'dcterms:identifier' if context == 'academic' else 'schema:identifier', 'type': 'literal'}

            elif context == 'academic':
                if 'keyword' in col_lower or 'subject' in col_lower: prop = {'predicate': 'dcterms:subject', 'type': 'literal', 'separator': ';'}
                elif 'year' in col_lower: prop = {'predicate': 'dcterms:issued', 'type': 'literal', 'datatype': 'xsd:gYear'}
                elif 'date' in col_lower: prop = {'predicate': 'dcterms:issued', 'type': 'literal', 'datatype': 'xsd:date'}
                elif 'title' in col_lower: prop = {'predicate': 'dc:title', 'type': 'literal'}
                elif 'abstract' in col_lower: prop = {'predicate': 'dcterms:abstract', 'type': 'literal'}
                elif 'doi' in col_lower: prop = {'predicate': 'bibo:doi', 'type': 'literal'}
                elif 'link' in col_lower or 'url' in col_lower: prop = {'predicate': 'foaf:page', 'type': 'uri'}
                else: prop = {'predicate': f'ex:{self._sanitize_for_uri(col)}', 'type': 'literal'}
            
            else: # General context
                if 'keyword' in col_lower or 'subject' in col_lower: prop = {'predicate': 'schema:keywords', 'type': 'literal', 'separator': ';'}
                elif 'year' in col_lower: prop = {'predicate': 'schema:datePublished', 'type': 'literal', 'datatype': 'xsd:gYear'}
                elif 'date' in col_lower: prop = {'predicate': 'schema:datePublished', 'type': 'literal', 'datatype': 'xsd:date'}
                elif 'title' in col_lower or 'name' in col_lower: prop = {'predicate': 'schema:name', 'type': 'literal'}
                elif 'description' in col_lower: prop = {'predicate': 'schema:description', 'type': 'literal'}
                elif 'doi' in col_lower: prop = {'predicate': 'bibo:doi', 'type': 'literal'}
                elif 'link' in col_lower or 'url' in col_lower: prop = {'predicate': 'schema:url', 'type': 'uri'}
                else: prop = {'predicate': f'ex:{self._sanitize_for_uri(col)}', 'type': 'literal'}
            
            if prop:
                mapping['properties'][col] = prop
                processed_cols.add(col)

        self.log("Generación de mapeo inteligente completada.")
        return mapping

    def show_data_preview(self):
        for item in self.data_table.get_children(): self.data_table.delete(item)
        if self.df is None: return
        self.data_table['columns'] = list(self.df.columns)
        self.data_table['show'] = 'headings'
        for column in self.df.columns:
            self.data_table.heading(column, text=column)
            self.data_table.column(column, width=120, anchor='w')
        for _, row in self.df.head(20).iterrows():
            self.data_table.insert('', 'end', values=list(row.map(lambda x: str(x)[:100])))

    def log(self, message):
        def _log():
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.configure(state='disabled')
            self.log_area.yview(tk.END)
        self.root.after(0, _log)

    def update_progress(self, value):
        def _update(): self.progress['value'] = value
        self.root.after(0, _update)

    def clear_logs(self):
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state='disabled')
    
    def start_conversion(self):
        if self.df is None: messagebox.showwarning("Advertencia", "Por favor, cargue un archivo CSV."); return
        if self.mapping_data is None: messagebox.showwarning("Advertencia", "Por favor, cargue un archivo de mapeo YAML."); return
        if self.conversion_thread and self.conversion_thread.is_alive(): messagebox.showinfo("Información", "La conversión ya está en progreso."); return
        
        self.stop_conversion = False
        self.graph = Graph()
        self.clear_logs()
        self.progress['value'] = 0
        
        self.conversion_thread = threading.Thread(target=self.run_conversion_engine)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
    
    def stop_process(self):
        if self.conversion_thread and self.conversion_thread.is_alive():
            self.stop_conversion = True
            self.log(">>> Solicitud de detención enviada. Finalizando la fila actual...")
        else:
            self.log("No hay un proceso de conversión activo para detener.")
    
    def save_rdf(self):
        if len(self.graph) == 0: messagebox.showwarning("Advertencia", "No hay datos RDF para guardar."); return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".ttl",
            filetypes=[("Turtle", "*.ttl"), ("RDF/XML", "*.rdf"), ("N-Triples", "*.nt"), ("All files", "*.*")]
        )
        if not path: return

        format_map = {'.ttl': 'turtle', '.rdf': 'xml', '.nt': 'nt'}
        file_ext = '.' + path.split('.')[-1]
        rdf_format = format_map.get(file_ext, 'turtle')

        try:
            self.graph.serialize(destination=path, format=rdf_format, encoding='utf-8')
            self.log(f"Archivo RDF guardado exitosamente en: {path}")
            messagebox.showinfo("Éxito", f"Archivo RDF guardado como '{rdf_format}'.")
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo:\n{e}")

    def run_conversion_engine(self):
        try:
            self.log("--- INICIANDO MOTOR DE CONVERSIÓN RDF ---")
            
            ns_map = {k: Namespace(v) for k, v in self.mapping_data.get('namespaces', {}).items()}
            for prefix, namespace in ns_map.items(): self.graph.bind(prefix, namespace)
            base_uri = Namespace(self.mapping_data['base_uri'])

            subject_conf = self.mapping_data['subject']
            pk_col = subject_conf['primary_key']
            uri_template = subject_conf['uri_template']
            subject_class = self._resolve_prefix(subject_conf['class'], ns_map)

            total_rows = len(self.df)
            self.progress['maximum'] = total_rows

            for idx, row in self.df.iterrows():
                if self.stop_conversion:
                    self.log("--- CONVERSIÓN DETENIDA POR EL USUARIO ---")
                    return
                
                self.update_progress(idx + 1)
                pk_val = row.get(pk_col)
                if pd.isna(pk_val) or str(pk_val).strip() == '':
                    self.log(f"ADVERTENCIA: Saltando fila {idx + 1} por clave primaria vacía.")
                    continue

               
                s_uri_val = self._sanitize_for_uri(str(pk_val))
                subject_uri = base_uri[uri_template.format(value=s_uri_val)]
                self.graph.add((subject_uri, RDF.type, subject_class))
                
                for col, prop_conf in self.mapping_data.get('properties', {}).items():
                    if col not in row or pd.isna(row[col]): continue

                    predicate = self._resolve_prefix(prop_conf['predicate'], ns_map)
                    
                    ## MEJORA ##: Lógica robusta para dividir valores multivaluados.
                    # Se eliminan los espacios en blanco de cada valor y se ignoran los valores vacíos
                    # que podrían resultar de separadores al final de la cadena (ej: "val1;val2;").
                    separator = prop_conf.get('separator')
                    if separator:
                        values = [v.strip() for v in str(row[col]).split(separator) if v.strip()]
                    else:
                        values = [str(row[col])]
                    
                    if not values: continue

                    prop_type = prop_conf.get('type', 'literal')

                    if prop_type == 'literal':
                        for value in values:
                            datatype = self._resolve_prefix(prop_conf['datatype'], ns_map) if 'datatype' in prop_conf else None
                            self.graph.add((subject_uri, predicate, Literal(value, datatype=datatype)))
                    
                    elif prop_type == 'uri':
                        for value in values:
                            try:
                                self.graph.add((subject_uri, predicate, URIRef(value)))
                            except Exception as e:
                                self.log(f"ADVERTENCIA: Fila {idx+1}, valor '{value}' en columna '{col}' no es una URI válida. Saltando. Error: {e}")

                    ## MEJORA ##: Lógica robusta para manejar relaciones multivaluadas y sus propiedades.
                    # Se reemplaza el frágil sistema de búsqueda por índice con una iteración paralela por índice (i),
                    # lo que permite manejar correctamente valores duplicados y listas de diferente longitud.
                    elif prop_type == 'relation':
                        target_conf = prop_conf['target']
                        target_class = self._resolve_prefix(target_conf['class'], ns_map)
                        target_uri_template = target_conf['uri_template']

                        # Recolectar las columnas de origen para las sub-propiedades
                        sub_prop_sources = {}
                        for sub_prop in target_conf.get('properties', []):
                            source_col_name = sub_prop.get('source')
                            if source_col_name and source_col_name != 'self':
                                source_values_raw = str(row.get(source_col_name, ''))
                                if separator:
                                    sub_prop_sources[source_col_name] = [v.strip() for v in source_values_raw.split(separator)]
                                else:
                                    sub_prop_sources[source_col_name] = [source_values_raw.strip()]

                        # Iterar sobre cada valor de la columna principal usando un índice
                        for i, value in enumerate(values):
                            o_uri_val = self._sanitize_for_uri(value)
                            # Se elimina el UUID para que la misma entidad (ej. autor) tenga la misma URI en todo el grafo
                            object_uri = base_uri[target_uri_template.format(value=o_uri_val)]
                            
                            self.graph.add((subject_uri, predicate, object_uri))
                            self.graph.add((object_uri, RDF.type, target_class))
                            
                            # Añadir propiedades a la entidad relacionada (objeto)
                            for sub_prop in target_conf.get('properties', []):
                                sub_predicate = self._resolve_prefix(sub_prop['predicate'], ns_map)
                                source_col = sub_prop.get('source')
                                sub_val = None

                                if source_col == 'self':
                                    sub_val = value
                                elif source_col in sub_prop_sources:
                                    # Se usa el índice 'i' para obtener el valor correspondiente de la otra columna
                                    if i < len(sub_prop_sources[source_col]):
                                        sub_val = sub_prop_sources[source_col][i]
                                    else:
                                        self.log(f"ADVERTENCIA: Fila {idx + 1}, col '{col}'. El número de valores en '{col}' y '{source_col}' no coincide. "
                                                 f"No se pudo asignar propiedad '{sub_prop['predicate']}' para '{value}'.")
                                
                                if sub_val and str(sub_val).strip():
                                    self.graph.add((object_uri, sub_predicate, Literal(sub_val)))
            
            self.log(f"\n--- CONVERSIÓN COMPLETADA EXITOSAMENTE ---\nTotal de triples RDF generados: {len(self.graph)}")

        except Exception as e:
            # Log completo del error para facilitar la depuración
            error_details = traceback.format_exc()
            self.log(f"ERROR CRÍTICO DURANTE LA CONVERSIÓN: {e}\n{error_details}")
            messagebox.showerror("Error de Conversión", f"Ocurrió un error inesperado:\n{e}\n\nRevise los logs para más detalles.")

    def _resolve_prefix(self, value, ns_map):
        if not isinstance(value, str) or ':' not in value:
            return URIRef(value)
        prefix, name = value.split(':', 1)
        namespace = ns_map.get(prefix)
        if namespace:
            return namespace[name]
        else:
            self.log(f"ADVERTENCIA: Prefijo '{prefix}' no encontrado en los namespaces. Usando URN.")
            return URIRef(f"urn:prefix-not-found:{prefix}:{name}")

    def _sanitize_for_uri(self, value):
        value = str(value).lower()
        value = re.sub(r'\s+', '_', value)
        value = re.sub(r'[^\w\-\._~]', '', value) # Caracteres permitidos en URIs
        return value[:70]

if __name__ == "__main__":
    root = tk.Tk()
    app = RDFConverterApp(root)
    root.mainloop()
# MassEdit Configuration Reference

Este documento describe el formato de configuración YAML usado por **MassEdit**.

---

## 1. Root Structure

Todo archivo de configuración debe seguir esta estructura:

```yaml
version: "1.0.0"

project:
mode:
select:
verify:
plan:
sandbox:
execute:
logging:
report:
commit:
pipeline:
```

---

## 2. Project

Define el directorio raíz del proyecto.

```yaml
project:
  root: "./my_project"
```

| Field | Type   | Description              |
|-------|--------|--------------------------|
| root  | string | Base working directory   |

---

## 3. Mode

Controla el comportamiento global de ejecución.

```yaml
mode:
  confirm: true
  stop_on_error: false
  continue_on_file_error: true
  max_global_errors: 10
  max_file_failures: 20
  on_limit_reached: abort
```

| Field                 | Type | Description                        |
|-----------------------|------|------------------------------------|
| confirm               | bool | Ask before commit                  |
| stop_on_error         | bool | Stop immediately on error          |
| continue_on_file_error| bool | Continue on per-file error         |
| max_global_errors     | int  | Maximum total errors               |
| max_file_failures     | int  | Maximum failed files               |
| on_limit_reached      | enum | abort / partial_commit / rollback  |

---

## 4. Select

Define qué archivos son seleccionados.

```yaml
select:
  show_results: true
  confirm: true
  include:
    - "**/*.md"
  exclude:
    - ".git/**"

filters:
  min_size_kb: 1
  max_size_kb: 5000
```
| Field              | Type   | Description                                                                 |
|--------------------|--------|-----------------------------------------------------------------------------|
| show_results          | bool    | Muestra los paths de los archivos seleccionados                                        |
| confirm          | bool    | Confirmacion necesaria para seguir la ejecucion del programa                                        |

---

## 5. Verify

Validación previa a la ejecución.  
Todos los campos son opcionales: si no están presentes en el YAML, no se aplican.

```yaml
verify:
  fail_fast: true
  require_write: true
  require_read: true
  max_file_size_mb: 10
  min_file_size_kb: 1
  allowed_extensions:
    - ".md"
    - ".txt"
  max_files: 100
  show_results: true
  confirm: true
```

| Field              | Type   | Description                                                                 |
|--------------------|--------|-----------------------------------------------------------------------------|
| fail_fast          | bool   | Detiene la validación al primer error                                       |
| require_write      | bool   | Requiere permisos de escritura                                              |
| require_read       | bool   | Requiere permisos de lectura                                                |
| max_file_size_mb   | int    | Tamaño máximo permitido en MB                                               |
| min_file_size_kb   | int    | Tamaño mínimo permitido en KB (evita archivos vacíos o demasiado pequeños) |
| allowed_extensions | list   | Lista de extensiones permitidas (ej. `.md`, `.txt`)                         |
| max_files          | int    | Número máximo de archivos a procesar                                        |

---

## 6. Plan Content

Transformaciones a nivel de texto.

### Operaciones soportadas

- **fill** (regex replacement)
```yaml
- operation: fill
  files: "**/*.md"
  pattern: "TODO"
  with: "DONE"
```

- **create** (append content)
```yaml
- operation: create
  files: "**/*.md"
  with: "Text"
```

- **replace** (replace content)
```yaml
- operation: replace
  mode: full
  with: ""

- operation: replace
  mode: regex
  pattern: "\\s+$"
  with: ""
```

- **delete** (remove content)
```yaml
- operation: delete
  mode: full

- operation: delete
  mode: regex
  pattern: "\\s+$"
```

---

## 7. Plan Metadata

Edición de YAML frontmatter.

```yaml
- operation: [create, fill, replace]
  name: "Spaced_Repetition"
  type: "list"
  value: "ED"
```

### Operaciones soportadas
- create → Crear si falta
- fill → Completar si está vacío
- replace → Reemplazar valor
- delete → Eliminar campo

### Replace/Delete Modes
- full → Aplicar incondicionalmente
- regex → Aplicar si el valor coincide

### Tipos soportados
- number  
- text  
- date  
- list  

**Semántica de listas**:
- Sin duplicados  
- Orden ignorado  
- Inserciones idempotentes  

---

## 8. Plan Filesystem

Operaciones sobre el sistema de archivos.

```yaml
- operation: move
  from: "docs/"
  to: "archive/docs/"

- operation: create
  path: "new_folder/"

- operation: delete
  path: "old_folder/"
```

Todas las operaciones se ejecutan primero en sandbox.

---

## 9. Sandbox

Configuración del entorno aislado.

```yaml
sandbox:
  enabled: true
  tmp_dir: /tmp/massedit
  max_size_mb: 5000
  cleanup: true
```

| Field     | Type   | Description                                      |
|-----------|--------|--------------------------------------------------|
| enabled   | bool   | Enable sandbox                                   |
| tmp_dir   | path   | Temp directory                                   |
| max_size_mb| int   | Max sandbox size                                 |
| cleanup   | bool   | **Indica si se elimina automáticamente el sandbox después de la ejecución.** |

---

## 10. Execute

```yaml
execute:
  parallel: true
  workers: 4
  batch_size: 100
  timeout_sec: 300
```

---

## 11. Logging

```yaml
logging:
  level: info
  file: "massedit.log"
```

---

## 12. Report

```yaml
report:
  cli_summary: true
  summary: true
  json: "report.json"
```

---

## 13. Commit

```yaml
commit:
  auto: false
  require_clean_run: true
  mode: replace
  clean_dir: false
```

| Field     | Type   | Description                                      |
|-----------|--------|--------------------------------------------------|
| auto      | bool   | automatically commit                             |
| require_clean_run      | bool   | dont commit if any error happend                             |
| mode      | enum   | (replace, merge) merge or replace the original tree with the sanboxed one                             |
| clean_dir | bool   | only work of mode = replace control wather the replace mode deletes empty directories (clean directories) or not                              |

---

## 14. Pipeline

Define el orden de ejecución.

```yaml
pipeline:
  - select
  - verify
  - sandbox
  - plan
  - execute
  - report
  - commit
```

---

## 15. Examples

Ver el directorio `/examples`.

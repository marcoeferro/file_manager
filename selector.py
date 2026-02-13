import glob
import os
import re
import sys

class Selector:
    def __init__(self, config):
        self.config = config

    def select(self):
        root = self.config['project']['root']
        include = self.config.get('select', {}).get('include', [])
        exclude = self.config.get('select', {}).get('exclude', [])
        filters = self.config.get('select', {}).get('filters', {})
        title_pattern = self.config.get('select', {}).get('title_pattern', {})
        metadata = self.config.get('select', {}).get('metadata', {})
        show_results = self.config.get('select', {}).get('show_results', {})
        confirm = self.config.get('select', {}).get('confirm', {})

        # Archivos incluidos
        files = set()
        for pattern in include:
            files.update(glob.glob(os.path.join(root, pattern), recursive=True))

        # Archivos excluidos
        excluded = set()
        for pattern in exclude:
            excluded.update(glob.glob(os.path.join(root, pattern), recursive=True))

        # Filtrar por exclusión y existencia
        selected = [f for f in files if f not in excluded and os.path.isfile(f)]

        # Filtros de tamaño
        min_size = filters.get('min_size_kb')
        max_size = filters.get('max_size_kb')
        if min_size is not None or max_size is not None:
            filtered = []
            for f in selected:
                size_kb = os.path.getsize(f) / 1024
                if (min_size is None or size_kb >= min_size) and (max_size is None or size_kb <= max_size):
                    filtered.append(f)
            selected = filtered

        # Filtro por patrón de título (regex sobre nombre de archivo)
        if title_pattern.get('regex'):
            regex = re.compile(title_pattern['regex'])
            selected = [f for f in selected if regex.search(os.path.basename(f))]

        # Filtro por metadata YAML incrustada
        if metadata:
            key = metadata.get('name')
            value = metadata.get('value')
            mtype = metadata.get('type')
            filtered = []
            for f in selected:
                if self._match_metadata(f, key, value, mtype):
                    filtered.append(f)
            selected = filtered
        if show_results:
            for f in selected:
                print(os.path.normpath(f))
        if confirm:
            continuar = input("DESEA CONTINUAR ? (y/n)").strip().lower()
            if continuar != "y":
                sys.exit("Ejecución detenida por el usuario")
        return selected

    def _match_metadata(self, filepath, key, value, mtype):
        """
        Busca en el bloque YAML inicial delimitado por --- ... ---
        la clave 'key'. Si type=list, busca valores con '-'.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines or lines[0].strip() != "---":
                return False

            yaml_lines = []
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                yaml_lines.append(line.rstrip("\n"))

            # Buscar la clave con regex
            pattern = re.compile(rf"^{key}\s*:")
            found = False
            values = []
            for line in yaml_lines:
                if pattern.match(line):
                    found = True
                elif found:
                    if line.startswith("-"):
                        val = line.lstrip("-").strip()
                        values.append(val)
                    elif line and not line.startswith(" "):
                        # fin de la sección
                        break

            if mtype == "list":
                return value in values
            elif mtype == "string":
                # tomar la parte derecha del "key: valor"
                for line in yaml_lines:
                    if pattern.match(line):
                        right = line.split(":", 1)[1].strip()
                        return right == value
            return False
        except Exception:
            return False

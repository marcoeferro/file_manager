import re
import yaml
import os
import shutil
import glob

class Planner:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def build_tasks(self, files):
        tasks = []

        plan_cfg = self.config.get('plan', {})

        # Content tasks
        for f in files:
            for op in plan_cfg.get('content', []):
                tasks.append(lambda f=f, op=op: self.apply_content(f, op))

            for op in plan_cfg.get('metadata', []):
                tasks.append(lambda f=f, op=op: self.apply_metadata(f, op))

        # Filesystem tasks (no dependen de files)
        for op in plan_cfg.get('filesystem', []):
            tasks.append(lambda op=op: self.apply_filesystem(op))

        return tasks

    def apply_content(self, path, op):
        try:
            with open(path, 'r+', encoding='utf-8') as f:
                data = f.read()

                mode = op.get('mode', 'regex')
                operation = op['operation']

                if operation == 'fill':
                    data = re.sub(op['pattern'], op['with'], data)

                elif operation == 'create':
                    data += "\n" + op['with']

                elif operation == 'replace':
                    if mode == 'full':
                        data = op['with']
                    else:
                        data = re.sub(op['pattern'], op['with'], data)

                elif operation == 'delete':
                    if mode == 'full':
                        data = ''
                    else:
                        data = re.sub(op['pattern'], '', data)

                f.seek(0)
                f.write(data)
                f.truncate()
        except Exception as e:
            self.logger.error(f"Content operation failed on {path}: {e}")

    def apply_metadata(self, path, op):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                return

            parts = content.split('---', 2)
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2]

            name = op.get('name')
            value = op.get('value')
            mode = op.get('mode', 'full')
            ops = op.get('operation')
            if isinstance(ops, str):
                ops = [ops]

            for action in ops:
                if action == 'create' and name not in meta:
                    meta[name] = value

                elif action == 'fill' and name in meta and not meta[name]:
                    meta[name] = value

                elif action == 'replace' and name in meta:
                    if mode == 'regex':
                        meta[name] = re.sub(op['pattern'], value, str(meta[name]))
                    else:
                        meta[name] = value

                elif action == 'delete' and name in meta:
                    if mode == 'regex':
                        if re.match(op['pattern'], str(meta[name])):
                            del meta[name]
                    else:
                        del meta[name]

            new_meta = yaml.dump(meta, sort_keys=False)
            new_content = f"---\n{new_meta}---{body}"

            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            self.logger.error(f"Metadata operation failed on {path}: {e}")

    def apply_filesystem(self, op):
        try:
            operation = op['operation']

            if operation == 'move':
                # Archivos a mover según patrón
                files = glob.glob(op['files'], recursive=True) if 'files' in op else []
                dest = op['to']

                # Crear carpeta destino si no existe
                os.makedirs(dest, exist_ok=True)

                for f in files:
                    if os.path.isfile(f):
                        shutil.move(f, os.path.join(dest, os.path.basename(f)))

            elif operation == 'create':
                os.makedirs(op['path'], exist_ok=True)

            elif operation == 'delete':
                if os.path.isdir(op['path']):
                    shutil.rmtree(op['path'])
                elif os.path.isfile(op['path']):
                    os.remove(op['path'])

        except Exception as e:
            self.logger.error(f"Filesystem operation failed: {e}")

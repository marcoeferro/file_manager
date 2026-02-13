# sandbox.py
import os
import shutil

class Sandbox:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.tmp = config['sandbox']['tmp_dir']

    def setup(self, files):
        if not self.config['sandbox']['enabled']:
            return files

        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp)

        os.makedirs(self.tmp, exist_ok=True)

        sandboxed = []
        for f in files:
            rel = os.path.relpath(f, self.config['project']['root'])
            dst = os.path.join(self.tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(f, dst)
            sandboxed.append(dst)

        self.logger.info("Sandbox created")
        return sandboxed

    def commit(self):
        root = self.config['project']['root']
        commit_cfg = self.config.get('commit', {})

        show_results = commit_cfg.get('show_results', False)
        auto = commit_cfg.get('auto', False)
        require_clean = commit_cfg.get('require_clean_run', False)
        mode = commit_cfg.get('mode', 'merge')  # valores posibles: 'merge' o 'replace'
        clean_dir = commit_cfg.get('clean_dir', False)  # valores posibles: 'merge' o 'replace'

        # Mostrar resultados del sandbox
        if show_results:
            self.logger.info("Sandbox contents before commit:")
            for root_dir, _, files in os.walk(self.tmp):
                for f in files:
                    rel = os.path.relpath(os.path.join(root_dir, f), self.tmp)
                    print(rel)

        # Confirmación manual si auto = False
        if not auto:
            commit = input("¿Quieres commitear? (y/n): ").strip().lower()
            if commit != "y":
                self.logger.info("Commit cancelado por el usuario")
                return

        # Chequear require_clean_run (ejemplo simple)
        if require_clean:
            if getattr(self.logger, "errors", 0) > 0:
                self.logger.warning("Commit abortado: ejecución no fue limpia")
                return

        # Modo replace: limpiar root antes de copiar
        if mode == "replace":
            self.logger.info("Commit mode: replace (root será sustituido por sandbox)")
            for root_dir, dirs, files in os.walk(root, topdown=False):
                for f in files:
                    os.remove(os.path.join(root_dir, f))
                if clean_dir:
                    for d in dirs:
                        os.rmdir(os.path.join(root_dir, d))

        else:
            self.logger.info("Commit mode: merge (sandbox se copia encima del root)")

        # Copiar sandbox al root
        for root_dir, _, files in os.walk(self.tmp):
            for f in files:
                src = os.path.join(root_dir, f)
                rel = os.path.relpath(src, self.tmp)
                dst = os.path.join(root, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

        shutil.rmtree(self.tmp)
        self.logger.info("Sandbox committed")
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
        for root_dir, _, files in os.walk(self.tmp):
            for f in files:
                src = os.path.join(root_dir, f)
                rel = os.path.relpath(src, self.tmp)
                dst = os.path.join(root, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

        shutil.rmtree(self.tmp)
        self.logger.info("Sandbox committed")



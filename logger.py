# logger.py
import logging
import os

def _make_path(config):
    # Construir la ruta completa
    if config.get('logging', {}).get('directory'):
        path = os.path.join(config['logging']['directory'], config['logging']['file'])
    else:
        path = config['logging']['file']

    # Crear directorio si no existe
    logdir = os.path.dirname(path)
    if logdir:  # evita problemas si path es solo un nombre de archivo
        os.makedirs(logdir, exist_ok=True)

    return path


class Logger:
    def __init__(self, config):
        level = config['logging']['level'].upper()
        logfile = _make_path(config)

        logging.basicConfig(
            level=getattr(logging, level),
            format='[%(asctime)s] %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(logfile),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("MassEdit")

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

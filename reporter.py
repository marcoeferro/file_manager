# reporter.py
import json
import time
from pathlib import Path
import os

def _make_path(config,file):
    report_config = config.get('report', {})

    # Construir la ruta completa
    if report_config.get('directory'):
        path = os.path.join(report_config['directory'], report_config[file])
    else:
        path = report_config[file]

    # Crear directorio si no existe
    logdir = os.path.dirname(path)
    if logdir:  # evita problemas si path es solo un nombre de archivo
        os.makedirs(logdir, exist_ok=True)

    return path

class Reporter:

    def __init__(self, config, logger=None):

        self.config = config
        self.logger = logger
        self.start_ts = time.time()

        self.stats = {
            "files_processed": 0,
            "files_success": 0,
            "files_failed": 0,
            "operations": 0,
            "errors": [],
            "start_time": None,
            "end_time": None,
            "duration_sec": None
        }

    # -----------------------------------------
    # Tracking
    # -----------------------------------------

    def start(self):

        self.stats["start_time"] = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def file_success(self):

        self.stats["files_processed"] += 1
        self.stats["files_success"] += 1

    def file_failed(self, file, error):

        self.stats["files_processed"] += 1
        self.stats["files_failed"] += 1

        self.stats["errors"].append({
            "file": str(file),
            "error": str(error)
        })

    def operation_done(self):

        self.stats["operations"] += 1

    # -----------------------------------------
    # Finalization
    # -----------------------------------------

    def finish(self):

        self.stats["end_time"] = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        end = time.time()

        self.stats["duration_sec"] = round(
            end - self.start_ts, 2
        )

        report_cfg = self.config.get("report", {})
        path_json = _make_path(config=self.config,file="json_file")
        path_summary = _make_path(config=self.config,file="summary_file")

        if report_cfg.get("cli_summary"):
            self._print_cli_summary()

        if report_cfg.get("json_file"):
            self._write_json(path_json)

        if report_cfg.get("summary_file"):
            self._write_summary_txt(path_json)

    # -----------------------------------------
    # Outputs
    # -----------------------------------------

    def _print_cli_summary(self):

        print("\n" + "=" * 50)
        print(" MASS EDIT REPORT ")
        print("=" * 50)

        print(f" Files processed : {self.stats['files_processed']}")
        print(f" Files success   : {self.stats['files_success']}")
        print(f" Files failed    : {self.stats['files_failed']}")
        print(f" Operations      : {self.stats['operations']}")
        print(f" Duration (sec)  : {self.stats['duration_sec']}")

        if self.stats["errors"]:

            print("\n Errors:")

            for e in self.stats["errors"][:5]:
                print(f"  - {e['file']}: {e['error']}")

            if len(self.stats["errors"]) > 5:
                print(
                    f"  ... {len(self.stats['errors']) - 5} more"
                )

        print("=" * 50 + "\n")

    def _write_json(self, path):

        out = Path(path)

        out.parent.mkdir(parents=True, exist_ok=True)

        with open(out, "w", encoding="utf-8") as f:
            json.dump(
                self.stats,
                f,
                indent=2,
                ensure_ascii=False
            )

        if self.logger:
            self.logger.info(f"JSON report written to {out}")

    def _write_summary_txt(self,path):

        path = Path(path)

        with open(path, "w", encoding="utf-8") as f:

            f.write("MassEdit Summary\n")
            f.write("=" * 30 + "\n")

            for k, v in self.stats.items():
                f.write(f"{k}: {v}\n")

        if self.logger:
            self.logger.info(f"Summary written to {path}")

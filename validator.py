import os

class Validator:
    def __init__(self, config, logger, reporter=None):
        self.config = config
        self.logger = logger
        self.reporter = reporter

    def validate_files(self, files):
        verify_cfg = self.config.get('verify', {})
        valid = []

        max_size_mb = verify_cfg.get('max_file_size_mb')
        max_size = max_size_mb * 1024 * 1024 if max_size_mb else None

        min_size_kb = verify_cfg.get('min_file_size_kb')
        min_size = min_size_kb * 1024 if min_size_kb else None

        require_write = verify_cfg.get('require_write', False)
        require_read = verify_cfg.get('require_read', False)
        fail_fast = verify_cfg.get('fail_fast', False)

        allowed_exts = verify_cfg.get('allowed_extensions', [])
        max_files = verify_cfg.get('max_files')

        for f in files:
            try:
                # Validar extensión
                if allowed_exts and not any(f.endswith(ext) for ext in allowed_exts):
                    self.logger.warning(f"Extension not allowed: {f}")
                    if self.reporter:
                        self.reporter.file_failed(f, "Extension not allowed")
                    if fail_fast:
                        return []
                    continue

                # Validar tamaño
                size = os.path.getsize(f)
                if max_size and size > max_size:
                    self.logger.warning(f"File too large: {f}")
                    if self.reporter:
                        self.reporter.file_failed(f, "File too large")
                    if fail_fast:
                        return []
                    continue

                if min_size and size < min_size:
                    self.logger.warning(f"File too small: {f}")
                    if self.reporter:
                        self.reporter.file_failed(f, "File too small")
                    if fail_fast:
                        return []
                    continue

                # Validar permisos
                if require_write and not os.access(f, os.W_OK):
                    self.logger.warning(f"No write permission: {f}")
                    if self.reporter:
                        self.reporter.file_failed(f, "No write permission")
                    if fail_fast:
                        return []
                    continue

                if require_read and not os.access(f, os.R_OK):
                    self.logger.warning(f"No read permission: {f}")
                    if self.reporter:
                        self.reporter.file_failed(f, "No read permission")
                    if fail_fast:
                        return []
                    continue

                valid.append(f)
                if self.reporter:
                    self.reporter.file_success()

                if max_files and len(valid) >= max_files:
                    self.logger.warning("Reached maximum number of files allowed")
                    break

            except Exception as e:
                self.logger.error(f"Validation error {f}: {e}")
                if self.reporter:
                    self.reporter.file_failed(f, str(e))
                if fail_fast:
                    return []

        return valid

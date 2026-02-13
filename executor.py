# executor.py

import concurrent.futures


class Executor:

    def __init__(self, config, logger, reporter):

        self.config = config
        self.logger = logger
        self.reporter = reporter

    def run(self, tasks):

        results = []

        # Sequential
        if not self.config["execute"]["parallel"]:

            for task in tasks:

                try:
                    res = task()
                    results.append(res)

                    self.reporter.file_success()
                    self.reporter.operation_done()

                except Exception as e:

                    self.reporter.file_failed("unknown", e)

                    if self.config["mode"]["stop_on_error"]:
                        raise

            return results

        # Parallel
        workers = self.config["execute"]["workers"]
        timeout = self.config["execute"]["timeout_sec"]

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=workers
        ) as pool:

            futures = [
                pool.submit(t) for t in tasks
            ]

            for f in concurrent.futures.as_completed(
                futures,
                timeout=timeout
            ):

                try:
                    res = f.result()
                    results.append(res)

                    self.reporter.file_success()
                    self.reporter.operation_done()

                except Exception as e:

                    self.reporter.file_failed("unknown", e)

                    if self.config["mode"]["stop_on_error"]:
                        raise

        return results

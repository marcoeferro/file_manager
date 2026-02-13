# main.py

import yaml

from selector import Selector
from validator import Validator
from sandbox import Sandbox
from planner import Planner
from executor import Executor
from logger import Logger
from reporter import Reporter

# -----------------------------------------
# Config loader
# -----------------------------------------

def load_config(path="config.yml"):

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# -----------------------------------------
# Main
# -----------------------------------------

def main():

    # Load config
    config = load_config()

    # Logger
    logger = Logger(config)

    logger.info("Starting MassEdit")

    # Reporter
    reporter = Reporter(config, logger)
    reporter.start()

    # Pipeline components
    selector = Selector(config)
    validator = Validator(config, logger)
    sandbox = Sandbox(config, logger)
    planner = Planner(config, logger)

    executor = Executor(
        config,
        logger,
        reporter
    )

    # -----------------------------------------
    # Pipeline
    # -----------------------------------------

    files = selector.select()

    logger.info(f"Selected {len(files)} files")

    files = validator.validate_files(files)

    logger.info(f"Validated {len(files)} files")

    sandboxed = sandbox.setup(files)

    tasks = planner.build_tasks(sandboxed)

    executor.run(tasks)

    reporter.finish()

    # -----------------------------------------
    # Commit
    # -----------------------------------------

    if config["commit"]["auto"]:
        sandbox.commit()

    logger.info("Finished")


if __name__ == "__main__":
    main()

import os
import subprocess
import sys
import argparse
import logging
import subprocess
from threading import Thread

from uvicorn.main import main as uvicorn_main
from alembic.config import Config
from alembic import command
# from alembic.config import main as alembic_main

# from commandbay.core.db import engine, Base
from commandbay.utils.environ import app_data_dir_path, environment as env
from commandbay.server import app


logger = logging.getLogger(__name__)


class ServerNamespace(argparse.Namespace):
    "Default to production=True so we don't accidentally ship a prod release running dev mode"
    dev:bool = False
    host:str
    port:str


def parse_args():
    """This is where we bring the command line and the outer environment together,
    which enables command-line overwriting of environment/default values.

    :return: arguments object which brings together environment options and
    command-line-specified arguments
    :rtype: ServerNamespace
    """
    if env is None:
        return (None, None)
    cl_args = argparse.ArgumentParser()
    cl_args.add_argument('--dev', default=False, action='store_true')
    cl_args.add_argument('--host', default=env.webserver.bind_host)
    cl_args.add_argument('--port', default=env.webserver.backend_port)
    pargs, unknown = cl_args.parse_known_args(namespace=ServerNamespace)
    return pargs, unknown


def ensure_database_updated():
    print("ensure_database_updated")
    # if not os.path.exists(env.sqlite_file_path):
    #     Base.metadata.create_all(engine)
    alembic_ini_filepath = app_data_dir_path('alembic.ini')
    config = Config(alembic_ini_filepath)
    alembic_dir_path = app_data_dir_path('alembic')
    config.file_config.set('alembic', 'script_location', alembic_dir_path)
    command.upgrade(config, 'head')


def start_frontend_thread():
    def frontend_server_thread():
        subprocess.run('cd frontend; npm run dev', shell=True)
    thread = Thread(target=frontend_server_thread, daemon=True)
    thread.start()


def main():
    """
    Main function to execute the script.

    This function retrieves the Python interpreter path from Poetry and then
    executes the main script (main_script.py) in the Poetry environment, passing
    along any arguments it received. It checks to prevent recursive execution
    by ensuring that it's not already running in the Poetry environment.
    """
    pargs, unknown = parse_args()
    if pargs is None:
        return

    sys.argv.extend([
        # "commandbay.server:app",
        "--host", pargs.host,
        "--port", pargs.port,
    ])
    if pargs.dev:
        os.environ['PRODUCTION'] = '0'
        mode = 'development'
        sys.argv.extend("--reload")
    else:
        mode = 'production'

    if unknown:
        if unknown[0] == '--':
            unknown = unknown[1:]
        sys.argv.extend(unknown)

    ensure_database_updated()
    if pargs.dev:
        start_frontend_thread()
    sys.argv.append('commandbay.server:app')
    print(f"Running {mode} server:", sys.argv)
    try:
        uvicorn_main()
    # override KeyboardInterrupt so it's considered exit code=2
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(2)


if __name__ == '__main__':
    logger.setLevel(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting with PID: %s", os.getpid())
    main()

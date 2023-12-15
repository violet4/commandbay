"""
Welcome to
   _____                                          _ ____
  / ____|                                        | |  _ \
 | |     ___  _ __ ___  _ __ ___   __ _ _ __   __| | |_) | __ _ _   _
 | |    / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` |  _ < / _` | | | |
 | |___| (_) | | | | | | | | | | | (_| | | | | (_| | |_) | (_| | |_| |
  \_____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|____/ \__,_|\__, |
                                                                 __/ |
                                                                |___/
Once the server is started, you can visit the user interface in
your web browser at:

    http://localhost:7321

If you have any issues please reach out on github at https://github.com/violet4/commandbay/issues

"""
# ascii art courtesy https://patorjk.com/software/taag/#p=display&h=1&v=0&f=Big&t=CommandBay
import os
import subprocess
import sys
import argparse
import logging
import subprocess
import signal

from uvicorn.main import main as uvicorn_main
from alembic.config import Config
from alembic import command
# from alembic.config import main as alembic_main

# from commandbay.core.db import engine, Base
from commandbay.utils.environ import app_data_dir_path, environment as env
try:
    from commandbay.server import app
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"error: '{e}'")

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


def start_npm_dev():
    npm_process = subprocess.Popen(['npm', 'run', 'dev'], cwd='frontend')
    def signal_handler(signal, frame):
        npm_process.terminate()
        exit()
    signal.signal(signal.SIGINT, signal_handler)
    return npm_process


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
    sys.argv = [sys.argv[0]]

    sys.argv.extend([
        # "commandbay.server:app",
        "--host", pargs.host,
        "--port", pargs.port,
    ])
    if pargs.dev:
        os.environ['PRODUCTION'] = '0'
        mode = 'development'
        sys.argv.append("--reload")
    else:
        mode = 'production'

    if unknown:
        if unknown[0] == '--':
            unknown = unknown[1:]
        sys.argv.extend(unknown)

    ensure_database_updated()
    npm_proc = start_npm_dev() if pargs.dev else None
    sys.argv.append('commandbay.server:app')
    print(f"Running {mode} server: '{sys.argv}'", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    try:
        uvicorn_main()
    # override KeyboardInterrupt so it's considered exit code=2
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(2)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        input("Press enter key to exit")
    finally:
        if npm_proc is not None:
            npm_proc.terminate()


if __name__ == '__main__':
    logger.setLevel(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting with PID: %s", os.getpid())
    main()

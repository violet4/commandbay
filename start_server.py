import os
import subprocess
import sys
import argparse
import logging
import platform

logger = logging.getLogger(__name__)
logger.info("Starting with PID: %s", os.getpid())


#TODO:log error messages anywhere these imports are unexpectedly None
try:
    from uvicorn.main import main as uvicorn_main
except ImportError as e:
    logger.error("failed to import uvicorn.main.main: %s", e)
    uvicorn_main = None
try:
    from alembic.config import Config
except ImportError as e:
    logger.error("failed to import alembic.config.Config: %s", e)
    Config = None
try:
    from alembic import command
except ImportError as e:
    logger.error("failed to import alembic.command: %s", e)
    command = None
try:
    from alembic.config import main as alembic_main
except ImportError as e:
    logger.error("failed to import alembic.config.main: %s", e)
    alembic_main = None
try:
    from commandbay.core.db import engine, Base
except ImportError as e:
    logger.error("failed to import engine and/or Base from commandbay.core.db: %s", e)
    engine = Base = None
try:
    from commandbay.utils.environ import environment as env
except ImportError as e:
    logger.error("failed to import commandbay.utils.environ.environment: %s", e)
    env = None


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


def get_poetry_exe_path(exe_name:str) -> str:
    """
    Returns the path of the Python interpreter managed by Poetry.

    This function executes the 'poetry env info -p' command to retrieve the
    path of the Python interpreter that Poetry is using for the current project.

    Returns:
        str: The path to the Python interpreter managed by Poetry.

    Raises:
        subprocess.CalledProcessError: If the 'poetry env info -p' command fails.
    """
    try:
        path = subprocess.check_output(["poetry", "run", which(), exe_name], text=True).strip().split('\n')[0]
        return path
    except subprocess.CalledProcessError as e:
        print(f"Error occurred when trying to find poetry python executable path: {e}")
        sys.exit(1)


def ensure_database_updated():
    print("ensure_database_updated")
    if (
        alembic_main is None
        or engine is None
        or env is None
        or Base is None
        or Config is None
        or command is None
    ):
        return
    # if not os.path.exists(env.sqlite_file_path):
    #     Base.metadata.create_all(engine)
    config = Config('alembic.ini')
    command.upgrade(config, 'head')


def start_frontend_thread():
    from threading import Thread
    def frontend_server_thread():
        import subprocess
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
    poetry_python_path = get_poetry_exe_path('python')
    uvicorn_path = get_poetry_exe_path('uvicorn')
    main_script_path = __file__

    # Ensure this script is not recursively calling itself
    if sys.executable != poetry_python_path or uvicorn_main is None:
        # Pass all the arguments given to the original script to the main script
        os.execl(poetry_python_path, poetry_python_path, main_script_path, *sys.argv[1:])

    pargs, unknown = parse_args()
    if pargs is None:
        return

    # from commandbay.server import app
    uvicorn_arguments = [
        "commandbay.server:app",
        "--host", pargs.host,
        "--port", pargs.port,
    ]
    if pargs.dev:
        os.environ['PRODUCTION'] = '0'
        mode = 'development'
        uvicorn_arguments.append("--reload")
    else:
        mode = 'production'

    if unknown:
        if unknown[0] == '--':
            unknown = unknown[1:]
        uvicorn_arguments.extend(unknown)

    ensure_database_updated()
    if pargs.dev:
        start_frontend_thread()
    sys.argv = [uvicorn_path]+uvicorn_arguments
    print(f"Running {mode} server:", sys.argv)
    sys.exit(uvicorn_main())


def which():
    if platform.system() == 'Windows':
        return 'where'
    else:
        return 'which'


if __name__ == '__main__':
    try:
        sys.exit(main())
    # override KeyboardInterrupt so it's considered exit code=2
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(2)

import subprocess
import sys

args = sys.argv[1:]

command = ["poetry", "run", "uvicorn", "commandbay.server:app", "--host", "localhost", "--reload", "--port", "7321"]+args
subprocess.run(command)

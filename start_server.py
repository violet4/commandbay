import subprocess
import sys

args = sys.argv[1:]

command = ["poetry", "run", "uvicorn", "commandbay.server:app", "--host", "localhost", "--reload", "--port", "5000"]+args
subprocess.run(command)

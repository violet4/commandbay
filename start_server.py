import subprocess

command = ["poetry", "run", "uvicorn", "twitch_bot.server:app", "--host", "localhost", "--reload", "--port", "5000"]
subprocess.run(command)

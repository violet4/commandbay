import subprocess

command = ["poetry", "run", "uvicorn", "twitch_bot.server:app", "--host", "localhost", "--reload"]
subprocess.run(command)

Handy cross-platform Twitch bot capabilities exposed through a localhost HTTP server.

# Getting Started

* `cp env_sample.txt env.txt`
* add spotify credentials to `env.txt` if you want spotify access
* `poetry install`
* run the bot: `python start_server.py`
* Test it out: visit http://localhost:5000/docs in your web browser to see and interact with the API through a SwaggerUI

Run the tests:

* `poetry run pytest --cov=twitch_bot tests/`

# Command Bay

Handy cross-platform Twitch bot capabilities exposed through a localhost HTTP server.

# Getting Started

* `cp env_sample.txt env.txt`
* add spotify credentials to `env.txt` if you want spotify access
* `poetry install --only=main`
* run the server: `python start_server.py`
* Test it out: visit http://localhost:7321/api/v0/docs in your web browser to see and interact with the API through a SwaggerUI

Run the web interface:
* `cd frontend`
* `npm install`
* `npm run dev`
* visit http://localhost:7321 in your browser (note that the backend server must be running)

Run the tests:

* `poetry run pytest --cov=commandbay tests/`
* generate html coverage reports: `poetry run coverage html`

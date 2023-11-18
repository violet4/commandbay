#!/bin/sh
poetry run flask --app twitch_bot.server:app run -h localhost --debug --with-threads

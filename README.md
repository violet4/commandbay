
a handy twitch bot.

* greets users as they enter the channel. keeps track of users we've seen before in a sqlite3 database, so we don't re-greet them if we have to restart the bot. can also re-greet a user if we haven't seen them interact in a predefined number of minutes (default 180 minutes, i.e. 3 hours).
* keeps track of user events, e.g. when a user joins the channel, leaves the channel, or sends a message (not including the message content). optimized to reduce storage space by utilizing good relational database practices.
* cross-platform text-to-speech using the pyttsx3 library, so you don't have to keep visually checking for messages.
* has the ability to add commands in separate files in the plugins directory, and they automatically get loaded. a sample is included.

How to set up:
* `cp env_sample.txt env.txt`
* fill out env.txt (it contains instructions on how to set it up)
* * poetry install
* run the bot: `poetry run python twitch_bot/bot.py`

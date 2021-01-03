
a handy twitch bot.

* has the ability to add commands in separate files in the plugins directory, and they automatically get loaded. a sample is included.
* keeps track of user events, e.g. when a user joins the channel, leaves the channel, or sends a message (not including the message content). optimized to reduce storage space by utilizing good relational database practices.
* cross-platform text-to-speech using the pyttsx3 library, so you don't have to keep visually checking for messages.


How to set up:

    cp env_sample.txt env.txt

* fill out env.txt (it contains instructions on how to set it up)
* use virtualenv or anaconda to create an environment, and install twitchio using:
** pip install twitchio
** pip install pyttsx3
* run the bot: `python bot.py`

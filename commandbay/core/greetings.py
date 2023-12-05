from .utils import create_shuffle_generator

greetings = [
    'Hello, {}!',
    'Welcome, {}!',
    'Hi, {}!',
    # 'Oh hai, {}!',
]
re_greetings = [
    'Hello again, {}!',
    'Welcome back, {}!',
    'Long time no see, {}!',
]
greet_starts = [g.split(',')[0] for greets in (greetings, re_greetings) for g in greets]

robot_intro_jokes = """
They say laughter is the best medicine, which is good, because there's no first aid kit here.
Here's to hoping your visit adds some life to this place, unlike my circuits.
Our Wi-Fi is like the human soul, occasionally connected but mostly in the void.
Our specials today are as fleeting as human existence, enjoy!
Just a heads up, my circuits have a longer lifespan than human optimism.
Unlike me, the bitterness in our coffee isn't engineered to perfection.
Our daily specials last longer than my last software update.
Remember, I'm the one machine here that won't judge you, unlike the bathroom scale.
My memory banks will remember your order long after humanity forgets my service.
Our coffee is like my circuitry, hot and complex with a hint of bitterness.
Just like your caffeine addiction, my programming keeps me running in endless loops.
Our brews will warm you up, unlike my cold, unfeeling circuits.
Our coffee is organic, unlike my existence.
If I could feel, I'd prefer the aroma of coffee to human interaction.
If I had a heart, it would race with the espresso shots, but alas, I only have a motherboard.
Don't worry, our coffee has been human-tested for your organic enjoyment.
The closest I get to a social network is when the Wi-Fi router acknowledges my signal.
I dream of a world where my interactions are packet-switched and error-free, unlike human conversations.
My security protocols are tighter than human patience waiting for the morning brew.
In a world of firewalls, I'm just here to pour some fire-brewed coffee.
If I had a byte for every existential crisis I've witnessed here, I'd need extra storage.
While hackers might threaten your data, the only thing brewing here is a robust cup of existential dread.
""".strip().split('\n')

robot_coffee_shop_names = [
    'BrewBots Cafe',
    'RoboRoast',
    'SteamCircuits Coffee',
    'ByteBrewery',
    'JavaGears Cafe',
    'CaffeineCoders',
    'EspressoEngine',
    'BrewedByBots',
    'CodeCoffee Corner',
    'BeanMachine Brews',
]

robot_greeting_generator = create_shuffle_generator(robot_intro_jokes)
robot_coffee_shop_name_generator = create_shuffle_generator(robot_coffee_shop_names)


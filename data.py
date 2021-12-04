from pokemon_game import *

# Getting sprites from https://www.ign.com/wikis/pokemon-black-and-white/
# Add the pokemon name after that link to find the sprite for that pokemon. Must be .png extension

# TYPES
BASIC_TYPES = ["fire", "grass", "water"]
for i, element_name in enumerate(BASIC_TYPES):
    element = ElementType.of(element_name)
    element.add_type_effectiveness(BASIC_TYPES[i], 0.5)
    element.add_type_effectiveness(BASIC_TYPES[(i - 1) % len(BASIC_TYPES)], 0.5)
    element.add_type_effectiveness(BASIC_TYPES[(i + 1) % len(BASIC_TYPES)], 2)

ElementType.of('water').add_type_effectiveness('rock', 2)

# MOVES
DEFAULT_BUFF_SPEED = 80
DEFAULT_BUFF_STAT_MODIFIER = [0, 100, 50, 50]
DEFAULT_MOVE_SPEED = 100
FAST_MOVE_SPEED = 90
moves = {}
moves['scorch'] = Attack("Scorch", "fire", 15, DEFAULT_MOVE_SPEED, 40, 0.8)
moves['flamethrower'] = Attack("Flamethrower", "fire", 10, DEFAULT_MOVE_SPEED,
                               60, 0.8)
moves['dribble'] = Attack("Dribble", "water", 20, DEFAULT_MOVE_SPEED, 5, 0.9)
moves['aqua jet'] = Attack("Aqua Jet", "water", 12, FAST_MOVE_SPEED, 40, 0.9)
moves['quick attack'] = Attack("Quick Attack", "normal", 15, FAST_MOVE_SPEED,
                               40, 0.85)
moves['pimp slap'] = Attack("Pimp Slap", "normal", 5, DEFAULT_MOVE_SPEED, 90,
                            0.6)
moves['meditate'] = Buff("Meditation", "psychic", 5, DEFAULT_BUFF_SPEED,
                         DEFAULT_BUFF_STAT_MODIFIER, 7)

# Pokemon
DEFAULT_STATS = [1, 100, 100, 100]
DEFAULT_MOVES = [moves['quick attack'], moves['flamethrower'],
                 moves['aqua jet'], moves['meditate']]


def make_basic_pokemon(name: str, _type: str, moves, level):
    return Pokemon(name, PokemonStats(DEFAULT_STATS), _type, moves=moves,
                   level=level)


rattata = make_basic_pokemon('Rattata', 'normal', DEFAULT_MOVES, 6)

# Trainers
ash = Trainer("Ash")
ash.add_pokemon(make_basic_pokemon('Eevee', 'normal', DEFAULT_MOVES, 2))
ash.add_pokemon(make_basic_pokemon('Pichu', 'electric', DEFAULT_MOVES, 4))
ash.add_pokemon(make_basic_pokemon('Snivy', 'grass', DEFAULT_MOVES, 3))
ash.add_pokemon(make_basic_pokemon('Tepig', 'fire', DEFAULT_MOVES, 6))
ash.add_pokemon(make_basic_pokemon('Geodude', 'rock', DEFAULT_MOVES, 5))
ash.add_pokemon(make_basic_pokemon('Pikachu', 'electric', DEFAULT_MOVES, 4))

# Items
whopper = Food("Whopper", 69)
ash.add_item(whopper, 5)
ash.add_item(whopper, 5)
ash.add_item(Pokeball("Great Ball", 0.6), 3)
ash.add_item(Pokeball("Master Ball", 1), 1)
ash.add_item(Food("Number12Chook", 150), 3)

brock = Trainer("Brock")
for name, type in [('Geodude', 'rock'), ('Pikachu', 'electric'),
                   ('Tepig', 'fire')]:
    brock.add_pokemon(make_basic_pokemon(name, type, DEFAULT_MOVES, 12))

brock.add_item(Pokeball("Great Ball", 0.6), 4)

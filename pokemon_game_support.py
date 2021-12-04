from random import random
from typing import Tuple

SUPPLIED_VERSION = 1.0

# Stats
STAT_HIT_CHANCE = 0
STAT_MAX_HEALTH = 1
STAT_ATTACK = 2
STAT_DEFENSE = 3

LEVEL_UP_STAT_GROWTH = 1.05

# Action Priorities
DEFAULT_ACTION_PRIORITY = 0
SPEED_BASED_ACTION_PRIORITY = 1

# Pokeballs
POKEBALL_INVALID_BATTLE_TYPE = "Pokeballs have no effect in trainer battles."
POKEBALL_UNSUCCESSFUL_CATCH = "It was so close, but {} escaped!"
POKEBALL_SUCCESSFUL_CATCH = "{} was caught!"
POKEBALL_FULL_TEAM = "{} was caught, but there was no more room."

# Fleeing
FLEE_SUCCESS = "Got away safely!"
FLEE_INVALID = "Unable to escape a trainer battle."

MAXIMUM_MOVE_SLOTS = 4
MAXIMUM_POKEMON_ROSTER = 6

WRONG_FILE_MESSAGE = """When you have completed all non-masters tasks, run
the game.py file to play a test Pokemon battle with the GUI."""

# Types
Stats = Tuple[float, int, int, int]


class ElementType(object):
    """A class which represents elemental types of pokemon and their moves."""

    _elements = {}

    @staticmethod
    def of(name: str) -> 'ElementType':
        """A static method which returns the instance corresponding to the
        supplied name, creating it if it doesn't yet exist.
        
        Parameters:
            name (str): The unique name of the elemental type.
        
        Returns:
            (ElementType): The element type corresponding to the given name.
        """
        if name in ElementType._elements:
            return ElementType._elements[name]
        return ElementType(name)

    def __init__(self, name: str) -> None:
        """ Creates an ElementType instance and adds it to the class-wide
        dictionary.

        Parameters:
            name (str): The unique name of the elemental type.
        """
        self._name = name
        self._effectiveness = {}
        ElementType._elements[name] = self

    def add_type_effectiveness(self, type: str, effectiveness: float) -> None:
        """Associates a type and effectiveness for this instance.

        Parameters:
            type (str): The unique name of the added type
            effectiveness (float): The damage multiplier when a move of this
                    instance's type attacks a pokemon of the supplied type.
        
        """
        self._effectiveness[type] = effectiveness

    def get_effectiveness(self, defending_type: str) -> float:
        """Get the effectiveness of this instance's type against the supplied
        defending type.
        
        Parameters:
            defending_type (str): The unique name of the defending type
            
        Returns:
            (float): The damage multiplier of a move against the defending type
        """
        return self._effectiveness.get(defending_type, 1.0)

    def __str__(self) -> str:
        """(str): Return a string representation of this class"""
        return self._name

    def __repr__(self) -> str:
        """(str): Return a string representation of this class"""
        return str(self)


def did_succeed(chance: float) -> bool:
    """Performs a 'roll' based on the supplied chance, and returns true iff
    the roll succeeded.
    
    Parameters:
        chance (float): The probability in the range [0, 1] that the roll
        succeeded.
        
    Returns:
        (bool): True iff the roll succeeded
    """
    return random() < chance


class NoPokemonException(Exception):
    pass

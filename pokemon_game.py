from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from pokemon_game_support import *
from math import floor


class PokemonStats(object):
    """A class modelling the stats of a pokemon. These stats must be
    non-negative. """

    def __init__(self, stats: Stats) -> None:
        """
        Constructs an instance of PokemonStats.

         Parameters:
             stats (Stats): The base list of stats to encapsulate.
                            The format of the incoming stats are:
                            (hit_chance, health, attack, defense)
        """
        self._stats = stats

    def level_up(self) -> None:
        """Grows the PokemonStats instance after the pokemon has levelled up."""

        # hit_chance changed to 1.0
        new_stats = [1.0]

        # increase the rest by 5%
        for i in (STAT_MAX_HEALTH, STAT_ATTACK, STAT_DEFENSE):
            new_stats.append(floor(self._stats[i] * LEVEL_UP_STAT_GROWTH))

        self._stats = tuple(new_stats)

    def get_hit_chance(self) -> float:
        """(float) Return the pokemon's current chance at making a successful
        attack. """
        return self._stats[STAT_HIT_CHANCE]

    def get_max_health(self) -> int:
        """(int) Return the pokemon's max health."""
        return self._stats[STAT_MAX_HEALTH]

    def get_attack(self) -> int:
        """"(int) Return the pokemon's attack stat"""
        return self._stats[STAT_ATTACK]

    def get_defense(self) -> int:
        """(int) Return the pokemon's defense stat"""
        return self._stats[STAT_DEFENSE]

    def apply_modifier(self, modifier: Stats) -> PokemonStats:
        """Applies a stat modifier and returns the newly constructed,
        modified pokemon stats.

        Parameters:
            modifier (Stats): A list of stat modifications to apply.

        Returns:
            (PokemonStats): a newly constructed pokemon stats.
        """
        modified_stats = []
        for i, change in enumerate(modifier):
            modified_val = self._stats[i] + change
            if modified_val < 0:
                modified_val = 0
            modified_stats.append(modified_val)

        return PokemonStats(tuple(modified_stats))

    def __str__(self) -> str:
        """(str) Returns a string representation of this class."""
        return f'{self.__class__.__name__}({self._stats})'

    def __repr__(self) -> str:
        """(str) Returns a string representation of this class."""
        return self.__str__()


class Pokemon(object):
    """A class which represents a Pokemon."""

    def __init__(
            self, name: str, stats: PokemonStats, element_type: str,
            moves: List[Move], level: int = 1
    ) -> None:
        """Creates a Pokemon instance.

        Parameters:
            name (str): The name of this pokemon
            stats (PokemonStats): The pokemon's stats
            element_type (str): The name of the type of this pokemon.
            moves (list): A list containing the moves that this pokemon will
                        have learned after it is instantiated.
            level (int): The pokemon's level.
        """
        self._name = name
        self._stats = stats
        self._stat_modifiers = {}  # keep track of the rounds of the modifiers
        self._combined_modifier = [0.0, 0, 0, 0]  # keep track of the overall effect of the modifiers
        self._element_type = element_type

        self._moves = {}
        for move in moves:
            self._moves[move] = move.get_max_uses()

        self._level = level
        self._health = stats.get_max_health()
        self._experience = self._level ** 3

    def get_name(self) -> str:
        """(str) Get this pokemon's name."""
        return self._name

    def get_health(self) -> int:
        """(str) Get the remaining health of this pokemon."""
        return self._health

    def get_max_health(self) -> int:
        """(int) Get the maximum health of this pokemon before stat modifiers
        are applied. """
        return self._stats.get_max_health()

    def get_element_type(self) -> str:
        """(str) Get the name of the type of this pokemon."""
        return self._element_type

    def get_remaining_move_uses(self, move: Move) -> int:
        """Gets the number of moves left for the supplied move, or 0 if the
        pokemon doesn't know the move.

        Parameters:
            move (Move): The move to check.

        Returns:
            (int): the number of moves left for the supplied move, or 0 if the
            pokemon doesn't know the move.
        """
        return self._moves.get(move, 0)

    def get_level(self) -> int:
        """(int) Get the level of this pokemon."""
        return self._level

    def get_experience(self) -> int:
        """(int) Return the current pokemon's experience."""
        return self._experience

    def get_next_level_experience_requirement(self) -> int:
        """(int) Return the total experience required for the pokemon to be
        one level higher. """
        return (self._level + 1) ** 3

    def get_move_info(self) -> List[Tuple[Move, int]]:
        """(list) Return a list of the pokemon's known moves and their
        remaining uses. """

        move_info = list(self._moves.items())
        move_info.sort(key=lambda move_uses_tuple: move_uses_tuple[
            0].get_name())  # sort by name
        return move_info

    def has_fainted(self) -> bool:
        """(bool) Return true iff the pokemon has fainted."""
        return self.get_health() == 0

    def modify_health(self, change: int) -> None:
        """Modify the pokemon's health by the supplied amount.

        Parameters:
            change (int): The health change to be applied to the pokemon.
        """
        max_health = self.get_stats().get_max_health()
        self._health += change
        if self._health < 0:
            self._health = 0
        elif self._health > max_health:
            self._health = max_health

    def gain_experience(self, experience: int) -> None:
        """Increase the experience of this pokemon by the supplied amount, and level up if necessary.

        Parameters:
            experience (int): The amount of experience points to increase.
        """
        self._experience += experience
        while self._experience >= self.get_next_level_experience_requirement():
            self.level_up()

    def level_up(self) -> None:
        """Increase the level of this pokemon. leveling up grows the
        pokemon's stats, and increase its current health by the amount that
        the maximum hp increased. """
        old_max_health = self.get_max_health()
        self._stats.level_up()

        # increase its current health
        max_health_increment = self.get_max_health() - old_max_health
        self.modify_health(max_health_increment)

        self._level += 1

    def experience_on_death(self) -> int:
        """(int) The experience awarded to the victorious pokemon if this
        pokemon faints. """
        return floor(200 * self.get_level() / 7)

    def can_learn_move(self, move: Move) -> bool:
        """Returns true iff the pokemon can learn the given move. i.e. they
        have learned less than the maximum number of moves for a pokemon and
        they haven't already learned the supplied move.

        Parameters:
            move (Move): move for pokemon to learn.

        Returns:
             (bool): true iff the pokemon can learn the given move.
        """
        return not (len(
            self._moves) == MAXIMUM_MOVE_SLOTS or move in self._moves)

    def learn_move(self, move: Move) -> None:
        """Learns the given move, assuming the pokemon is able to.

        Parameters:
            move (Move): move for pokemon to learn.
        """
        self._moves[move] = move.get_max_uses()

    def forget_move(self, move: Move) -> None:
        """Forgets the supplied move, if the pokemon knows it.

        Parameters:
            move (Move): move for pokemon to forget.
        """
        self._moves.pop(move, 0)

    def has_moves_left(self) -> bool:
        """(bool) Returns true iff the pokemon has any moves they can use"""
        return len(self._moves) > 0

    def reduce_move_count(self, move: Move) -> None:
        """Reduce the move count of the move if the pokemon has learnt it.

        Parameters:
            move (Move): move for pokemon to reduce.
        """
        if self.get_remaining_move_uses(move) > 0:
            self._moves[move] -= 1
            if self._moves[move] == 0:
                self.forget_move(move)

    def add_stat_modifier(self, modifier: Stats, rounds: int) -> None:
        """Adds a stat modifier for a supplied number of rounds.

        Parameters:
            modifier (Stats): A stat modifier to be applied to the pokemon.
            rounds (int): The number of rounds that the stat modifier will be in
                        effect for.
        """
        self._stat_modifiers[PokemonStats(modifier)] = [rounds, modifier]
        for stat in (
        STAT_HIT_CHANCE, STAT_MAX_HEALTH, STAT_ATTACK, STAT_DEFENSE):
            self._combined_modifier[stat] += modifier[stat]

        self.modify_health(
            0)  # update health if it exceeds the modified max_health

    def get_stats(self) -> PokemonStats:
        """(PokemonStats) Return the pokemon stats after applying all current
        modifications. """
        return self._stats.apply_modifier(tuple(self._combined_modifier))

    def post_round_actions(self) -> None:
        """Update the stat modifiers by decrementing their remaining turns."""
        delete_modifiers = []
        for stat_modifier, (_, modifier) in self._stat_modifiers.items():
            self._stat_modifiers[stat_modifier][
                0] -= 1  # decrease the round by 1, then remove it if it ends
            if self._stat_modifiers[stat_modifier][0] == 0:
                for stat in (
                STAT_HIT_CHANCE, STAT_MAX_HEALTH, STAT_ATTACK, STAT_DEFENSE):
                    self._combined_modifier[stat] -= modifier[stat]
                delete_modifiers.append(stat_modifier)

        # update health if it exceeds the modified max_health
        self.modify_health(0)
        # delete modifiers that are no longer working
        for delete_modifier in delete_modifiers:
            del self._stat_modifiers[delete_modifier]

    def rest(self) -> None:
        """Returns this pokemon to max health, removes any remaining stat
        modifiers, and resets all move uses to their maximums. """
        self._health = self.get_max_health()

        # removes any remaining stat modifiers
        self._stat_modifiers.clear()
        self._combined_modifier = [0.0, 0, 0, 0]

        # resets all move uses
        for move in self._moves.keys():
            self._moves[move] = move.get_max_uses()

    def __str__(self) -> str:
        """(str) Returns a simple representation of this pokemon's name and
        level. """
        return f'{self._name} (lv{self._level})'

    def __repr__(self) -> str:
        """(str) Returns a string representation of this pokemon"""
        return self.__str__()


class Trainer(object):
    """A class representing a pokemon trainer."""

    def __init__(self, name: str) -> None:
        """Create an instance of the Trainer class.

        Parameters:
            name (str): The name of the trainer.
        """
        self._name = name
        self._inventory = {}
        self._roster = []
        self._current_pokemon_index = 0

    def get_name(self) -> str:
        """(str) Return the trainer's name."""
        return self._name

    def get_inventory(self) -> Dict[Item, int]:
        """(dict) Returns the trainer's inventory."""
        return self._inventory

    def get_current_pokemon(self) -> Pokemon:
        """(Pokemon) Gets the current pokemon, or raises a NoPokemonException
        if the trainer doesn't have a single pokemon."""
        try:
            return self._roster[self._current_pokemon_index]
        except IndexError:
            raise NoPokemonException

    def get_all_pokemon(self) -> List[Pokemon]:
        """(list) Returns the trainer's pokemon."""
        return list(tuple(self._roster))

    def rest_all_pokemon(self) -> None:
        """Rests all pokemon in the party"""
        for pokemon in self._roster:
            pokemon.rest()

    def can_add_pokemon(self, pokemon: Pokemon) -> bool:
        """Returns true iff the supplied pokemon can be added to this
        trainer's roster.

        Parameters:
            pokemon (Pokemon): The pokemon to add.

        Returns:
            (bool): True iff the supplied pokemon can be added to this trainer's
                roster.
        """
        return not (len(
            self._roster) == MAXIMUM_POKEMON_ROSTER or pokemon in self._roster)

    def all_pokemon_fainted(self) -> bool:
        """(bool) Return true iff all the trainer's pokemon have fainted."""
        for pokemon in self._roster:
            if not pokemon.has_fainted():
                return False
        return True

    def add_pokemon(self, pokemon: Pokemon) -> None:
        """Adds a new pokemon into the roster, assuming that doing so would
        be valid.

        Parameters:
            pokemon (Pokemon): The pokemon to add.
        """
        self._roster.append(pokemon)

    def can_switch_pokemon(self, index: int) -> bool:
        """Determines if the pokemon index would be valid to switch to.

        Parameters:
            index (int): The index of the next pokemon in the roster.

        Returns:
            (bool): True iff the switch would be valid.
        """
        # index out of range
        if index > len(self._roster) - 1:
            return False
        # the pokemon is currently out
        if self._current_pokemon_index == index:
            return False
        # the pokemon hasn't fainted
        if self._roster[index].has_fainted():
            return False
        return True

    def switch_pokemon(self, index: int) -> None:
        """Switches pokemon to the one at the supplied index, assuming that
        the switch is valid.

        Parameters:
           index (int): The index of the pokemon to switch to.
        """
        self._current_pokemon_index = index

    def add_item(self, item: Item, uses: int) -> None:
        """Adds an item to the trainer's inventory and increments its uses by
        the supplied amount.

        Parameters:
            item (Item): The item to add.
            uses (int): The quantity of the item to be added to the inventory.
        """
        self._inventory[item] = self._inventory.get(item, 0) + uses

    def has_item(self, item: Item) -> bool:
        """(bool) Returns true if the item is in the trainer's inventory and has
         uses.

        Parameters:
            item (Item): The item to check.

        Returns:
            (bool): True if the item is in the trainer's inventory and has uses.
        """
        return item in self._inventory and self._inventory.get(item, 0) > 0

    def use_item(self, item: Item) -> None:
        """If the item is present in the trainer's inventory, decrement its
        count. Removes the item from the inventory entirely if its count hits
        0.

        Parameters:
            item (Item): The item to use.
        """
        if self.has_item(item):
            self._inventory[item] -= 1
            if self._inventory[item] == 0:
                del self._inventory[item]

    def __str__(self) -> str:
        """(str) Returns a string representation of a Trainer"""
        return f"{self.__class__.__name__}(\'{self._name}\')"

    def __repr__(self) -> str:
        """(str) Returns a string representation of a Trainer"""
        return self.__str__()


class Battle(object):
    """A class which represents a pokemon battle. """

    def __init__(self, player: Trainer, enemy: Trainer,
                 is_trainer_battle: bool) -> None:
        """Creates an instance of a trainer battle.

        Parameters:
            player (Trainer): The trainer corresponding to the player character.
            enemy (Trainer): The enemy trainer.
            is_trainer_battle (bool): True iff the battle takes place between trainers.
        """
        self._player = player
        self._enemy = enemy
        self._is_trainer_battle = is_trainer_battle
        self._turn = None
        self._action_queue = []
        self._over = False

    def get_turn(self) -> Optional[bool]:
        """Get whose turn it currently is.

        Returns:
            (Optional): None if the round just started.
                        True if it is the player's turn, False the enemy's.
        """
        return self._turn

    def get_trainer(self, is_player: bool) -> Trainer:
        """Gets the trainer corresponding to the supplied parameter.

        Parameters:
            is_player: True iff the trainer we want is the player.

        Returns:
            (Trainer): player or enemy.
        """
        return self._player if is_player else self._enemy

    def attempt_end_early(self) -> None:
        """Ends the battle early if it's not a trainer battle."""
        if not self.is_trainer_battle():
            self._over = True

    def is_trainer_battle(self) -> bool:
        """(bool) Returns true iff the battle is between trainers"""
        return self._is_trainer_battle

    def is_action_queue_full(self) -> bool:
        """(bool) Returns true if both trainers have an action queued."""
        return len(self._action_queue) == 2

    def is_action_queue_empty(self) -> bool:
        """(bool) Returns true if neither trainer have an action queued."""
        return len(self._action_queue) == 0

    def trainer_has_action_queued(self, is_player: bool) -> bool:
        """Returns true iff the supplied trainer has an action queued

        Parameters:
            is_player (bool): True iff the trainer we want to check for is the player.

        Returns:
            (bool): True iff the supplied trainer has an action queued
        """
        for _, trainer in self._action_queue:
            if trainer == is_player:
                return True
        return False

    def is_ready(self) -> bool:
        """(bool) Returns true iff the next action is ready to be performed.

        The battle is deemed ready if neither trainer has performed an action
        this round and the action queue is full, or if one trainer has
        performed an action, and the other trainer is in the queue. """

        # neither trainer has performed an action this round
        no_performed = self.get_turn() is None

        # one performed
        one_performed = self.get_turn() is not None

        # the other in queue
        the_other_in_queue = self.trainer_has_action_queued(self.get_turn())

        return (no_performed and self.is_action_queue_full()) or (
                    one_performed and the_other_in_queue)

    def queue_action(self, action: Action, is_player: bool) -> None:
        """Attempts to queue the supplied action if it's valid given the
        battle state, and came from the right trainer.

        Parameters:
            action (Action): The action we are attempting to queue
            is_player (bool): True iff the action is going to be performed by
                            the player.
        """

        # The trainer is already in the queue
        if self.trainer_has_action_queued(is_player):
            return None

        # The queue is ready
        if self.is_ready():
            return None

        # The action is invalid given the game state
        if not action.is_valid(self, is_player):
            return None

        self._action_queue.append((action, is_player))

    def enact_turn(self) -> Optional[ActionSummary]:
        """(Optional[ActionSummary]) Attempts to perform the next action in
        the queue, and returns a summary of its effects if it was valid.

        If the next action in the queue is invalid, it should still be
        removed from the queue. If this was the last turn to be performed
        that round, perform the post round actions. """
        summary = ActionSummary()

        # first turn
        if self.get_turn() is None:
            # evaluate the priority of actions
            if self._action_queue[0][0].get_priority() <= \
                    self._action_queue[1][0].get_priority():
                action_to_perform, performer = self._action_queue.pop(0)
            else:
                action_to_perform, performer = self._action_queue.pop(1)

            if action_to_perform.is_valid(self, performer):
                summary.combine(action_to_perform.apply(self, performer))

            self._turn = not performer

        # last turn
        else:
            action_to_perform, performer = self._action_queue.pop()
            if action_to_perform.is_valid(self, performer):
                summary.combine(action_to_perform.apply(self, performer))

            # round ends
            self._turn = None
            for trainer in (self._player, self._enemy):
                for pokemon in trainer.get_all_pokemon():
                    pokemon.post_round_actions()
        return summary

    def is_over(self) -> bool:
        """(bool) Returns true iff the battle is over. A battle is over if a
        trainer has fled, or if all of the pokemon have fainted for either
        trainer. """
        if self._over or \
                self._player.all_pokemon_fainted() or \
                self._enemy.all_pokemon_fainted():
            self._over = True
            return True
        return False


class ActionSummary(object):
    """A class containing messages about actions and their effects."""

    def __init__(self, message: Optional[str] = None) -> None:
        """Constructs a new ActionSummary with an optional message.

         Parameters:
             message (Optional): An optional message to be included.
        """
        self._message = [] if message is None else [message]

    def get_messages(self) -> List[str]:
        """(list) Returns a list of the messages contained within this
        summary. """
        return self._message

    def add_message(self, message: str) -> None:
        """Adds the supplied message to the message builder.

        Parameters:
            message (str): The message to add.
        """
        self._message.append(message)

    def combine(self, summary: ActionSummary) -> None:
        """Combines two ActionSummaries.

        Parameters:
            summary (ActionSummary): A summary containing the messages to add.
        """
        self._message.extend(summary.get_messages())


class Action(object):
    """An abstract class detailing anything which takes up a turn in battle.
    Applying an action can be thought of as moving the game from one state to
    the next. """

    def get_priority(self) -> int:
        """(int) Returns the priority of this action, which is used to
        determine which action is performed first each round in the battle.
        Lower values of priority are 'quicker' than higher values """
        return DEFAULT_ACTION_PRIORITY

    def is_valid(self, battle: Battle, is_player: bool) -> bool:
        """Determines if the action would be valid for the given trainer and
        battle state.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (bool): True iff it would be valid.
        """

        # not valid if the game is over
        if battle.is_over():
            return False

        # not valid if it is not at the beginning of the round and not the
        # trainer's turn
        if battle.get_turn() is not None and battle.get_turn() != is_player:
            return False
        return True

    def apply(self, battle: Battle, is_player: bool) -> ActionSummary:
        """Applies the action to the game state and returns a summary of the
        effects of doing so. On the base Action class, this method should
        raise a NotImplementedError.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """(str) Returns a string representation of an Action."""
        return f'{self.__class__.__name__}()'

    def __repr__(self) -> str:
        """(str) Returns a string representation of an Action."""
        return self.__str__()


class Flee(Action):
    """An action where the trainer attempts to run away from the battle."""

    def is_valid(self, battle: Battle, is_player: bool) -> bool:
        """Determines if an attempt to flee would be valid for a given battle
        state. Fleeing is considered a valid action if the base action
        validity checks pass, and the trainer's current pokemon has not
        fainted. This does not mean, however, that a trainer can flee trainer
        battles. In that case, fleeing is considered wasting a turn.

        Parameters:
            battle (Battle): The ongoing pokemon battle.
            is_player (bool): True iff the player is using this action.

        Returns:
            (bool): True iff it would be valid.
        """

        # valid action
        if not super().is_valid(battle, is_player):
            return False

        # and current pokemon not fainted
        if battle.get_trainer(is_player).get_current_pokemon().has_fainted():
            return False
        return True

    def apply(self, battle: Battle, is_player: bool) -> ActionSummary:
        """The trainer attempts to flee the battle. The resulting message
        depends on whether or not the action was successful.

        Parameters
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (ActionSummary): the message to return after applying flee.
        """
        if battle.is_trainer_battle():
            summary = FLEE_INVALID
        else:
            summary = FLEE_SUCCESS
            battle.attempt_end_early()
        return ActionSummary(summary)


class SwitchPokemon(Action):
    """An action representing the trainer's intention to switch pokemon."""

    def __init__(self, next_pokemon_index: int) -> None:
        """Creates an instance of the SwitchPokemon class.

        Parameters:
            next_pokemon_index (int): The index of the pokemon the trainer wants
             to switch to.
        """
        self._next_pokemon_index = next_pokemon_index

    def is_valid(self, battle: Battle, is_player: bool) -> bool:
        """Determines if switching pokemon would be valid for a given trainer
        and battle state.

        Parameters:
            battle (Battle): The ongoing pokemon battle.
            is_player (bool): True iff the player is using this action.

        Returns:
            (bool): True iff it would be valid.
        """

        # valid action
        if not super().is_valid(battle, is_player):
            return False

        # and trainer can switch
        if not battle.get_trainer(is_player).can_switch_pokemon(
                self._next_pokemon_index):
            return False
        return True

    def apply(self, battle: Battle, is_player: bool) -> ActionSummary:
        """The trainer switches pokemon, assuming that the switch would be valid.

        Parameters
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (ActionSummary): the message to return after switching.
        """
        trainer = battle.get_trainer(is_player)
        summary = ActionSummary()

        if not trainer.get_current_pokemon().has_fainted():
            summary.add_message(
                f'{trainer.get_current_pokemon().get_name()}, return!')

        trainer.switch_pokemon(self._next_pokemon_index)
        summary.add_message(
            f'{trainer.get_name()} switched to {trainer.get_current_pokemon().get_name()}.')
        return summary

    def __str__(self) -> str:
        """(str) Returns a string representation of a SwitchPokemon."""
        return f'{self.__class__.__name__}({self._next_pokemon_index})'


class Item(Action):
    """An abstract class representing an Item, which a trainer may attempt to
    use to influence the battle. """

    def __init__(self, name: str) -> None:
        """Creates an Item

        Parameters:
            name (str): The name of the item.
        """
        self._name = name

    def get_name(self) -> str:
        """(str) Return the name of this item"""
        return self._name

    def is_valid(self, battle: Battle, is_player: bool) -> bool:
        """Determines if using the item would be a valid action for the given trainer and battle state.

        Parameters:
            battle (Battle): The ongoing pokemon battle.
            is_player (bool): True iff the player is using this item.

        Returns:
            (bool): True iff it would be valid.
        """

        # valid action
        if not super().is_valid(battle, is_player):
            return False

        # and current pokemon not fainted
        if battle.get_trainer(is_player).get_current_pokemon().has_fainted():
            return False

        # and trainer has the item
        if not battle.get_trainer(is_player).has_item(self):
            return False
        return True

    def decrement_item_count(self, trainer: Trainer) -> None:
        """Decrease the count of this item by one in the trainer's inventory

        Parameters
            trainer (Trainer): The trainer attempting to use this item.
        """
        trainer.use_item(self)

    def __str__(self):
        """(str) Returns a string representation of an Item"""
        return f"{self.__class__.__name__}(\'{self._name}\')"


class Pokeball(Item):
    """An item which a trainer can use to attempt to catch wild pokemon."""

    def __init__(self, name: str, catch_chance: float) -> None:
        """Creates a pokeball instance, used to catch pokemon in wild battles

        Parameters:
            name (str): The name of this pokeball
            catch_chance (float): The chance this pokeball has of catching a pokemon.
        """
        super().__init__(name)
        self._catch_chance = catch_chance

    def apply(self, battle: Battle, is_player: bool) -> ActionSummary:
        """Attempt to catch the enemy pokemon and returns an ActionSummary
        containing information about the catch attempt.

        Parameters
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (ActionSummary): the message to return after applying the pokeball.
        """
        trainer = battle.get_trainer(is_player)
        wild_pokemon = battle.get_trainer(not is_player).get_current_pokemon()

        self.decrement_item_count(trainer)
        # catching not possible in trainer battles
        if battle.is_trainer_battle():
            return ActionSummary(POKEBALL_INVALID_BATTLE_TYPE)

        # failure catching
        if not did_succeed(self._catch_chance):
            return ActionSummary(
                POKEBALL_UNSUCCESSFUL_CATCH.format(wild_pokemon.get_name()))

        # no room
        if not trainer.can_add_pokemon(wild_pokemon):
            return ActionSummary(
                POKEBALL_FULL_TEAM.format(wild_pokemon.get_name()))

        # succeed
        trainer.add_pokemon(wild_pokemon)
        battle.attempt_end_early()
        return ActionSummary(
            POKEBALL_SUCCESSFUL_CATCH.format(wild_pokemon.get_name()))


class Food(Item):
    """An Item which restores HP to the pokemon whose trainer uses it."""

    def __init__(self, name: str, health_restored: int) -> None:
        """Create a Food instance.

        Parameters
            name (str): The name of this food.
            health_restored (int): The number of health points restored when a
            pokemon eats this piece of food.
        """
        super().__init__(name)
        self._health_restored = health_restored

    def apply(self, battle: Battle, is_player: bool) -> ActionSummary:
        """The trainer's current pokemon eats the food. Their current
        pokemon's health should consequently increase by the amount of health
        restored by this food.

        Parameters
            battle (Battle): The ongoing pokemon battle.
            is_player (bool): True iff the player is using the food.

        Returns:
            (ActionSummary): the message to return after eating the food.
        """
        trainer = battle.get_trainer(is_player)
        pokemon = trainer.get_current_pokemon()

        self.decrement_item_count(trainer)
        pokemon.modify_health(self._health_restored)
        return ActionSummary(f"{pokemon.get_name()} ate {self.get_name()}.")


class Move(Action):
    """An abstract class representing all learnable pokemon moves."""

    def __init__(self, name: str, element_type: str, max_uses: int,
                 speed: int) -> None:
        """Creates an instance of the Move class.

        Parameters:
            name (str): The name of this move
            element_type (str): The name of the type of this move
            max_uses (int): The number of time this move can be used before resting
            speed (int): The speed of this move, with lower values corresponding to faster moves priorities.
        """
        self._name = name
        self._element_type = element_type
        self._max_uses = max_uses
        self._speed = speed

    def get_name(self) -> str:
        """(str) Return the name of this move"""
        return self._name

    def get_element_type(self) -> str:
        """(str) Return the type of this move"""
        return self._element_type

    def get_max_uses(self) -> int:
        """(int) Return the maximum times this move can be used"""
        return self._max_uses

    def get_priority(self) -> int:
        """(int) Returns the priority of this move."""
        return SPEED_BASED_ACTION_PRIORITY + self._speed

    def is_valid(self, battle: Battle, is_player: bool) -> bool:
        """Determines if the move would be valid for the given trainer and
        battle state.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
             (bool): True iff it would be valid.
        """
        pokemon = battle.get_trainer(is_player).get_current_pokemon()

        # valid action
        if not super().is_valid(battle, is_player):
            return False

        # and current pokemon not fainted
        if pokemon.has_fainted():
            return False

        # and current pokemon has learnt this move and has remaining uses
        if pokemon.get_remaining_move_uses(self) == 0:
            return False
        return True

    def apply(self, battle: Battle, is_player: bool) -> ActionSummary:
        """Applies the Move to the game state. Generally, the move should be
        performed, and the appropriate pokemon's remaining moves should be
        updated.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (ActionSummary): the message to return after applying the move.
        """
        trainer = battle.get_trainer(is_player)
        enemy = battle.get_trainer(not is_player)
        pokemon = trainer.get_current_pokemon()
        pokemon.reduce_move_count(self)
        summary = ActionSummary(f'{pokemon.get_name()} used {self.get_name()}.')

        # performing the move
        summary.combine(self.apply_ally_effects(trainer))
        summary.combine(self.apply_enemy_effects(trainer, enemy))
        return summary

    def apply_ally_effects(self, trainer: Trainer) -> ActionSummary:
        """Apply this move's effects to the ally trainer; if appropriate,
        and return the resulting ActionSummary.

        Parameters
            trainer (Trainer): The trainer whose pokemon is using the move.

        Returns:
            (ActionSummary): The message to return after applying the move on ally.
        """
        summary = ActionSummary()
        pokemon = trainer.get_current_pokemon()

        if type(self) is Buff:
            summary.add_message(
                f'{pokemon.get_name()} was buffed for {self.get_rounds()} turns.')
            pokemon.add_stat_modifier(self.get_modification(),
                                      self.get_rounds())
        return summary

    def apply_enemy_effects(self, trainer: Trainer,
                            enemy: Trainer) -> ActionSummary:
        """Apply this move's effects to the enemy; if appropriate, and return
        the resulting ActionSummary.

        Parameters
            trainer (Trainer): The trainer whose pokemon is using the move.
            enemy (Trainer): The trainer whose pokemon is the target of the move.

        Returns:
            (ActionSummary): The message to return after applying the move on enemy.
        """
        summary = ActionSummary()
        pokemon = trainer.get_current_pokemon()
        enemy_pokemon = enemy.get_current_pokemon()

        if type(self) is Debuff:
            summary.add_message(
                f'{enemy_pokemon.get_name()} was debuffed for {self.get_rounds()} turns.')
            enemy_pokemon.add_stat_modifier(self.get_modification(),
                                            self.get_rounds())

        if type(self) is Attack:
            if not self.did_hit(pokemon):
                summary.add_message(f'{enemy_pokemon.get_name()} missed!')
            else:
                enemy_pokemon.modify_health(
                    -self.calculate_damage(pokemon, enemy_pokemon))
                if enemy_pokemon.has_fainted():
                    summary.add_message(
                        f'{enemy_pokemon.get_name()} has fainted.')

                    experience = enemy_pokemon.experience_on_death()
                    pokemon.gain_experience(experience)
                    summary.add_message(
                        f'{pokemon.get_name()} gained {experience} exp.')

        return summary

    def __str__(self):
        """(str) Returns a string representation of a Move."""
        return f"{self.__class__.__name__}('{self.get_name()}', '{self.get_element_type()}', {self.get_max_uses()})"


class Attack(Move):
    """A class representing damaging pokemon moves, that may be used against
    an enemy pokemon. """

    def __init__(
            self, name: str, element_type: str, max_uses: int, speed: int,
            base_damage: int, hit_chance: float
    ) -> None:
        """Creates an instance of an attacking move.

        Parameters:
            name (str): The name of this move
            element_type (str): The name of the type of this move
            max_uses (int): The number of time this move can be used before resting
            speed (int): The speed of this move, with lower values corresponding to faster moves.
            base_damage (int): The base damage of this move.
            hit_chance (float): The base hit chance of this move.
        """

        super().__init__(name, element_type, max_uses, speed)
        self._base_damage = base_damage
        self._hit_chance = hit_chance

    def did_hit(self, pokemon: Pokemon) -> bool:
        """Determine if the move hit, based on the product of the pokemon's
        current hit chance, and the move's hit chance. Returns True iff it
        hits.

        Parameters:
            pokemon (Pokemon): The attacking pokemon.

        Returns:
            (bool): True iff it hits.
        """
        return did_succeed(
            pokemon.get_stats().get_hit_chance() * self._hit_chance)

    def calculate_damage(self, pokemon: Pokemon, enemy_pokemon: Pokemon) -> int:
        """Calculates what would be the total damage of using this move,
        assuming it hits, based on the stats of the attacking and defending
        pokemon.

        Parameters:
            pokemon (Pokemon): The attacking trainer's pokemon
            enemy_pokemon (Pokemon): The defending trainer's pokemon

        Returns:
            (int): The damage.
        """
        attack_type = self.get_element_type()
        defense_type = enemy_pokemon.get_element_type()

        effectiveness = ElementType.of(attack_type).get_effectiveness(
            defense_type)
        attack_stat = pokemon.get_stats().get_attack()
        defense_stat = enemy_pokemon.get_stats().get_defense()
        return floor(self._base_damage * effectiveness * attack_stat / (
                    defense_stat + 1))


class StatusModifier(Move):
    """An abstract class to group commonalities between buffs and debuffs."""

    def __init__(
            self, name: str, element_type: str, max_uses: int, speed: int,
            modification: Stats, rounds: int
    ) -> None:
        """Creates an instance of this class

        Parameters:
            name (str): The name of this move
            element_type (str): The name of the type of this move
            max_uses (int): The number of time this move can be used before resting
            speed (int): The speed of this move, with lower values corresponding to faster moves priorities.
            modification (Stats): A list of the same structure as the PokemonStats,
                                to be applied for the duration of the supplied number of rounds.
            rounds (int): The number of rounds for the modification to be in effect.
        """
        super().__init__(name, element_type, max_uses, speed)
        self._modification = modification
        self._rounds = rounds

    def get_modification(self):
        """(Stats) Returns a list of modifiers to be applied for the duration
        of the supplied number of rounds """
        return self._modification

    def get_rounds(self):
        """(int) Returns the number of rounds for the modification to be in
        effect. """
        return self._rounds


class Buff(StatusModifier):
    """Moves which buff the trainer's selected pokemon.
    A buff is a stat modifier that is applied to the pokemon using the move."""
    pass


class Debuff(StatusModifier):
    """Moves which debuff the enemy trainer's selected pokemon. A debuff is a
    stat modifier that is applied to the enemy pokemon which is the target of
    this move. """
    pass


# Below are the classes and functions which pertain only to masters students.
class Strategy(object):
    """An abstract class providing behaviour to determine a next action given
    a battle state. """

    @staticmethod
    def _switch_to_next_pokemon(battle: Battle, is_player: bool) -> Action:
        """Returns a SwitchPokemon action, assuming the current pokemon has fainted.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (SwitchPokemon): The action to perform.
        """
        trainer = battle.get_trainer(is_player)

        all_pokemon = trainer.get_all_pokemon()
        for index, next_pokemon in enumerate(all_pokemon):
            if not next_pokemon.has_fainted():
                return SwitchPokemon(index)

    def get_next_action(self, battle: Battle, is_player: bool) -> Action:
        """Determines and returns the next action for this strategy,
        given the battle state and trainer.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (Action): The action to perform.
        """
        raise NotImplementedError()


class ScaredyCat(Strategy):
    """A strategy where the trainer always attempts to flee. Switches to the
    next available pokemon if the current one faints, and then keeps
    attempting to flee. """

    def get_next_action(self, battle: Battle, is_player: bool) -> Action:
        """Determines and returns the next action for this strategy,
        given the battle state and trainer.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (Action): The action to perform.
        """
        trainer = battle.get_trainer(is_player)
        pokemon = trainer.get_current_pokemon()

        # If the current pokemon is dead, choose first non-dead.
        if pokemon.has_fainted():
            return Strategy._switch_to_next_pokemon(battle, is_player)

        return Flee()


class TeamRocket(Strategy):
    """A tough strategy used by Pokemon Trainers that are members of Team
    Rocket. """

    def get_next_action(self, battle: Battle, is_player: bool) -> Action:
        """Determines and returns the next action for this strategy,
        given the battle state and trainer.

        Parameters:
            battle (Battle): The ongoing pokemon battle
            is_player (bool): True iff the player is using this action.

        Returns:
            (Action): The action to perform.
        """
        trainer = battle.get_trainer(is_player)
        enemy = battle.get_trainer(not is_player)
        pokemon = trainer.get_current_pokemon()
        enemy_pokemon = enemy.get_current_pokemon()
        defense_type = enemy_pokemon.get_element_type()

        # Switch to the next available pokemon if the current one faints or
        # Attempt to flee any wild battle
        if pokemon.has_fainted() or not battle.is_trainer_battle():
            return ScaredyCat().get_next_action(battle, is_player)

        # Catch pikachu
        if enemy_pokemon.get_name().lower() == 'pikachu':
            # throw pokeball if some exist in the inventory
            for item in trainer.get_inventory().keys():
                if type(item) is Pokeball:
                    return item

        if not pokemon.has_moves_left():
            return Flee()

        # Choose first move with a type effectiveness greater than 1x against
        # the enemy pokemon's type
        candidate_move = []
        for move, uses in pokemon.get_move_info():
            if uses > 0:
                candidate_move.append(move)
                attack_type = move.get_element_type()
                if ElementType.of(attack_type).get_effectiveness(
                        defense_type) > 1:
                    return move

        # Otherwise, use the first available move with uses
        return candidate_move[0]


def create_encounter(trainer: Trainer, wild_pokemon: Pokemon) -> Battle:
    """Creates a Battle corresponding to an encounter with a wild pokemon.

    Parameters:
        trainer (Trainer): The adventuring trainer.
        wild_pokemon (Pokemon): The pokemon that the player comes into contact with.

    Returns:
        (Battle): The battle to create.
    """
    enemy = Trainer('')
    enemy.add_pokemon(wild_pokemon)
    return Battle(trainer, enemy, False)


if __name__ == "__main__":
    print(WRONG_FILE_MESSAGE)

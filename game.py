import tkinter as tk

import data
from pokemon_game import *
from battle_view import GUIBattleView


class PokemonBattle(object):
    """Controller class used to play out player battles"""

    def __init__(self, battle: Battle, enemy_strategy: Strategy,
                 view: GUIBattleView) -> None:
        """ Create an instance of a PokemonBattle.

        battle (Battle): The model of the state of the battle
        player_strategy (Strategy): The player's strategy
        enemy_strategy (Strategy): The enemy's strategy
        view (GUIBattleView): The view to use
        """
        self._battle = battle
        self._enemy_strategy = enemy_strategy
        self._view = view
        self._view.set_action_handler(self.handle_player_action)

    def play(self) -> None:
        """Plays out the game"""
        self._view.play()

    def prompt_player_action(self):
        """Check if the player has fainted, and if so force them to choose a
        new pokemon """
        player = self._battle.get_trainer(True)
        if player.get_current_pokemon().has_fainted():
            self._view.display_pokemon_selector()

    def handle_player_action(self, action: Action) -> None:
        if action.is_valid(self._battle, True):
            self._battle.queue_action(action, True)
            self._queue_enemy_turn()
            self.perform_available_actions()
        else:
            callback = self.prompt_player_action
            self._view.display_dialogue(
                ActionSummary(message='Invalid action!'), on_ok=callback)

    def _update_battlefield(self) -> None:
        player_pokemon = self._battle.get_trainer(True).get_current_pokemon()
        enemy_pokemon = self._battle.get_trainer(False).get_current_pokemon()
        self._view.update_battlefield(player_pokemon, enemy_pokemon)

    def perform_available_actions(self) -> None:
        if self._battle.is_ready():
            turn_summary = self._battle.enact_turn()
            if turn_summary is not None:
                self._update_battlefield()
                self._view.display_dialogue(turn_summary,
                                            on_ok=self.perform_available_actions)
            # Check if the action caused the game to be over.
            if self._battle.is_over():
                self.game_over()
                return
        if self._battle.is_action_queue_empty():
            self.prompt_appropriate_user()

    def prompt_appropriate_user(self):
        # If nothing unexpected happened, the round is over.
        if not self._battle.get_turn():
            self._queue_enemy_turn()
            self.perform_available_actions()
        else:
            self.prompt_player_action()

    def game_over(self):
        print('HERE')
        self._view.display_dialogue(ActionSummary("Game over"),
                                    on_ok=self._view.exit)

    def _queue_enemy_turn(self):
        self._battle.queue_action(
            self._enemy_strategy.get_next_action(self._battle, False), False)


class DefaultAIStrategy(Strategy):
    """A class, used by the enemy AI to determine which actions
    to take given a battle state."""

    def get_next_action(self, battle: Battle, is_player: bool) -> Action:
        trainer = battle.get_trainer(is_player)
        pokemon = trainer.get_current_pokemon()

        # If the current pokemon is dead, choose first non-dead.
        if pokemon.has_fainted():
            all_pokemon = trainer.get_all_pokemon()
            for index, next_pokemon in enumerate(all_pokemon):
                if not next_pokemon.has_fainted():
                    return SwitchPokemon(index)

        # Otherwise, choose first move with uses
        for move, uses in pokemon.get_move_info():
            if uses > 0:
                return move

        return Flee()


def main():
    battle = Battle(data.ash, data.brock, True)

    root = tk.Tk()
    root.geometry('600x420')

    player = battle.get_trainer(True)
    enemy_pokemon = battle.get_trainer(False).get_current_pokemon()
    view = GUIBattleView(root, player, enemy_pokemon)

    controller = PokemonBattle(battle, DefaultAIStrategy(), view)
    controller.play()

    root.mainloop()


if __name__ == "__main__":
    main()

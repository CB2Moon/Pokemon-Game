from enum import Enum
from typing import List
import tkinter as tk
from tkinter import messagebox

from PIL import ImageTk, Image

from pokemon_game import *

TYPE_COLOURS = {
    'fire': 'orange red',
    'water': 'PaleTurquoise1',
    'normal': 'sandy brown',
    'grass': 'green3',
    'electric': 'gold',
    'rock': 'sienna4',
    'psychic': 'pink',
}


class Stats(Enum):
    HP_RECT = 1
    HP_TEXT = 2
    NAME_TEXT = 3
    LEVEL_TEXT = 4
    EXP_RECT = 5
    EXP_TEXT = 6
    EXP_RATIO = 7
    HP = 8
    MAX_HP = 9


class GUIBattleView:
    """ A GUI view for pokemon battles."""

    def __init__(self, root: tk.Tk, player: Trainer,
                 enemy_pokemon: Pokemon) -> None:
        """ Constructor for GUIBattleView.

        Parameters:
            root (tk.Tk): The master window to put the widgets into.
            player (Trainer)): The player.
            enemy_pokemon (Pokemon): The enemy's current pokemon.
        """
        player_pokemon = player.get_current_pokemon()
        self._trainer = player

        root.title("Pokemon Battle Simulator")
        self._root = root

        self._battlefield = BattleField(root, player_pokemon, enemy_pokemon)
        self._battlefield.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self._dialogue = Dialogue(root)
        self._dialogue.pack(side=tk.TOP, expand=True, fill=tk.X)

    def play(self) -> None:
        """ Displays welcome message. """
        self.display_dialogue(ActionSummary(message='Welcome to Pokemon!'))

    def display_dialogue(self, dialogue: ActionSummary,
                         on_ok: Optional['function'] = None) -> None:
        """ Displays all dialogue messages in the dialogue list in order. User
            presses enter to move to seeing the next message. If on_ok is not
            None, it will be called once the user presses enter on the last
            message.

        Parameters:
            dialogue (list<str>): The dialogue to display in order.
            on_ok (function | None): If not None, this function will be executed
                                     when the user presses Return on the last
                                     message.
        """
        self._dialogue.add_dialogue(dialogue)
        self._update_dialogue(on_ok=on_ok)

    def set_action_handler(self, handler: 'function') -> None:
        """ Sets the handler to be called when an action has been requested.

        Parameters:
            handler (function): A reference to the function to be called once an
                                action has occurred.
        """
        self._dialogue.set_action_handler(handler)

    def _update_dialogue(self, on_ok: Optional['function'] = None,
                         switch_pokemon: bool = False) -> None:
        """ Updates the dialogue frame. This will move to the next dialogue to
            display if there is one, and will bind the on_ok to the Return
            button if one is provided. If there is not dialogue to display this
            function will display the action selector, unless switch_pokemon is
            set to True, in which case the Pokemon selector will be displayed.

        Parameters:
            on_ok (function | None): The callback to bind the Return key to.
            switch_pokemon (bool): True iff pokemon selector should be displayed.
        """
        pokemon = self._trainer.get_all_pokemon()
        moves = self._trainer.get_current_pokemon().get_move_info()
        inventory = self._trainer.get_inventory()

        self._dialogue.next_dialogue(pokemon, moves, inventory, on_ok=on_ok,
                                     switch_pokemon=switch_pokemon)

    def display_pokemon_selector(self) -> None:
        """ Displays the pokemon_selector. """
        self._update_dialogue(switch_pokemon=True)

    def update_battlefield(self, player_pokemon: Pokemon,
                           enemy_pokemon: Pokemon) -> None:
        """ Updates the battlefield to display information about the provided
            player pokemon and enemy pokemon.

        Parameters:
            player_pokemon (Pokemon): The player's current pokemon.
            enemy_pokemon (Pokemon): The enemy's current pokemon.
        """
        self._battlefield.draw(player_pokemon, enemy_pokemon)

    def exit(self):
        self._root.quit()


class BattleField(tk.Canvas):
    """ A Canvas on which the Pokemon battle is drawn. """

    BAR_WIDTH = 250
    STATS_BAR_COLOUR = 'floral white'

    def __init__(self, master: tk.Tk, player_pokemon: Pokemon,
                 enemy_pokemon: Pokemon, width: int = 600, height: int = 300,
                 **kwargs) -> None:
        """ Constructor for BattleField.

        Parameters:
            master (tk.Tk): The window to put this Canvas into.
            player_pokemon (Pokemon): The player's current pokemon.
            enemy_pokemon (Pokemon): The enemy's current pokemon.
            width (int): The width (in pixels) of the battlefield.
            height (int): The height (in pixels) of the battlefield.
        """
        super().__init__(master, width=width, height=height, **kwargs)
        self._width = width
        self._height = height

        # Draw background
        self.draw_background()

        # Draw (and remember) status info
        start_pos = self._width // 9 * 4, self._height // 2
        self._player_stats = self.init_stats(start_pos, player_pokemon)
        self._enemy_stats = self.init_stats((5, 0), enemy_pokemon,
                                            players_turn=False)
        self.draw(player_pokemon, enemy_pokemon)

    def draw_sprite(self, pokemon_name: str, flip: bool) -> ImageTk.PhotoImage:
        """ Returns the sprite image for the pokemon with the given name.

        Parameters:
            pokemon_name (str): The name of the pokemon to get the sprite for.
            flip (bool): True iff we are drawing the player's pokemon, so the
                         sprite will be flipped to face the enemy.

        Returns:
            (ImageTk.PhotoImage): The sprite to be drawn on the Canvas
        """
        size = min(self._width // 3, self._height)
        img = Image.open(f'images/{pokemon_name}.png')
        img = img.resize((size, size))
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        return ImageTk.PhotoImage(image=img)

    def draw_background(self) -> None:
        """ Draws the background of the battlefield. """
        img = Image.open('images/background.jpeg')
        img = img.resize((self._width, self._height), Image.ANTIALIAS)
        self._bg = ImageTk.PhotoImage(image=img)
        self.create_image(self._width // 2, self._height // 2, image=self._bg)

    def draw(self, player_pokemon: Pokemon, enemy_pokemon: Pokemon) -> None:
        """ Updates the battlefield view to reflect the current player pokemon
            and enemy pokemon.

        Parameters:
            player_pokemon (Pokemon): The player's current pokemon.
            enemy_pokemon (Pokemon): The enemy's current pokemon.
        """
        # Draw the player's pokemon's sprite
        player_pokemon_name = player_pokemon.get_name().lower()
        player_pokemon_location = self._width // 9 * 2, self._height // 4 * 3
        self._player_img = self.draw_sprite(player_pokemon_name, True)
        self.create_image(*player_pokemon_location, image=self._player_img)

        # Draw the enemy's pokemon's sprite
        enemy_pokemon_name = enemy_pokemon.get_name().lower()
        enemy_location = self._width - self._width // 9 * 2, self._height // 4
        self._enemy_img = self.draw_sprite(enemy_pokemon_name, False)
        self.create_image(enemy_location, image=self._enemy_img)

        # Update stat information
        player_start_position = self._width // 9 * 4, self._height // 2
        self.draw_stats(player_start_position, player_pokemon)
        enemy_start_position = (5, 0)
        self.draw_stats(enemy_start_position, enemy_pokemon, players_turn=False)

    def _animate_bar(self, _id: int, bbox: Tuple[int, int, int, int], inc: int,
                     end: int, direction: int = 1) -> None:
        """ Animates a rectangle to go from where it is now to end.

        Parameters:
            _id (int): The id of the rectangle to animate.
            bbox (tuple<int * 4>): The bbox of the rectangle at the start.
            inc (int): The increments (in pixels) to move the bar by each step.
            end (int): The pixel to end at (y_max in bbox).
            direction (int): 1 to move forwards, -1 to move backwards.
        """
        x_min, y_min, x_max, y_max = bbox
        x_max += (inc * direction)
        to_go = (end - x_max) * direction

        # If we've reached the end, show the resulting rectangle
        if to_go <= 0:
            self.coords(_id, x_min, y_min, end, y_max)
            return

        # Otherwise, take one step and call this method again
        bbox = x_min, y_min, x_max, y_max
        self.coords(_id, *bbox)
        self.after(10, lambda: self._animate_bar(_id, bbox, inc, end,
                                                 direction=direction))

    def _animate_text(self, _id: int, hp: int, end: int, inc: int, max_hp: int):
        """ Animates the hp text with given id to go from hp down to end.

        Parameters:
            _id (int): The id of the text to configure.
            hp (int): The current hp to draw.
            end (int): The hp to end at.
            inc (int): The increment to change by each time.
            max_hp (int): The maximum hp of the pokemon.
        """
        if hp <= end:
            self.itemconfig(_id, text=f'{int(end)}/{max_hp}')
            return
        self.itemconfig(_id, text=f'{int(hp)}/{max_hp}')
        self.after(10,
                   lambda: self._animate_text(_id, hp - inc, end, inc, max_hp))

    def _animate_hp(self, stats: Stats, new_health: int,
                    bbox: Tuple[int, int, int, int]) -> None:

        """ Animates the health information when a change occurs.

        Parameters:
            stats (Stats): The relevant pokemons stats information, before the
                           health change.
            new_health (int): The new health of the pokemon.
            bbox (tuple<int * 4>): The bbox of the rectangle (not using in-built
                                   bbox method for rectangles because it's too
                                   inaccurate).
        """
        hp, hp_max = new_health
        rect_id, text_id = stats[Stats.HP_RECT], stats[Stats.HP_TEXT]

        # Animate HP bar
        x_min, _, x_max, _ = bbox
        goal_x = x_min + (BattleField.BAR_WIDTH - 30) * (hp / hp_max)
        inc = max((x_max - goal_x) // 20, 1)
        self._animate_bar(rect_id, bbox, inc, goal_x, direction=-1)

        # Animate HP/max_HP text
        old_hp = stats[Stats.HP]
        text_inc = max((old_hp - hp) // 20, 1)
        self._animate_text(text_id, old_hp, hp, text_inc, hp_max)

    def _animate_exp(self, stats: Stats, new_exp: int,
                     bbox: Tuple[int, int, int, int]) -> None:
        """ Animates the exp information when a change occurs.

        Parameters:
            stats (Stats): The relevant pokemons stats information, before the
                           exp change.
            new_exp (int): The new exp of the pokemon.
            bbox (tuple<int * 4>): The bbox of the rectangle (not using in-built
                                   bbox method for rectangles because it's too
                                   inaccurate).
        """
        start_x, _, end_x, _ = bbox
        goal_x = start_x + 230 * new_exp
        inc = max((goal_x - end_x) // 20, 1)
        self._animate_bar(stats[Stats.EXP_RECT], bbox, inc, goal_x)

    def _draw_initial_health(self, start_pos: Tuple[int, int], pokemon: Pokemon,
                             stats: Stats) -> None:
        """ Draw and log initial health information.

        Parameters:
            start_pos (tuple<int, int>): The top left pixel of the stats box.
            pokemon (Pokemon): The pokemon to draw the health of.
            stats (Stats): The stat information for this pokemon.
        """
        start_x, start_y = start_pos
        stat_bar_width = (self._width // 9) * 5
        hp_x = start_x + stat_bar_width // 5
        hp_y = start_y + 55

        # Background HP background bar and text
        self.create_rectangle(hp_x, hp_y, hp_x + BattleField.BAR_WIDTH,
                              hp_y + 20,
                              fill='black')
        self.create_text(hp_x + 15, hp_y + 10, fill='gold', text='HP')

        # Create the green bar and HP/max_HP text to display current health info
        hp, hp_max = pokemon.get_health(), pokemon.get_max_health()
        stats[Stats.HP] = hp
        stats[Stats.MAX_HP] = hp_max

        hp_bar_x = hp_x + 30
        hp_bar_y = hp_y + 2
        hp_width = (BattleField.BAR_WIDTH - 31) * (hp / hp_max)
        bbox = hp_bar_x, hp_bar_y, hp_bar_x + hp_width, hp_bar_y + 16
        stats[Stats.HP_RECT] = self.create_rectangle(bbox, fill='green')
        text_pos = hp_x + 30, hp_y + 35
        hp_text = f'{pokemon.get_health()}/{pokemon.get_max_health()}'
        stats[Stats.HP_TEXT] = self.create_text(text_pos, text=hp_text)

    def _draw_initial_exp(self, start_pos, pokemon: Pokemon, stats):
        """ Draw and log initial xp information.

        Parameters:
            start_pos (tuple<int, int>): The top left pixel of the stats box.
            pokemon (Pokemon): The pokemon to draw the exp of.
            stats (Stats): The stat information for this pokemon.
        """
        start_x, start_y = start_pos
        exp_ratio = pokemon.get_experience() / pokemon.get_next_level_experience_requirement()
        stats[Stats.EXP_RATIO] = exp_ratio
        stat_bar_width = (self._width // 9) * 5

        # Create background box for exp info
        xp_start_x = start_x + 10
        xp_end_x = start_x + stat_bar_width - 10
        xp_start_y = (start_y + self._height // 2) - 20
        bg_bbox = xp_start_x, xp_start_y, xp_end_x, xp_start_y + 10
        self.create_rectangle(bg_bbox, fill=BattleField.STATS_BAR_COLOUR,
                              width=2)

        # Draw exp bar proportional to amount of exp
        width = (xp_end_x - xp_start_x) * exp_ratio
        bbox = xp_start_x, xp_start_y, xp_start_x + width, xp_start_y + 10
        stats[Stats.EXP_RECT] = self.create_rectangle(bbox, fill='blue',
                                                      width=2)

    def init_stats(self, start_pos: Tuple[int, int], pokemon: Pokemon,
                   players_turn: bool = True) -> None:
        """ Draw the stats (the white box with hp, level, name, exp info) for
            one pokemon at the start. Logs important information about what is
            being displayed and the id's of elements that may be configured
            later.

        Parameters:
            start_pos (tuple<int, int>): The pixel of the top left corner.
            pokemon (Pokemon): The pokemon being displayed.
            players_turn (bool): True iff it's the player's pokemon.
        """
        stats = {}

        start_x, start_y = start_pos
        stat_bar_width = (self._width // 9) * 5

        # Draw background rectangle
        bottom_y = (start_y + self._height // 2) - 20
        if not players_turn:
            # enemy, so can be shorter
            bottom_y -= 20
        bbox = start_x, start_y + 20, start_x + stat_bar_width, bottom_y
        self.create_rectangle(bbox, fill=BattleField.STATS_BAR_COLOUR, width=2)

        # Draw pokemon name and level
        name = f'{pokemon.get_name().upper()}'
        level = f'Lv{pokemon.get_level()}'
        stats[Stats.NAME_TEXT] = self.create_text(start_x + 40, start_y + 35,
                                                  text=name)
        stats[Stats.LEVEL_TEXT] = self.create_text(
            start_x + stat_bar_width - 35,
            start_y + 35, text=level)

        # Draw health information
        self._draw_initial_health(start_pos, pokemon, stats)

        # Draw exp information if this is the players pokemon
        if players_turn:
            self._draw_initial_exp(start_pos, pokemon, stats)

        return stats

    def draw_stats(self, start_pos: Tuple[int, int], pokemon: Pokemon,
                   players_turn: bool = True) -> None:
        """ Configure the existing elements on the battlefield to reflect the
            state of the game now.


        Parameters:
            start_pos (tuple<int, int>): The top left pixel of the stats box.
            pokemon (Pokemon): The pokemon whose stats are being drawn.
            players_turn (bool): True iff the pokemon belongs to the player.
        """
        stats = self._player_stats if players_turn else self._enemy_stats
        start_x, start_y = start_pos

        self.itemconfig(stats[Stats.NAME_TEXT],
                        text=f'{pokemon.get_name().upper()}')
        self.itemconfig(stats[Stats.LEVEL_TEXT],
                        text=f'Lv{pokemon.get_level()}')

        # If the health information has changed, animate it to update
        hp, hp_max = pokemon.get_health(), pokemon.get_stats().get_max_health()
        old_hp, old_hp_max = stats[Stats.HP], stats[Stats.MAX_HP]

        if hp != old_hp or hp_max != old_hp_max:
            # Health information has changed since last drawn, so update it
            hp_x_start = start_x + self._width // 9 + 30
            hp_x_end = self.bbox(stats[Stats.HP_RECT])[2]
            bbox = hp_x_start, start_y + 57, hp_x_end, start_y + 73
            self._animate_hp(stats, (hp, hp_max), bbox)

            # Update our record of what we're displaying
            stats[Stats.HP] = hp
            stats[Stats.MAX_HP] = hp_max

        if players_turn:
            exp_ratio = pokemon.get_experience() / pokemon.get_next_level_experience_requirement()
            old_exp_ratio = stats[Stats.EXP_RATIO]
            if exp_ratio != old_exp_ratio:
                # Something about the exp bar for the player has changed so update
                xp_start_x = start_x + 10
                xp_start_y = start_y + self._height // 2 - 20
                hp_end_x = self.bbox(stats[Stats.EXP_RECT])[2]
                bbox = xp_start_x, xp_start_y, hp_end_x, xp_start_y + 10
                self._animate_exp(stats, exp_ratio, bbox)
                stats[Stats.EXP_RATIO] = exp_ratio


class Dialogue(tk.Frame):
    """ A dialogue box to display text and action information. """

    MOVES_COLOUR = 'floral white'
    ACTION_COLOURS = {
        'BAG': 'goldenrod',
        'FIGHT': 'orange red',
        'POKéMON': 'forest green',
        'RUN': 'RoyalBlue1',
    }

    def __init__(self, master: tk.Tk, **kwargs) -> None:
        """ Constructor for Dialogue.

        Parameters:
            master (tk.Tk): The window to place this frame into.
        """
        super().__init__(master, **kwargs)
        self._master = master
        self._dialogue = []
        self._handler = None

    def set_action_handler(self, handler: 'function') -> None:
        """ Sets the action handler to be called when an action is registered
            on dialogue widgets.

        Parameters:
            handler (function): A reference to the function to be called when an
                                action is registered.
        """
        self._handler = handler

    def add_dialogue(self, dialogue: ActionSummary) -> None:
        """ Adds the strings in dialogue to the dialogue to be displayed to the
            user. Does not display until update is called.

        Parameters:
            dialogue (ActionSummary): Dialogue strings to add.
        """
        self._dialogue.extend(dialogue.get_messages())

    def clear_frame(self):
        """ Clears the Dialogue frame. """
        for widgets in self.winfo_children():
            widgets.destroy()

    def display_text(self, text: str) -> None:
        """ Displays the given text in the dialogue box.

        Parameters:
            text (str): The text to display.
        """
        lbl = tk.Label(self, height=7, bg=Dialogue.MOVES_COLOUR,
                       relief=tk.GROOVE, text=text)
        lbl.pack(expand=True, fill=tk.BOTH)

    def acknowledge(self, pokemon: List[Pokemon], moves: List[Move],
                    inventory: Dict[Item, int], on_ok: Optional['function']):
        """ Removes the most recently displayed message and updates the dialogue.

        Parameters:
            pokemon (list<Pokemon>): All pokemon the player has.
            moves (list<Move>): The moves of the current pokemon.
            inventory (dict<item, int>): The player's current inventory.
            on_ok (function | None): If provided, this function will be executed
                                     when all dialogues have been acknowledged.
        """
        if on_ok is not None and len(self._dialogue) == 1:
            on_ok()
        if len(self._dialogue) > 0:
            self._dialogue.pop(0)
        self.next_dialogue(pokemon, moves, inventory, on_ok=on_ok)

    def next_dialogue(self, pokemon: List[Pokemon], moves: List[Move],
                      inventory: Dict[Item, int],
                      on_ok: Optional['function'] = None,
                      switch_pokemon: bool = False):
        """ Update the dialogue to display the next thing. This will be the next
            dialogue message if one exists. If no dialogue is queued, the action
            selector will be displayed unless switch_pokemon is set to True, in
            which case the pokemon selector will be displayed.

        Parameters:
            pokemon (list<Pokemon>): All pokemon the player has.
            moves (list<Move>): The moves of the current pokemon.
            inventory (dict<item, int>): The player's current inventory.
            on_ok (function | None): If provided, this function will be executed
                                     when all dialogues have been acknowledged.
        """
        self.clear_frame()
        if len(self._dialogue) > 0:
            self.display_text(self._dialogue[0])
            command = lambda e: self.acknowledge(pokemon, moves, inventory,
                                                 on_ok=on_ok)
            self._master.bind('<Return>', command)
        elif switch_pokemon:
            self.display_pokemon_selector(pokemon)
        else:
            self.display_action_selector(pokemon, moves, inventory)

    def display_action_selector(self, pokemon: List[Pokemon], moves: List[Move],
                                inventory: Dict[Item, int]) -> None:
        """ Prompts user for action.

        Parameters:
            pokemon (list<Pokemon>): All pokemon the player has.
            moves (list<Move>): All actions the player's current pokemon has.
            inventory (dict<Item, int>): The player's inventory.
        """
        self.columnconfigure(2, weight=0)

        tk.Label(self, text='What will you do?').pack(side=tk.LEFT,
                                                      fill=tk.BOTH)

        # Outer frame for action labels
        action_frame = tk.Frame(self)
        action_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)

        # Construct, display, and bind each action button
        self._display_action(action_frame, 'FIGHT', 0,
                             lambda e: self.display_moves(moves))
        self._display_action(action_frame, 'BAG', 1,
                             lambda e: self.display_bag(inventory))
        self._display_action(action_frame, 'POKéMON', 2,
                             lambda e: self.display_pokemon_selector(pokemon))
        self._display_action(action_frame, 'RUN', 3,
                             lambda e: self._handler(Flee()))

    def _display_action(self, outer_frame: tk.Frame, name: str, idx: int,
                        command: 'function') -> None:
        """ Construct, displays, and binds a single action.

        Parameters:
            outer_frame (tk.Frame): The frame to put the action label in.
            name (str): The name of the action.
            idx (int): The index of the action label (clockwise from top left).
            command (function): The function to bind left click to.
        """
        bg = Dialogue.ACTION_COLOURS.get(name)
        button = tk.Label(outer_frame, text=name, bd=2, bg=bg, relief=tk.GROOVE,
                          height=3, fg='white')
        button.grid(row=idx // 2, column=idx % 2, sticky='nesw')
        button.bind('<Button-1>', command)

    def display_bag(self, inventory: Dict[Item, int]) -> None:
        """ Displays the item sin the bag. Not implemented yet.

        Parameters:
            inventory (dict<Item, int>): The player's inventory.
        """
        if len(inventory) == 0:
            self.add_dialogue(ActionSummary("No items in inventory."))
            self.next_dialogue()
        self.clear_frame()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        visible_items = list(inventory.items())[:4]
        for i, (item, uses) in enumerate(visible_items):
            text = f'{item.get_name()}\nUses: {uses}'
            bg = TYPE_COLOURS.get('electric')
            lbl = tk.Label(self, text=text, bg=bg, relief=tk.GROOVE, height=3)
            lbl.grid(row=i // 2, column=i % 2, sticky='ew')
            lbl.bind('<Button-1>',
                     lambda e, i=i: self._handler(visible_items[i][0]))

    def display_pokemon_selector(self, pokemons: List[Pokemon]) -> None:
        """ Displays the pokemon selector.

        Parameters:
            pokemons (list<Pokemon>): All pokemon the player has.
        """
        self.clear_frame()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        for i, pokemon in enumerate(pokemons):
            row = i // 3
            col = i % 3
            colour = TYPE_COLOURS.get(pokemon.get_element_type())
            if pokemon.has_fainted():
                colour = 'light grey'
            pkm_lbl = tk.Label(self, text=pokemon.get_name(), height=3,
                               bg=colour, relief=tk.GROOVE)
            pkm_lbl.grid(row=row, column=col, sticky='nesw')
            pkm_lbl.bind('<Button-1>',
                         lambda e, i=i: self._handler(SwitchPokemon(i)))

    def display_moves(self, moves: List[Move]) -> None:
        """ Displays all available moves for the current pokemon.

        Parameters:
            moves (list<Move>): The moves available.
        """
        self.clear_frame()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        for i, move_info in enumerate(moves):
            move, uses = move_info
            text = f'{move.get_name()}\nPP: {uses}/{move.get_max_uses()}'
            bg = TYPE_COLOURS.get(move.get_element_type())
            lbl = tk.Label(self, text=text, bg=bg, relief=tk.GROOVE, height=3)
            lbl.grid(row=i // 2, column=i % 2, sticky='ew')
            lbl.bind('<Button-1>', lambda e, i=i: self._handler(moves[i][0]))

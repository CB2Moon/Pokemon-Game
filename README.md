# Pokemon-Game

A simple python Pokémon game for fun.

## Interface

![](https://user-images.githubusercontent.com/95510991/144701409-94069b29-9475-486c-a120-6cfdc54bde13.png)

## Introduction

Pokémon battles take place between two trainers, say, Ash and Brock. Both Ash and Brock have a roster of (at most) six Pokémon, that battle until all Pokémon in one roster have fainted. Trainers  
can only ever have one Pokémon on the battle field while the rest are in reserve.

Battles are turn-based. Each turn, a trainer may select an action to perform. These actions have priority, and are enacted in order of that priority.

If a Pokémon faints in battle, the only valid action its trainer may take, is to switch it out for another non-fainted Pokémon from the roster, presuming one exists. If all Pokémon in a roster have fainted, the trainer whose Pokémon are left standing is the winner, and the battle ends.

*   To play the game, run _**game.py**_.
    *   Click the colored _`buttons`_ to make actions.
    *   Press _`Enter`_ to go next.
*   You can change the data of Pokémon, moves and items as you like in _**data.py**_
*   _**pokemon\_game.py**_ and _**pokemon\_game\_support.py**_ are the engine of this game.
*   _**battle\_view.py**_ is used to draw the game.

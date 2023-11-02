import random

import logging
from logging import debug, info
from typing import Callable, List

import dominionator.cards as dmc

#
START_CARDS = tuple(3 * [dmc.EstateCard] + 7 * [dmc.CopperCard])
TURN_DRAW = 5


class Player(object):
    # Class for managing
    # This class is not an "agent" which makes decisions or affects other parts of the game.
    # Rather, this class is for tracking the player's state, and cards under their control
    def __init__(self, name: str, start_cards: List[dmc.Card]):
        self.name = name

        # Deck & card status
        self.hand = []
        self.deck = []
        self.discard = []
        self.inplay = []

        # Turn resources
        self.coins = 0
        self.actions = 0

        # Set by the game engine running a count
        self.victory_points = 0

        # This will start the game by shuffling all cards and drawing 5
        self.discard = start_cards
        self.clean_up()

    def _log(self, logfn: Callable[[str], None], message: str):
        logfn(f"[{self.name}]: {message}")

    def _shuffle_if_needed(self, n_cards: int):
        if len(self.deck) < n_cards:
            self._log(debug, f"deck size check. Has {len(self.deck)} needs {n_cards}")
            self._log(info, "shuffles discard under deck")
            random.shuffle(self.discard)
        self.deck += self.discard
        self.discard = []

    def draw(self, n_cards: int):
        self._shuffle_if_needed(n_cards)
        self._log(info, f"draws {n_cards} cards")
        self.hand += self.deck[0:n_cards]
        self.deck = self.deck[n_cards:]

    def play_from_hand(self, hand_i: int) -> dmc.Card:
        # Plays a card from the players hand. It assumes the index of the card has already been
        # selected via another method. Returns a card for the GameState to handle.
        played_card = self.hand.pop(hand_i)
        self.inplay += [played_card]
        return played_card

    def clean_up(self):
        self._log(info, f"cleans up")

        # Put hand and cards in play into the discard pile
        self.discard += self.hand
        self.hand = []
        self.discard += self.inplay
        self.inplay = []

        # Reset and draw 5 cards
        self.actions = 1
        self.coins = 0
        self.draw(TURN_DRAW)

    def all_cards(self):
        return self.hand + self.deck + self.discard + self.inplay

    def __str__(self) -> str:
        player_str = (
            f"<{self.name}> @{self.actions} ${self.coins} ^{self.victory_points}\n"
            f"inplay: {self.inplay} hand: {self.hand}\n"
            f"deck: -->{self.deck}\n"
            f"discard: {self.discard}<--"
        )
        return player_str


class BoardState(object):

    def __init__(self):
        logging.info("[Board]: Initialised")
        self.players = [
            Player("PlayerOne", [CardClass() for CardClass in START_CARDS]),
            Player("PlayerTwo", [CardClass() for CardClass in START_CARDS])
        ]

        self.supply = {
            'Copper': [dmc.CopperCard()] * 30,
            'Estate': [dmc.EstateCard()] * 8,
        }

        self.trash = []

    def __str__(self):
        game_str = f"<Supply>\n{self.supply}\n"
        for player in self.players:
            game_str += f"{str(player)}\n"
        return game_str

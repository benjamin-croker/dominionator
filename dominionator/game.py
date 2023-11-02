import random

from logging import debug, info
from typing import Callable, List, Type

import cards

#
START_CARDS = tuple(3 * [cards.EstateCard] + 7 * [cards.Copper])
TURN_DRAW = 5


class Board(object):
    pass


class Player(object):
    # Class for managing
    # This class is not an "agent" which makes decisions or affects other parts of the game.
    # Rather, this class is for tracking the player's state, and cards under their control
    def __init__(self, name: str, start_cards: List[cards.Card]):
        self.name = name

        # Deck & card status
        self.hand = []
        self.deck = []
        self.discard = []
        self.inplay = []

        # Turn resources
        self.coins = 0
        self.actions = 0

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

    def draw(self, n_cards: int):
        self._shuffle_if_needed(n_cards)
        self._log(info, f"draws {n_cards} cards")
        self.hand += self.deck[0:n_cards]
        self.deck = self.deck[n_cards:]

    def play_from_hand(self, hand_i: int) -> cards.Card:
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


class GameState(object):
    pass

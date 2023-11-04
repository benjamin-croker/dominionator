import random

import logging
from logging import debug, info
from typing import Callable, List
# Don't import the parent cards package, as that refers to this module
# Only import the cardlist itself, which has no dependencies
import dominionator.cards.cardlist as dmcl

START_CARDS = tuple(3 * [dmcl.EstateCard] + 7 * [dmcl.CopperCard])
TURN_DRAW = 5


class Player(object):
    # Class for managing
    # This class is not an "agent" which makes decisions or affects other parts of the game.
    # Rather, this class is for tracking the player's state, and cards under their control
    def __init__(self, name: str, index: int, start_cards: List[dmcl.Card]):
        self.name = name
        self.index = index

        # Deck & card status
        self.hand = []
        self.deck = []
        self.discard = []
        self.inplay = []

        # Turn resources
        self.coins = 0
        self.actions = 0
        self.buys = 0

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

    def draw_from_deck(self, n_cards: int):
        self._shuffle_if_needed(n_cards)
        self._log(info, f"draws {n_cards} cards")
        self.hand += self.deck[0:n_cards]
        self.deck = self.deck[n_cards:]

    def play_from_hand(self, shortname: str) -> dmcl.Card:
        # Plays a card from the players hand. It assumes the index of the card
        # selected via another method. Returns a card for the GameState to handle.

        # Selects a card with the selected name. This method is used as it will
        # make interfacing with an automated agent easier, by reducing the action
        # space to selecting one of the kingdom cards to play, instead of selecting
        # an index from a hand which could be an arbitrary size.

        hand_i = [card.shortname for card in self.hand].index(shortname)
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
        self.buys = 1
        self.draw_from_deck(TURN_DRAW)

    def all_cards(self):
        return self.hand + self.deck + self.discard + self.inplay

    def __str__(self) -> str:
        player_str = (
            f"<{self.name}> @{self.actions} ${self.coins} &{self.buys} ^{self.victory_points}\n"
            f"inplay: {self.inplay} hand: {self.hand}\n"
            f"deck: -->{self.deck}\n"
            f"discard: {self.discard}<--"
        )
        return player_str


class BoardState(object):

    def __init__(self):
        logging.info("[Board]: Initialised")
        self.players = [
            Player("PlayerOne", 0, [CardClass() for CardClass in START_CARDS]),
            Player("PlayerTwo", 1, [CardClass() for CardClass in START_CARDS])
        ]
        self.active_player_i = 0

        self.supply = {
            dmcl.CopperCard.shortname: [dmcl.CopperCard()] * 30,
            dmcl.EstateCard.shortname: [dmcl.EstateCard()] * 8,
            dmcl.MilitiaCard.shortname: [dmcl.MilitiaCard()] * 10,
        }

        self.trash = []

    def active_player(self):
        return self.players[self.active_player_i]

    def other_players(self, player: Player):
        # returns other players in clockwise play order
        i = player.index
        return self.players[i + 1:] + self.players[:i]

    def __str__(self):
        game_str = "<Supply>\n"
        for k, v in self.supply.items():
            game_str += f"{k}:{v}\n"
        for player in self.players:
            if player.index == self.active_player_i:
                game_str += '*'
            game_str += f"{str(player)}\n"
        return game_str

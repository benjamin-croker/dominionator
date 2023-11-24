from typing import Set
import logging
import numpy as np

import dominionator.board as dmb
import dominionator.player as dmp
import dominionator.agents.base as dma_base

NCARDS = 33
# Define order of cards, used consistently in each part of the vector
CARD_OFFSET = {
    '$1': 0,
    '$2': 1,
    # ...
    'AR': 32  # Artisan
}

# These are all multiples of NCARDS
SUPPLY_OFFSET = 0
TRASH_OFFSET = 1

PLAYER1_DECK_OFFSET = 2
PLAYER1_HAND_OFFSET = 3
PLAYER1_INPLAY_OFFSET = 4
PLAYER1_DISCARD_OFFSET = 5

PLAYER2_DECK_OFFSET = 6
PLAYER2_HAND_OFFSET = 7
PLAYER2_INPLAY_OFFSET = 8
PLAYER2_DISCARD_OFFSET = 9

LOCATION_OFFSET = {
    'SUPPLY': 0,
    'TRASH': 1,
    'PLAYER1_DECK': 2,
    'PLAYER1_HAND': 3,
    'PLAYER1_INPLAY': 4,
    'PLAYER1_DISCARD': 5,
    'PLAYER2_DECK': 6,
    'PLAYER2_HAND': 7,
    'PLAYER2_INPLAY': 8,
    'PLAYER2_DISCARD': 9
}

VECTOR_SIZE = 10 * NCARDS


class MlAgent(dma_base.Agent):

    def __init__(self):
        super().__init__()
        self._state = np.zeros(VECTOR_SIZE)

    def _reset_state_vector(self):
        # faster than reallocating (hopefully?)
        self._state = self._state * 0

    def _add_state_count(self, location: str, shortname: str, card_count: int = 1):
        self._state[NCARDS * LOCATION_OFFSET[location] + CARD_OFFSET[shortname]] += card_count

    def _game_state_vector(self, board: dmb.BoardState):
        # Create a vector with the counts of all the cards in the different locations:
        # - In supply
        # - In trash
        # - Player 1 deck, hand, inplay, discard
        # - Player 2 deck, hand, inplay, discard
        # There are 26 kingdom and 7 basic = 33 unique cards in total
        # There are 10 locations in total
        # TODO: the Library will need another "set aside" location, as well as
        #   a temporary "in flight" location where the card has been drawn and
        #   the player is deciding to place in hand or set aside

        self._reset_state_vector()

        # 1: Supply
        [self._add_state_count('SUPPLY', shortname, len(cards))
         for shortname, cards in board.supply.items()]
        # 2: Trash
        [self._add_state_count('TRASH', card.shortname)
         for card in board.trash]
        # 3: Player 1 deck
        [self._add_state_count('PLAYER1_DECK', card.shortname)
         for card in board.players[0].deck]

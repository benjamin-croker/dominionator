import logging
import dominionator.board as dmb
import dominionator.cards.cardlist as dmcl
from typing import Callable

# Type for functions in dictionaries above
CardFunction = Callable[[dmb.Player, dmb.BoardState], None]


def _play_copper(player: dmb.Player, _board: dmb.BoardState):
    # Board state is unaffected besides the player
    player.coins += 1


def _play_militia(player: dmb.Player, board: dmb.BoardState):
    raise NotImplementedError()


_PLAYABLE_CARD_LIST = {
    dmcl.CopperCard.shortname: _play_copper,
    dmcl.MilitiaCard.shortname: _play_militia,
}


def _count_estate(player: dmb.Player, _board: dmb.BoardState):
    # Estate has constant VP
    player.victory_points += 1


_COUNTABLE_CARD_LIST = {
    dmcl.EstateCard.shortname: _count_estate
}


def get_play_card_fn(shortname: str) -> CardFunction:
    # Deliberately let this raise an exception
    return _PLAYABLE_CARD_LIST[shortname]


def get_count_card_fn(shortname: str) -> CardFunction:
    return _COUNTABLE_CARD_LIST[shortname]

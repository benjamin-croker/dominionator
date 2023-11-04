import logging
import dominionator.board as dmb
import dominionator.cards.cardlist as dmcl
from typing import Callable

# Type for functions in dictionaries above
CardFunction = Callable[[dmb.Player, dmb.BoardState], None]


# --------- Victory ---------
def _count_estate(player: dmb.Player, _board: dmb.BoardState):
    # Estate has constant VP
    player.victory_points += 1


def _count_duchy(player: dmb.Player, _board: dmb.BoardState):
    # Estate has constant VP
    player.victory_points += 3


def _count_province(player: dmb.Player, _board: dmb.BoardState):
    # Estate has constant VP
    player.victory_points += 6


_COUNTABLE_CARD_LIST = {
    dmcl.EstateCard.shortname: _count_estate,
    dmcl.DuchyCard.shortname: _count_duchy,
    dmcl.ProvinceCard.shortname: _count_province
}


def get_play_card_fn(shortname: str) -> CardFunction:
    # Deliberately let this raise an exception
    return _PLAYABLE_CARD_LIST[shortname]


def get_count_card_fn(shortname: str) -> CardFunction:
    return _COUNTABLE_CARD_LIST[shortname]


# --------- Treasures ---------
def _play_copper(player: dmb.Player, _board: dmb.BoardState):
    # Board state is unaffected besides the player
    player.coins += 1


def _play_silver(player: dmb.Player, _board: dmb.BoardState):
    # The first silver played generates another $1 for every merchant played
    player.coins += 2
    # The currently playing silver is already "in play"
    player.coins += (
            int(player.count_inplay(dmcl.SilverCard.shortname) == 1) *
            player.count_inplay(dmcl.MerchantCard.shortname)
    )


def _play_gold(player: dmb.Player, _board: dmb.BoardState):
    # Board state is unaffected besides the player
    player.coins += 3


# --------- Actions ---------
def _play_militia(_player: dmb.Player, _board: dmb.BoardState):
    raise NotImplementedError()


def _play_merchant(player: dmb.Player, _board: dmb.BoardState):
    player.draw_from_deck(1)
    player.actions += 1
    # The effect where +$1 is granted the first time a silver is played
    # is handled in the routine for playing silver


_PLAYABLE_CARD_LIST = {
    dmcl.CopperCard.shortname: _play_copper,
    dmcl.SilverCard.shortname: _play_silver,
    dmcl.GoldCard.shortname: _play_gold,
    dmcl.MilitiaCard.shortname: _play_militia,
    dmcl.MerchantCard.shortname: _play_merchant,
}

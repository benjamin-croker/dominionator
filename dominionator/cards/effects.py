import dominionator.board as dmb
import dominionator.agents as dma
import dominionator.cards.cardlist as dmcl
from typing import Callable, List, Dict

# Type for functions in dictionaries above
CardFunction = Callable[
    [dmb.Player, dmb.BoardState, Dict[str, dma.Agent]], None
]


# --------- Victory ---------
def _count_curse(player: dmb.Player,
                  _board: dmb.BoardState,
                  _agents: Dict[str, dma.Agent]):
    # Curse has constant VP
    player.victory_points -= 1


def _count_estate(player: dmb.Player,
                  _board: dmb.BoardState,
                  _agents: Dict[str, dma.Agent]):
    # Estate has constant VP
    player.victory_points += 1


def _count_duchy(player: dmb.Player,
                 _board: dmb.BoardState,
                 _agents: Dict[str, dma.Agent]):
    # Estate has constant VP
    player.victory_points += 3


def _count_province(player: dmb.Player,
                    _board: dmb.BoardState,
                    _agents: Dict[str, dma.Agent]):
    # Estate has constant VP
    player.victory_points += 6


_COUNTABLE_CARD_LIST = {
    dmcl.CurseCard.shortname: _count_curse,
    dmcl.EstateCard.shortname: _count_estate,
    dmcl.DuchyCard.shortname: _count_duchy,
    dmcl.ProvinceCard.shortname: _count_province
}


def get_count_card_fn(shortname: str) -> CardFunction:
    return _COUNTABLE_CARD_LIST[shortname]


# --------- Treasures ---------
def _play_copper(player: dmb.Player,
                 _board: dmb.BoardState,
                 _agents: Dict[str, dma.Agent]):
    # Board state is unaffected besides the player
    player.coins += 1


def _play_silver(player: dmb.Player,
                 _board: dmb.BoardState,
                 _agents: Dict[str, dma.Agent]):
    # The first silver played generates another $1 for every merchant played
    player.coins += 2
    # The currently playing silver is already "in play"
    player.coins += (
            int(player.count_inplay(dmcl.SilverCard.shortname) == 1) *
            player.count_inplay(dmcl.MerchantCard.shortname)
    )


def _play_gold(player: dmb.Player,
               _board: dmb.BoardState,
               _agents: Dict[str, dma.Agent]):
    # Board state is unaffected besides the player
    player.coins += 3


# --------- Actions ---------

def _check_attack_reaction(player: dmb.Player,
                           board: dmb.BoardState,
                           agents: Dict[str, dma.Agent]) -> List[dmb.Player]:
    # Allows other players to react to an attack, and returns a list of players
    # which are affected.
    other_players = board.get_other_players(player)

    # TODO: expansions will need to handle revealing multiple cards for different effects.
    # This could include playing the card.
    other_player_revealed = [
        agents[p.name].get_input_reveal_card_from_hand(
            p, board, allowed=list(p.get_attack_reaction_cards()) + [dma.NO_SELECT]
        ) for p in other_players
    ]

    # Return players who can be attacked - i.e. did not reveal a moat
    return [
        p for p, revealed in zip(other_players, other_player_revealed)
        if revealed not in [dmcl.MoatCard.shortname]
    ]


def _play_militia(player: dmb.Player,
                  board: dmb.BoardState,
                  agents: Dict[str, dma.Agent]):
    player.coins += 2
    for attacked_player in _check_attack_reaction(player, board, agents):
        while len(attacked_player.hand) > 3:
            selected = agents[attacked_player.name].get_input_discard_card_from_hand(
                attacked_player, board, list(attacked_player.get_discardable_cards())
            )
            attacked_player.discard_from_hand(selected)


def _play_merchant(player: dmb.Player,
                   _board: dmb.BoardState,
                   _agents: Dict[str, dma.Agent]):
    player.draw_from_deck(1)
    player.actions += 1
    # The effect where +$1 is granted the first time a silver is played
    # is handled in the routine for playing silver


def _play_moat(player: dmb.Player,
               _board: dmb.BoardState,
               _agents: Dict[str, dma.Agent]):
    # This is the action part of the card, not the reaction to attacks
    player.draw_from_deck(2)


_PLAYABLE_CARD_LIST = {
    dmcl.CopperCard.shortname: _play_copper,
    dmcl.SilverCard.shortname: _play_silver,
    dmcl.GoldCard.shortname: _play_gold,
    dmcl.MilitiaCard.shortname: _play_militia,
    dmcl.MerchantCard.shortname: _play_merchant,
    dmcl.MoatCard.shortname: _play_moat,
}


def get_play_card_fn(shortname: str) -> CardFunction:
    # Deliberately let this raise an exception
    return _PLAYABLE_CARD_LIST[shortname]

import dominionator.board as dmb
import dominionator.cards as dmc


def _count_estate(player: dmb.Player, _board_state: dmb.BoardState):
    # Estate has constant VP
    player.victory_points += 1


CARD_LIST = {
    'Estate': _count_estate
}


def count_vp(card: dmc.Card, player: dmb.Player, board_state: dmb.BoardState):
    _fn = CARD_LIST.get(card.name)
    if _fn is None:
        raise ValueError(f"No instructions for {card.name}")
    return _fn(player, board_state)

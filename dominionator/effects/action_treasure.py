import dominionator.board as dmb
import dominionator.cards as dmc


def _play_copper(player: dmb.Player, _board_state: dmb.BoardState):
    # Board state is unaffected besides the player
    player.coins += 1


CARD_LIST = {
    'Copper': _play_copper
}


def play(card: dmc.Card, player: dmb.Player, board_state: dmb.BoardState):
    _fn = CARD_LIST.get(card.name)
    if _fn is None:
        raise ValueError(f"No instructions for {card.name}")
    return _fn(player, board_state)

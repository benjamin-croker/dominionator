from ..game import Player
from ..game import GameState


class Card(object):
    # Design principles for the cards:
    # - Cards don't move themselves
    # - Cards 'operate' on the game as a whole

    name = ""
    shortname = ""

    # To be overwritten by child classes
    cost = 0

    # Card type
    is_action = False
    is_reaction = False
    is_treasure = False
    is_attack = False
    is_victory = False

    def play(self, origin_player: Player, game_state: GameState):
        # In general, cards can affect anything in the game, so the entire game state
        # is passed in. The player who played the card is also necessary to know.
        raise NotImplementedError("play() must be implemented by child class")

    def calc_vpoints(self, origin_player: Player, game_state: GameState):
        raise NotImplementedError("calc_vpoints() must be implemented by child class")
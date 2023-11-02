from .card import Card
from ..game import Player, GameState


class EstateCard(Card):
    name = "Estate"
    shortname = "E1"
    cost = 2
    is_victory = True

    def play(self, origin_player: Player, game_state: GameState):
        raise ValueError(f"{self.name} can not be played")

    def calc_vpoints(self, origin_player: Player, game_state: GameState):
        return 1


class Copper(Card):
    name = "Copper"
    shortname = "$1"
    cost = 0
    is_treasure = True

    def play(self, origin_player: Player, game_state: GameState):


    def calc_vpoints(self, origin_player: Player, game_state: GameState):
        return 0

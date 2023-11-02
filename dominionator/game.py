import logging

import dominionator.board as dmb
import dominionator.effects.victory as fxv
import dominionator.effects.action_treasure as fxc


class Game(object):
    def __init__(self):
        logging.info("[Game]: Initialised")
        self.board = dmb.BoardState()
        self.recount_vp()

    def recount_vp(self):
        [
            fxv.count_vp(card, player, self.board)
            for player in self.board.players
            for card in player.all_cards()
            if card.is_victory
        ]

    def __str__(self):
        return str(self.board)

import logging

import dominionator.board as dmb
import dominionator.cards.effects as dmce
import dominionator.cards.cardlist as dmcl


class Game(object):
    def __init__(self):
        logging.info("[Game]: Initialised")
        self.board = dmb.BoardState()
        self.recount_vp()

    def count_vp(self, card: dmcl.Card, player: dmb.Player):
        fn = dmce.get_count_card_fn(card.shortname)
        fn(player, self.board)

    def play_action_treasure(self, card: dmcl.Card, player: dmb.Player):
        fn = dmce.get_play_card_fn(card.shortname)
        fn(player, self.board)

    def recount_vp(self):
        [
            self.count_vp(card, player)
            for player in self.board.players
            for card in player.all_cards()
            if card.is_victory
        ]

    def get_input(self):
        pass

    def __str__(self):
        return str(self.board)

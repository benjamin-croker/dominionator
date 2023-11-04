from typing import Callable, List
import logging

import dominionator.board as dmb
import dominionator.agents as dma
import dominionator.cards.effects as dmce
import dominionator.cards.cardlist as dmcl


class Game(object):
    def __init__(self):
        logging.info("[Game]: Initialised")
        self.board = dmb.BoardState()
        self.recount_vp()
        self.agents = {
            player.name: dma.HumanAgent()
            for player in self.board.players
        }

    def count_vp(self, card: dmcl.Card, player: dmb.Player):
        fn = dmce.get_count_card_fn(card.shortname)
        fn(player, self.board)

    def play_action_treasure(self, shortname, player: dmb.Player):
        logging.info(f"[GAME]: {player.name} plays {shortname}")
        player.play_from_hand(shortname)
        fn = dmce.get_play_card_fn(shortname)
        fn(player, self.board)

    def buy_card(self, shortname: str, player: dmb.Player):
        logging.info(f"[GAME]: {player.name} buys {shortname}")
        self.board.gain_card_from_supply_to_active_player(shortname)

    def recount_vp(self):
        [
            self.count_vp(card, player)
            for player in self.board.players
            for card in player.all_cards()
            if card.is_victory
        ]

    def _active_player_agent(self):
        return self.agents[self.board.get_active_player().name]

    def _player_play_action_treasure_loop(self,
                                          player: dmb.Player,
                                          agent: dma.Agent,
                                          playable_cards_fn: Callable[[], List[dmcl.Card]]):
        playable_cards = playable_cards_fn()

        while playable_cards is not None:
            # Find allowable cards for playing
            allowed = [card.shortname for card in playable_cards] + [dma.NO_SELECT]
            selected = agent.get_input_play_card_from_hand(
                player=player, board=self.board, allowed=allowed
            )
            if selected == dma.NO_SELECT:
                break
            # no effect on action if playing treasures
            if player.phase == dmb.Phase.ACTION:
                player.actions -= 1
            self.play_action_treasure(selected, player)

    def _player_buy_loop(self, player, agent):
        buyable_cards = self.board.get_buyable_supply_cards_for_active_player()
        while buyable_cards is not None:
            allowed = [card.shortname for card in buyable_cards] + [dma.NO_SELECT]
            selected = agent.get_input_buy_card_from_supply(
                player=player, board=self.board, allowed=allowed
            )
            if selected == dma.NO_SELECT:
                break
            player.buys -= 1
            self.buy_card(selected, player)

    def _active_player_turn_loop(self):
        player = self.board.get_active_player()
        agent = self._active_player_agent()

        # Action phase. This loop enacts playing the cards
        player.start_action_phase()
        self._player_play_action_treasure_loop(player, agent, player.get_playable_action_cards)

        # Buy phase
        player.start_buy_phase()
        self._player_play_action_treasure_loop(player, agent, player.get_playable_action_cards)
        self._player_buy_loop(player, agent)

        # self._active_player_buy_loop(player, agent)
        player.start_cleanup_phase()

    def start_main_loop(self):
        game_ended = False
        while not game_ended:
            self._active_player_turn_loop()
            # TODO: this is technically incorrect.
            # The game ends before the next player starts their turn
            self.board.advance_turn_to_next_player()

    def __str__(self):
        return str(self.board)

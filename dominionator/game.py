import logging

import dominionator.board as dmb
import dominionator.agents as dma
import dominionator.cards.effects as dmce


class Game(object):
    def __init__(self):
        logging.info("[Game]: Initialised")
        self.board = dmb.BoardState()
        self.recount_vp()
        self.agents = {
            player.name: dma.HumanAgent()
            for player in self.board.players
        }

    def _count_vp(self, shortname: str, player: dmb.Player):
        fn = dmce.get_count_card_fn(shortname)
        fn(player, self.board)

    def recount_vp(self):
        for player in self.board.players:
            player.victory_points = 0
            [
                self._count_vp(card.shortname, player)
                for card in player.all_cards()
                if card.is_victory
            ]

    def play_action_treasure(self, shortname, player: dmb.Player):
        logging.info(f"[GAME]: {player.name} plays {shortname}")
        player.play_from_hand(shortname)
        fn = dmce.get_play_card_fn(shortname)
        fn(player, self.board)

    def buy_card(self, shortname: str, player: dmb.Player):
        logging.info(f"[GAME]: {player.name} buys {shortname}")
        self.board.gain_card_from_supply_to_active_player(shortname)

    def get_active_player_agent(self):
        return self.agents[self.board.get_active_player().name]

    def _player_play_action_loop(self,
                                 player: dmb.Player,
                                 agent: dma.Agent):
        logging.debug(f"[GAME]: {player.name} action loop")
        playable_cards = player.get_playable_action_cards()

        while len(playable_cards) > 0:
            allowed = list(playable_cards) + [dma.NO_SELECT]
            selected = agent.get_input_play_card_from_hand(
                player=player, board=self.board, allowed=allowed
            )
            if selected == dma.NO_SELECT:
                break
            player.actions -= 1

            self.play_action_treasure(selected, player)
            playable_cards = player.get_playable_action_cards()

    def _player_play_treasure_loop(self,
                                   player: dmb.Player,
                                   agent: dma.Agent):
        logging.debug(f"[GAME]: {player.name} play treasure loop")
        playable_cards = player.get_playable_treasure_cards()
        autoplay_treasures = False

        while len(playable_cards) > 0:
            if autoplay_treasures:
                # keep getting the first treasure until we run out
                selected = list(playable_cards)[0]
            else:
                allowed = list(playable_cards) + [dma.NO_SELECT, dma.ALL_TREASURES]
                selected = agent.get_input_play_card_from_hand(
                    player=player, board=self.board, allowed=allowed
                )

            if selected == dma.NO_SELECT:
                break
            elif selected == dma.ALL_TREASURES:
                autoplay_treasures = True
                continue
            else:
                self.play_action_treasure(selected, player)
                playable_cards = player.get_playable_treasure_cards()

    def _player_buy_loop(self, player, agent):
        buyable_cards = self.board.get_buyable_supply_cards_for_active_player()
        logging.debug(f"[GAME]: {player.name} buy loop. Buyable: {buyable_cards}")

        while len(buyable_cards) > 0:
            allowed = list(buyable_cards) + [dma.NO_SELECT]
            selected = agent.get_input_buy_card_from_supply(
                player=player, board=self.board, allowed=allowed
            )
            if selected == dma.NO_SELECT:
                break
            player.buys -= 1
            self.buy_card(selected, player)
            buyable_cards = self.board.get_buyable_supply_cards_for_active_player()

    def active_player_turn_loop(self):
        player = self.board.get_active_player()
        agent = self.get_active_player_agent()

        player.reset_resources()

        # Action phase. This loop enacts playing the cards
        player.start_action_phase()
        self._player_play_action_loop(player, agent)

        # Buy phase
        player.start_buy_phase()
        self._player_play_treasure_loop(player, agent)
        self._player_buy_loop(player, agent)

        # Cleanup phase
        player.start_cleanup_phase()

    def start_main_loop(self):
        game_ended = False

        while not game_ended:
            self.active_player_turn_loop()
            self.recount_vp()
            game_ended = self.board.is_end_condition()
            if not game_ended:
                self.board.advance_turn_to_next_player()

        logging.info("[GAME]: Ended")
        return str(self.board)

    def __str__(self):
        return str(self.board)

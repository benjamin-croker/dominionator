import logging
from logging import debug, info
from typing import Dict, List, Callable

import dominionator.board as dmb
import dominionator.player as dmp
import dominionator.agents as dma
import dominionator.cards.effects as dmce
import dominionator.cards.cardlist as dmcl
import dominionator.statlog as dlog


class Game(object):
    def __init__(self,
                 players: Dict[str, Dict[str, str]],
                 kingdom: List[str],
                 start_cards: List[str],
                 stat_log: dlog.StatLog,
                 game_index: int = 0):
        """
        :param players:
            Dictionary of playerName: config mappings. Must contain an "agent" key.
            e.g. { "Player1": {"agent": "Human"}, "Player2": {"agent": "Human"}}
        :param kingdom:
            List of short/long card names to include in the supply along with the base cards
        :param start_cards:
            List of short/long card names to use in the starting hand for each player
        :param stat_log:
            Object to log game statistics to
        :param game_index:
            Integer used for identifying games if multiple games are run in a simulation
        """

        self._log(info, "initialised")
        self.board = dmb.BoardState(list(players.keys()), kingdom, start_cards)
        self.agents = {
            player_name: dma.lookup[player_conf['agent']]()
            for player_name, player_conf in players.items()
        }
        self.stat_log = stat_log
        self.game_index = game_index
        self.recount_vp()

    @staticmethod
    def _log(logfn: Callable[[str], None], message: str):
        logfn(f"[GAME]: {message}")

    def _stat_log(self, player: dmp.Player):
        self.stat_log.add_items_from_turnstats(
            self.game_index, self.board.turn_num, player.name, player.turnstats
        )

    def _count_vp(self, shortname: str, player: dmp.Player):
        fn = dmce.get_count_card_fn(shortname)
        fn(player, self.board, self.agents)

    def recount_vp(self):
        for player in self.board.players:
            player.victory_points = 0
            [
                self._count_vp(card.shortname, player)
                for card in player.all_cards()
                if card.is_type(dmcl.CardType.VICTORY) or card.is_type(dmcl.CardType.CURSE)
            ]

    def get_active_player_agent(self):
        return self.agents[self.board.get_active_player().name]

    def _play_action_treasure(self, player: dmp.Player, shortname: str):
        player.play_from_hand(shortname)
        fn = dmce.get_play_card_fn(shortname)
        fn(player, self.board, self.agents)

    def _player_play_action_loop(self,
                                 player: dmp.Player,
                                 agent: dma.Agent):
        self._log(debug, f"{player.name} action loop")
        used_actions = 0
        playable_cards = player.get_playable_action_cards()

        while len(playable_cards) > 0:
            allowed = playable_cards.union({dma.NO_SELECT})
            selected = agent.get_input_play_action_card_from_hand(
                player=player, board=self.board, allowed=allowed
            )
            if selected == dma.NO_SELECT:
                break
            player.actions -= 1
            player.play_from_hand(selected)
            self._log(debug, f"playing {selected} for {player.name}")
            dmce.get_play_card_fn(selected)(player, self.board, self.agents)

            used_actions += 1

            playable_cards = player.get_playable_action_cards()

        player.turnstats['used_actions'] = used_actions
        player.turnstats['unused_actions'] = player.actions
        player.turnstats['total_actions'] = used_actions + player.actions

    def _player_play_treasure_loop(self,
                                   player: dmp.Player,
                                   agent: dma.Agent):
        logging.debug(f"[GAME]: {player.name} play treasure loop")
        playable_cards = player.get_playable_treasure_cards()
        autoplay_treasures = False

        # any coins are from actions
        action_coins = player.coins

        while len(playable_cards) > 0:
            if autoplay_treasures:
                # keep getting the first treasure until we run out
                selected = list(playable_cards)[0]
            else:
                allowed = playable_cards.union({dma.NO_SELECT, dma.ALL_TREASURES})
                selected = agent.get_input_play_treasure_card_from_hand(
                    player=player, board=self.board, allowed=allowed
                )

            if selected == dma.NO_SELECT:
                break
            elif selected == dma.ALL_TREASURES:
                autoplay_treasures = True
                continue
            else:
                player.play_from_hand(selected)
                self._log(debug, f"playing {selected} for {player.name}")
                dmce.get_play_card_fn(selected)(player, self.board, self.agents)

                playable_cards = player.get_playable_treasure_cards()

        # any extra coins are from treasures
        total_coins = player.coins
        treasure_coins = total_coins - action_coins
        player.turnstats['action_coins'] = action_coins
        player.turnstats['treasure_coins'] = treasure_coins
        player.turnstats['total_coins'] = total_coins

    def _player_buy_loop(self, player, agent):
        buyable_cards = self.board.get_buyable_supply_cards_for_active_player()
        logging.debug(f"[GAME]: {player.name} buy loop. Buyable: {buyable_cards}")

        # These are at their highest at the start of the buy phase
        self.recount_vp()
        total_coins = player.coins
        total_buys = player.buys
        vp_start_buy = player.victory_points

        while len(buyable_cards) > 0:
            allowed = buyable_cards.union({dma.NO_SELECT})
            selected = agent.get_input_buy_card_from_supply(
                player=player, board=self.board, allowed=allowed
            )
            if selected == dma.NO_SELECT:
                break

            logging.info(f"[GAME]: {player.name} buys {selected}")
            player.buys -= 1
            player.coins -= self.board.supply[selected][0].cost
            self.board.gain_card_from_supply_to_player(player, selected)

            buyable_cards = self.board.get_buyable_supply_cards_for_active_player()

        self.recount_vp()
        player.turnstats['spent_coins'] = total_coins - player.coins
        player.turnstats['unspent_coins'] = player.coins

        player.turnstats['used_buys'] = total_buys - player.buys
        player.turnstats['unused_buys'] = player.buys
        player.turnstats['total_buys'] = total_buys

        player.turnstats['gained_vp'] = player.victory_points - vp_start_buy
        player.turnstats['total_vp'] = player.victory_points

    @staticmethod
    def _player_cleanup(player):
        # count cards still in hand
        player.turnstats['unplayed_action_cards'] = player.count_cards_in_hand(
            dmcl.CardType.ACTION
        )
        player.turnstats['unplayed_treasure_cards'] = player.count_cards_in_hand(
            dmcl.CardType.TREASURE
        )

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
        self._player_cleanup(player)
        player.start_cleanup_phase()

        # Reset and log turn statistics
        # No need to recount VP as this happens at the end of the buy phase
        self._stat_log(player)
        agent.reward_outcomes(player, self.board)
        player.reset_turnstats()

    def check_winner(self):
        self.recount_vp()

        p1, p2 = self.board.players[0], self.board.players[1]
        p1_str = f"{p1.name}:{p1.victory_points}"
        p2_str = f"{p2.name}:{p2.victory_points}"
        margin = abs(p1.victory_points - p2.victory_points)
        self._log(info, f"Game ended. Final points {p1_str} {p2_str}")

        if p1.victory_points > p2.victory_points:
            self._log(info, f"{p1.name} wins")
            p1.turnstats = {'won_game': 1, 'lost_game': 0, 'tied_game': 0, 'win_margin': margin}
            p2.turnstats = {'won_game': 0, 'lost_game': 1, 'tied_game': 0, 'win_margin': margin}

        elif p1.victory_points < p2.victory_points:
            self._log(info, f"{p2.name} wins")
            p1.turnstats = {'won_game': 0, 'lost_game': 1, 'tied_game': 0, 'win_margin': margin}
            p2.turnstats = {'won_game': 1, 'lost_game': 0, 'tied_game': 0, 'win_margin': margin}

        elif self.board.active_player_i == 0:
            # Players have equal points but second player hasn't had their turn
            self._log(info, f"{p2.name} wins")
            p1.turnstats = {'won_game': 0, 'lost_game': 1, 'tied_game': 0, 'win_margin': margin}
            p2.turnstats = {'won_game': 1, 'lost_game': 0, 'tied_game': 0, 'win_margin': margin}

        else:  # tie
            self._log(info, "tie")
            p1.turnstats = {'won_game': 0, 'lost_game': 0, 'tied_game': 1, 'win_margin': margin}
            p2.turnstats = {'won_game': 0, 'lost_game': 0, 'tied_game': 1, 'win_margin': margin}

        self._stat_log(p1)
        self.agents[p1.name].reward_outcomes(p1, self.board)
        self._stat_log(p2)
        self.agents[p2.name].reward_outcomes(p1, self.board)

    def start_main_loop(self):
        game_ended = False

        while not game_ended:
            self.active_player_turn_loop()
            game_ended = self.board.is_end_condition()
            if not game_ended:
                self.board.advance_turn_to_next_player()

        self._log(info, str(self.board))
        self.check_winner()

    def __str__(self):
        return str(self.board)

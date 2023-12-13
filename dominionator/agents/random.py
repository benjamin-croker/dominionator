import random
from typing import Set

import dominionator.agents.base as dma_base
import dominionator.board as dmb
import dominionator.player as dmp


class RandomAgent(dma_base.Agent):
    @staticmethod
    def _random_choice(allowed: Set[str]) -> str:
        return random.choice(tuple(allowed))

    def get_input_play_action_card_from_hand(self,
                                             player: dmp.Player,
                                             board: dmb.BoardState,
                                             allowed: Set[str]) -> str:
        # Should never own an action card
        return self._random_choice(allowed)

    def get_input_play_treasure_card_from_hand(self,
                                               player: dmp.Player,
                                               board: dmb.BoardState,
                                               allowed: Set[str]) -> str:
        return self._random_choice(allowed)

    def get_input_discard_card_from_hand(self,
                                         player: dmp.Player,
                                         board: dmb.BoardState,
                                         allowed: Set[str]) -> str:
        return self._random_choice(allowed)

    def get_input_trash_card_from_hand(self,
                                       player: dmp.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        return self._random_choice(allowed)

    def get_input_reveal_card_from_hand(self,
                                        player: dmp.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        return self._random_choice(allowed)

    def get_input_topdeck_card_from_discard(self,
                                            player: dmp.Player,
                                            board: dmb.BoardState,
                                            allowed: Set[str]) -> str:
        return self._random_choice(allowed)

    def get_input_buy_card_from_supply(self,
                                       player: dmp.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        return self._random_choice(allowed)

    def get_input_gain_card_from_supply(self,
                                        player: dmp.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        return self._random_choice(allowed)

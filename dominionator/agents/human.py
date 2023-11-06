from typing import Set
import logging

import dominionator.board as dmb
import dominionator.agents.base as dma_base


class HumanAgent(dma_base.Agent):

    # This may need to print out the board state if it's not printed as part
    # of the main game loop
    @staticmethod
    def _generic_input(instruction: str, allowed: Set[str]):
        selected = dma_base.WAITING_INPUT  # assumes this is never a valid input
        while selected not in allowed:
            selected = input(f"{instruction}:{allowed} > ")
        return selected

    def get_input_play_card_from_hand(self,
                                      player: dmb.Player,
                                      board: dmb.BoardState,
                                      allowed: Set[str]) -> str:
        logging.info(board)
        return self._generic_input(f"{player.name} PLAY_FROM_HAND", allowed)

    def get_input_discard_card_from_hand(self,
                                         player: dmb.Player,
                                         board: dmb.BoardState,
                                         allowed: Set[str]) -> str:
        logging.info(board)
        return self._generic_input(f"{player.name} DISCARD_FROM_HAND", allowed)

    def get_input_trash_card_from_hand(self,
                                       player: dmb.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        logging.info(board)
        return self._generic_input(f"{player.name} TRASH_FROM_HAND", allowed)

    def get_input_reveal_card_from_hand(self,
                                        player: dmb.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        logging.info(board)
        return self._generic_input(f"{player.name} REVEAL_FROM_HAND", allowed)

    def get_input_topdeck_card_from_discard(self,
                                            player: dmb.Player,
                                            board: dmb.BoardState,
                                            allowed: Set[str]) -> str:
        # Returns card shortname
        logging.info(board)
        return self._generic_input(f"{player.name} TOPDECK_FROM_DISCARD", allowed)

    def get_input_buy_card_from_supply(self,
                                       player: dmb.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        logging.info(board)
        return self._generic_input(f"{player.name} BUY_FROM_SUPPLY", allowed)

    def get_input_gain_card_from_supply(self,
                                        player: dmb.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        logging.info(board)
        return self._generic_input(f"{player.name} GAIN_FROM_SUPPLY", allowed)

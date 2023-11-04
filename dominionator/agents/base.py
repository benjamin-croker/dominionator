from typing import List
import dominionator.board as dmb

WAITING_INPUT = ''
NO_SELECT = '-1'


class Agent(object):

    def get_input_play_card_from_hand(self,
                                      player: dmb.Player,
                                      board: dmb.BoardState,
                                      allowed: List[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_discard_card_from_hand(self,
                                         player: dmb.Player,
                                         board: dmb.BoardState,
                                         allowed: List[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_trash_card_from_hand(self,
                                       player: dmb.Player,
                                       board: dmb.BoardState,
                                       allowed: List[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_reveal_card_from_hand(self,
                                        player: dmb.Player,
                                        board: dmb.BoardState,
                                        allowed: List[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_buy_card_from_supply(self,
                                       player: dmb.Player,
                                       board: dmb.BoardState,
                                       allowed: List[str]) -> str:
        # Returns card shortname
        raise NotImplementedError

    def get_input_gain_card_from_supply(self,
                                        player: dmb.Player,
                                        board: dmb.BoardState,
                                        allowed: List[str]) -> str:
        # Returns card shortname
        raise NotImplementedError

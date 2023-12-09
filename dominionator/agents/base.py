from typing import Set
import dominionator.board as dmb
import dominionator.player as dmp

WAITING_INPUT = ''
NO_SELECT = '-1'
ALL_TREASURES = '$A'


class Agent(object):

    def get_input_play_action_card_from_hand(self,
                                             player: dmp.Player,
                                             board: dmb.BoardState,
                                             allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_play_treasure_card_from_hand(self,
                                               player: dmp.Player,
                                               board: dmb.BoardState,
                                               allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_discard_card_from_hand(self,
                                         player: dmp.Player,
                                         board: dmb.BoardState,
                                         allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_trash_card_from_hand(self,
                                       player: dmp.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_reveal_card_from_hand(self,
                                        player: dmp.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_topdeck_card_from_discard(self,
                                            player: dmp.Player,
                                            board: dmb.BoardState,
                                            allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError()

    def get_input_buy_card_from_supply(self,
                                       player: dmp.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError

    def get_input_gain_card_from_supply(self,
                                        player: dmp.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        # Returns card shortname
        raise NotImplementedError

    # Agents have the capability to reward themselves at the end of each turn,
    # typically by looking at the Player's turn statistics
    # For most agents this is not used, but is a capability for ML and RL agents.
    def reward_outcomes(self, player: dmp.Player, board: dmb.BoardState):
        pass

    # Any steps that need to happen when the game ends can be added here
    def finalise(self):
        pass

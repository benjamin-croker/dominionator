import numpy as np
import uuid
import os
from pathlib import Path
from typing import Set, Type, Callable, Tuple

import dominionator.agents.base as dma_base
import dominionator.agents.bigmoney as dma_bigmoney
import dominionator.agents.random as dma_random
import dominionator.board as dmb
import dominionator.player as dmp
# Constants defining vector structure
from dominionator.agents.vector_spec import *

StateActionVectorTuple = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]


class _MlAgent(dma_base.Agent):

    def __init__(self):
        super().__init__()
        self._agent_id = ''
        self._instance_id = str(uuid.uuid4())
        # Working vectors that are added
        self._info = ''  # action type that the working vectors apply to
        self._state = np.zeros(STATE_VECTOR_SIZE, dtype=np.int16)
        self._action_mask = np.zeros(ACTION_VECTOR_SIZE, dtype=np.int16)
        self._action_selected = np.zeros(ACTION_VECTOR_SIZE, dtype=np.int16)
        self._reward = 0

        # Vectors updated incrementally throughout the game
        self._info_array = np.zeros((MAX_STATES, 1), dtype='U32')  # 32 char limit
        self._state_array = np.zeros((MAX_STATES, STATE_VECTOR_SIZE), dtype=np.int16)
        self._action_mask_array = np.zeros((MAX_STATES, ACTION_VECTOR_SIZE), dtype=np.int16)
        self._action_selected_array = np.zeros((MAX_STATES, ACTION_VECTOR_SIZE), dtype=np.int16)
        self._reward_array = np.zeros((MAX_STATES, 1), dtype=np.int16)
        self._index = 0

    def _reset_state_vector(self):
        # faster than reallocating (hopefully?)
        self._state = self._state * 0

    def _reset_action_mask_vector(self):
        self._action_mask = self._action_mask * 0

    def _reset_action_selected_vector(self):
        self._action_selected = self._action_selected * 0

    def _reset_reward(self):
        self._reward = 0

    def _inc_state_card_count(self, location: str, shortname: str, card_count: int = 1):
        self._state[LOCATION_OFFSET[location] + CARD_OFFSET[shortname]] += card_count

    def _set_state_game_phase_ind(self, phase_name: str, value: int):
        self._state[GAME_PHASE_OFFSET[phase_name]] = value

    def set_game_state_vector(self, board: dmb.BoardState):
        # Create a vector with the counts of all the cards in the different locations:
        # - In supply
        # - In trash
        # - Player 1 deck, hand, inplay, discard
        # - Player 2 deck, hand, inplay, discard
        # There are 26 kingdom and 7 basic = 33 unique cards in total
        # There are 10 locations in total
        # TODO: the Library will need another "set aside" location, as well as
        #   a temporary "in flight" location where the card has been drawn and
        #   the player is deciding to place in hand or set aside

        self._reset_state_vector()

        # 1: Supply
        [self._inc_state_card_count('SUPPLY', shortname, len(cards))
         for shortname, cards in board.supply.items()]
        # 2: Trash
        [self._inc_state_card_count('TRASH', card.shortname)
         for card in board.trash]

        # 3: Player 1 deck
        [self._inc_state_card_count('PLAYER1_DECK', card.shortname)
         for card in board.players[0].deck]
        # 4: Player 1 deck
        [self._inc_state_card_count('PLAYER1_HAND', card.shortname)
         for card in board.players[0].hand]
        # 5: Player 1 deck
        [self._inc_state_card_count('PLAYER1_INPLAY', card.shortname)
         for card in board.players[0].inplay]
        # 6: Player 1 deck
        [self._inc_state_card_count('PLAYER1_DISCARD', card.shortname)
         for card in board.players[0].discard]

        # 7: Player 2 deck
        [self._inc_state_card_count('PLAYER2_DECK', card.shortname)
         for card in board.players[1].deck]
        # 8: Player 2 deck
        [self._inc_state_card_count('PLAYER2_HAND', card.shortname)
         for card in board.players[1].hand]
        # 9: Player 2 deck
        [self._inc_state_card_count('PLAYER2_INPLAY', card.shortname)
         for card in board.players[1].inplay]
        # 10: Player 2 deck
        [self._inc_state_card_count('PLAYER2_DISCARD', card.shortname)
         for card in board.players[1].discard]

        # 11: Game turn
        self._set_state_game_phase_ind('GAME_TURN', board.turn_num)
        # 12: Player 1 points
        self._set_state_game_phase_ind('PLAYER1_POINTS', board.players[0].victory_points)
        # 13: Player 2 points
        self._set_state_game_phase_ind('PLAYER2_POINTS', board.players[0].victory_points)

        # 14: Player 1 is action phase
        self._set_state_game_phase_ind(
            'PLAYER1_ACTION_PHASE', int(board.players[0].phase == dmp.Phase.ACTION)
        )
        # 15: Player 1 is action phase
        self._set_state_game_phase_ind(
            'PLAYER1_BUY_PHASE', int(board.players[0].phase == dmp.Phase.BUY)
        )
        # 16: Player 2 is action phase
        self._set_state_game_phase_ind(
            'PLAYER2_ACTION_PHASE', int(board.players[1].phase == dmp.Phase.ACTION)
        )
        # 17: Player 2 is action phase
        self._set_state_game_phase_ind(
            'PLAYER2_BUY_PHASE', int(board.players[1].phase == dmp.Phase.BUY)
        )

    def _set_action_allowed_ind(self, action_type: str, shortname: str):
        # only applies to "card-type" actions. I.e. selecting/playing/buying a card
        self._action_mask[ACTION_TYPE_OFFSET[action_type] + ACTION_OFFSET[shortname]] = 1

    def set_action_mask_vector(self, action_type: str, allowed: Set[str]):
        self._reset_action_mask_vector()
        [self._set_action_allowed_ind(action_type, shortname) for shortname in allowed]

    def _set_action_selected_ind(self, action_type: str, shortname: str):
        self._action_selected[ACTION_TYPE_OFFSET[action_type] + ACTION_OFFSET[shortname]] = 1

    def set_action_selected_vector(self, action_type: str, selected: str):
        self._reset_action_selected_vector()
        self._action_selected[ACTION_TYPE_OFFSET[action_type] + ACTION_OFFSET[selected]] = 1

    def set_action_info(self, action_type: str):
        self._info = action_type

    # Call this before any action input is required, (and when the game ends).
    # Doing so will ensure that any rewards gained are associated with the previous
    # state/action before adding a new entry.

    # Note that the first index will be all zeros in all arrays, as no prior information
    # exists when the first action has been taken
    def collect_vectors(self):
        self._info_array[self._index, 0] = self._info
        self._state_array[self._index, :] = self._state
        self._action_mask_array[self._index, :] = self._action_mask
        self._action_selected_array[self._index, :] = self._action_selected
        self._reward_array[self._index, 0] = self._reward

        self._index += 1

    def truncate_vectors(self):
        # drop the first row, and any rows with no data
        self._info_array = self._info_array[1:self._index, 0]
        self._state_array = self._state_array[1:self._index, :]
        self._action_mask_array = self._action_mask_array[1:self._index, :]
        self._action_selected_array = self._action_selected_array[1:self._index, :]
        self._reward_array = self._reward_array[1:self._index, 0]

    def reward_outcomes(self, player: dmp.Player, board: dmb.BoardState):
        self._reset_reward()
        t_stats = player.turnstats

        if t_stats['used_actions'] is not None:
            # 2 point per action played
            self._reward += 2 * t_stats['used_actions']
            # Bonus points if it's an attack
            self._reward += t_stats['delivered_attacks']
            # -1 point per unused action
            self._reward -= t_stats['unused_actions']

            # 1 point per coin generated
            self._reward += t_stats['total_coins']
            # 1 extra point per coin spent
            self._reward += t_stats['spent_coins']

            # 1 point per gained vp, but offset so estates are penalised
            self._reward += int(t_stats['gained_vp'] > 0) * (t_stats['gained_vp'] - 2)

            # -2 points per card left in hand
            self._reward -= 2 * t_stats['unplayed_action_cards']
            self._reward -= 2 * t_stats['unplayed_treasure_cards']

        if t_stats['won_game'] is not None:
            # lost_game should be set too
            self._reward += (100 * t_stats['won_game'] * abs(t_stats['win_margin']))
            self._reward -= (20 * t_stats['lost_game'] * abs(t_stats['win_margin']))

    def finalise(self):
        self.collect_vectors()
        self.truncate_vectors()

    def get_state_action_vectors(self) -> StateActionVectorTuple:
        return (
            self._state_array,
            self._action_mask_array, self._action_selected_array,
            self._reward_array
        )

    def write_log_to_disc(self):
        # Log the vectors
        outdir = os.path.join('logs', 'ml_agent', self._agent_id)
        Path(outdir).mkdir(parents=True, exist_ok=True)

        np.savetxt(
            fname=os.path.join(outdir, f'{self._instance_id}_info.csv'),
            X=self._info_array, delimiter=',', fmt='%s',  # %s is string format
            header='ACTION_TYPE', comments=''
        )
        np.savetxt(
            fname=os.path.join(outdir, f'{self._instance_id}_state.csv'),
            X=self._state_array, delimiter=',', fmt='%d',  # %d is integer format
            header=','.join(STATE_VECTOR_HEADER), comments=''
        )
        np.savetxt(
            fname=os.path.join(outdir, f'{self._instance_id}_action_mask.csv'),
            X=self._action_mask_array, delimiter=',', fmt='%d',
            header=','.join(ACTION_VECTOR_HEADER), comments=''
        )
        np.savetxt(
            fname=os.path.join(outdir, f'{self._instance_id}_action_selected.csv'),
            X=self._action_selected_array, delimiter=',', fmt='%d',
            header=','.join(ACTION_VECTOR_HEADER), comments=''
        )
        np.savetxt(
            fname=os.path.join(outdir, f'{self._instance_id}_reward.csv'),
            X=self._reward_array, delimiter=',', fmt='%d',
            header='REWARD', comments=''
        )


def wrap_deterministic_agent_with_state_logging(agent_class: Type[dma_base]):
    # This function wraps any type of deterministic rules based agent with
    # the state-based logging of the ML agent.

    # This inheritance hierarchy will use MlAgent functions over agent_class
    # functions.
    class MLDeterministicAgent(_MlAgent, agent_class):
        def __init__(self):
            # Because MlAgent itself calls super(), agent_class init() method
            # will be called (although it doesn't do anything)
            super().__init__()
            self._agent_id = f'MLDeterministicAgent-{agent_class.__name__}'

        def _get_action(self,
                        player: dmp.Player,
                        board: dmb.BoardState,
                        allowed: Set[str],
                        action_type: str,
                        parent_get_input_method: Callable) -> str:
            # Reset and cleanup the previous action information
            self.collect_vectors()
            # Current state and action mask
            self.set_action_info(action_type)
            self.set_game_state_vector(board)
            self.set_action_mask_vector(action_type, allowed)
            # Selected action
            selected = parent_get_input_method(self, player, board, allowed)
            self.set_action_selected_vector(action_type, selected)
            return selected

        def get_input_play_action_card_from_hand(self,
                                                 player: dmp.Player,
                                                 board: dmb.BoardState,
                                                 allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'PLAY_ACTION_CARD_FROM_HAND',
                agent_class.get_input_play_action_card_from_hand
            )

        def get_input_play_treasure_card_from_hand(self,
                                                   player: dmp.Player,
                                                   board: dmb.BoardState,
                                                   allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'PLAY_TREASURE_CARD_FROM_HAND',
                agent_class.get_input_play_treasure_card_from_hand
            )

        def get_input_discard_card_from_hand(self,
                                             player: dmp.Player,
                                             board: dmb.BoardState,
                                             allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'DISCARD_CARD_FROM_HAND',
                agent_class.get_input_discard_card_from_hand
            )

        def get_input_trash_card_from_hand(self,
                                           player: dmp.Player,
                                           board: dmb.BoardState,
                                           allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'TRASH_CARD_FROM_HAND',
                agent_class.get_input_trash_card_from_hand
            )

        def get_input_reveal_card_from_hand(self,
                                            player: dmp.Player,
                                            board: dmb.BoardState,
                                            allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'REVEAL_CARD_FROM_HAND',
                agent_class.get_input_reveal_card_from_hand
            )

        def get_input_topdeck_card_from_discard(self,
                                                player: dmp.Player,
                                                board: dmb.BoardState,
                                                allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'TOPDECK_CARD_FROM_DISCARD',
                agent_class.get_input_topdeck_card_from_discard
            )

        def get_input_buy_card_from_supply(self,
                                           player: dmp.Player,
                                           board: dmb.BoardState,
                                           allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'BUY_CARD_FROM_SUPPLY',
                agent_class.get_input_buy_card_from_supply
            )

        def get_input_gain_card_from_supply(self,
                                            player: dmp.Player,
                                            board: dmb.BoardState,
                                            allowed: Set[str]) -> str:
            return self._get_action(
                player, board, allowed, 'GAIN_CARD_FROM_SUPPLY',
                agent_class.get_input_gain_card_from_supply
            )

    return MLDeterministicAgent


MlSmithyBigMoneyAgent = wrap_deterministic_agent_with_state_logging(
    dma_bigmoney.SmithyBigMoneyAgent
)
MlRandomAgent = wrap_deterministic_agent_with_state_logging(
    dma_random.RandomAgent
)

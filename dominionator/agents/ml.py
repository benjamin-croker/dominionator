import numpy as np
from typing import Set

import dominionator.agents.base as dma_base
import dominionator.board as dmb
import dominionator.player as dmp

# State vector is primarily formed from vectors with card counts in each location:
# - In supply
# - In trash
# - Player 1 deck, hand, inplay, discard
# - Player 2 deck, hand, inplay, discard
# Other data captured in the game state is
# - Game turn count
# - Player 1 score
# - Player 2 score
# Indicators for tracking the point within a player's turn
# - Player 1 action phase, buy phase
# - Player 2 action phase, buy phase

# There are 26 kingdom and 7 basic = 33 unique cards in total
NCARDS = 33
# Define order of cards, used consistently in each part of the vector
CARD_OFFSET = {
    '$1': 0,
    '$2': 1,
    # ...
    'AR': 32  # Artisan
}

# There are 10 locations in total. Define order of the different location counts
# within the vector in multiples of NCARDS
LOCATION_OFFSET = {
    'SUPPLY': 0 * NCARDS,
    'TRASH': 1 * NCARDS,
    'PLAYER1_DECK': 2 * NCARDS,
    'PLAYER1_HAND': 3 * NCARDS,
    'PLAYER1_INPLAY': 4 * NCARDS,
    'PLAYER1_DISCARD': 5 * NCARDS,
    'PLAYER2_DECK': 6 * NCARDS,
    'PLAYER2_HAND': 7 * NCARDS,
    'PLAYER2_INPLAY': 8 * NCARDS,
    'PLAYER2_DISCARD': 9 * NCARDS
}
CARD_COUNT_OFFSET = len(LOCATION_OFFSET) * NCARDS
GAME_PHASE_OFFSET = {
    'GAME_TURN': 0 + CARD_COUNT_OFFSET,
    'PLAYER1_POINTS': 1 + CARD_COUNT_OFFSET,
    'PLAYER2_POINTS': 2 + CARD_COUNT_OFFSET,
    'PLAYER1_ACTION_PHASE': 3 + CARD_COUNT_OFFSET,
    'PLAYER1_BUY_PHASE': 4 + CARD_COUNT_OFFSET,
    'PLAYER2_ACTION_PHASE': 5 + CARD_COUNT_OFFSET,
    'PLAYER2_BUY_PHASE': 6 + CARD_COUNT_OFFSET
}
STATE_VECTOR_SIZE = CARD_COUNT_OFFSET + len(GAME_PHASE_OFFSET)

# Action vector is generally framed as all possible combinations of the 33 cards
# in Dominion, and actions defined by the base agent:
# - get_input_play_action_card_from_hand
# - get_input_play_treasure_card_from_hand
# - get_input_discard_card_from_hand
# - get_input_trash_card_from_hand
# - get_input_reveal_card_from_hand
# - get_input_topdeck_card_from_discard
# - get_input_buy_card_from_supply
# - get_input_gain_card_from_supply
# Each position in the action vector means something specific e.g:
# - "Reveal a Gold from hand"
# Of course, only a small number of actions will be possible at any point
# TODO: create card-specific actions for cards like Sentry, which has an
#   option to swap the top 2 cards on deck
ACTION_TYPE_OFFSET = {
    'PLAY_ACTION_CARD_FROM_HAND': 0 * NCARDS,
    'PLAY_TREASURE_CARD_FROM_HAND': 1 * NCARDS,
    'DISCARD_CARD_FROM_HAND': 2 * NCARDS,
    'TRASH_CARD_FROM_HAND': 3 * NCARDS,
    'REVEAL_CARD_FROM_HAND': 4 * NCARDS,
    'TOPDECK_CARD_FROM_DISCARD': 5 * NCARDS,
    'BUY_CARD_FROM_SUPPLY': 6 * NCARDS,
    'GAIN_CARD_FROM_SUPPLY': 7 * NCARDS,
}
ACTION_VECTOR_SIZE = len(ACTION_TYPE_OFFSET) * NCARDS


class MlAgent(dma_base.Agent):

    def __init__(self):
        super().__init__()
        self._state = np.zeros(STATE_VECTOR_SIZE)
        self._action = np.zeros(ACTION_VECTOR_SIZE)
        self._reward = 0

    def _reset_state_vector(self):
        # faster than reallocating (hopefully?)
        self._state = self._state * 0

    def _reset_action_vector(self):
        self._action = self._action * 0

    def _reset_reward(self):
        self._reward = 0

    def _inc_state_card_count(self, location: str, shortname: str, card_count: int = 1):
        self._state[LOCATION_OFFSET[location] + CARD_OFFSET[shortname]] += card_count

    def _set_state_game_phase(self, phase_name: str, value: int):
        self._state[GAME_PHASE_OFFSET[phase_name]] = value

    def _game_state_vector(self, board: dmb.BoardState):
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
        self._set_state_game_phase('GAME_TURN', board.turn_num)
        # 12: Player 1 points
        self._set_state_game_phase('PLAYER1_POINTS', board.players[0].victory_points)
        # 13: Player 2 points
        self._set_state_game_phase('PLAYER2_POINTS', board.players[0].victory_points)

        # 14: Player 1 is action phase
        self._set_state_game_phase(
            'PLAYER1_ACTION_PHASE', int(board.players[0].phase == dmp.Phase.ACTION)
        )
        # 15: Player 1 is action phase
        self._set_state_game_phase(
            'PLAYER1_BUY_PHASE', int(board.players[0].phase == dmp.Phase.BUY)
        )
        # 16: Player 2 is action phase
        self._set_state_game_phase(
            'PLAYER2_ACTION_PHASE', int(board.players[1].phase == dmp.Phase.ACTION)
        )
        # 17: Player 2 is action phase
        self._set_state_game_phase(
            'PLAYER2_BUY_PHASE', int(board.players[1].phase == dmp.Phase.BUY)
        )

    def _set_action(self, action_type: str, shortname: str):
        self._action[ACTION_TYPE_OFFSET[action_type] + CARD_OFFSET[shortname]] = 1

    def _allowed_action_vector(self, action_type: str, allowed: Set[str]):
        self._reset_action_vector()
        # ALL_TREASURES is just a handy shortcut, not needed for this agent
        [self._set_action(action_type, shortname)
         for shortname in allowed
         if shortname != dma_base.ALL_TREASURES]

    def reward_outcomes(self, player: dmp.Player, board: dmb.BoardState):
        self._reset_reward()
        t_stats = player.turnstats

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

import dominionator.cards.cardlist as dmcl

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
CARD_SHORTNAMES = [c.shortname for c in dmcl.CARD_LIST]
NCARDS = len(CARD_SHORTNAMES)
# Define order of cards, used for offsets in the vector
# All cards, for discarding, gaining, trashing, tracking location etc
CARD_OFFSET = {shortname: i for i, shortname in enumerate(CARD_SHORTNAMES)}

# Number of options for most actions also inlcudes NO_SELECT = '-1' and ALL_TREASURES = '$A'
ACTION_SHORTNAMES = CARD_SHORTNAMES + ['-1', '$A']
NACTION = len(ACTION_SHORTNAMES)
ACTION_OFFSET = CARD_OFFSET | {'-1': len(CARD_OFFSET), '$A': len(CARD_OFFSET) + 1}

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
STATE_VECTOR_HEADER = \
    [
        f'{loc}_{shortname}'
        for loc in ['SPL', 'TRS', 'P1DK', 'P1HD', 'P1IP', 'P1DS', 'P2DK', 'P2HD', 'P2IP', 'P2DS']
        for shortname in CARD_SHORTNAMES
    ] + ['G_T', 'GP1_P', 'GP2_P', 'GP1_A', 'GP1_B', 'GP2_A', 'GP2_B']

# Action vector is generally framed as all possible combinations of the 33 cards
# in Dominion, and all actions defined by the base agent:
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
# For some actions however, only a subset of cards can ever apply, and the
# vector offsets are adjusted accordingly. E.g. can't play Gold when choosing
# an action to play.
# TODO: create card-specific actions for cards like Sentry, which has an
#   option to swap the top 2 cards on deck
ACTION_TYPE_OFFSET = {
    'PLAY_ACTION_CARD_FROM_HAND': 0 * NACTION,
    'PLAY_TREASURE_CARD_FROM_HAND': 1 * NACTION,
    'DISCARD_CARD_FROM_HAND': 2 * NACTION,
    'TRASH_CARD_FROM_HAND': 3 * NACTION,
    'REVEAL_CARD_FROM_HAND': 4 * NACTION,
    'TOPDECK_CARD_FROM_DISCARD': 5 * NACTION,
    'BUY_CARD_FROM_SUPPLY': 6 * NACTION,
    'GAIN_CARD_FROM_SUPPLY': 7 * NACTION,
}
ACTION_VECTOR_SIZE = len(ACTION_TYPE_OFFSET) * NACTION
ACTION_VECTOR_HEADER = \
    [
        f'{action_type}_{shortname}'
        for action_type in ['PL_A_HD', 'PL_T_HD', 'DS_HD', 'TR_HD', 'RV_HD', 'TD_DS', 'BY_SPL', 'GA_SPL']
        for shortname in ACTION_SHORTNAMES
    ]

# Maximum number of state/action/reward states to track
# This is needed so the arrays can be pre-allocated, rather than dynamically
# created in the game loops.
MAX_STATES = 1000

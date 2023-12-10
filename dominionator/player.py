from enum import Enum
import random
import logging
from logging import debug, info
from typing import List, Callable, Set

from dominionator.cards import cardlist as dmcl


class Phase(Enum):
    WAITING = 0
    ACTION = 1
    BUY = 2
    CLEANUP = 3


class Location(Enum):
    HAND = 0
    DECK = 1
    DISCARD = 2
    INPLAY = 3


TURN_DRAW = 5


def _create_turnstats_dict(in_progess_val=0, game_ended_val=None):
    return {
        # Action phase
        'used_actions': in_progess_val,
        'unused_actions': in_progess_val,
        'total_actions': in_progess_val,

        # Attack interactions
        'delivered_attacks': in_progess_val,

        # Buy phase - coins and their source
        'action_coins': in_progess_val,
        'treasure_coins': in_progess_val,
        # Buy phase - purchase cards
        'spent_coins': in_progess_val,
        'unspent_coins': in_progess_val,
        'total_coins': in_progess_val,
        'used_buys': in_progess_val,
        'unused_buys': in_progess_val,
        'total_buys': in_progess_val,

        # Cleanup phase - unplayed cards
        'unplayed_action_cards': in_progess_val,
        'unplayed_treasure_cards': in_progess_val,

        # VP changes and running total
        'gained_vp': in_progess_val,
        'total_vp': in_progess_val,

        # Overall game outcome. Values with None will be ignored until set, which
        # is the desired behaviour for these statistics
        'won_game': game_ended_val,
        'lost_game': game_ended_val,
        'tied_game': game_ended_val,
        'win_margin': game_ended_val
    }


class Player(object):
    # Class for managing
    # This class is not an "agent" which makes decisions or affects other parts of the game.
    # Rather, this class is for tracking the player's state, and cards under their control
    def __init__(self, name: str, index: int, start_cards: List[dmcl.Card]):
        self.name = name
        self.index = index

        # Deck & card status
        self.hand = []
        self.deck = []
        self.discard = []
        self.inplay = []

        # Turn resources
        self.coins = 0
        self.actions = 0
        self.buys = 0
        self.phase = Phase.WAITING

        # Set by the game engine by running a count
        self.victory_points = 0

        # Ongoing log used to track player statistics reset every turn, and
        # controlled by the game engine
        self.turnstats = _create_turnstats_dict()

        # This will start the game by shuffling all cards and drawing 5
        self.discard = start_cards
        self.start_cleanup_phase()
        logging.debug(f"[{self.name}]: initialised")

    def _log(self, logfn: Callable[[str], None], message: str):
        logfn(f"[{self.name}]: {message}")

    def _shuffle_if_needed(self, n_cards: int):
        if len(self.deck) < n_cards:
            self._log(debug, f"deck size check. Has {len(self.deck)} needs {n_cards}")
            self._log(info, "shuffles discard under deck")
            random.shuffle(self.discard)
            self.deck += self.discard
            self.discard = []

    def draw_from_deck(self, n_cards: int):
        self._shuffle_if_needed(n_cards)

        if len(self.deck) < n_cards:
            self._log(debug, f"less than {n_cards} available")
            n_cards = len(self.deck)

        self._log(info, f"draws {n_cards} cards")
        self.hand += self.deck[0:n_cards]
        self.deck = self.deck[n_cards:]

    def get_playable_action_cards(self) -> Set[str]:
        if self.phase != Phase.ACTION or self.actions < 1:
            return set()
        return set([
            card.shortname for card in self.hand
            if card.is_type(dmcl.CardType.ACTION)
        ])

    def count_cards_in_hand(self, card_type: dmcl.CardType = dmcl.CardType.ANY) -> int:
        return len([card for card in self.hand if card.is_type(card_type)])

    def get_attack_reaction_cards(self) -> Set[str]:
        # Just the moat in the base set
        return set([
            card.shortname for card in self.hand
            if card.is_type(dmcl.CardType.ATTACK_REACTION)
        ])

    def get_playable_treasure_cards(self) -> Set[str]:
        if self.phase != Phase.BUY:
            return set()
        return set([
            card.shortname for card in self.hand
            if card.is_type(dmcl.CardType.TREASURE)
        ])

    def get_discardable_cards(self, card_type: dmcl.CardType = dmcl.CardType.ANY) -> Set[str]:
        return set([
            card.shortname for card in self.hand
            if card.is_type(card_type)
        ])

    def get_trashable_cards(self, card_type: dmcl.CardType = dmcl.CardType.ANY) -> Set[str]:
        return set([
            card.shortname for card in self.hand
            if card.is_type(card_type)
        ])

    def get_discarded_cards(self) -> Set[str]:
        return set([card.shortname for card in self.discard])

    def play_from_hand(self, shortname: str):
        # Plays a card from the players hand. It assumes the card is selected via
        # another method. Returns a card for the GameState or card effect function
        # to handle.

        # Cards are selected by name, not hand position. This method is used as it will
        # make interfacing with an automated agent easier, by reducing the action
        # space to selecting one of the kingdom cards to play, instead of selecting
        # an index from a hand which could be an arbitrary size.

        # This, and other similar functions assume that the Game has already
        # checked it is possible to make this move before calling the function

        self._log(info, f"plays {shortname}")
        hand_i = [card.shortname for card in self.hand].index(shortname)
        played_card = self.hand.pop(hand_i)
        self.inplay += [played_card]

    def discard_from_hand(self, shortname: str):
        self._log(info, f"discards {shortname}")
        hand_i = [card.shortname for card in self.hand].index(shortname)
        discarded_card = self.hand.pop(hand_i)
        self.discard += [discarded_card]

    def trash_from_hand(self, shortname: str) -> dmcl.Card:
        # This method must be called by the Board, which places the card in the trash
        self._log(info, f"trashes {shortname}")
        hand_i = [card.shortname for card in self.hand].index(shortname)
        return self.hand.pop(hand_i)

    def gain_from_supply(self, card: dmcl.Card, gain_to: Location = Location.DISCARD):
        # This method must be called by the Board which takes the card off the supply
        self._log(info, f"gains {card.shortname} to {gain_to}")
        if gain_to == Location.DISCARD:
            self.discard += [card]
        elif gain_to == Location.DECK:
            # goes on the top of deck
            self.deck = [card] + self.deck
        elif gain_to == Location.HAND:
            self.hand += [card]
        elif gain_to == Location.INPLAY:
            self.inplay += [card]

    def move_from_hand_to_top_of_deck(self, shortname: str):
        self._log(info, f"moves {shortname} to deck")
        hand_i = [card.shortname for card in self.hand].index(shortname)
        self.deck = [self.hand.pop(hand_i)] + self.deck

    def topdeck_from_discard(self, shortname: str):
        self._log(info, f"topdecks {shortname} from discard to deck")
        hand_i = [card.shortname for card in self.discard].index(shortname)
        self.deck = [self.discard.pop(hand_i)] + self.deck

    def count_inplay(self, shortname: str):
        return len([
            card.shortname for card in self.inplay if card.shortname == shortname
        ])

    def reset_resources(self):
        self.actions = 1
        self.coins = 0
        self.buys = 1

    def start_action_phase(self):
        self._log(info, f"starts action phase")
        self.phase = Phase.ACTION

    def start_buy_phase(self):
        self._log(info, f"starts buy phase")
        self.phase = Phase.BUY

    def start_cleanup_phase(self):
        self._log(info, f"cleans up")
        self.phase = Phase.CLEANUP

        # Put hand and cards in play into the discard pile
        self.discard += self.hand
        self.hand = []
        self.discard += self.inplay
        self.inplay = []

        # Draw 5 cards
        self.draw_from_deck(TURN_DRAW)

    def reset_turnstats(self, in_progess_val=0, game_ended_val=None):
        self.turnstats = _create_turnstats_dict(in_progess_val, game_ended_val)

    def all_cards(self) -> List[dmcl.Card]:
        return self.hand + self.deck + self.discard + self.inplay

    def all_cards_names(self) -> List[str]:
        return [card.shortname for card in self.all_cards()]

    def __str__(self) -> str:
        player_str = (
            f"<{self.name}> @{self.actions} ${self.coins} &{self.buys} ^{self.victory_points}\n"
            f"inplay: {self.inplay} hand: {self.hand}\n"
            f"{self.discard}<--discard | deck-->{self.deck}\n"
        )
        return player_str

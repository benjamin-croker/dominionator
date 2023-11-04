import random
from enum import Enum
import logging
from logging import debug, info
from typing import Callable, List

# Don't import the parent cards package, as that refers to this module
# Only import the cardlist itself, which has no dependencies
import dominionator.cards.cardlist as dmcl

START_CARDS = tuple(3 * [dmcl.EstateCard] + 7 * [dmcl.CopperCard])
TURN_DRAW = 5


class Phase(Enum):
    WAITING = 0
    ACTION = 1
    BUY = 2
    CLEANUP = 3


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

        # Set by the game engine running a count
        self.victory_points = 0

        # This will start the game by shuffling all cards and drawing 5
        self.discard = start_cards
        self.start_cleanup_phase()

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
        self._log(info, f"draws {n_cards} cards")
        self.hand += self.deck[0:n_cards]
        self.deck = self.deck[n_cards:]

    def get_playable_action_cards(self):
        if self.phase != Phase.ACTION or self.actions < 1:
            return None
        return [card for card in self.hand if card.is_action]

    def get_playable_treasure_cards(self):
        if self.phase != Phase.BUY:
            return None
        return [card for card in self.hand if card.is_treasure]

    def play_from_hand(self, shortname: str):
        # Plays a card from the players hand. It assumes the index of the card
        # selected via another method. Returns a card for the GameState to handle.

        # Selects a card with the selected name. This method is used as it will
        # make interfacing with an automated agent easier, by reducing the action
        # space to selecting one of the kingdom cards to play, instead of selecting
        # an index from a hand which could be an arbitrary size.

        hand_i = [card.shortname for card in self.hand].index(shortname)
        played_card = self.hand.pop(hand_i)
        self.inplay += [played_card]

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

        # Reset and draw 5 cards
        self.actions = 1
        self.coins = 0
        self.buys = 1
        self.draw_from_deck(TURN_DRAW)

    def all_cards(self):
        return self.hand + self.deck + self.discard + self.inplay

    def __str__(self) -> str:
        player_str = (
            f"<{self.name}> @{self.actions} ${self.coins} &{self.buys} ^{self.victory_points}\n"
            f"inplay: {self.inplay} hand: {self.hand}\n"
            f"deck: -->{self.deck}\n"
            f"discard: {self.discard}<--"
        )
        return player_str


class BoardState(object):

    def __init__(self):
        logging.info("[Board]: Initialised")
        self.players = [
            Player("PlayerOne", 0, [CardClass() for CardClass in START_CARDS]),
            Player("PlayerTwo", 1, [CardClass() for CardClass in START_CARDS])
        ]
        self.active_player_i = 0

        self.supply = {
            dmcl.CopperCard.shortname: [dmcl.CopperCard()] * 30,
            dmcl.EstateCard.shortname: [dmcl.EstateCard()] * 8,
            dmcl.MilitiaCard.shortname: [dmcl.MilitiaCard()] * 10,
        }

        self.trash = []

    def get_active_player(self):
        return self.players[self.active_player_i]

    def get_other_players(self, player: Player):
        # returns other players in clockwise play order
        i = player.index
        return self.players[i + 1:] + self.players[:i]

    def advance_turn_to_next_player(self):
        self.get_active_player().phase = Phase.WAITING
        self.active_player_i = (self.active_player_i + 1) % len(self.players)

    def get_gainable_supply_cards_for_cost(self, cost_limit: int, exact=False):
        # This function is generic check for any type of gaining
        # Todo: return None rather than [] if nothing available
        buyable = [
            supply_pile[0] for _, supply_pile in self.supply.items()
            if len(supply_pile) > 0 and (
                    (supply_pile[0].cost == cost_limit) or
                    (not exact and (supply_pile[0].cost < cost_limit))
            )
        ]
        if len(buyable) == 0:
            return None
        return buyable

    def get_buyable_supply_cards_for_active_player(self):
        player = self.get_active_player()
        if player.phase != Phase.BUY or player.buys <= 0:
            return None
        return self.get_gainable_supply_cards_for_cost(player.coins)

    def gain_card_from_supply_to_active_player(self, shortname: str):
        player = self.get_active_player()
        logging.info(f"[Board]: {player.name} gains {shortname}")
        # TODO: check there are enough cards
        card = self.supply[shortname].pop(0)
        player.discard += [card]

    def __str__(self):
        game_str = "<Supply>\n"
        for k, v in self.supply.items():
            game_str += f"{k}:{v}\n"
        for player in self.players:
            if player.index == self.active_player_i:
                game_str += '*'
            game_str += f"{str(player)}\n"
        return game_str

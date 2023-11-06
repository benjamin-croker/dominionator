import random
from enum import Enum
import logging
from logging import debug, info
from typing import Callable, List, Set

# Don't import the parent cards package, as that refers to this module
# Only import the cardlist itself, which has no dependencies
import dominionator.cards.cardlist as dmcl

START_CARDS = tuple(5 * [dmcl.CellarCard] + 5 * [dmcl.HarbingerCard])
TURN_DRAW = 5


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

        if len(self.deck) < n_cards:
            self._log(debug, f"less than {n_cards} available")
            n_cards = len(self.deck)

        self._log(info, f"draws {n_cards} cards")
        self.hand += self.deck[0:n_cards]
        self.deck = self.deck[n_cards:]

    def get_playable_action_cards(self) -> Set[str]:
        if self.phase != Phase.ACTION or self.actions < 1:
            return set()
        return set([card.shortname for card in self.hand if card.is_action])

    def get_attack_reaction_cards(self) -> Set[str]:
        # Just the moat in the base set
        return set([card.shortname for card in self.hand if card.is_attack_reaction])

    def get_playable_treasure_cards(self) -> Set[str]:
        if self.phase != Phase.BUY:
            return set()
        return set([card.shortname for card in self.hand if card.is_treasure])

    def get_discardable_cards(self) -> Set[str]:
        return set([card.shortname for card in self.hand])

    def get_trashable_cards(self) -> Set[str]:
        return set([card.shortname for card in self.hand])

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

    def gain_from_supply(self, card: dmcl.Card, location: Location):
        # This method must be called by the Board which takes the card off the supply
        self._log(info, f"gains {card.shortname} to {location}")
        if location == Location.DISCARD:
            self.discard += [card]
        elif location == Location.DECK:
            # goes on the top of deck
            self.deck = [card] + self.deck
        elif location == Location.HAND:
            self.hand += [card]
        elif location == Location.INPLAY:
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

    def all_cards(self) -> List[dmcl.Card]:
        return self.hand + self.deck + self.discard + self.inplay

    def __str__(self) -> str:
        player_str = (
            f"<{self.name}> @{self.actions} ${self.coins} &{self.buys} ^{self.victory_points}\n"
            f"inplay: {self.inplay} hand: {self.hand}\n"
            f"{self.discard}<--discard | deck-->{self.deck}\n"
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
            dmcl.CopperCard.shortname: [dmcl.CopperCard()] * 46,
            dmcl.SilverCard.shortname: [dmcl.SilverCard()] * 40,
            dmcl.GoldCard.shortname: [dmcl.GoldCard()] * 30,
            dmcl.EstateCard.shortname: [dmcl.EstateCard()] * 8,
            dmcl.DuchyCard.shortname: [dmcl.DuchyCard()] * 8,
            dmcl.ProvinceCard.shortname: [dmcl.ProvinceCard()] * 8,
            dmcl.MerchantCard.shortname: [dmcl.MerchantCard()] * 10,
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

    def get_gainable_supply_cards_for_cost(self, cost_limit: int, exact=False) -> Set[str]:
        # This function is generic check for any type of gaining
        return set([
            supply_pile[0].shortname for _, supply_pile in self.supply.items()
            if len(supply_pile) > 0 and (
                    (supply_pile[0].cost == cost_limit) or
                    (not exact and (supply_pile[0].cost < cost_limit))
            )
        ])

    def get_buyable_supply_cards_for_active_player(self) -> Set[str]:
        player = self.get_active_player()
        if player.phase != Phase.BUY or player.buys <= 0:
            return set()
        return self.get_gainable_supply_cards_for_cost(player.coins)

    def gain_card_from_supply_to_player(self,
                                        player: Player,
                                        shortname: str,
                                        gain_to=Location.DISCARD):
        logging.info(f"[BOARD]: {player.name} gains {shortname}")
        # The Game object must check card is gainable before calling
        card = self.supply[shortname].pop(0)
        # TODO: pass this to the player to handle
        player.gain_from_supply()
        player.discard += [card]

    def trash_card_from_player_hand(self, player: Player, shortname: str):
        # The player removes the card from their own hand and returns it
        # for the Board to trash
        self.trash += [player.trash_from_hand(shortname)]

    def is_end_condition(self):
        # Find the empty supply piles
        empty_supply = [
            shortcode for shortcode, supply_pile in self.supply.items()
            if len(supply_pile) == 0
        ]
        return (len(empty_supply) >= 3) or (dmcl.ProvinceCard.shortname in empty_supply)

    def __str__(self):
        br = '--------------------'
        game_str = f"\n{br}\n<Supply>\n"
        for k, v in self.supply.items():
            game_str += f"{k}:{len(v)}|"
        game_str += f'\n{br}\n'
        for player in self.players:
            pre = ''
            if player.index == self.active_player_i:
                pre = '*'
            game_str += f"{pre}{str(player)}{br}\n"
        return game_str

import logging
from typing import Set, List, Type

# Don't import the parent cards package, as that refers to this module
# Only import the cardlist itself, which has no dependencies
import dominionator.cards.cardlist as dmcl
import dominionator.player as dmp

START_CARDS = tuple(5 * [dmcl.RemodelCard] + 5 * [dmcl.RemodelCard])


def _supply_size(card_class: Type[dmcl.Card]):
    if dmcl.CardType.VICTORY in card_class.types:
        return 8
    else:
        return 10


class BoardState(object):

    def __init__(self, player_names: List[str], kingdom: List[str], start_cards: List[str]):
        if len(player_names) != 2:
            raise NotImplementedError("Only 2 player games are currently implemented")

        self.players = [
            dmp.Player(player_name, i, [dmcl.lookup[card_name]() for card_name in start_cards])
            for i, player_name in enumerate(player_names)
        ]
        self.active_player_i = 0
        self.turn_num = 1

        supply_basic = {
            dmcl.CopperCard.shortname: [dmcl.CopperCard()] * 46,
            dmcl.SilverCard.shortname: [dmcl.SilverCard()] * 40,
            dmcl.GoldCard.shortname: [dmcl.GoldCard()] * 30,
            dmcl.EstateCard.shortname: [dmcl.EstateCard()] * 8,
            dmcl.DuchyCard.shortname: [dmcl.DuchyCard()] * 8,
            dmcl.ProvinceCard.shortname: [dmcl.ProvinceCard()] * 8,
            dmcl.CurseCard.shortname: [dmcl.CurseCard()] * 20,
        }
        supply_kingdom = {
            CardClass.shortname: [CardClass()] * _supply_size(CardClass)
            for CardClass in [
                dmcl.lookup[card_name] for card_name in kingdom
            ]
        }
        self.supply = supply_basic | supply_kingdom
        self.trash = []

        logging.info("[Board]: Initialised")

    def get_active_player(self):
        return self.players[self.active_player_i]

    def get_other_players(self, player: dmp.Player):
        # returns other players in clockwise play order
        i = player.index
        return self.players[i + 1:] + self.players[:i]

    def advance_turn_to_next_player(self):
        self.get_active_player().phase = dmp.Phase.WAITING
        self.active_player_i = (self.active_player_i + 1) % len(self.players)
        # Advance turn counter if we're back to the start
        if self.active_player_i == 0:
            self.turn_num += 1

    def get_gainable_supply_cards_for_cost(self,
                                           cost_limit: int,
                                           exact: bool = False,
                                           card_type: dmcl.CardType = dmcl.CardType.ANY
                                           ) -> Set[str]:
        # This function is generic check for any type of gaining
        return set([
            supply_pile[0].shortname for _, supply_pile in self.supply.items()
            if (
                       len(supply_pile) > 0
               ) and (
                       (supply_pile[0].cost == cost_limit) or
                       (not exact and (supply_pile[0].cost < cost_limit))
               ) and (
                   supply_pile[0].is_type(card_type)
               )
        ])

    def get_supply_pile_size(self, shortname: str):
        return len(self.supply[shortname])

    def get_buyable_supply_cards_for_active_player(self) -> Set[str]:
        player = self.get_active_player()
        if player.phase != dmp.Phase.BUY or player.buys <= 0:
            return set()
        return self.get_gainable_supply_cards_for_cost(player.coins)

    def gain_card_from_supply_to_player(self,
                                        player: dmp.Player,
                                        shortname: str,
                                        gain_to=dmp.Location.DISCARD):
        logging.info(f"[BOARD]: {player.name} gains {shortname}")
        # The Game object must check card is gainable before calling
        player.gain_from_supply(card=self.supply[shortname].pop(0), gain_to=gain_to)

    def trash_card_from_player_hand(self, player: dmp.Player, shortname: str) -> dmcl.Card:
        # The player removes the card from their own hand and returns it
        # for the Board to trash.
        trashed_card = player.trash_from_hand(shortname)
        self.trash += [trashed_card]
        # This returns the card in case the calling function needs to know what
        # was trashed
        return trashed_card

    def is_end_condition(self):
        # Find the empty supply piles
        empty_supply = [
            shortcode for shortcode, supply_pile in self.supply.items()
            if len(supply_pile) == 0
        ]
        return (len(empty_supply) >= 3) or (dmcl.ProvinceCard.shortname in empty_supply)

    def __str__(self):
        br = '--------------------'
        game_str = f"\n{br}\n<Supply> Turn {self.turn_num}\n|"
        for k, v in list(self.supply.items())[0:-10]:
            game_str += f"{k}:{len(v)}|"
        game_str += '\n|'
        for k, v in list(self.supply.items())[-10:]:
            game_str += f"{k}:{len(v)}|"
        game_str += f'\n{br}\n'
        for player in self.players:
            pre = ''
            if player.index == self.active_player_i:
                pre = '*'
            game_str += f"{pre}{str(player)}{br}\n"
        return game_str

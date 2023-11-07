from enum import Enum


class CardType(Enum):
    ACTION = 1
    REACTION = 2
    ATTACK = 3
    # Specify different events the card can react to. In the base set it's
    # just Moat, which reacts to attack
    ATTACK_REACTION = 4
    TREASURE = 5
    VICTORY = 6
    CURSE = 7
    # Add a special value so functions which filter for a specific type of card
    # (e.g. gain a treasure, trash an action from your hand) can be generalised
    # to work with no filters (e.g. gain a card)
    ANY = 8


class Card(object):
    # Design principles for the cards:
    # - Cards don't move themselves
    # - Cards 'operate' on the game as a whole

    name = ""
    shortname = ""

    # To be overwritten by child classes
    cost = 0

    # Card type
    types = {}

    def is_type(self, card_type: CardType):
        return (card_type in self.types) or (card_type == CardType.ANY)

    def __str__(self):
        return self.shortname

    def __repr__(self):
        return self.shortname


# --------- Victory ---------
class CurseCard(Card):
    name = "Curse"
    shortname = "V-"
    cost = 0
    types = {CardType.CURSE}


class EstateCard(Card):
    name = "Estate"
    shortname = "V1"
    cost = 2
    types = {CardType.VICTORY}


class DuchyCard(Card):
    name = "Duchy"
    shortname = "V3"
    cost = 5
    types = {CardType.VICTORY}


class ProvinceCard(Card):
    name = "Province"
    shortname = "V6"
    cost = 8
    types = {CardType.VICTORY}


# --------- Treasures ---------
class CopperCard(Card):
    name = "Copper"
    shortname = "$1"
    cost = 0
    types = {CardType.TREASURE}


class SilverCard(Card):
    name = "Silver"
    shortname = "$2"
    cost = 3
    types = {CardType.TREASURE}


class GoldCard(Card):
    name = "Gold"
    shortname = "$3"
    cost = 6
    types = {CardType.TREASURE}


# --------- Actions ---------
class CellarCard(Card):
    name = "Cellar"
    shortname = "CL"
    cost = 2
    types = {CardType.ACTION}


class ChapelCard(Card):
    name = "Chapel"
    shortname = "CH"
    cost = 2
    types = {CardType.ACTION}


class MoatCard(Card):
    name = "Moat"
    shortname = "MO"
    cost = 2
    types = {CardType.ACTION, CardType.ATTACK_REACTION}


class HarbingerCard(Card):
    name = "Harbinger"
    shortname = "HR"
    cost = 3
    types = {CardType.ACTION}


class MerchantCard(Card):
    name = "Merchant"
    shortname = "MC"
    cost = 3
    types = {CardType.ACTION}


class VillageCard(Card):
    name = "Village"
    shortname = "VL"
    cost = 3
    types = {CardType.ACTION}


class MilitiaCard(Card):
    name = "Militia"
    shortname = "ML"
    cost = 4
    types = {CardType.ACTION, CardType.ATTACK}


class RemodelCard(Card):
    name = "Remodel"
    shortname = "RM"
    cost = 4
    types = {CardType.ACTION}


class SmithyCard(Card):
    name = "Smithy"
    shortname = "SM"
    cost = 4
    types = {CardType.ACTION}


class WorkshopCard(Card):
    name = "Workshop"
    shortname = "WO"
    cost = 4
    types = {CardType.ACTION}


class MarketCard(Card):
    name = "Market"
    shortname = "MK"
    cost = 5
    types = {CardType.ACTION}


class MineCard(Card):
    name = "Mine"
    shortname = "MN"
    cost = 5
    types = {CardType.ACTION}

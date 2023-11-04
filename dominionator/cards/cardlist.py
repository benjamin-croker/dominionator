class Card(object):
    # Design principles for the cards:
    # - Cards don't move themselves
    # - Cards 'operate' on the game as a whole

    name = ""
    shortname = ""

    # To be overwritten by child classes
    cost = 0

    # Card type
    is_action = False
    is_reaction = False
    is_treasure = False
    is_attack = False
    is_victory = False

    def __str__(self):
        return self.shortname

    def __repr__(self):
        return self.shortname


# --------- Victory ---------
class EstateCard(Card):
    name = "Estate"
    shortname = "V1"
    cost = 2
    is_victory = True


class DuchyCard(Card):
    name = "Duchy"
    shortname = "V3"
    cost = 5
    is_victory = True


class ProvinceCard(Card):
    name = "Province"
    shortname = "V6"
    cost = 8
    is_victory = True


# --------- Treasures ---------
class CopperCard(Card):
    name = "Copper"
    shortname = "$1"
    cost = 0
    is_treasure = True


class SilverCard(Card):
    name = "Silver"
    shortname = "$2"
    cost = 3
    is_treasure = True


class GoldCard(Card):
    name = "Gold"
    shortname = "$3"
    cost = 6
    is_treasure = True


# --------- Actions ---------
class MilitiaCard(Card):
    name = "Militia"
    shortname = "ML"
    cost = 4
    is_action = True
    is_attack = True


class MerchantCard(Card):
    name = "Merchant"
    shortname = "MC"
    cost = 3
    is_action = True

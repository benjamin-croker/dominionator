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


class EstateCard(Card):
    name = "Estate"
    shortname = "V1"
    cost = 2
    is_victory = True


class CopperCard(Card):
    name = "Copper"
    shortname = "$1"
    cost = 0
    is_treasure = True


class MilitiaCard(Card):
    name = "Militia"
    shortname = "Ml"
    cost = 4
    is_action = True
    is_attack = True

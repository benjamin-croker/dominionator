import unittest
import dominionator.cards.cardlist as dmcl


class CardUniqueNameTestCase(unittest.TestCase):
    def test_names_unique(self):
        shortnames = [c.shortname for c in dmcl.CARD_LIST]
        self.assertEqual(len(shortnames), len(set(shortnames)))

    def test_all_cards_in_lookup(self):
        for shortname in [c.shortname for c in dmcl.CARD_LIST]:
            self.assertIn(shortname, dmcl.CARD_LOOKUP)
        for name in [c.name for c in dmcl.CARD_LIST]:
            self.assertIn(name, dmcl.CARD_LOOKUP)


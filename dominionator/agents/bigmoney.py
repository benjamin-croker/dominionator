import logging
from typing import Set

import dominionator.board as dmb
import dominionator.player as dmp
import dominionator.cards.cardlist as dmcl
import dominionator.agents.base as dma_base


class BigMoneyAgent(dma_base.Agent):
    @staticmethod
    def _check_selected(selected: str, allowed: Set[str]):
        if selected not in allowed:
            raise ValueError(
                f"BigMoney agent wants to play {selected} but is not an option"
            )
        return selected

    def get_input_play_action_card_from_hand(self,
                                             player: dmp.Player,
                                             board: dmb.BoardState,
                                             allowed: Set[str]) -> str:
        # Should never own an action card
        return self._check_selected(dma_base.NO_SELECT, allowed)

    def get_input_play_treasure_card_from_hand(self,
                                               player: dmp.Player,
                                               board: dmb.BoardState,
                                               allowed: Set[str]) -> str:
        # Always play all treasures
        return self._check_selected(dma_base.ALL_TREASURES, allowed)

    def get_input_discard_card_from_hand(self,
                                         player: dmp.Player,
                                         board: dmb.BoardState,
                                         allowed: Set[str]) -> str:
        # Cards to discard, in order of preference.
        pref_order = [
            dmcl.CopperCard.shortname,
            dmcl.SilverCard.shortname,
            dmcl.GoldCard.shortname
        ]
        # add special options:
        #   * discard nothing
        #   * anything not in this list which would preferable to the above
        pref_special = [
            dma_base.NO_SELECT,
            allowed.difference(pref_order).pop()
        ]
        return [c for c in pref_special + pref_order if c in allowed][0]

    def get_input_trash_card_from_hand(self,
                                       player: dmp.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        # Same as discarding
        return self.get_input_discard_card_from_hand(
            player, board, allowed
        )

    def get_input_reveal_card_from_hand(self,
                                        player: dmp.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        # Same as discarding
        return self.get_input_discard_card_from_hand(
            player, board, allowed
        )

    def get_input_topdeck_card_from_discard(self,
                                            player: dmp.Player,
                                            board: dmb.BoardState,
                                            allowed: Set[str]) -> str:
        # Topdeck gold or silver if possible
        pref_order = [
            dmcl.GoldCard.shortname,
            dmcl.SilverCard.shortname,
            dma_base.NO_SELECT
        ]
        return [c for c in pref_order if c in allowed][0]

    def get_input_buy_card_from_supply(self,
                                       player: dmp.Player,
                                       board: dmb.BoardState,
                                       allowed: Set[str]) -> str:
        logging.debug(board)
        pref_order = [
            dmcl.ProvinceCard.shortname,
            dmcl.GoldCard.shortname,
            dmcl.SilverCard.shortname,
            dma_base.NO_SELECT
        ]
        n_provinces = board.get_supply_pile_size(dmcl.ProvinceCard.shortname)
        # If there's only once province, always buy the best VP you can
        # This prevents buying gold right near the end when the duchys have
        # run out
        if n_provinces <= 1:
            pref_order[1:1] = [dmcl.DuchyCard.shortname, dmcl.EstateCard.shortname]
        # Go for Duchy over Gold if <= 4 Provinces
        elif n_provinces <= 4 and player.coins in {6, 7}:
            pref_order[1:1] = [dmcl.DuchyCard.shortname]
        # Go for Duchy over Silver if <= 5 Provinces
        elif n_provinces <= 5 and player.coins == 5:
            pref_order[2:2] = [dmcl.DuchyCard.shortname]
        # Go for Estate over Silver if <= 2 Provinces
        elif n_provinces <= 2 and player.coins in {3, 4}:
            pref_order[2:2] = [dmcl.EstateCard.shortname]
        # Go for Estate over Nothing if <= 3 Provinces
        elif n_provinces <= 3 and player.coins == 2:
            pref_order[3:3] = [dmcl.EstateCard.shortname]

        return [c for c in pref_order if c in allowed][0]

    def get_input_gain_card_from_supply(self,
                                        player: dmp.Player,
                                        board: dmb.BoardState,
                                        allowed: Set[str]) -> str:
        # Same as buying
        return self.get_input_buy_card_from_supply(
            player, board, allowed
        )

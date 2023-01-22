from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemGlueAll(ItemBase):
    """
    Makes all players sbut the collecting player turn slower.
    """

    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_SHORT
        self.image_path = "Data/IconGlueAll.png"
        self.player = None  # Will be defined during method call activate.
        self.players_to_ignore = []

    def activate(self, player):
        """
        Decreases the turn rate of all players but the collecting player by one step.

        :param player: Player instance that picks up this item.
        """
        self.player = player
        # Choose next smaller value from the RATE list
        for p in self.controller.players:
            if p == self.player or p.turn_rate == RATE_MIN or p.turn_rate == RATE_RIGHT_ANGLE:
                self.players_to_ignore.append(p)
            else:
                p.turn_rate = RATES[max(RATES.index(p.turn_rate) - 1, 0)]

    def deactivate(self):
        """"
        Increases the turn rate of all players but this player by one step.

        :return: None
        """
        # Choose next greater value from the RATE list
        for p in self.controller.players:
            if p in self.players_to_ignore or p.turn_rate == RATE_RIGHT_ANGLE:
                pass
            else:
                p.turn_rate = RATES[min(RATES.index(p.turn_rate) + 1, len(RATES) - 1)]

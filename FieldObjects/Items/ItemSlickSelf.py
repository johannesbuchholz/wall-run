
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemSlickSelf:
    """
    Makes the collecting player turn faster.
    """
    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)

        self.duration = DURATION_LONG
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconSlickSelf.png"

        self.player = None  # Will be defined during method call activate.

        self.ignore = None

    def activate(self, player):
        """
        Increases the turn rate of the collecting player by one step.

        :param player: Player instance that picks up this item.
        """
        self.player = player
        # Choose next greater value from the RATE list
        if self.player.turn_rate == RATE_MAX or self.player.turn_rate == RATE_RIGHT_ANGLE:
            self.ignore = True
        else:
            self.player.turn_rate = RATES[min(RATES.index(self.player.turn_rate) + 1, len(RATES) - 1)]

    def deactivate(self):
        """"
        Decreases the turn rate of this player by one step.

        :return: None
        """
        # Choose next smaller value from the RATE list
        if self.ignore or self.player.turn_rate == RATE_RIGHT_ANGLE:
            pass
        else:
            self.player.turn_rate = RATES[max(RATES.index(self.player.turn_rate) - 1, 0)]

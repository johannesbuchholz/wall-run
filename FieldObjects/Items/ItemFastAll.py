
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemFastAll(ItemBase):
    """
    Increases the speed of every player but the collecting player by one step if possible.
    """
    # __init__ from base class.
    def __init__(self, pos, controller, gamescreen):
        ItemBase.__init__(self, pos, controller, gamescreen)
        self.duration = DURATION_NORMAL
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconFastAll.png"
        self.players_to_ignore = []  # Stores all players having max speed at the time of collecting this item.

    def activate(self, player):
        """
        Increases the speed of every player but the collecting player by one step if possible.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        for p in self.controller.players:
            if p == self.player or p.speed == SPEED_MAX:
                # Ignore player for this item
                self.players_to_ignore.append(p)
            else:
                # Choose next greater value from the SPEEDS list
                p.speed = SPEEDS[min(SPEEDS.index(p.speed) + 1, len(SPEEDS) - 1)]

    def deactivate(self):
        """
        :return: None
        """
        for p in self.controller.players:
            if p in self.players_to_ignore:
                pass
            else:
                # Choose next smaller value from the SPEEDS list
                p.speed = SPEEDS[max(SPEEDS.index(p.speed) - 1, 0)]

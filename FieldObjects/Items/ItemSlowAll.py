
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemSlowAll(ItemBase):
    """
    Decrease the speed of every player but the collecting player by one step.
    """
    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_NORMAL
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconSlowAll.png"
        self.players_to_ignore = []  # Stores all players to ignore by this item

    def activate(self, player):
        """
        Decrease the speed of every player but the collecting player by one step.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        for p in self.controller.players:
            if p == self.player or p.speed == SPEED_MIN:
                # Ignore player for this item
                self.players_to_ignore.append(p)
            else:
                # Choose next smaller value from the SPEEDS list
                p.speed = SPEEDS[max(SPEEDS.index(p.speed) - 1, 0)]

    def deactivate(self):
        """
        Increase the speed of every player but the collecting player by one step.

        :return: None
        """
        for p in self.controller.players:
            if p in self.players_to_ignore:
                pass
            else:
                # Choose next bigger value from the SPEEDS list
                p.speed = SPEEDS[min(SPEEDS.index(p.speed) + 1, len(SPEEDS) - 1)]


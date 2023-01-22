from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemBigAll(ItemBase):
    """
    Increases the size of every player but the collecting player by one step.
    """

    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_NORMAL
        self.image_path = "Data/IconBigAll.png"
        self.players_to_ignore = []  # Stores all players to ignore by this item

    def activate(self, player):
        """
        Increase the size of every player but the collecting player by one step.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        for p in self.controller.players:
            if p == self.player or p.size == SIZE_MAX:
                # Ignore player for this item
                self.players_to_ignore.append(p)
            else:
                # Choose next smaller value from the SPEEDS list
                p.size = SIZES[min(SIZES.index(p.size) + 1, len(SIZES) - 1)]

    def deactivate(self):
        """
        Decrease the size of every player but the collecting player by one step.

        :return: None
        """
        for p in self.controller.players:
            if p in self.players_to_ignore:
                pass
            else:
                # Choose next bigger value from the SPEEDS list
                p.size = SIZES[max(SIZES.index(p.size) - 1, 0)]


from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemClear(ItemBase):
    """
    Clears all walls within the game field.
    """
    # __init__ from base class.
    def __init__(self, pos, controller, gamescreen):
        ItemBase.__init__(self, pos, controller, gamescreen)
        self.duration = DURATION_INSTANT
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconClear.png"

    def activate(self, player):
        """
        Clears all walls within the game field.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        self.gamescreen.clear_walls()

    def deactivate(self):
        """
        Does nothing.

        :return: None
        """
        pass

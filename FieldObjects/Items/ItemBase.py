
from Utils.Const import *


class ItemBase:
    """
    This class represents the base class of all that may appear on the screen. This class should not be instantiated.
    """
    def __init__(self, pos, controller, gamescreen):
        """
        Creates an base Item.

        :param pos: Position of the item as tuple of size 2 (x,y)
        :param controller: Controller instance of the game screen.
        :param gamescreen: The gamescreen instance where this item is placed in.
        """

        self.pos = pos
        self.controller = controller
        self.gamescreen = gamescreen

        # This value should be manually adjusted depending on the respective Item that inherits this class.
        self.duration = DURATION_NORMAL
        self.image_path = "Data/DefaultIcon.png"  # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)

        self.player = None  # Will be defined during method call activate.

    def activate(self, player):
        """
        :param player: Player instance that picks up this item.
        """
        self.player = player

    def deactivate(self):
        """
        Deactivates the effect of this item. This function applies the reversed effect compared to the method activate.
        :return:
        """
        pass
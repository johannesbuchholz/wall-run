from Utils.Const import *


class ItemBase:
    """
    This class represents the base class of all items that may appear on the screen. It does not have any effect.
    """

    def __init__(self, controller, gamescreen):
        """
        Creates a base Item.

        :param controller: Controller instance of the game screen.
        :param gamescreen: The gamescreen instance where this item is placed in.
        """

        self.controller = controller
        self.gamescreen = gamescreen

        # This value should be manually adjusted depending on the respective Item that inherits this class.
        self.duration = DURATION_NORMAL
        self.image_path = "Data/DefaultIcon.png"

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

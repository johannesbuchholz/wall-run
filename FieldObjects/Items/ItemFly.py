
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemFly(ItemBase):
    """
    Makes the player flying and being able to cross any walls while not making a wall by himself during the time
    of this item being active.
    """
    # __init__ from base class.
    def __init__(self, pos, controller, gamescreen):
        ItemBase.__init__(self, pos, controller, gamescreen)
        self.duration = DURATION_SHORT
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconFly.png"

    def activate(self, player):
        """
        Sets the activating players flying attribute to True.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        self.player.flying = True

    def deactivate(self):
        """
        Sets the activating players flying attribute to False. If there is another younger ItemFly in action for
        this player, this function does nothing.

        :return: None
        """
        # check for already running instances of this item for this player
        items = [item
                 for item, _ in self.gamescreen.items_active
                 if item.player == self.player and item.__class__.__name__ == self.__class__.__name__
                 ]
        if len(items) > 1:
            # There is a younger Item instance running, so do nothing.
            return
        # Reset flying status
        self.player.flying = False

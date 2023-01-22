from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemRemoveBorder(ItemBase):
    """
    Toggles the game screen borders off.
    """

    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_NORMAL
        self.image_path = "Data/IconRemoveBorder.png"

    def activate(self, player):
        """
        Toggles the game screen borders off.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        # Toggle Effectively
        self.gamescreen.toggle_border(on=False)
        # Toggle visually
        self.gamescreen.display_border(on=False)

    def deactivate(self):
        """
        Toggles borders on again. If there is another younger Item of this kind in action, this function does nothing.

        :return: None
        """
        # check for already running instances of this item for ANY player
        items = [item
                 for item, _ in self.gamescreen.items_active
                 if item.__class__.__name__ == self.__class__.__name__
                 ]
        if len(items) > 1:
            # There is a younger Item instance running, so do nothing.
            return
        # Toggle Effectively
        self.gamescreen.toggle_border(on=True)
        # Toggle visually
        self.gamescreen.display_border(on=True)

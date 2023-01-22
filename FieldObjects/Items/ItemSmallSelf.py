from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemSmallSelf(ItemBase):
    """
    Increases the size of every player but the collecting player by one step.
    """

    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_NORMAL
        self.image_path = "Data/IconSmallSelf.png"
        self.was_at_min_size = False

    def activate(self, player):
        """
        Decrease the size of the collecting player by one step.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        if self.player.size == SIZE_MIN:
            self.was_at_min_size = True
        else:
            # Choose next smaller value from the SIZE list
            self.player.size = SIZES[max(SIZES.index(self.player.size) - 1, 0)]

    def deactivate(self):
        """
        Increase the size of the collecting player by one step.

        :return: None
        """
        items = [item
                 for item, _ in self.gamescreen.items_active
                 if item.player == self.player and item.__class__.__name__ == self.__class__.__name__
                 ]
        if self.was_at_min_size and len(items) > 1:
            # There is a younger Item instance running and the player was already at min size, so do nothing.
            return
        else:
            # Choose next greater value from the SPEEDS list
            self.player.size = SIZES[min(SIZES.index(self.player.size) + 1, len(SIZES) - 1)]

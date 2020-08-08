
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemFastSelf(ItemBase):
    """
    Increases the speed of the collecting player by one step if possible.
    """
    # __init__ from base class.
    def __init__(self, pos, controller, gamescreen):
        ItemBase.__init__(self, pos, controller, gamescreen)
        self.duration = DURATION_SHORT
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconFastSelf.png"
        self.was_at_max_speed = False

    def activate(self, player):
        """
        Increases the speed of the collecting player by one step if possible.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        if self.player.speed == SPEED_MAX:
            return
        else:
            # Choose next greater value from the SPEEDS list
            self.player.speed = SPEEDS[min(SPEEDS.index(self.player.speed) + 1, len(SPEEDS) - 1)]

    def deactivate(self):
        """
        Decreases the speed of this player by one step unless the player already was on max speed when collecting
        this item. In that case the duration is refreshed, by ignoring this older items deactivate effect.

        :return: None
        """
        # check for already running instances of this item for this player
        items = [item
                 for item, _ in self.gamescreen.items_active
                 if item.player == self.player and item.__class__.__name__ == self.__class__.__name__
                 ]
        if self.was_at_max_speed and len(items) > 1:
            # There is a younger Item instance running and the player was already at max speed, so do nothing.
            return
        else:
            # Choose next smaller value from the SPEEDS list
            self.player.speed = SPEEDS[max(SPEEDS.index(self.player.speed) - 1, 0)]

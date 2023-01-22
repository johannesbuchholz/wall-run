from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemSlowSelf(ItemBase):
    """
    Decreases the speed of the collecting player by one step.
    """

    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_SHORT
        self.image_path = "Data/IconSlowSelf.png"
        self.ignore = False  # Indicates if this Items effect should be ignored

    def activate(self, player):
        """
        Decreases the speed of the collecting player by one step.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        # Choose next smaller value from the SPEEDS list
        if self.player.speed == SPEED_MIN:
            self.ignore = True
        else:
            self.player.speed = SPEEDS[max(SPEEDS.index(self.player.speed) - 1, 0)]

    def deactivate(self):
        """
        Increases the speed of this player by one step.

        :return: None
        """
        # Choose next greater value from the SPEEDS list
        if self.ignore:
            pass
        else:
            self.player.speed = SPEEDS[min(SPEEDS.index(self.player.speed) + 1, len(SPEEDS) - 1)]

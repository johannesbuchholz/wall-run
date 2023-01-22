from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemZiggZaggAll(ItemBase):
    """
    sets the collecting everybody's but the collecting players turn rate to RATE_RIGHT_ANGLE.
    Every turn will then be a 90 degree turn.
    """

    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_SHORT
        self.image_path = "Data/IconZiggZaggAll.png"

    def activate(self, player):
        """
        Sets the collecting everybody's but the collecting players turn rate to RATE_RIGHT_ANGLE.
        Every turn will then be a 90 degree turn.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        # Set turn rate
        for p in self.controller.players:
            if p != self.player:
                p.turn_rate = RATE_RIGHT_ANGLE
                p.move_command = DIR_STRAIGHT  # Reset move command in order to avoid instant death.

    def deactivate(self):
        """
        Resets all player's but the collecting player's turn rate to RATE_NORMAL.
        If there is another younger Item in action for this player, this function does nothing.

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
        # Reset turn rate
        for p in self.controller.players:
            if p != self.player:
                p.turn_rate = RATE_NORMAL

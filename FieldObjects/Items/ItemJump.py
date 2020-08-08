
from Utils.Const import *


class ItemJump:
    """
    Moves the players 30 times the players speed pixels in forward direction.
    """
    # __init__ from base class.
    def __init__(self, pos, controller, gamescreen):
        self.pos = pos
        self.controller = controller
        self.gamescreen = gamescreen

        self.duration = DURATION_ONETIME
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconJump.png"

        self.player = None  # Will be defined during method call activate.

        self.previous_speed = None

    def activate(self, player):
        """
        Sets the players speed to 20 times the players speed in pixels per tick for one tick.

        :param player: Player instance that picks up this item.
        """
        self.player = player
        self.previous_speed = self.player.speed
        self.player.speed = 30 * self.player.speed

    def deactivate(self):
        """
        Resets the players speed to its previous value.

        :return:
        """
        self.player.speed = self.previous_speed

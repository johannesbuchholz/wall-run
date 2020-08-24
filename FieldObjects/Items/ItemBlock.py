
from numpy import random
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemBlock(ItemBase):
    """
    Places a Block randomly on the field.
    """
    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_INFINITE  # No effective usage
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconBlock.png"
        self.rng = random.default_rng()
        self.blocksize = 80

    def activate(self, player):
        """
        Places a random square on the field.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        x_rand = self.rng.integers(self.blocksize, self.controller.field_size - self.blocksize)
        y_rand = self.rng.integers(self.blocksize, self.controller.field_size - self.blocksize)
        # Visually
        self.gamescreen.field_image.put(data="White",
                                        to=(x_rand, y_rand, x_rand + self.blocksize, y_rand + self.blocksize)
                                        )
        # Effectively
        self.gamescreen.walls[x_rand:x_rand+self.blocksize, y_rand:y_rand+self.blocksize] = -1

    def deactivate(self):
        """
        Does nothing.

        :return: None
        """
        pass

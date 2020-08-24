
from numpy.random import default_rng
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *


class ItemPackage(ItemBase):
    """
    Places three random items on the game field.
    """
    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_INSTANT
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconPackage.png"
        self.rng = default_rng()

    def activate(self, player):
        """
        Places a random square on the field.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player

        random_item_names = self.rng.choice(self.controller.item_names, size=3)
        for name in random_item_names:
            x_rand = self.rng.integers(ITEMSIZE, self.controller.field_size - ITEMSIZE)
            y_rand = self.rng.integers(ITEMSIZE, self.controller.field_size - ITEMSIZE)
            self.gamescreen.place_item(name=name, pos=(x_rand, y_rand))

    def deactivate(self):
        """
        Does nothing.

        :return: None
        """
        pass

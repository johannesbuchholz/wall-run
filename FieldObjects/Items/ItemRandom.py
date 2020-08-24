
from numpy.random import default_rng
from FieldObjects.Items.ItemBase import ItemBase
from Utils.Const import *
from importlib import import_module


class ItemRandom(ItemBase):
    """
    Activates a random item effect.
    """
    # __init__ from base class.
    def __init__(self, controller, gamescreen):
        ItemBase.__init__(self, controller, gamescreen)
        self.duration = DURATION_INSTANT
        # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)
        self.image_path = "Data/IconRandom.png"
        self.rng = default_rng()

        self.available_item_names = self.controller.all_items
        if self.available_item_names.__contains__("ItemRandom"):
            self.available_item_names.remove("ItemRandom")

    def activate(self, player):
        """
        Creates a random item instance and acts as if player collecvted this item.

        :param player: Player instance that collected this item.
        :return: None
        """
        self.player = player
        # emulate a random item
        item_to_create = self.rng.choice(self.available_item_names)
        item_module = import_module("FieldObjects.Items."+item_to_create)
        item_class = getattr(item_module, item_to_create)
        emulated_item = item_class(self.controller, self.gamescreen)

        # Activate the random item and place it in the gamescreen's active items.
        emulated_item.activate(self.player)
        self.gamescreen.items_active.append((emulated_item, self.gamescreen.tick_count + emulated_item.duration))

    def deactivate(self):
        """
        Does nothing.

        :return: None
        """
        pass

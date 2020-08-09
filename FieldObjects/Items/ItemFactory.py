"""
Creates instances of classes from this package by name.

In order to use this factory for a new defined item class, simply add the appropriate import statement
at the beginning of this module.
"""

# --- Add import statements for all item classes that shall be targeted by the item instantiation method. ---

from FieldObjects.Items.ItemFly import ItemFly
from FieldObjects.Items.ItemRemoveBorder import ItemRemoveBorder
from FieldObjects.Items.ItemZiggZaggSelf import ItemZiggZaggSelf
from FieldObjects.Items.ItemZiggZaggAll import ItemZiggZaggAll
from FieldObjects.Items.ItemClear import ItemClear
from FieldObjects.Items.ItemFastAll import ItemFastAll
from FieldObjects.Items.ItemFastSelf import ItemFastSelf
from FieldObjects.Items.ItemSlowAll import ItemSlowAll
from FieldObjects.Items.ItemSlowSelf import ItemSlowSelf
from FieldObjects.Items.ItemJump import ItemJump
from FieldObjects.Items.ItemGlueAll import ItemGlueAll
from FieldObjects.Items.ItemSlickSelf import ItemSlickSelf
from FieldObjects.Items.ItemBlock import ItemBlock
from FieldObjects.Items.ItemRandom import ItemRandom
from FieldObjects.Items.ItemPackage import ItemPackage


# Stores all imported classes in a dictionary and thus makes them callable by their names.
all_modules = globals()


def create_item_by_name(name, *args):
    """
    Creates an instance of the Item given by name.

    :param args: Arguments to pass to the constructor of the given class.
    :param name: String, Name of the class to be instantiated.
    :return: Item object.
    """
    return all_modules[name](*args)

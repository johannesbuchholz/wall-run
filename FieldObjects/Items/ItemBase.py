
from Utils.Const import *


def create_dot_trace_layers(pos):
    """
    This function creates the dot trace (the picture) of this item. The picture will be a square of size
    Const.ITEMSIZE.

    The ItemBase picture is just a white border on the square.

    :param pos: Tuple of size 2 of int indicating the position where the picture should be drawn (upper left corner).
    :return: Dot trace of this item which is a list of tuples of size two. Each tuple contains a list of tuples and
    a color name. Each such tuple defines a color layer which consists of the absolute positions of the pixels and
    its respective color. Example:
        [([(26,29), (26,30), (26,31)], "blue"),
         ([(27,29), (27,30), (27,31)], "green"),
         ...
        ]

    The base version simply draws a white square of size 10 (pixels).
    """
    dot_trace_layers = []
    x, y = pos
    # Create white dots
    white_dots = []
    white_dots += [(x+a, y) for a in range(ITEMSIZE)]  # Top row
    white_dots += [(x + a, y+ITEMSIZE) for a in range(ITEMSIZE)]  # Bottom row
    white_dots += [(x, y + a) for a in range(1, ITEMSIZE-1)]  # Left column excluding top and bottom pixel
    white_dots += [(x+ITEMSIZE, y + a) for a in range(1, ITEMSIZE-1)]  # Right column excluding top and bottom pixel
    white_layer = (white_dots, "white")
    # Append layers
    dot_trace_layers.append(white_layer)
    # output layers
    return dot_trace_layers


class ItemBase:
    """
    This class represents the base class of all that may appear on the screen. This class should not be instantiated.
    """
    def __init__(self, pos, controller, gamescreen):
        """
        Creates an base Item.

        :param pos: Position of the item as tuple of size 2 (x,y)
        :param controller: Controller instance of the game screen.
        :param gamescreen: The gamescreen instance where this item is placed in.
        """

        self.pos = pos
        self.controller = controller
        self.gamescreen = gamescreen

        # This value should be manually adjusted depending on the respective Item that inherits this class.
        self.duration = DURATION_NORMAL
        self.image_path = "Data/DefaultIcon.png"  # Relative path to item icon. (from __main__, 20 x 20 pixels, .png)

        self.player = None  # Will be defined during method call activate.
        self.dot_trace_layers = create_dot_trace_layers(self.pos)

    def activate(self, player):
        """
        :param player: Player instance that picks up this item.
        """
        self.player = player

    def deactivate(self):
        """
        Deactivates the effect of this item. This function applies the reversed effect compared to the method activate.
        :return:
        """
        pass
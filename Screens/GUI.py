import os
import pathlib
import sys
from tkinter import (Tk, Frame)

from Screens import (RuleScreenClass, OptionScreenClass, GameScreenClass, TitleScreenClass)


class GUI(Tk):
    """
    This class provides field general user interface for the game.
    There are three types of windows:
        1. Title Screen
        2. Game Window
        3. Options
        4. Rules
    """

    def __init__(self):
        """
        This class represents field GUI instance of the game.
        It initialises all frames and brings the title screen to the front.
        """

        # ATTRIBUTES
        # size related
        self.scale = 1.0
        self.option_size = "1200x900"
        self.canvas_size = 890
        self.field_size = 860

        # font related
        self.font_basic = ("Sans", int(12 * self.scale))
        self.font_medium = ("Sans", int(16 * self.scale))
        self.font_big = ("Sans", int(26 * self.scale))
        self.font_bigger = ("Sans", int(38 * self.scale))

        # Screen initialisation
        Tk.__init__(self)
        self.geometry(self.option_size)

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.title("Wall Run")
        # self.iconphoto(False, PhotoImage(file='.png'))

        # game related
        # dummy_player1 = PlayerBotConeStrategy(name="Bot1", color="Red")
        # dummy_player2 = PlayerBotContLossStrategy(name="Bot2", color="Blue")
        # dummy_player3 = PlayerBotContLossStrategy(name="Bot3", color="Orange")
        self.players = [
            # dummy_player1,
            # dummy_player2,
            # dummy_player3
        ]
        self.max_rounds = 5
        # All items registered
        self.all_items = ["ItemClear", "ItemBlock", "ItemJump", "ItemGlueAll", "ItemSlickSelf", "ItemFly",
                          "ItemRemoveBorder", "ItemZiggZaggSelf", "ItemZiggZaggAll", "ItemFastAll", "ItemFastSelf",
                          "ItemSlowAll", "ItemSlowSelf", "ItemRandom", "ItemPackage", "ItemBigAll", "ItemSmallSelf"]
        # All items chosen for the current game. Might be changed by options.
        self.item_names = list(self.all_items)
        # GUI objects
        self.frames = {"Title": TitleScreenClass.TitleScreen(parent=container, controller=self),
                       "Rules": RuleScreenClass.RuleScreen(parent=container, controller=self),
                       "Options": OptionScreenClass.
                       OptionScreen(parent=container, controller=self),
                       "Game": GameScreenClass.GameScreen(parent=container, controller=self)}

        self.frames["Title"].grid(row=0, column=0, sticky="nsew")
        self.frames["Game"].grid(row=0, column=0, sticky="nsew")
        self.frames["Rules"].grid(row=0, column=0, sticky="nsew")
        self.frames["Options"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("Title")

        self.frames["Options"].apply()  # apply basic settings

    def show_frame(self, page_name):
        """
        Show field frame for the given page name
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def exit_session(self):
        """
        Destroys self and exits the python kernel.
        """
        self.destroy()
        exit()


def get_execution_path() -> str:
    execution_path = pathlib.Path(sys.argv[0])
    if execution_path.is_absolute():
        if execution_path.is_file():
            return str(execution_path.parent)
        else:
            return str(execution_path)
    else:
        if execution_path.is_file():
            return os.getcwd() + "/" + str(execution_path.parent)
        else:
            return os.getcwd() + "/" + str(execution_path)

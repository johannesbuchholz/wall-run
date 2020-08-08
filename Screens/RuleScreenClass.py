
from tkinter import *


class RuleScreen(Frame):
    def __init__(self, controller, parent):
        Frame.__init__(self, master=parent)
        self.parent = parent
        self.controller = controller
        return

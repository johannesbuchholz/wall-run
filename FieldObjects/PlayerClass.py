
from pynput import keyboard
from Utils.Const import *


class Player:
    """
    Represents one player and stores all player specific Information.
    """
    def __init__(self, name, color, keys={"left": keyboard.Key.left, "right": keyboard.Key.right}, alive=True,
                 speed=SPEED_NORMAL, size=SIZE_NORMAL, flying=False, pos=(100, 100), angle=0):
        """
        Initialises all attributes. These are
            name: string,
            color: string
            control keys: {left:, right:}
            status related:
                alive: bool,
                speed: int,
                size: int (radius of the dot in pixels),
                flying: bool
            movement related:
                position: (int, int)
                angle: facing angle as int within [0, 360), 0 is facing east, 90 is facing north etc
                turn_rate: angle difference possible per tick (int from [0, 359])
            wins: number of won rounds.
        The listener is started by calling
            listener.start()
            listener.join() # Optional
        One can create a new listener by calling make_listener.
        which starts a blocking thread monitoring the keyboard. Stop the Listener by calling stop().
        """

        # ATTRIBUTES
        # Basic
        self.name = name
        self.color = color
        self.keys = keys

        # Status
        self.alive = alive
        self.speed = speed
        self.size = size
        self.flying = flying

        # Directional
        self.pos = pos
        self.angle = angle
        self.turn_rate = RATE_NORMAL

        self.wins = 0

        # FUNCTIONAL ATTRIBUTES
        self.move_command = DIR_STRAIGHT  # -1: left (DIR_LEFT) , 0: straight (DIR_STRAIGHT), 1: right (DIR_RIGHT)
        self.listener = None  # is defined in function call self.make_listener
        self.dot_trace = None  # Will be defined during put_players in the GameScreen Class.

    def make_listener(self):
        """
        Creates a new keyboard listener for this player and stores it in the attribute
            self.listener

        :return: None
        """

        # LISTENER
        def on_press(key):
            # Movement functionality
            if key == self.keys["left"]:
                self.move_command = DIR_LEFT
            elif key == self.keys["right"]:
                self.move_command = DIR_RIGHT
            else:
                return

        def on_release(key):
            if key == self.keys["left"] or key == self.keys["right"]:
                self.move_command = DIR_STRAIGHT
            else:
                return

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)

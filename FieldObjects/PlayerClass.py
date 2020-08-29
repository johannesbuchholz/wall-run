
from pynput import keyboard
from Utils.Const import *
from numpy import sin, cos, radians


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

        self.wins = 0

        # Status
        self.alive = alive
        self.speed = speed
        self.size = size
        self.flying = flying
        self.turn_rate = RATE_NORMAL

        # Positional
        self.pos = pos
        self.angle = angle

        self.dot_trace = None  # Will be defined during put_players and move in the GameScreen Class.
        self.data_strings = None  # Used for efficiently drawing the player's dot-trace
        self.rect_corners = None  # Used for efficiently drawing the player's dot-trace
        self.collision_head = []  # Defined during the call of self.compute_collision_head.
        self.base_tolerance = 6  # Higher values mean more tolerance heads (also longer tick-processing)
        self.tolerance_heads = []  # Stores the last self.tolerance_count dot_traces

        # FUNCTIONAL ATTRIBUTES
        self.move_command = DIR_STRAIGHT  # -1: left (DIR_LEFT) , 0: straight (DIR_STRAIGHT), 1: right (DIR_RIGHT)
        self.listener = None  # is defined in function call self.make_listener
        self.key_is_held_down = False  # Indicate if a move-command key is currently held down.

    def update_tolerance_heads(self):
        """
        Copies the current dot_trace into the list self.tolerance_heads and removes the oldest one.

        :return:
        """
        tolerance_count = max(1, int(self.base_tolerance / self.speed))
        self.tolerance_heads.append(self.dot_trace)
        if len(self.tolerance_heads) > tolerance_count:
            self.tolerance_heads.__delitem__(0)

    def compute_collision_head(self):
        """
        Computes the "upper" half of the player's dot which will be used for collision checking. In particular, this is
        a subset of the player's dot-trace which consists of the half-circle facing in the current direction of
        movement including the diameter.

        The result of this computation is saved in self.collision_head as a list of tuple of size of int 2.

        :return:
        """
        v1, v2 = cos(radians(self.angle)), sin(radians(self.angle))
        p, q = self.pos
        self.collision_head = [(x, y) for (x, y) in self.dot_trace if (x-p)*v1+(y-q)*v2 >= 0]

    def pixel_in_tolerance(self, pix):
        """
        Checks if the given pixel is contained in the tolerance dot-traces.

        :param pix: tuple of size 2 of int, representing the pixel i question.
        :return: bool, True if the pix is contained in self.tolerance_heads, False otherwise.
        """
        for dot_trace in self.tolerance_heads:
            if pix in dot_trace:
                return True
        return False

    def make_listener(self):
        """
        Creates a new keyboard listener for this player and stores it in the attribute
            self.listener

        :return: None
        """
        # LISTENER
        def on_press(key):
            # Movement functionality
            if self.key_is_held_down:
                # Prevent sending multiple move commands if movement key is held down.
                return
            else:
                if key == self.keys["left"]:
                    self.key_is_held_down = True
                    self.move_command = DIR_LEFT
                elif key == self.keys["right"]:
                    self.key_is_held_down = True
                    self.move_command = DIR_RIGHT
                else:
                    return

        def on_release(key):
            if key == self.keys["left"] or key == self.keys["right"]:
                self.key_is_held_down = False
                self.move_command = DIR_STRAIGHT
            else:
                return

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)

from numpy import sin, cos, radians
from pynput import keyboard

from Utils.Const import *


class Player:
    """
    Represents one player and stores all player specific Information.
    """

    def __init__(self, name, color, keys={"left": keyboard.Key.left, "right": keyboard.Key.right}, alive=True,
                 speed=SPEED_NORMAL, size=SIZE_NORMAL, flying=False, pos=(100, 100), angle=0):
        """
        Initialises all attributes.
        Additional information on certain fields:
            name: string,
            color: string, matching a python color string.
            keys: dict with keys "left" and "right" mapping to pynput.keyboard.Key.
            alive: bool,
            speed: int,
            size: int (radius of the dot in pixels),
            flying: bool
            position: (int, int)
            angle: facing angle as int within [0, 360), 0 is facing east, 90 is facing south etc.
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
        self.turn_rate = RATE_NORMAL  # Angle the player can turn each tick (int from [0, 359])

        # Positional
        self.pos = pos
        self.angle = angle

        self.dot_trace = None  # Will be defined during put_players and move in the GameScreen Class.
        self.data_strings = None  # Used for efficiently drawing the player's dot-trace.
        self.rect_corners = None  # Used for efficiently drawing the player's dot-trace.
        self.collision_head = []  # Defined during the call of self.compute_collision_head.
        self.head_tolerance_count = 2  # Number of latest player positions that do not count for collision.
        self.tolerance_heads = []  # Stores the last self.tolerance_count dot_traces

        # FUNCTIONAL ATTRIBUTES
        self.move_command = DIR_STRAIGHT  # -1: left (DIR_LEFT) , 0: straight (DIR_STRAIGHT), 1: right (DIR_RIGHT)
        self.listener = None  # is defined in function call self.make_listener
        self.key_is_held_down = False

    def update_tolerance_heads(self):
        """
        Copies the current dot_trace into the list self.tolerance_heads and removes the oldest one.

        :return:
        """
        self.tolerance_heads.append(self.dot_trace)
        if len(self.tolerance_heads) > self.head_tolerance_count:
            self.tolerance_heads.__delitem__(0)

    def compute_collision_head(self):
        """
        Computes the "upper" half of the player's dot which will be used for collision checking. In particular, this is
        a subset of the player's dot-trace which consists of the half-circle facing in the current direction of
        movement including the diameter.

        The result of this computation is saved in self.collision_head as a list of tuple of size of int 2.

        :return: None.
        """
        current_facing_angle = self.angle
        if self.move_command == DIR_LEFT:
            current_facing_angle += self.turn_rate
        elif self.move_command == DIR_LEFT:
            current_facing_angle -= self.turn_rate
        v1, v2 = cos(radians(current_facing_angle)), sin(radians(current_facing_angle))
        p, q = self.pos
        self.collision_head = [(x, y) for (x, y) in self.dot_trace if (x - p) * v1 + (y - q) * v2 >= 0]

    def pixel_in_tolerance(self, pix):
        """
        Checks if the given pixel is contained in the tolerance dot-traces.

        :param pix: tuple of size 2 of int, representing the pixel i question.
        :return: bool, True if the pix is contained in self.tolerance_heads , False otherwise.
        """
        for head_trace in self.tolerance_heads:
            if pix in head_trace:
                return True
        return False

    def make_listener(self):
        """
        Creates a new keyboard listener for this player and stores it in the attribute
            self.listener

        :return: None
        """

        def on_press(key):
            if self.key_is_held_down and self.turn_rate == RATE_RIGHT_ANGLE:
                self.move_command = DIR_STRAIGHT
                return
            if key == self.keys["left"] and self.move_command != DIR_LEFT:
                self.key_is_held_down = True
                self.move_command = DIR_LEFT
            elif key == self.keys["right"] and self.move_command != DIR_RIGHT:
                self.key_is_held_down = True
                self.move_command = DIR_RIGHT

        def on_release(key):
            if key == self.keys["left"] or key == self.keys["right"]:
                self.key_is_held_down = False
                self.move_command = DIR_STRAIGHT

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    def compute_move_command(self, walls):
        """
        Computes an appropriate move-direction according to the current walls placed on the field and this players
        position.

        Tis does nothing for the base player class.

        :param walls: 2-d numpy array array of int,  -1 entries are supposed to be walls.
        :return: None
        """
        return

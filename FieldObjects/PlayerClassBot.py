from FieldObjects.PlayerClass import Player
from pynput import keyboard
from Utils.Const import *
from numpy import shape, sqrt

from Utils.HelperFunctions import (stochastic_gradient_descent, is_contained_in_cone, is_point_on_left_side)
from Utils.TargetFunctions import target_function_cont, target_function_cont_d


class PlayerBotContLossStrategy(Player):
    """
    Represents one player and stores all player specific Information.
    """

    def __init__(self, name, color, keys={"left": keyboard.Key.left, "right": keyboard.Key.right}, alive=True,
                 speed=SPEED_NORMAL, size=SIZE_NORMAL, flying=False, pos=(100, 100), angle=0):
        """
        Calls the inherited __init__-method
        """
        Player.__init__(self, name, color, keys, alive, speed, size, flying, pos, angle)

        self.busy = False
        self.target_angle = None
        self.target_tolerance = self.turn_rate  # angle difference under which the target is considered as reached.
        self.scope = 60  # Look-Out number of pixels in each direction of the current position

    def compute_move_command(self, walls):
        """
        Computes an appropriate move-direction according to the current walls placed on the field and this players
        position.

        :param walls: 2-d numpy array array of int,  -1 entries are supposed to be walls.
        :return: None
        """
        if self.busy:
            return
        elif not self.alive:
            self.target_angle = None
            return

        self.busy = True
        self.target_tolerance = self.turn_rate

        # compute new target-angle
        x, y = self.pos
        field_size, _ = shape(walls)
        wall_points = [(i, j)
                       for i in range(x - self.scope, x + self.scope + 1)
                       for j in range(y - self.scope, y + self.scope + 1)
                       if walls[i % field_size, j % field_size] == -1]
        if wall_points:
            t = stochastic_gradient_descent(f=target_function_cont, deriv=target_function_cont_d,
                                            x0=self.angle, stepsize=270, samples=wall_points, batchsize=20,
                                            maxit=15, choose_best=False, **{"pos": self.pos, "lam": 0.0})
            self.target_angle = round(t) % 360
        else:
            self.target_angle = self.angle
        self.issue_move_command()
        self.busy = False
        return

    def is_target_angle_reached(self):
        """
        Check if the target-angle was reached by the last execution of the currently present move-command.

        :return: boolean
        """
        # print("----------------------------")
        # print("current angle: ", self.angle)
        # print("target: ", self.target_angle)
        lower_bound = (self.target_angle - self.target_tolerance) % 360
        upper_bound = (self.target_angle + self.target_tolerance) % 360
        if upper_bound < lower_bound:
            upper_bound_alt = 359
            lower_bound_alt = 0
        else:
            upper_bound_alt = upper_bound
            lower_bound_alt = lower_bound
        # print(lower_bound <= self.angle <= upper_bound_alt or lower_bound_alt <= self.angle <= upper_bound)
        return lower_bound <= self.angle <= upper_bound_alt or lower_bound_alt <= self.angle <= upper_bound

    def issue_move_command(self):
        """
        Changes the current move command whether the target-angle is reached faster by field left or right turn.
        If the current target-angle is reached this function makes the player move straight.

        :return: None
        """
        if self.is_target_angle_reached():
            self.move_command = DIR_STRAIGHT
            return
        lower_bound = (self.target_angle - 180) % 360
        upper_bound = self.target_angle
        if upper_bound < lower_bound:
            lower_bound_alt = 0
            upper_bound_alt = 359
        else:
            lower_bound_alt = lower_bound
            upper_bound_alt = upper_bound
        if lower_bound <= self.angle <= upper_bound_alt or lower_bound_alt <= self.angle <= upper_bound:
            self.move_command = DIR_RIGHT
        else:
            self.move_command = DIR_LEFT


class PlayerBotConeStrategy(Player):
    """
   Represents one player and stores all player specific Information.
   """

    def __init__(self, name, color, keys={"left": keyboard.Key.left, "right": keyboard.Key.right}, alive=True,
                 speed=SPEED_NORMAL, size=SIZE_NORMAL, flying=False, pos=(100, 100), angle=0):
        """
        Calls the inherited __init__-method
        """
        Player.__init__(self, name, color, keys, alive, speed, size, flying, pos, angle)

        self.busy = False
        self.scope_radius = 80  # radius around pos to consider wall-points
        self.apex_angle = 40  # apex angle of cone from current position, should be even and be less than 180 degrees.

    def compute_move_command(self, walls):
        """
        Computes an appropriate move-direction according to the current walls placed on the field and this players
        position.

        :param walls: 2-d numpy array array of int,  -1 entries are supposed to be walls.
        :return: None
        """
        # if self.busy:
        #     return
        #  self.busy = True
        wall_points = self.get_normed_wall_points_in_scope(walls)
        angle_step = 10
        tolerance_close_distance = 10
        danger_score_left = 0.0
        danger_score_right = 0.0
        print("---------------------------")
        # left cone
        for i, j in wall_points:
            norm = sqrt(i ** 2 + j ** 2)
            if (is_contained_in_cone(i, j, facing_angle=self.angle - angle_step, apex_angle=self.apex_angle)
                    and norm > tolerance_close_distance):
                danger_score_left -= norm
            if (is_contained_in_cone(i, j, facing_angle=self.angle + angle_step, apex_angle=self.apex_angle)
                    and norm > tolerance_close_distance):
                danger_score_right -= norm
        x, y = self.pos
        print("current pos (x, y)=", x, y)
        print("current angle =", self.angle)
        print("left: ", danger_score_left)
        print("right: ", danger_score_right)

        if danger_score_left > danger_score_right:
            self.move_command = DIR_RIGHT
        elif danger_score_left < danger_score_right:
            self.move_command = DIR_LEFT
        else:
            self.move_command = DIR_STRAIGHT
        #  self.busy = False

    def compute_move_command_old(self, walls):
        """
        Computes an appropriate move-direction according to the current walls placed on the field and this players
        position.

        :param walls: 2-d numpy array array of int,  -1 entries are supposed to be walls.
        :return: None
        """
        if self.busy:
            return
        self.busy = True

        wall_points = self.get_normed_wall_points_in_scope(walls)
        print("---------------------------")
        x, y = self.pos
        print("current pos (x, y)=", x, y)
        print("current angle =", self.angle)
        print("Wallpoint n: ", len(wall_points))
        left_score = 0
        right_score = 0
        cone_points = []
        for i, j in wall_points:
            if is_contained_in_cone(i, j, facing_angle=self.angle, apex_angle=self.apex_angle):
                cone_points.append((i, j))
                if is_point_on_left_side(self.angle, i, j):
                    left_score += 1 #/ sqrt(i ** 2 + j ** 2)
                else:
                    right_score += 1 #/ sqrt(i ** 2 + j ** 2)
        if left_score < right_score:
            self.move_command = DIR_LEFT
        elif left_score > right_score:
            self.move_command = DIR_RIGHT
        else:
            self.move_command = DIR_STRAIGHT
        print("Cone points: ", len(cone_points))
        print("Left points: ", left_score)
        print("Right points: ", right_score)
        print("New move command: ", self.move_command)
        self.busy = False

    def get_normed_wall_points_in_scope(self, walls):
        """
        Returns a list of 2-D points occurring in a self.scope_radius around the current position moving each point
        as if self.pos is the origin.

        :param walls: Squared 2-D numpy array of size greater than self.scope_radius.
        :return: List of tuple of size 2 of int, coordinates from walls where a -1 entry is present.
        The returned are moved such that their respective origin is self.pos.
        """
        # Convention is that walls contains -1 at [x, y] if the canvas pixel (x, y) shows a wall.
        x, y = self.pos
        n, _ = shape(walls)
        return [(i-x, j-y)
                for i in range(x - self.scope_radius, x + self.scope_radius + 1)
                for j in range(y - self.scope_radius, y + self.scope_radius + 1)
                if walls[i % n, j % n] == -1]

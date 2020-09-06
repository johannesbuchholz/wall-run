from FieldObjects.PlayerClass import Player
from pynput import keyboard
from Utils.Const import *
from numpy import sin, cos, radians, arctan, rad2deg, argwhere
from random import choices
from scipy.optimize import minimize


class PlayerBot(Player):
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
        self.scope = 80  # Look-Out number of pixels in each direction of the current position
        self.cone_angle = 2  # apex angle of cone from current position, should be even.

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

        # if not self.target_angle or self.is_target_angle_reached():
        # print("target angle is reached: ", self.target_angle)
        # compute new target-angle
        x, y = self.pos
        scope_matrix = walls[x - self.scope:x + self.scope + 1,
                       y - self.scope:y + self.scope + 1]  # side length equals 2*scope+1
        wall_points = argwhere((scope_matrix == -1))
        t = stochastic_gradient_descent(f=self.target_function_cont, deriv=self.target_function_cont_deriv,
                                        x0=self.angle, stepsize=1, samples=wall_points, batchsize=None,
                                        maxit=10, choose_best=False, **{"a": self.cone_angle}
                                        )
        self.target_angle = (360 - round(t)) % 360  # game-angles increase clockwise, hence we adjust this here
        print("NEW target angle: ", self.target_angle)
        self.issue_move_command()
        self.busy = False
        return

    def is_target_angle_reached(self):
        """
        Check if the target-angle was reached by the last execution of the currently present move-command.

        :return: boolean
        """
        print("----------------------------")
        print("current angle: ", self.angle)
        print("target: ", self.target_angle)
        lower_bound = (self.target_angle - self.target_tolerance) % 360
        upper_bound = (self.target_angle + self.target_tolerance) % 360
        if upper_bound < lower_bound:
            upper_bound_alt = 359
            lower_bound_alt = 0
        else:
            upper_bound_alt = upper_bound
            lower_bound_alt = lower_bound
        print(lower_bound <= self.angle <= upper_bound_alt or lower_bound_alt <= self.angle <= upper_bound)
        return lower_bound <= self.angle <= upper_bound_alt or lower_bound_alt <= self.angle <= upper_bound

    def issue_move_command(self):
        """
        Changes the current move command whether the target-angle is reached faster by a left or right turn.
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

    def target_function_cont(self, t, wall_points, a):
        """
        Continuous loss-function for a given target angle t, tolerance value a (similar to cone apex-angle) and the
        current wall-scope.\n
        The idea is to punish a target angle t, where many wall-points lie "close" to the facing-axis given by t.
        What close actually means, can be adjusted with the tolerance value.
        The Loss function then can be written as:

        - Loss(t) = sum over {(x, y)-wall_points} of -((b(x,y) - t)/(1+a))**2
        - b(x,y) = arctan(y/x)

        Explanation of the terms:
            Consider a 2-d plane and a cone at the origin with apex angle a and facing angle t,
            where t=0 means facing east.
            Angles increase counter-clockwise. We search for an angle t, where fewest points of walls with entry -1 lie
            inside that cone.\n
            A point (x, y) lies within the cone, if and only if arctan(y/x) is in [t-a/2, t+a/2]. The above Loss-Function
            is the attempt to define a continuous representation of that idea.

        :param t: float, angle in degree in [0, 360), this is the objective-parameter to minimize over.
        :param wall_points: list of tuple of size 2 of int, all locations of wall entries (-1 values)
        The coordinates should be shifted, such that (0, 0) is the player's current position.
        :param a: float > 0, tolerance value, greater a results in lesser punishment.
        :return: float, Loss function value of the give target angle (will always be <= 0).
        """
        temp_sum = 0
        for i, j in wall_points:
            # compute coordinates for each pixel, such that self.pos is the origin.
            x = i - self.scope
            y = j - self.scope
            temp_sum -= (arctan_lim(x, y) - t) ** 2
        return 1 / (1 + a) ** 2 * temp_sum

    def target_function_cont_deriv(self, t, wall_points, a):
        """
        First derivative of the target function defined in self.target_function_cont.

        :param t: float, angle in [0, 360), this is the objective-parameter to minimize over.
        :param wall_points: 2-d numpy array of int, contains either 0 or -1 entries.
        The matrix is build such that the pixes at wall_points[scope, scope] is the player's position.
        :param a: float > 0, tolerance value, greater a results in lesser punishment.
        :return: float, Loss function value of the give target angle (will always be <= 0).
        """
        temp_sum = 0
        for i, j in wall_points:
            # compute coordinates for each pixel, such that self.pos is the origin.
            x = i - self.scope
            y = j - self.scope
            temp_sum += (arctan_lim(x, y) - t)
        return 2 / (1 + a) ** 2 * temp_sum


def stochastic_gradient_descent(f, deriv, x0, stepsize, samples, batchsize=5, maxit=100, choose_best=False, **kwargs):
    """
    Computes the approximate minimum of the function, that produced jac, which is its first derivative.

    :param f: target loss function: (x, samples, **kwargs) -> float
    :param deriv: function: (x, samples, **kwargs) -> array of shape x0.shape
    :param x0: array of according dim, tarting point
    :param stepsize: float, stepsize
    :param samples: list of tetermining each sum-term of the loss function.
    :param batchsize: int, number of samples to draw for each step.
    :param maxit: int, number of total iterations
    :param kwargs: key word arguments to pass to deriv.
    :param choose_best: boolean, if True, the best computed value will be returned.
    :return: array of shape x0.shape.
    """
    x = x0
    x_best = x0
    for i in range(maxit):
        if not batchsize or batchsize >= len(samples):
            random_samples = samples
        else:
            random_samples = choices(samples, k=batchsize)
        x = x - stepsize / (1+i) * deriv(x, random_samples, **kwargs)
        if choose_best and f(x, samples, **kwargs) < f(x_best, samples, **kwargs):
            x_best = x
    if choose_best:
        return x_best
    else:
        return x


def cone_contains(x, y, t, a):
    """
    Consider a 2-d plane and a cone at the origin with apex angle a and facing angle t, where t=0 means facing east.
    Angles increase counter-clockwise.
    This function computes if the point pix lies inside the described cone.

    :param x: float, x-coordinate of the point in question.
    :param y: float, y-coordinate of the point in question.
    :param t: float in [0, 360), facing angle of the cone in degrees.
    :param a: float in [0, 360), apex angle of the cone in degrees.
    :return: boolean, True if pix is contained in the cone, False otherwise.
    """
    return t - a / 2 <= arctan_lim(x, y) <= t + a / 2


def arctan_lim(x, y):
    """
    Inverse of the tangents function with limes values for x = 0 and y -> inf, y-> -inf.
    if x == 0 and y >= 0:
        b = 90.0
    elif x == 0 and y < 0:
        b = 270.0
    else:
        b = rad2deg(arctan(y/x))
    :param x: float, length of the adjacent leg
    :param y: float, length of the opposite leg
    :return: float in [0, 360), arctan(y/x) in DEGREES
    """
    if x == 0 and y >= 0:
        return 90.0
    elif x == 0 and y < 0:
        return 270.0
    else:
        return rad2deg(arctan(y / x))

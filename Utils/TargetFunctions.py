from numpy.core._multiarray_umath import deg2rad, sqrt, cos, sin


def target_function_cont(t, wall_points, pos, lam=0.0):
    """
    Continuous loss-function for field given target angle and the current wall-points around the point pos.

    The idea is to punish field target angle t, where many wall-points lie "close" to the facing-axis given by t.
    We project every wall-point onto the unit-circle and compute field point dependant on t on the circle lying furthest
    away from every other point in euclidean 2-norm.
    The Loss function then can be written as:

    - Loss(t) = - 1/n SUM_(x, y) {||(x , y) - (field(t), b(t))||**2} + 1/2 * lam * ||t||**2
    - (field(t), b(t)) = (cos(t), sin(t))

    This Results in the Loss-Term:

    - Loss(t)
            = 2/n * SUM_(x, y){x * cos(t) + y * sin(t) - 1} + 1/2 * lam * ||t||**2
            = 2*cos(t)/n * SUM_x + 2*sin(t)/n * SUM_y - 1 + 1/2 * lam * ||t||**2

    Remember, that the coordinate (i, j) from wall_points describes the coordinates on the playing-field, where
    field wall pixel is present.

    :param t: float, angle in degree in [0, 360), this is the objective-parameter to minimize over.
    :param pos: tuple of size 2 of int, position which is considered the center of all wall-points.
    :param wall_points: list of tuple of size 2 of int, all locations of wall entries (-1 values)
    The coordinates should be shifted, such that (0, 0) is the player's current position.
    :param lam: float, l-2 regularization factor, default 0.
    :return: float, Loss function value of the give target angle.
    """
    sum_x = 0
    sum_y = 0
    pos_x, pos_y = pos
    t = deg2rad(t)  # angles in radians
    for i, j in wall_points:
        # compute coordinates for each pixel, such that self.pos is the origin.
        x = i - pos_x
        y = j - pos_y
        # project onto unit-sphere
        if not x == y == 0:
            x_norm = x / sqrt(x ** 2 + y ** 2)
            y_norm = y / sqrt(x ** 2 + y ** 2)
        else:
            x_norm = y_norm = 0
        sum_x += x_norm
        sum_y += y_norm
    return 2/len(wall_points) * cos(t) * sum_x + 2/len(wall_points) * sin(t) * sum_y - 1 + 0.5 * lam * t**2


def target_function_cont_d(t, wall_points, pos, lam=0.0):
    """
    First derivative of the target function defined in self.target_function_cont.

    :param t: float, angle in [0, 360), this is the objective-parameter to minimize over.
    :param pos: tuple of size 2 of int, position which is considered the center of all wall-points.
    :param wall_points: 2-d numpy array of int, contains either 0 or -1 entries.
    The matrix is build such that the pixes at wall_points[scope, scope] is the player's position.
    :param lam: float, l-2 regularization factor, default 0.
    :return: float, Loss function value of the give target angle (will always be <= 0).
    """
    sum_x = 0
    sum_y = 0
    pos_x, pos_y = pos
    t = deg2rad(t)  # angles in radians
    for i, j in wall_points:
        # compute coordinates for each pixel, such that self.pos is the origin.
        x = i - pos_x
        y = j - pos_y
        # project onto unit-sphere
        if not x == y == 0:
            x_norm = x / sqrt(x ** 2 + y ** 2)
            y_norm = y / sqrt(x ** 2 + y ** 2)
        else:
            x_norm = y_norm = 0
        sum_x += x_norm
        sum_y += y_norm
    return -2 / len(wall_points) * sin(t) * sum_x + 2 / len(wall_points) * cos(t) * sum_y + lam * t


def target_function_cont_dd(t, wall_points, pos, lam=0.0):
    """
    Second derivative of the target function defined in self.target_function_cont.

    :param t: float, angle in [0, 360), this is the objective-parameter to minimize over.
    :param pos: tuple of size 2 of int, position which is considered the center of all wall-points.
    :param wall_points: 2-d numpy array of int, contains either 0 or -1 entries.
    The matrix is build such that the pixes at wall_points[scope, scope] is the player's position.
    :param lam: float, l-2 regularization factor, default 0.
    :return: float, Loss function value of the give target angle (will always be <= 0).
    """
    sum_x = 0
    sum_y = 0
    pos_x, pos_y = pos
    t = deg2rad(t)  # angles in radians
    for i, j in wall_points:
        # compute coordinates for each pixel, such that self.pos is the origin.
        x = i - pos_x
        y = j - pos_y
        # project onto unit-sphere
        if not x == y == 0:
            x_norm = x / sqrt(x ** 2 + y ** 2)
            y_norm = y / sqrt(x ** 2 + y ** 2)
        else:
            x_norm = y_norm = 0
        sum_x += x_norm
        sum_y += y_norm
    return 2 / len(wall_points) * cos(t) * sum_x - 2 / len(wall_points) * sin(t) * sum_y + lam
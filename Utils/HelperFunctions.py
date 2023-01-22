from random import choices

from numpy import inf, rad2deg, deg2rad, sqrt, arctan, arccos, arcsin, sin, cos, radians


def replace_hex_color(string, col):
    """
    Given field string this function finds all occurences of hex color strings like "#ff00ff" and replaces them
    by the given color string.

    :param string: string, expects that only hex colors start with an "#".
    :return: string, resulting string
    """
    out = ""
    i = 0
    while i < len(string):
        if string[i] == "#":
            out += col
            i += 7
        else:
            out += string[i]
            i += 1
    return out


def get_rectangle_corners(point_set):
    """
    Computes the top left pixel and bottom right pixel of the rectangle enclosing the given 2-d pointset,
    assuming the points all have positive coordinates.

    :param point_set: list of tuple of int, each value needs to be positive
    :return: (field, b, x, y), with (field, b) top-left pixel and (x, y) bottom-right pixel
    """
    # -- determine top-left and bottom-right pixel
    # top-left pixel pair
    a = inf
    b = inf
    # bottom-right pixel pair
    x = -1
    y = -1
    for p, q in point_set:
        #  assert p >= 0 and q >= 0, "Only positive values are allowed but got ({}, {}).".format(p, q)
        if p < a:
            a = p
        if q < b:
            b = q
        if p > x:
            x = p
        if q > y:
            y = q
    return a, b, x, y


def stochastic_gradient_descent(f, deriv, x0, stepsize, samples, batchsize=-1, maxit=100, choose_best=False, **kwargs):
    """
    Computes the approximate minimum of the function, that produced jac, which is its first derivative.

    :param f: target loss function: (x, samples, **kwargs) -> float
    :param deriv: function: (x, samples, **kwargs) -> array of shape x0.shape
    :param x0: array of according dim, tarting point
    :param stepsize: float, stepsize
    :param samples: list of tetermining each sum-term of the loss function.
    :param batchsize: int, number of samples to draw for each step. If negative, use all samples.
    :param maxit: int, number of total iterations
    :param kwargs: key word arguments to pass to deriv.
    :param choose_best: boolean, if True, the best computed value will be returned.
    :return: array of shape x0.shape.
    """
    # print("Starting optimization...")
    x = x0
    x_best = x0
    no_sampling = False
    for i in range(maxit):
        # print("--- Iteration ", i)
        if batchsize < 0 or batchsize >= len(samples):
            random_samples = samples
            no_sampling = True
            # print("No sampling. Default to common gradient descent.")
        else:
            random_samples = choices(samples, k=batchsize)

        if no_sampling:
            x = x - deriv(x, random_samples, **kwargs)
        else:
            x = x - stepsize / (1 + i) ** 2 * deriv(x, random_samples, **kwargs)
        # print("Current x: ", x)
        # print("Current loss: ", f(x, samples, **kwargs))
        # print("Current garadient: ", deriv(x, samples, **kwargs))
        if choose_best and f(x, samples, **kwargs) < f(x_best, samples, **kwargs):
            x_best = x
    # print("---------- Done.")
    if choose_best:
        return x_best
    else:
        return x


def cone_contains(x, y, t, a):
    """
    Consider field 2-d plane and field cone at the origin with apex angle field and facing angle t.
    Angles increase clockwise with 0 degrees facing east.
    This function computes if the point (x, y) lies inside the described cone.

    :param x: float, x-coordinate of the point in question.
    :param y: float, y-coordinate of the point in question.
    :param t: float in [0, 360), facing angle of the cone in degrees.
    :param a: float in [0, 90], apex angle of the cone in degrees.
    :return: boolean, True if (x, y) is contained in the cone, False otherwise.
    """
    if x == y == 0:
        return True
    t = t % 360
    # if t > 0:
    #     t = 360 - t
    x_norm = x / sqrt(x ** 2 + y ** 2)
    y_norm = y / sqrt(x ** 2 + y ** 2)
    t_x, t_y = get_point_from_angle(t)
    a_x, a_y = get_point_from_angle((t + a / 2) % 360)
    print("(x,y) = ({0}, {1})".format(x, y), "t = ", t, "t+a/2%360 = ", t + a / 2 % 360)
    print("x-t: ", (x_norm - t_x) ** 2 + (y_norm - t_y) ** 2, "a/2-t: ", (a_x - t_x) ** 2 + (a_y - t_y) ** 2)
    return (x_norm - t_x) ** 2 + (y_norm - t_y) ** 2 <= (a_x - t_x) ** 2 + (a_y - t_y) ** 2


def arctan_lim(x, y):
    """
    Inverse of the tangents function with limes values for x = 0 and y -> inf, y-> -inf.

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


def get_angle_between_vectors(x, y, p, q):
    """
    Returns the angle between the two points (x, y) and (p, q).
    Neither of both points should be (0, 0).

    :param x: int, 1st x-coordinate
    :param y: int, 1st y-coordinate
    :param p: int, 2nd x-coordinate
    :param q: int, 2nd y-coordinate
    :return: float, Angle in integer degrees in [0, 180)
    """
    return rad2deg(arccos((x * p + y * q) / (sqrt((x ** 2 + y ** 2) * (p ** 2 + q ** 2)))))


def get_point_from_angle(angle):
    """
    Given an angle in degrees in [0, 360), this function computes the corresponding point on the unit-circle.
    Angle increases clockwise with 0 degrees pointing east.
    The result is the solution to the equation-system
        sin(angle) = -y/1
        x**2+y**2 = 1.

    :param angle: float, angle in degrees from 0 to exclusively 360.
    :return: tuple of size two of float, the point on the circle corresponding to the given angle.
    """
    assert 0 <= angle < 360, "Angle has to be from [0, 360) but was " + str(angle) + "."

    if 0 <= angle < 90 or 270 <= angle <= 360:
        sign = 1
    else:
        sign = -1
    angle = deg2rad(360 - angle)
    return sign * sqrt(1 - sin(angle) ** 2), sin(angle)


def get_angle_of_point(x, y):
    """
    Given a point (x, y), this function returns the appropriate angle.
    Angles increase clockwise with 0 degrees facing east.

    :param x: float, x-coordinate
    :param y: float, y-coordinate
    :return: tuple of size two of float, the point on the circle corresponding to the given angle.
    """
    if x == y == 0:
        return 0

    norm = sqrt(x ** 2 + y ** 2)
    if x > 0 and y >= 0:
        return rad2deg(arcsin(abs(y) / norm))
    elif x <= 0 and y > 0:
        return 90 + rad2deg(arcsin(abs(y) / norm))
    elif x < 0 and y <= 0:
        return 180 + rad2deg(arcsin(abs(y) / norm))
    else:
        return 270 + rad2deg(arcsin(abs(y) / norm))


def get_normal_from_angle(angle):
    """
    This function returns a 2-d normal vector of the 2-d hyperplane defined by the angle.
    In fact the returned vector is the result of taking the unit vector facing in the direction of angle turned
    counter clockwise by 90 degrees.
    The angle is assumed to increases clockwise with 0 degrees facing east.

    :param angle: float, angle in degrees
    :return: tuple of size 2 of float.
    """
    v1, v2 = get_direction_from_angle(angle)
    return -v2, v1


def is_point_on_left_side(angle, x, y):
    """
    This function decides if a given point (x, y) is on the left side of the hyperplane defined by the angle.
    Points within the hyperplane are considered to lie on the left side.

    :param angle: float, angle in degrees
    :param x: scalar, x-coordinate
    :param y: scalar, y-coordinate
    :return:
    """
    n1, n2 = get_normal_from_angle(angle)
    return x * n1 + y * n2 >= 0


def get_direction_from_angle(angle):
    """
    Returns a normed 2-d vector of float describing the direction corresponding angle (in degrees).
    Angle increases clockwise and 0 degrees corresponds to (0, 1).

    :param angle: float, angel in degrees [0, 360), greater values will be scaled back into this interval.
    :return: tuple of size two of float, normed 2-d vector
    """
    rad = radians(angle)
    return cos(rad), -sin(rad)


def is_contained_in_cone(x, y, facing_angle, apex_angle):
    """
    Decides if the given point (x, y) lies strictly inside cone facing facing_angle with apex angel of apex_angle.

    :param x: float, x-coordinate
    :param y:float, y-coordinate
    :param facing_angle: float, angle in degrees in [0, 360), increasing clock-wise, 0 degree facing east
    :param apex_angle: float, angle in degrees in [0, 180)
    :return: boolean, true if the point is strictly contained in the cone.
    """
    assert 180 >= apex_angle >= 0, "apex_angle must be in [0, 360)."
    x_left, y_left = get_direction_from_angle(facing_angle - apex_angle / 2)
    x_right, y_right = get_direction_from_angle(facing_angle + apex_angle / 2)

    n_x_left, n_y_left = -y_left, x_left  # normal of left cone vector
    n_x_right, n_y_right = y_right, -x_right  # normal of right cone vector

    # point inside cone if both normal vectors have angle of more than 90 degrees to the point
    # or equivalently if each scalar products of the normal vectors with the point is lesser than 0.
    return n_x_left * x + n_y_left * y < 0 and n_x_right * x + n_y_right * y < 0

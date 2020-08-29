
from numpy import inf


def replace_hex_color(string, col):
    """
    Given a string this function finds all occurences of hex color strings like "#ff00ff" and replaces them
    by the given color string.

    :param string: string, expects that only hex colors start with an "#".
    :return: string, resulting string
    """
    out = ""
    i = 0;
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
    :return: (a, b, x, y), with (a, b) top-left pixel and (x, y) bottom-right pixel
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

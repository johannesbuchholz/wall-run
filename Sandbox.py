import numpy as np

from Utils.HelperFunctions import *

print(get_point_from_angle(180))
print(cone_contains(-1, 0, 180, 30))

d = 15
walls = np.zeros((d, d), "int")

walls[0, :] = -1
walls[-2:, :] = -1
walls[:, -1] = -1
walls[:, 0] = -1

scope_radius = 3
x, y = 2, 6
angle = 270
apex_angle = 30

walls[x, y] = -1
n, _ = np.shape(walls)

a = [(i - x, j - y)
     for i in range(x - scope_radius, x + scope_radius + 1)
     for j in range(y - scope_radius, y + scope_radius + 1)
     if walls[i % n, j % n] == -1 and sqrt((i - x) ** 2 + (j - y) ** 2) < scope_radius]

print(walls)
print(a)

left_score = 0
right_score = 0
cone_points = []

for i, j in a:
    if cone_contains(i, j, t=angle, a=apex_angle):
        cone_points.append((i, j))
        if is_point_on_left_side(angle, i, j):
            left_score += 1
        else:
            right_score += 1
print("left score: ", left_score)
print("right score: ", right_score)

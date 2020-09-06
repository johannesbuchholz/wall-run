
import timeit

setup = """
import numpy as np  
a = np.zeros((160, 160))
x = (1,3,4,5,6,8,4,5,6,7,9,6,3,4)
y = (3,2,4,7,6,3,4,5,6,7,1,6,2,1)
a[x, y] = -1
"""

code1 = """
np.argwhere((a==-1))
"""

code2 = """
n, m = a.shape
o = []
for i in range(n):
 for j in range(m):
  if a[i, j] == -1:
   o.append([i, j])
"""
print("argwhere: ", timeit.timeit(stmt=code1, setup=setup, number=1000)/1000)
print("for-loop: ", timeit.timeit(stmt=code2, setup=setup, number=1000)/1000)
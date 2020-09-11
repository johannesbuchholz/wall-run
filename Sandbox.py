
from FieldObjects import PlayerClassBot as p
import numpy as np
from timeit import default_timer

a = np.zeros((15, 15), "int")
a[:,:8] = -1


s = np.argwhere((a == -1))
n = round(len(s)/4)

start = default_timer()
sol = p.stochastic_gradient_descent(f=p.target_function_cont, deriv=p.target_function_cont_deriv,
                                    x0=0, stepsize=180, samples=s, batchsize=8, choose_best=False,
                                    maxit=10,
                                    **{"pos": (7, 7)}
                                    )
end = default_timer()
print(a)
print("Duration: ", round(end-start, 4))
print("Samples: ", n)
print("Computation result: ", round(sol, 4))
print("Target-Angle: ", round(sol) % 360)

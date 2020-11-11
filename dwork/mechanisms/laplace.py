import math
from .random import random
from .exponential import exponential_noise


def laplace_noise(epsilon):
    if random() > 0.5:
        return exponential_noise(epsilon)
    else:
        return -exponential_noise(epsilon)

from .random import random
import math


def geometric_noise(epsilon, symmetric=True):
    p = math.exp(-epsilon)
    if random() > p:
        # the probability, that we return 0
        if symmetric:
            # if the noise is symmetric, we half the probability of returning 0
            if random() > 0.5:
                return 0
        else:
            return 0
    # we only return values > 0 here
    pv = 1.0 - p + p * random()
    k = math.log(1 - pv) / math.log(p)
    if symmetric:
        pv = random()
        if pv < 0.5:
            k = -k
    return int(k)

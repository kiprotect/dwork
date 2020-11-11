import math
from .random import random


def exponential_noise(epsilon):
    return -math.log(1 - random()) / epsilon

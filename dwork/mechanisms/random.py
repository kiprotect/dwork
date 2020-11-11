import secrets

sr = secrets.SystemRandom()


def random():
    return sr.random()

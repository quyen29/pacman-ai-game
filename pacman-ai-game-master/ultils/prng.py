# pseudo-random number generator theo thuật toán Linear Congruential Generator
class PRNG:
    def __init__(self, seed):
        self.state = seed

    def next(self):
        a = 1664525
        c = 1013904223
        m = 2 ** 32
        self.state = (a * self.state + c) % m
        return self.state

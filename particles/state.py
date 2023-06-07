from numpy import random


class State:
    def __init__(self,
                 position: float = 0,
                 alpha: float = 0) -> None:
        self.position = position
        if alpha != 0:
            self.alpha = alpha
        else:
            self.assign_random_alpha()

    def __str__(self):
        return f'[Position: {self.position} | Alpha: {self.alpha}]'

    def __eq__(self, other):
        if isinstance(other, State):
            return self.position == other.position and self.alpha == other.alpha
        return False

    def assign_random_alpha(self, center: float = 2, variance: float = 0.1):
        self.alpha = random.normal(loc=center, scale=variance)

    def assign_random_position(self, center: float = 0, variance: float = 0.1):
        self.position = random.normal(loc=center, scale=variance)

    def get_position(self):
        return self.position

    def get_alpha(self):
        return self.alpha

    def set_position(self, position: float):
        self.position = position

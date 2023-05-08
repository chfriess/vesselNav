from numpy import random

from map.map import Position


class State:
    def __init__(self, position: Position,
                 alpha: float = 0) -> None:
        if position.displacement < 0 or alpha < 0:
            raise ValueError("position must be greater than 0 and alpha must be non-negative")
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

    def get_position(self):
        return self.position

    def get_alpha(self):
        return self.alpha

    def set_position(self, position: Position):
        self.position = position

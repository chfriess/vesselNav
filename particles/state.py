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


class State3D(State):

    def __init__(self,
                 position: float = 0,
                 branch: int = 0,
                 alpha: float = 0):
        super().__init__(position=position,
                         alpha=alpha)
        self.branch = branch

    def __str__(self):
        return f'[Position: {self.position} | Branch: {self.branch} | Alpha: {self.alpha}]'

    def get_position(self):

        return {"branch": self.branch, "displacement": self.position}

    def set_position(self, position: float):
        self.position = position

    def set_branch(self, branch: int):
        self.branch = branch

    def get_branch(self):
        return self.branch

    def get_displacement(self):
        return self.position

from particles.state import State


class State3D(State):

    def __init__(self,
                 position: float = 0,
                 branch: int = 0,
                 alpha: float = 0):
        super().__init__(position=position,
                         alpha=alpha)
        self.branch = branch

    def __str__(self):
        return f'[Position: {self.position} | Branch: {self.position} | Alpha: {self.alpha}]'

    def get_position(self):
        return [self.branch, self.position]


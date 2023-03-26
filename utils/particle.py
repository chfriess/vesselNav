from utils.state import State


class Particle:
    """
    @param state: the current state estimate of the particle
    @param weight: the current weight of the particle
    """

    def __init__(self,
                 state: State,
                 weight: float = 0) -> None:
        self.state = state
        self.weight = weight

    def __str__(self):
        return f'[State: {str(self.state)} | Weight: {str(self.weight)}]'

    def __eq__(self, other):
        if isinstance(other, Particle):
            return self.state == other.state and self.weight == other.weight
        return False

    def get_state(self):
        return self.state

    def get_weight(self):
        return self.weight

    def set_weight(self, weight: float):
        self.weight = weight

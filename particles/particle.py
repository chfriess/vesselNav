from particles.state import State, State3D


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

    def get_position(self):
        return self.state.get_position()

    def get_weight(self):
        return self.weight

    def set_weight(self, weight: float):
        self.weight = weight


class Particle3D(Particle):
    def __init__(self,
                 state: State3D,
                 weight: float = 0):
        if not isinstance(state, State3D):
            raise ValueError("A 3D particle requires a 3D state")
        super().__init__(state, weight)



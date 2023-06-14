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


class SlidingParticle3D(Particle3D):
    def __init__(self,
                 state: State3D,
                 weight: float = 0) -> None:
        super().__init__(state, weight)
        self.reference_history = []
        self.last_reference_index = {"branch_index": state.get_position()["branch"],
                                     "displacement_index": round(state.get_position()["displacement"])}

    def __str__(self):
        return f'[State: {str(self.state)} | Weight: {self.weight} | ReferenceHistory: {str(self.reference_history)}]'

    def __eq__(self, other):
        if isinstance(other, SlidingParticle3D):
            return self.state == other.state \
                and self.weight == other.weight \
                and self.reference_history == other.reference_history
        return False

    def get_last_reference_index(self) -> dict:
        return self.last_reference_index

    def set_last_reference_index(self, branch_index: int, displacement_index: int):
        self.last_reference_index["branch_index"] = branch_index
        self.last_reference_index["displacement_index"] = displacement_index

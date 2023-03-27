from utils.particle import Particle
from utils.state import State


class SlidingParticle(Particle):

    def __init__(self,
                 state: State,
                 weight: float = 0) -> None:
        super().__init__(state, weight)
        self.reference_history = []
        self.last_reference_index = 0

    def __str__(self):
        return f'[State: {str(self.state)} | Weight: {self.weight} | ReferenceHistory: {str(self.reference_history)}]'

    def __eq__(self, other):
        if isinstance(other, SlidingParticle):
            return self.state == other.state \
                and self.weight == other.weight \
                and self.reference_history == other.reference_history
        return False

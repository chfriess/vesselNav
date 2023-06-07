from particles.particle import Particle
from particles.state3D import State3D


class Particle3D(Particle):
    def __init__(self,
                 state: State3D,
                 weight: float = 0):
        if not isinstance(state, State3D):
            raise ValueError("A 3D particle requires a 3D state")
        super().__init__(state, weight)


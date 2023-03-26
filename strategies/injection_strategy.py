from abc import abstractmethod
from utils.particle_set import ParticleSet


class InjectionStrategy:

    def __init__(self, map_borders: list):
        self.map_borders = map_borders

    @staticmethod
    def remove_number_of_worst_particles(particles: ParticleSet,
                                         number_to_remove: int) -> ParticleSet:
        particles.sort_descending_by_weight()
        for index in range(number_to_remove):
            particles.pop_last()
        return particles

    @abstractmethod
    def inject(self, particles: ParticleSet) -> ParticleSet:
        raise NotImplementedError

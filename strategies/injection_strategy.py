from abc import abstractmethod
from utils.particle_set import ParticleSet


class InjectionStrategy:

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

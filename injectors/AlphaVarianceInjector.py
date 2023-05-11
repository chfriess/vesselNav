from numpy import random
from strategies.injection_strategy import InjectionStrategy
from utils.particle_set import ParticleSet


class AlphaVariationInjector(InjectionStrategy):

    def __init__(self, map_borders: list,
                 percentage_of_particles_injected: float = 0.0,
                 alpha_variance: float = 0.0):
        super().__init__(map_borders)
        self.percentage_of_particles_injected = percentage_of_particles_injected,
        self.alpha_variance = alpha_variance

    def inject(self, particles: ParticleSet) -> ParticleSet:
        # TODO check why coosing percentage_of_particles_injected instead of hardcoded number yields a warning
        number_injected_particles = int(len(particles) * 0)
        particles.sort_ascending_by_weight()
        for index in range(number_injected_particles):
            particles[index].state.alpha = random.normal(loc=particles[index].state.alpha, scale=self.alpha_variance)
        return particles

from numpy import random
from strategies.injection_strategy import InjectionStrategy
from utils.particle_set import ParticleSet


class AlphaVariationInjector(InjectionStrategy):

    def __init__(self,
                 alpha_center: float = 2,
                 alpha_variance: float = 0.1):
        self.alpha_center = alpha_center
        self.alpha_variance = alpha_variance

    def inject(self, particles: ParticleSet) -> ParticleSet:
        number_injected_particles = int(len(particles) * 0.05)
        particles.sort_ascending_by_weight()
        for index in range(number_injected_particles):
            particles[index].state.alpha = random.normal(loc=particles[index].state.alpha, scale=0.1)
        return particles

from numpy import random
from strategies.injection_strategy import InjectionStrategy
from utils.particle_set import ParticleSet


class AlphaVariationInjector(InjectionStrategy):

    def __init__(self,
                 percentage_of_particles_injected: float = 0.05,
                 alpha_center: float = 1.5,
                 alpha_variance: float = 0.1):
        self.percentage_of_particles_injected = percentage_of_particles_injected
        self.alpha_center = alpha_center
        self.alpha_variance = alpha_variance

    def set_alpha_center(self, alpha: float):
        self.alpha_center = alpha

    def inject(self, particles: ParticleSet) -> ParticleSet:
        number_injected_particles = int(len(particles) * 0.05)
        particles.sort_ascending_by_weight()
        for index in range(number_injected_particles):
            particles[index].state.alpha = random.normal(loc=particles[index].state.alpha, scale=self.alpha_variance)
        return particles

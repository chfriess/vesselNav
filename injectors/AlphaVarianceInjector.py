from numpy import random
from strategies.injection_strategy import InjectionStrategy
from utils.particle_set import ParticleSet


class AlphaVariationInjector(InjectionStrategy):
    def inject(self, particles: ParticleSet) -> ParticleSet:
        number_injected_particles = int(len(particles) * 0.)
        particles.sort_ascending_by_weight()
        for index in range(number_injected_particles):
            particles[index].state.alpha = random.normal(loc=particles[index].state.alpha, scale=0.01)
        return particles

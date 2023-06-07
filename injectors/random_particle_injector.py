
from numpy import random

from strategies.injection_strategy import InjectionStrategy
from particles.particle import Particle
from utils.particle_set import ParticleSet
from particles.state import State


class RandomParticleInjector(InjectionStrategy):

    def __init__(self,
                 map_borders: list):
        self.map_borders = map_borders

    def inject(self, particles: ParticleSet) -> ParticleSet:
        if random.uniform(0, 1) <= 0.2:
            number_injected_particles = int(len(particles) * 0.05)
            particles = self.remove_number_of_worst_particles(particles=particles,
                                                              number_to_remove=number_injected_particles)
            for index in range(number_injected_particles):
                particles.append(Particle(State(position=random.uniform(self.map_borders[0], self.map_borders[1]),
                                                alpha=2)))
            return particles


from numpy import random

from strategies.injection_strategy import InjectionStrategy
from utils.particle import Particle
from utils.particle_set import ParticleSet
from utils.state import State


class RandomParticleInjector(InjectionStrategy):

    def inject(self, particles: ParticleSet) -> ParticleSet:
        number_injected_particles = int(len(particles) * 0)
        particles = self.remove_number_of_worst_particles(particles=particles,
                                                          number_to_remove=number_injected_particles)
        for index in range(number_injected_particles):
            # TODO: how to correctly inject the MatchingMatrix? or is this even necessary?
            particles.append(Particle(State(position=random.uniform(self.map_borders[0], self.map_borders[1]))))  # TODO: change to vessel tree position estimate

        return particles
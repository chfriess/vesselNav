from numpy import random
from particles.state import State3D
from strategies.injection_strategy import InjectionStrategy
from particles.particle import Particle
from utils.map3D import Map3D
from utils.particle_set import ParticleSet


class RandomParticleInjector3D(InjectionStrategy):

    def __init__(self, map3D: Map3D):
        self.map3D = map3D

    def inject(self,
               particles: ParticleSet) -> ParticleSet:
        number_injected_particles = int(len(particles) * 0.05)
        particles = self.remove_number_of_worst_particles(particles=particles,
                                                          number_to_remove=number_injected_particles)
        for index in range(number_injected_particles):
            vessel_index = random.randint(0, len(self.map3D.get_vessels()))
            # TODO: adapt to new vessel data structure
            position = random.uniform(0, len(self.map3D.get_vessel(vessel_index)))
            state = State3D(position=position, branch=vessel_index, alpha=2)
            particle = Particle(state=state)
            particles.append(particle=particle)
        return particles

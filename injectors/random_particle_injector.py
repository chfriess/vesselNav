from numpy import random
from particles.state import State3D
from strategies.injection_strategy import InjectionStrategy
from particles.particle import Particle
from utils.map3D import Map3D
from utils.particle_set import ParticleSet


class RandomParticleInjector(InjectionStrategy):

    def __init__(self,
                 map_borders: list):
        self.map_borders = map_borders

    def inject(self, particles: ParticleSet) -> ParticleSet:
        if random.uniform(0, 1) <= 0.2:
            number_injected_particles = int(len(particles) * 0.05)
            particles.sort_ascending_by_weight()
            for index in range(number_injected_particles):
                particles[index].state.position = random.normal(loc=particles[index].state.position, scale=0.1)
                particles[index].state.alpha = random.normal(loc=particles[index].state.alpha, scale=0.1)
        return particles


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
            position = random.uniform(0, len(self.map3D.get_vessel(vessel_index)))
            state = State3D(position=position, branch=vessel_index, alpha=2)
            particle = Particle(state=state)
            particles.append(particle=particle)
        return particles

# TODO 3D: 3D cluster position estimate, 3D model, generate 3D cluster position estimate
# TODO 3D: 3D post hoc estimator, 3D online estimator

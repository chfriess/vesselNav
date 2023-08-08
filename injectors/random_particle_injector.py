from numpy import random
from strategies.injection_strategy import InjectionStrategy
from utils.map3D import Map3D
from utils.particle_set import ParticleSet


class RandomParticleInjector3D(InjectionStrategy):

    def __init__(self, map3D: Map3D):
        self.map3D = map3D

    def inject(self,
               particles: ParticleSet) -> ParticleSet:
        number_injected_particles = int(len(particles) * 0.05)
        particles.sort_ascending_by_weight()

        for index in range(number_injected_particles):
            particles[index].reset_particle()
            vessel_index = random.randint(0, len(self.map3D.get_vessels()))
            position = random.uniform(0, self.map3D.get_vessel(vessel_index)[-1]["centerline_position"])
            particles[index].state.position = position
            particles[index].state.branch = vessel_index
            particles[index].set_alpha(random.normal(loc=particles[index].state.alpha, scale=0.1))
        return particles

from numpy import random

from particles.particle import Particle3D
from particles.state import State3D
from strategies.motion_strategy import MotionStrategy
from utils.map3D import Map3D
from utils.particle_set import ParticleSet


class MotionModel(MotionStrategy):

    def __init__(self, included_measurements: int = 10):
        if included_measurements < 1:
            raise ValueError("number of included measurements cannot be smaller than 1")
        self.included_measurements = included_measurements
        self.displacement_history = []

    def move_particles(self, previous_particle_set: ParticleSet,
                       displacement_measurement: float) -> ParticleSet:

        self.displacement_history.append(displacement_measurement)
        error = self.calculate_displacement_error(self.displacement_history)

        for particle in previous_particle_set:
            position_estimate = particle.state.position + (displacement_measurement * particle.state.alpha)
            particle.state.position = random.normal(loc=position_estimate,
                                                    scale=error)
        return previous_particle_set


class MotionModel3D(MotionStrategy):

    def __init__(self,
                 map3D: Map3D,
                 included_measurements: int = 10):
        if included_measurements < 1:
            raise ValueError("number of included measurements cannot be smaller than 1")
        self.included_measurements = included_measurements
        self.map3D = map3D
        self.displacement_history = []

    def move_particles(self, previous_particle_set: ParticleSet,
                       displacement_measurement: float) -> ParticleSet:

        self.displacement_history.append(displacement_measurement)
        error = self.calculate_displacement_error(self.displacement_history)
        for particle in previous_particle_set:
            position_estimate = particle.get_position()["displacement"] + (displacement_measurement * particle.state.alpha)
            if 0 < position_estimate < len(self.map3D.get_vessel(particle.get_position()["branch"])):
                particle.state.set_position(random.normal(loc=position_estimate, scale=error))
            elif position_estimate < 0:
                predecessor_index = self.map3D.get_index_of_predecessor(particle.get_position()["branch"])

                if predecessor_index is not -1:
                    predecessor = self.map3D.get_vessel(predecessor_index)
                    position_estimate = len(predecessor) - 1 + position_estimate
                    particle.state.set_position(random.normal(loc=position_estimate, scale=error))
                    particle.state.set_branch(predecessor_index)
                else:
                    particle.state.set_position(0)
            else:
                successor_indices = self.map3D.get_indices_of_successors(particle.get_position()["branch"])
                if not successor_indices == []:
                    successor_index = random.choice(successor_indices)
                    particle.state.set_position(random.normal(
                        loc=position_estimate - len(self.map3D.get_vessel(
                            particle.get_position()["branch"])), scale=error))
                    particle.state.set_branch(successor_index)
                else:
                    particle.state.set_position(random.normal(
                        loc=len(self.map3D.get_vessel(particle.get_position()["branch"])), scale=error))

        return previous_particle_set



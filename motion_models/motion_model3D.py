from numpy import random
from strategies.motion_strategy import MotionStrategy
from utils.map3D import Map3D
from utils.particle_set import ParticleSet


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
            position_estimate = particle.get_position()[0] + (displacement_measurement * particle.state.alpha)
            if 0 < position_estimate < len(self.map3D.get_vessel(particle.get_position()[1])):
                particle.state.set_position(random.normal(loc=position_estimate, scale=error))
            elif position_estimate < 0:
                predecessor_index = self.map3D.get_index_of_predecessor(particle.get_position()[0])
                predecessor = self.map3D.get_vessel(predecessor_index)
                position_estimate = len(predecessor) - 1 + position_estimate
                particle.state.set_position(random.normal(loc=position_estimate, scale=error))
                particle.state.set_branch(predecessor_index)
            else:
                successor_indices = self.map3D.get_indices_of_successors(particle.get_position()[0])
                successor_index = random.choice(successor_indices)
                particle.state.set_position(random.normal(
                    loc=position_estimate - len(self.map3D.get_vessel(particle.get_position()[0])), scale=error))
                particle.state.set_branch(successor_index)

        return previous_particle_set
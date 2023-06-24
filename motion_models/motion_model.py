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
    # TODO: refactor this ugly function
    def move_particles(self, previous_particle_set: ParticleSet,
                       displacement_measurement: float) -> ParticleSet:

        self.displacement_history.append(displacement_measurement)
        error = self.calculate_displacement_error(self.displacement_history)
        for particle in previous_particle_set:
            position_estimate = particle.get_position()["displacement"] \
                                + (displacement_measurement * particle.state.alpha)
            # TODO: adapt to new vessel data structure
            if 0 < position_estimate < len(self.map3D.get_vessel(particle.get_position()["branch"])):
                particle.state.set_position(random.normal(loc=position_estimate, scale=error))
            elif position_estimate < 0:
                current_index = particle.get_position()["branch"]
                while position_estimate < 0:
                    if current_index == -1:
                        position_estimate = 0
                        break
                    else:
                        current_predecessor = self.map3D.get_vessel(current_index)
                        # TODO: adapt to new vessel data structure
                        position_estimate = len(current_predecessor) + position_estimate
                        current_index = self.map3D.get_index_of_predecessor(current_index)

                # TODO now it also shows some variation if the position estimate is set to zero, is this okay?
                particle.state.set_position(random.normal(loc=position_estimate, scale=error))
                particle.state.set_branch(current_index)

            else:
                successor_index = particle.get_position()["branch"]
                current_branch = self.map3D.get_vessel(successor_index)
                successor_indices = self.map3D.get_indices_of_successors(successor_index)
                # TODO: adapt to new vessel data structure
                while position_estimate > len(current_branch) and not successor_indices == []:
                    # conversion to int is necessary, otherwise it is not json serializable
                    successor_index = int(random.choice(successor_indices))
                    # TODO: adapt to new vessel data structure
                    position_estimate = position_estimate - len(current_branch)
                    successor_indices = self.map3D.get_indices_of_successors(successor_index)
                    current_branch = self.map3D.get_vessel(successor_index)
                particle.state.set_position(random.normal(
                    loc=position_estimate, scale=error))
                particle.state.set_branch(successor_index)

        return previous_particle_set

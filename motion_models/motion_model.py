from numpy import random
from strategies.motion_strategy import MotionStrategy
from utils.map3D import Map3D
from utils.particle_set import ParticleSet

"""
The MotionModel3D takes a set of particles and applies the current displacement measurement.
The displacement measurement is a distance value. For each particle, this distance value
is multiplied by the object variable alpha of the respective particle. Then, the 
resulting value is used as center of a normal distribution with variance equal to the estimated
error of the displacement sensor. The new position estimate of the respective particle is then 
drawn from this normal distribution. After the position of each particle of the particle set was 
updated, the particle set is returned.
"""


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
            position_estimate = particle.get_position()["displacement"] \
                                + (displacement_measurement * particle.state.alpha)
            vessel_length = self.map3D.get_vessel(particle.get_position()["branch"])[-1]["centerline_position"]
            if 0 < position_estimate < vessel_length:
                particle.state.set_position(random.normal(loc=position_estimate, scale=error))
            elif position_estimate < 0:
                self.handle_backward_vessel_switch(particle=particle,
                                                   position_estimate=position_estimate,
                                                   error=error)
            else:
                self.handle_forward_vessel_switch(particle=particle,
                                                  position_estimate=position_estimate,
                                                  error=error)

        return previous_particle_set

    def handle_backward_vessel_switch(self, particle, position_estimate: float, error: float):
        current_index = particle.get_position()["branch"]
        while position_estimate < 0:
            if current_index == 0:
                position_estimate = 0
                break
            else:
                predecessor_vessel_length = self.map3D.get_vessel(current_index)[-1]["centerline_position"]
                position_estimate = predecessor_vessel_length + position_estimate
                current_index = self.map3D.get_index_of_predecessor(current_index)
        particle.state.set_position(random.normal(loc=position_estimate, scale=error))
        particle.state.set_branch(current_index)

    def handle_forward_vessel_switch(self, particle, position_estimate: float, error: float):
        successor_index = particle.get_position()["branch"]
        current_branch = self.map3D.get_vessel(successor_index)
        successor_indices = self.map3D.get_indices_of_successors(successor_index)
        while position_estimate > current_branch[-1]["centerline_position"] and not successor_indices == []:
            # conversion to int is necessary, otherwise it is not json serializable
            successor_index = int(random.choice(successor_indices))
            position_estimate = position_estimate - current_branch[-1]["centerline_position"]
            successor_indices = self.map3D.get_indices_of_successors(successor_index)
            current_branch = self.map3D.get_vessel(successor_index)
        particle.state.set_position(random.normal(
            loc=position_estimate, scale=error))
        particle.state.set_branch(successor_index)

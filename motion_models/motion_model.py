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

                current_index = particle.get_position()["branch"]
                current_predecessor = self.map3D.get_vessel(current_index)
                while position_estimate < 0:

                    current_index = self.map3D.get_index_of_predecessor(current_index)
                    current_predecessor = self.map3D.get_vessel(current_index)
                    position_estimate = len(current_predecessor) + position_estimate
                # TODO after testing: cleanup, just acces current_predecessor
                if current_index is not -1:
                    particle.state.set_position(random.normal(loc=position_estimate, scale=error))
                    particle.state.set_branch(current_index)
                else:
                    particle.state.set_position(0)
            else:
                successor_index = particle.get_position()["branch"]
                current_branch = self.map3D.get_vessel(successor_index)
                successor_indices = self.map3D.get_indices_of_successors(successor_index)
                while position_estimate > len(current_branch) and not successor_indices == []:
                    # conversion to int is necessary, otherwise it is not json serializable
                    successor_index = int(random.choice(successor_indices))
                    position_estimate = position_estimate - len(current_branch)
                    successor_indices = self.map3D.get_indices_of_successors(successor_index)
                    current_branch = self.map3D.get_vessel(successor_index)
                particle.state.set_position(random.normal(
                    loc=position_estimate, scale=error))
                particle.state.set_branch(successor_index)

        return previous_particle_set


if __name__ == "__main__":
    map3D = Map3D()
    aorta_before = [1 / 20 for _ in range(70)]
    aorta_middle = [1 / 20 for _ in range(5)]
    aorta_after = [1 / 20 for _ in range(130)]

    renal_left = [1 / 15 for _ in range(100)]
    renal_right = [1 / 15 for _ in range(100)]
    iliaca_left = [1 / 10 for _ in range(100)]
    iliaca_right = [1 / 10 for _ in range(100)]

    map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_before, 0)
    map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_before, 1)
    map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_after, 2)


    map3D.add_mapping([0, 1])
    map3D.add_mapping([1, 2])



    motion_model = MotionModel3D(map3D)
    particles = ParticleSet()
    for _ in range(100):
        state = State3D()
        state.set_branch(2)
        state.assign_random_position(center=5, variance=0)
        state.assign_random_alpha(center=1, variance=0)
        particle = Particle3D(state=state, weight=0)
        particles.append(particle)


    for particle in particles:
        print(particle.get_position())




    print("___________________________________________\n\n")

    particles = motion_model.move_particles(particles, -20)

    for particle in particles:
        print(particle.get_position())

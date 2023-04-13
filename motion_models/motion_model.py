from numpy import random
from scipy.stats import sem
from utils.particle_set import ParticleSet


class MotionModel:

    def __init__(self, included_measurements: int = 10):
        if included_measurements < 1:
            raise ValueError("number of included measurements cannot be smaller than 1")
        self.included_measurements = included_measurements
        self.displacement_history = []

    @staticmethod
    def calculate_displacement_error(displacements: list, included_measurements: int = 0):
        if len(displacements) < 2:
            return 0.3
        elif included_measurements <= 1 or included_measurements >= len(displacements):
            return sem(displacements)
        else:
            last_index = len(displacements) - 1
            return sem(displacements[(last_index - included_measurements):last_index])

    def move_particles(self, previous_particle_set: ParticleSet,
                       displacement_measurement: float) -> ParticleSet:

        self.displacement_history.append(displacement_measurement)
        error = self.calculate_displacement_error(self.displacement_history)

        for particle in previous_particle_set:
            position_estimate = particle.state.position + (displacement_measurement * particle.state.alpha)  # TODO: change to vessel tree position estimate
            particle.state.position = random.normal(loc=position_estimate,  # TODO: change to vessel tree position estimate
                                                    scale=error)
        return previous_particle_set

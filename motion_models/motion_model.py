from numpy import random
from scipy.stats import sem

from strategies.motion_strategy import MotionStrategy
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

import math

from strategies.measurement_strategy import MeasurementStrategy
from utils.map3D import Map3D
from utils.particle_set import ParticleSet


"""
The Ahistoric Measurement Model raw weights of each particle by simply comparing currently measured
impedance to the reference prediction based on the current position of each particle.
"""

class AhistoricMeasurementModel3D(MeasurementStrategy):

    def __init__(self, map3D: Map3D):
        super().__init__()
        self.map3D = map3D

    def get_reference(self):
        return self.map3D

    def retrieve_signal_prediction(self, particle) -> float:
        local_reference_value = self.map3D.get_reference_value(
            branch=particle.get_state().get_position()["branch"],
            displacement=particle.get_state().get_position()["displacement"])
        return local_reference_value

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        for particle in particles:
            particle.weight = math.pow((measurement - self.retrieve_signal_prediction(particle=particle)), 2)
        return particles

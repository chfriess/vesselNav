from strategies.measurement_strategy import MeasurementStrategy
from utils.particle import Particle
from utils.particle_set import ParticleSet


class AhistoricMeasurementModel(MeasurementStrategy):

    def __init__(self, reference_signal: list):
        super().__init__()
        self.reference_signal = reference_signal

    def retrieve_signal_prediction(self, particle: Particle) -> float:
        position = round(particle.get_state().get_position())
        if position < 0:
            return self.reference_signal[0]
        elif position > len(self.reference_signal) - 1:
            return self.reference_signal[len(self.reference_signal) - 1]
        else:
            return self.reference_signal[position]

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        for particle in particles:
            particle.weight = abs(measurement - self.retrieve_signal_prediction(particle=particle))
        return particles

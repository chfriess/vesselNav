from strategies.measurement_strategy import MeasurementStrategy
from utils.particle import Particle
from utils.particle_set import ParticleSet


class AhistoricMeasurementModel(MeasurementStrategy):

    def __init__(self, reference_signal: list): # TODO: change to vessel tree reference

        super().__init__()
        self.reference_signal = reference_signal # TODO: change to vessel tree reference


    def retrieve_signal_prediction(self, particle: Particle) -> float:
        position = round(particle.get_state().get_position()) # TODO: change to vessel tree position estimate
        if position < 0:  # TODO: change to vessel tree position estimate
            return self.reference_signal[0]  # TODO: change to vessel tree reference

        elif position > len(self.reference_signal) - 1:  # TODO: change to vessel tree position estimate
            return self.reference_signal[len(self.reference_signal) - 1]  # TODO: change to vessel tree reference
        else:
            return self.reference_signal[position]  # TODO: change to vessel tree position estimate

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        for particle in particles:
            particle.weight = abs(measurement - self.retrieve_signal_prediction(particle=particle))
        return particles

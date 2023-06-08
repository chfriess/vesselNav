import numpy as np
from tslearn.metrics import dtw
from strategies.measurement_strategy import MeasurementStrategy
from utils.particle_reference_retriever import ParticleReferenceRetriever
from utils.particle_set import ParticleSet


class SlidingDTWMeasurementModel(MeasurementStrategy):

    def __init__(self, reference_signal: list):

        super().__init__()
        self.reference_signal = reference_signal

        self.measurement_history = []
        self.particle_reference_retriever = ParticleReferenceRetriever()

    def get_reference(self):
        return self.reference_signal

    def reset_measurement_history(self):
        self.measurement_history = []

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        self.measurement_history.append(measurement)
        if len(self.measurement_history) > 10:
            self.measurement_history = self.measurement_history[-10:]

        for particle in particles:
            particle.reference_history += self.particle_reference_retriever.retrieve_reference_update(
                particle, self.reference_signal)
            if len(particle.reference_history) > 10:
                particle.reference_history = particle.reference_history[-10:]
            particle.weight = dtw(self.measurement_history, particle.reference_history)
        return particles


class SlidingDerivativeDTWMeasurementModel(SlidingDTWMeasurementModel):

    @staticmethod
    def derive_series(series: list) -> list:
        if len(series) < 3:
            return series
        series_np = np.array(series)
        derivative = 0.25 * series_np[2:] + 0.5 * series_np[1:-1] - 0.75 * series_np[:-2]

        return list(derivative)

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        self.measurement_history.append(measurement)
        if len(self.measurement_history) > 10:
            self.measurement_history = self.measurement_history[-10:]

        for particle in particles:
            particle.reference_history += self.particle_reference_retriever.retrieve_reference_update(
                particle, self.reference_signal)
            if len(particle.reference_history) > 10:
                particle.reference_history = particle.reference_history[-10:]
            particle.weight = dtw(self.derive_series(self.measurement_history),
                                  self.derive_series(particle.reference_history))
        return particles


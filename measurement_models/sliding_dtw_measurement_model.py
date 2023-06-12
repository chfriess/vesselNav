import numpy as np
from tslearn.metrics import dtw
from strategies.measurement_strategy import MeasurementStrategy
from utils.map3D import Map3D
from utils.particle_reference_retriever import ParticleReferenceRetriever, ParticleReferenceRetriever3D
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
        if len(self.measurement_history) > 20:
            self.measurement_history = self.measurement_history[-20:]

        for particle in particles:
            particle.reference_history += self.particle_reference_retriever.retrieve_reference_update(
                particle, self.reference_signal)
            if len(particle.reference_history) > 20:
                particle.reference_history = particle.reference_history[-20:]
            particle.weight = dtw(self.measurement_history, particle.reference_history)
        return particles


class SlidingDerivativeDTWMeasurementModel(SlidingDTWMeasurementModel):

    @staticmethod
    def smooth_exponentially(data: list,
                             alpha: float = 0.5) -> list:
        if len(data) < 1:
            raise ValueError("list must contain elements")
        if alpha <= 0 or alpha >= 1:
            raise ValueError("alpha must be between 0 and 1")
        fitted_data = [data[0]]
        for index in range(1, len(data)):
            next_fit = alpha * data[index] + (1 - alpha) * data[index - 1]
            fitted_data.append(next_fit)
        return fitted_data

    def derive_series(self, series: list) -> list:
        if len(series) < 3:
            return series
        series_np = np.array(self.smooth_exponentially(series))
        derivative = 0.25 * series_np[2:] + 0.5 * series_np[1:-1] - 0.75 * series_np[:-2]

        return list(derivative)

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        self.measurement_history.append(measurement)
        if len(self.measurement_history) > 20:
            self.measurement_history = self.measurement_history[-20:]

        for particle in particles:
            particle.reference_history += self.particle_reference_retriever.retrieve_reference_update(
                particle, self.reference_signal)
            if len(particle.reference_history) > 20:
                particle.reference_history = particle.reference_history[-20:]
            particle.weight = dtw(self.derive_series(self.measurement_history),
                                  self.derive_series(particle.reference_history))
        return particles


class SlidingCombinedDerivativeDTWMeasurementModel(SlidingDerivativeDTWMeasurementModel):

    def alpha_derive_series(self, series: list) -> list:
        alpha = 0.5
        if len(series) < 3:
            return series
        series_np = np.array(series)
        derivative = self.derive_series(series)
        combination = alpha * series_np[2:] + (1 - alpha) * np.array(derivative)
        return list(combination)

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        self.measurement_history.append(measurement)
        if len(self.measurement_history) > 20:
            self.measurement_history = self.measurement_history[-20:]

        for particle in particles:
            particle.reference_history += self.particle_reference_retriever.retrieve_reference_update(
                particle, self.reference_signal)
            if len(particle.reference_history) > 20:
                particle.reference_history = particle.reference_history[-20:]
            particle.weight = dtw(self.alpha_derive_series(self.measurement_history),
                                  self.alpha_derive_series(particle.reference_history))
        return particles


class SlidingDTWMeasurementModel3D(MeasurementStrategy):
    def __init__(self, map3D: Map3D):
        self.map3D = map3D
        self.measurement_history = []
        self.particle_reference_retriever = ParticleReferenceRetriever3D()

    def get_reference(self):
        return self.map3D

    def reset_measurement_history(self):
        self.measurement_history = []

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        self.measurement_history.append(measurement)
        if len(self.measurement_history) > 20:
            self.measurement_history = self.measurement_history[-20:]

        for particle in particles:
            particle.reference_history += self.particle_reference_retriever.retrieve_reference_update(
                particle, self.map3D)
            if len(particle.reference_history) > 20:
                particle.reference_history = particle.reference_history[-20:]
            particle.weight = dtw(self.measurement_history, particle.reference_history)
        return particles

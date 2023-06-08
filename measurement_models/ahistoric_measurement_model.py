from strategies.measurement_strategy import MeasurementStrategy
from particles.particle import Particle
from utils.map3D import Map3D
from utils.particle_set import ParticleSet


class AhistoricMeasurementModel(MeasurementStrategy):

    def __init__(self, reference_signal: list):

        super().__init__()
        self.reference_signal = reference_signal

    def get_reference(self):
        return self.reference_signal

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


class AhistoricMeasurementModel3D(MeasurementStrategy):

    def __init__(self, map3D: Map3D):
        super().__init__()
        self.map3D = map3D

    def get_reference(self):
        return self.map3D

    def retrieve_signal_prediction(self, particle: Particle) -> float:
        position = round(particle.get_state().get_position())
        if position < 0:
            return self.map3D.get_vessel(particle.get_state().get_branch())[0]
        elif position > len(self.map3D.get_vessel(particle.get_state().get_branch())) - 1:
            return self.map3D.get_vessel(particle.get_state().get_branch())[-1]
        else:
            return self.map3D.get_vessel(particle.get_state().get_branch())[position]

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        for particle in particles:
            particle.weight = abs(measurement - self.retrieve_signal_prediction(particle=particle))
        return particles

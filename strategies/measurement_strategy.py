import sys
from abc import abstractmethod
from utils.particle_set import ParticleSet


class MeasurementStrategy:

    def weight_particles(self, particles: ParticleSet, measurement: float):
        particles = self.raw_weight_particles(particles=particles, measurement=measurement)
        particles = self.invert_raw_weights(particles=particles)
        particles = self.normalize_particles(particles=particles)
        return particles


    @abstractmethod
    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        raise NotImplementedError

    @abstractmethod
    def get_reference(self):
        raise NotImplementedError

    def normalize_particles(self, particles: ParticleSet) -> ParticleSet:
        normalizer = self.calculate_normalizer(particles)
        if normalizer == 0:
            return particles
        for particle in particles:
            particle.weight = particle.weight / normalizer
        return particles

    @staticmethod
    def calculate_normalizer(particles: ParticleSet) -> float:
        normalizer = 0
        for particle in particles:
            normalizer += particle.weight
        if normalizer == 0:
            normalizer = sys.float_info.max
        return normalizer

    @staticmethod
    def invert_raw_weights(particles: ParticleSet) -> ParticleSet:
        for particle in particles:
            if particle.weight > 0.0001:
                particle.weight = 1 / particle.weight
            else:
                particle.weight = 10_000
        return particles

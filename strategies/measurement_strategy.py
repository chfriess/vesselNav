import math
import statistics
import sys
from abc import abstractmethod
from utils.particle_set import ParticleSet


class MeasurementStrategy:

    def weight_particles(self, particles: ParticleSet, measurement: float):
        particles = self.raw_weight_particles(particles=particles, measurement=measurement)
        particles = self.z_and_sigmoid_transform_particles(particles=particles)
        particles = self.normalize_particles(particles=particles)
        return particles

    @abstractmethod
    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        raise NotImplementedError

    @abstractmethod
    def get_reference(self):
        raise NotImplementedError

    def z_and_sigmoid_transform_particles(self, particles: ParticleSet) -> ParticleSet:
        mu = 0
        sigma = 0
        try:
            mu, sigma = self.determine_weight_mean_and_variance(particles)
        except statistics.StatisticsError:
            print("Statistics Error occurred")
            print(len(particles))
        if sigma == 0:
            sigma = 1
        for particle in particles:
            particle.weight = 1 / (self.sigmoid_transform((particle.weight - mu) / sigma))
        return particles

    @staticmethod
    def determine_weight_mean_and_variance(particles: ParticleSet) -> (float, float):
        weight_list = []
        for particle in particles:
            weight_list.append(particle.weight)
        return statistics.mean(weight_list), statistics.stdev(weight_list)

    @staticmethod
    def sigmoid_transform(x: float) -> float:
        try:
            acc = 1 + math.e ** (-x)
        except OverflowError:
            acc = 1
        try:
            result = 1 / acc
        except OverflowError:
            result = 0
        return result

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
            if particle.weight != 0:
                particle.weight = 1 / particle.weight
            else:
                particle.weight = 10_000
        return particles

import math
import statistics
from abc import abstractmethod
import logging
from collections import OrderedDict
from statistics import mean
import numpy as np
from sklearn.cluster import DBSCAN
from filter.particle_filter import ParticleFilter
from utils.position_estimate import PositionEstimate
from utils.particle_filter_component_enums import MeasurementType, InjectorType
from utils.particle_set import ParticleSet


class ModelInterface:
    def __init__(self, particle_filter: ParticleFilter = None,
                 particles: ParticleSet = None) -> None:

        self.particle_filter = particle_filter
        self.particles = particles

        self.update_steps = 1

    def reset_model(self):
        self.update_steps = 1

    @staticmethod
    def normalize_values(data: list) -> list:
        mu = statistics.mean(data)
        sigma = statistics.stdev(data)
        for i, el in enumerate(data):
            data[i] = (el - mu) / sigma
        return data

    @staticmethod
    def predict_impedance_from_diameter(diameter):
        # expects diameter in mm, converts it to m
        diameter = diameter / 1000
        circumference = diameter * math.pi
        csa = ((diameter / 2) ** 2) * math.pi
        sensor_distance = 3 / 1000
        tissue_conductivity = 0.30709
        blood_conductivity = 0.7
        return 1000 * ((csa * blood_conductivity) / sensor_distance + tissue_conductivity * circumference) ** (-1)

    @abstractmethod
    def setup_particle_filter(self,
                              map_path: str,
                              measurement_model: MeasurementType,
                              injector_type: InjectorType,
                              alpha_center: float
                              ):
        raise NotImplementedError

    @abstractmethod
    def setup_particles(self,
                        number_of_particles: int,
                        initial_position_center: float = 0.0,
                        initial_position_variance: float = 0.0,
                        alpha_center: float = 2.0,
                        alpha_variance: float = 0.1,
                        initial_branch: int = 0):
        raise NotImplementedError

    @staticmethod
    def setup_logger(loglevel: int,
                     log_directory: str,
                     filename: str):

        logger = logging.getLogger()
        if len(logger.handlers) > 0:
            for i in range(len(logger.handlers)):
                logger.removeHandler(logger.handlers[i])

        logger.setLevel(loglevel)

        file_handler = logging.FileHandler(log_directory + filename + ".log")
        formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    def update_model(self, displacement: float, impedance: float) -> None:
        logging.info("Update step #: " + str(self.update_steps))
        logging.info("Displacement measurement: " + str(displacement))
        logging.info("Impedance measurement: " + str(impedance))
        self.particles = self.particle_filter.filter(
            previous_particle_set=self.particles,
            displacement_measurement=displacement,
            impedance_measurement=impedance)
        for particle in self.particles:
            logging.debug("UpdatedParticle: " + str(particle))
        logging.info("Number of Particles: " + str(len(self.particles)))
        self.update_steps += 1

    @staticmethod
    def get_values_length(d):
        key, values = d
        return len(values)

    @staticmethod
    def estimate_current_position(self) -> PositionEstimate:
        raise NotImplementedError

    def get_particles(self):
        return self.particles

    def get_current_average_alpha(self) -> float:
        alphas = []
        for particle in self.particles:
            alphas.append(particle.state.alpha)
        return mean(alphas)

    def calculate_clusters_in_particle_set(self, positions) -> OrderedDict:
        reshaped_positions = np.reshape(positions, (-1, 1))
        clustering1 = DBSCAN(eps=3, min_samples=2).fit(reshaped_positions)

        labels = clustering1.labels_
        cluster_indices = list(np.unique(labels))

        if -1 in cluster_indices:
            cluster_indices.remove(-1)
        d = {}
        for index in cluster_indices:
            d[index] = [y for (x, y) in list(zip(labels, positions)) if x == index]

        clusters = OrderedDict(sorted(d.items(), key=self.get_values_length, reverse=True))
        return clusters

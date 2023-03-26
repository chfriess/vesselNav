from collections import OrderedDict

import numpy as np

import logging
from scipy.stats import sem
from statistics import mean
from sklearn.cluster import DBSCAN
import os

from filter.particle_filter import ParticleFilter
from utils.cluster_position_estimate import ClusterPositionEstimate
from utils.particle_set import ParticleSet
from utils.position_estimate import PositionEstimate


class Model:
    os.chdir("C:\\Users\\Chris\\OneDrive\\Desktop\\")
    logging.basicConfig(
        filename='particleFilterLog.log',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self, particle_filter: ParticleFilter,
                 particles: ParticleSet,
                 loglevel: int = logging.INFO,
                 log_directory: str = "C:\\Users\\Chris\\OneDrive\\Desktop\\") -> None:
        self.particle_filter = particle_filter
        self.particles = particles
        self.setup_logger(loglevel=loglevel,
                          log_directory=log_directory)

    @staticmethod
    def setup_logger(loglevel: int,
                     log_directory: str):
        os.chdir(log_directory)
        logging.basicConfig(
            filename='Model.log',
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=loglevel,
            datefmt='%Y-%m-%d %H:%M:%S')

    def update_model(self, displacement: float, impedance: float) -> None:
        logging.info("Displacement measurement: " + str(displacement))
        logging.info("Impedance measurement: " + str(impedance))
        self.particles = self.particle_filter.filter(
            previous_particle_set=self.particles,
            displacement_measurement=displacement,
            impedance_measurement=impedance)
        for particle in self.particles:
            logging.debug("UpdatedParticle: " + str(particle))
        logging.info("Number of Particles: " + str(len(self.particles)))

    def estimate_current_position_dbscan(self) -> ClusterPositionEstimate:
        positions = [particle.state.position for particle in self.particles]
        reshaped_positions = np.reshape(positions, (-1, 1))
        clustering1 = DBSCAN(eps=3, min_samples=2).fit(reshaped_positions)

        labels = clustering1.labels_
        cluster_indices = list(np.unique(labels))

        no_clusters = len(np.unique(labels))
        no_noise = int(np.sum(np.array(labels) == -1, axis=0))

        if -1 in cluster_indices:
            cluster_indices.remove(-1)
        d = {}
        for index in cluster_indices:
            d[index] = [y for (x, y) in list(zip(labels, positions)) if x == index]

        od = OrderedDict(sorted(d.items(), key=get_values_length, reverse=True))
        first_cluster = None
        second_cluster = None
        if len(od) > 0:
            first_cluster = PositionEstimate(mean(od[0]), sem(od[0]))
        if len(od) > 1:
            second_cluster = PositionEstimate(mean(od[1]), sem(od[1]))

        position_estimate = ClusterPositionEstimate(first_cluster=first_cluster, second_cluster=second_cluster,
                                                    number_of_clusters=no_clusters, number_of_noise=no_noise)
        logging.info("Best Position Estimate mean/sem = " + str(position_estimate) + "\n")
        return position_estimate

    def estimate_current_position_mean(self) -> PositionEstimate:
        # Resampling step already has taken place, therefore no weighted average is necessary
        position_sum = 0
        weight_sum = 0
        positions = []
        for particle in self.particles:
            position_sum += particle.state.position * particle.weight
            weight_sum += particle.weight
            positions.append(particle.state.position)
        if weight_sum == 0:
            position_estimate = PositionEstimate(mean(positions), sem(positions))
        else:
            position_estimate = PositionEstimate(position_sum / weight_sum, sem(positions))
        logging.info("Best Position Estimate mean/sem = " + str(position_estimate) + "\n")
        return position_estimate


def get_values_length(d):
    key, values = d
    return len(values)

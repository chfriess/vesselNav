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
        positions = [[particle.state.position.displacement, particle.state.position.branch]
                     for particle in self.particles]   # TODO: change to vessel tree position estimate
        reshaped_positions = np.reshape(positions, (-1, 2))
        print(reshaped_positions)
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

        #TODO: improve position estiamte
        position_estimate = ClusterPositionEstimate(positions=[],
                                                    clusters=od,
                                                    number_of_clusters=no_clusters,
                                                    number_of_noise=no_noise)
        logging.info("Best Position Estimate mean/sem = " + str(position_estimate.get_positions()[0]) + "\n")
        return position_estimate


def get_values_length(d):
    key, values = d
    return len(values)

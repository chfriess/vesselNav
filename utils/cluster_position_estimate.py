from collections import OrderedDict

from utils.position_estimate import PositionEstimate

# TODO
class ClusterPositionEstimate:

    def __init__(self,
                 positions: list,
                 clusters: OrderedDict,
                 number_of_clusters: int,
                 number_of_noise: int) -> None:
        self.positions = positions
        self.clusters = clusters
        self.number_of_clusters = number_of_clusters
        self.number_of_noise = number_of_noise

    def get_positions(self):
        return self.positions

    def get_clusters(self):
        return self.clusters

    def get_number_of_cluster(self):
        return self.number_of_clusters

    def get_number_of_noise(self):
        return self.number_of_noise

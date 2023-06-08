from abc import abstractmethod

from utils.position import Position, Position3D


class PositionEstimate:
    @abstractmethod
    def get_best_estimate(self):
        raise NotImplementedError

    @abstractmethod
    def get_error_of_best_estimate(self):
        raise NotImplementedError


class ClusterPositionEstimate(PositionEstimate):

    def __init__(self,
                 first_cluster: Position,
                 second_cluster: Position,
                 number_of_clusters: int,
                 number_of_noise: int) -> None:
        self.first_cluster = first_cluster
        self.second_cluster = second_cluster
        self.number_of_clusters = number_of_clusters
        self.number_of_noise = number_of_noise

    def __str__(self):
        return f'[first cluster: {str(self.first_cluster)} | second cluster: {str(self.second_cluster)} | ' \
               f'number of clusters: {str(self.number_of_clusters)} |' \
               f' number of noise points: {str(self.number_of_noise)}   ]'

    def get_first_cluster(self):
        return self.first_cluster

    def get_first_cluster_mean(self):
        if self.first_cluster is not None:
            return self.first_cluster.center
        else:
            return "__"

    def get_first_cluster_error(self):
        if self.first_cluster is not None:
            return self.first_cluster.error
        else:
            return "__"

    def get_second_cluster(self):
        return self.second_cluster

    def get_second_cluster_mean(self):
        if self.second_cluster is not None:
            return self.second_cluster.center
        else:
            return "__"

    def get_second_cluster_error(self):
        if self.second_cluster is not None:
            return self.second_cluster.error
        else:
            return "__"

    def get_number_of_cluster(self):
        return self.number_of_clusters

    def get_number_of_noise(self):
        return self.number_of_noise

    def get_best_estimate(self):
        return self.get_first_cluster_mean()

    def get_error_of_best_estimate(self):
        return self.get_first_cluster_error()


class ClusterPositionEstimate3D(PositionEstimate):

    def __init__(self,
                 number_of_cluster: int = 0):
        self.clusters = {}
        self.number_of_clusters = number_of_cluster

    def __str__(self):
        pass

    def add_cluster(self,
                    cluster: Position3D):
        if cluster.branch not in self.clusters.keys():
            self.clusters[cluster.branch] = [cluster]
        else:
            self.clusters[cluster.branch].append(cluster)

    def get_clusters(self):
        return self.clusters

    def get_best_cluster(self):
        if len(self.clusters) == 0:
            return None
        best_cluster = self.clusters[0]
        for cluster in self.clusters:
            if cluster.get_number_of_particles > best_cluster.get_number_of_particles():
                best_cluster = cluster
        return best_cluster

    def get_best_estimate(self):
        return self.get_best_cluster().get_center(), self.get_best_cluster().get_branch()

    def get_error_of_best_estimate(self):
        return self.get_best_cluster().get_error()

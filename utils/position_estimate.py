from abc import abstractmethod

from utils.position import Position3D


class PositionEstimate:
    @abstractmethod
    def get_clusters(self):
        raise NotImplementedError

    @abstractmethod
    def get_first_cluster(self):
        raise NotImplementedError

    @abstractmethod
    def get_second_cluster(self):
        raise NotImplementedError

    @abstractmethod
    def get_first_cluster_mean(self):
        raise NotImplementedError

    @abstractmethod
    def get_first_cluster_error(self):
        raise NotImplementedError

    @abstractmethod
    def get_second_cluster_mean(self):
        raise NotImplementedError

    @abstractmethod
    def get_second_cluster_error(self):
        raise NotImplementedError

    @abstractmethod
    def get_number_of_clusters(self):
        raise NotImplementedError

    @abstractmethod
    def get_number_of_noise(self):
        raise NotImplementedError


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

    def get_first_cluster(self):
        if len(self.clusters) == 0:
            return None
        best_cluster = None
        best_cluster_size = 0
        for branch in self.clusters.keys():
            for cluster in self.clusters[branch]:
                if cluster.get_number_of_particles() > best_cluster_size:
                    best_cluster = cluster
                    best_cluster_size = cluster.get_number_of_particles()
        return best_cluster

    def get_second_cluster(self):
        # TODO: speed up of this temporary hack
        if len(self.clusters) == 0:
            return None
        best_cluster = None
        second_best_cluster = None
        best_cluster_size = 0
        for branch in self.clusters.keys():
            for cluster in self.clusters[branch]:
                if cluster.get_number_of_particles() > best_cluster_size:
                    second_best_cluster = best_cluster
                    best_cluster = cluster
                    best_cluster_size = cluster.get_number_of_particles()
        return second_best_cluster

    def get_first_cluster_mean(self):
        return [self.get_first_cluster().get_center(), self.get_first_cluster().get_branch()]

    def get_first_cluster_error(self):
        return self.get_first_cluster().get_error()

    def get_second_cluster_mean(self):
        second_cluster = self.get_second_cluster()
        if second_cluster is not None:
            return [self.get_second_cluster().get_center(), self.get_second_cluster().get_branch()]
        else:
            return self.get_first_cluster_mean()

    def get_second_cluster_error(self):
        second_cluster = self.get_second_cluster()
        if second_cluster is not None:
            return second_cluster.get_error()
        else:
            return self.get_first_cluster_error()

    def get_number_of_clusters(self):
        pass

    def get_number_of_noise(self):
        raise NotImplementedError("Number of noise points not implemented for 3D position estimate")

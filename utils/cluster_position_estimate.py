from utils.position_estimate import PositionEstimate


class ClusterPositionEstimate:

    def __init__(self,
                 first_cluster: PositionEstimate,
                 second_cluster: PositionEstimate,
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

    def get_second_cluster(self):
        return self.second_cluster

    def get_number_of_cluster(self):
        return self.number_of_clusters

    def get_number_of_noise(self):
        return self.number_of_noise

from utils.cluster_position_estimate import ClusterPositionEstimate


class MultidimensionalClusterPositionEstimate:

    def __init__(self,
                 vessel_index: int,
                 cluster_position_estimate: ClusterPositionEstimate):
        self.vessel_index = vessel_index
        self.cluster_position_estimate = cluster_position_estimate

    def __str__(self):
        return f' index of vessel: {str(self.vessel_index)}' \
                f'[cluster position estimates: {str(self.cluster_position_estimate)}  ]'

    def get_vessel_index(self):
        return self.vessel_index

    def get_cluster_position_estimate(self):
        return self.cluster_position_estimate

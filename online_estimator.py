import logging

import numpy as np

from filter.model import Model
from utils.cluster_position_estimate import ClusterPositionEstimate
from utils.particle_filter_component_enums import MeasurementType


class OnlineEstimator:

    def __init__(self, model: Model = None):
        self.model = model

    def setup_model(self,
                    reference_path: str,
                    destination_path: str,
                    filename: str,
                    measurement_type: MeasurementType = MeasurementType.AHISTORIC,
                    number_of_particles: int = 1000,
                    initial_position_center: float = 0,
                    initial_position_variance: float = 0.5,
                    alpha_center: float = 1.5,
                    alpha_variance: float = 0.1,
                    ):
        self.model = Model()
        ref = list(np.load(reference_path))
        self.model.setup_logger(loglevel=logging.INFO,
                                log_directory=destination_path,
                                filename=filename + "_log")
        self.model.setup_particle_filter(reference=ref,
                                         measurement_model=measurement_type)
        self.model.setup_particles(number_of_particles=number_of_particles,
                                   initial_position_center=initial_position_center,
                                   inital_position_variance=initial_position_variance,
                                   alpha_center=alpha_center,
                                   alpha_variance=alpha_variance
                                   )

    def update_step(self, displacement: float, impedance: float) -> ClusterPositionEstimate:
        self.model.update_model(displacement=displacement, impedance=impedance)
        return self.model.estimate_current_position_dbscan()

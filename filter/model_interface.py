from abc import abstractmethod
import logging
from statistics import mean
from filter.particle_filter import ParticleFilter
from utils.map3D import Map3D
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

    @abstractmethod
    def setup_particle_filter(self,
                              map3D: Map3D,
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

    @abstractmethod
    def update_model(self, displacement: float, impedance: float) -> None:
        raise NotImplementedError

    @staticmethod
    def get_values_length(d):
        key, values = d
        return len(values)

    @staticmethod
    def estimate_current_position(self) -> PositionEstimate:
        raise NotImplementedError

    def get_current_average_alpha(self) -> float:
        alphas = []
        for particle in self.particles:
            alphas.append(particle.state.alpha)
        return mean(alphas)



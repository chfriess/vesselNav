from collections import OrderedDict
import numpy as np
import logging
from scipy.stats import sem
from statistics import mean
from sklearn.cluster import DBSCAN
from filter.particle_filter import ParticleFilter
from injectors.alpha_variance_injector import AlphaVariationInjector
from injectors.random_particle_injector import RandomParticleInjector
from measurement_models.ahistoric_measurement_model import AhistoricMeasurementModel
from measurement_models.sliding_dtw_measurement_model import SlidingDTWMeasurementModel
from motion_models.motion_model import MotionModel
from resamplers.low_variance_resampler import LowVarianceResampler
from utils.cluster_position_estimate import ClusterPositionEstimate
from utils.particle_filter_component_enums import MeasurementType, InjectorType
from particles.particle import Particle
from utils.particle_set import ParticleSet
from utils.position_estimate import PositionEstimate
from particles.sliding_particle import SlidingParticle
from particles.state import State


class Model:
    """
    os.chdir("C:\\Users\\Chris\\OneDrive\\Desktop\\")
    logging.basicConfig(
        filename='particleFilterLog.log',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    """

    def __init__(self, particle_filter: ParticleFilter = None,
                 particles: ParticleSet = None) -> None:

        self.particle_filter = particle_filter
        self.particles = particles

        self.update_steps = 1

    def reset_model(self):
        self.update_steps = 1

    def setup_particle_filter(self,
                              reference: list,
                              measurement_model: MeasurementType,
                              injector_type: InjectorType,
                              alpha_center: float
                              ):
        if injector_type == InjectorType.ALPHA_VARIANCE:
            injection_strategy = AlphaVariationInjector(map_borders=[0, len(reference)], alpha_center=alpha_center)
            logging.info("injector: alpha variance")
        elif injector_type == InjectorType.RANDOM_PARTICLE:
            injection_strategy = RandomParticleInjector(map_borders=[0, len(reference)])
            logging.info("injector: random particle")
        else:
            raise ValueError("Select a valid injection strategy: alpha variance or random particle")

        if measurement_model == MeasurementType.AHISTORIC:
            measurement_strategy = AhistoricMeasurementModel(reference_signal=reference)
            logging.info("measurement model: ahistoric")
        elif measurement_model == MeasurementType.SLIDING_DTW:
            measurement_strategy = SlidingDTWMeasurementModel(reference_signal=reference)
            logging.info("measurement model: sliding_dtw")
        else:
            raise ValueError("Select a valid measurement strategy: ahistoric or sliding_dtw")
        motion_model = MotionModel()
        resampling_strategy = LowVarianceResampler()

        self.particle_filter = ParticleFilter(motion_model=motion_model,
                                              measurement_strategy=measurement_strategy,
                                              resampler=resampling_strategy,
                                              injector=injection_strategy)

    def setup_particles(self,
                        number_of_particles: int,
                        initial_position_center: float = 0.0,
                        inital_position_variance: float = 0.0,
                        alpha_center: float = 2.0,
                        alpha_variance: float = 0.1):
        if self.particle_filter is None:
            raise ValueError("You must setup the particle filter before choosing the number of particles")
        self.particles = ParticleSet()
        logging.info("Number of particles = " + str(number_of_particles))
        logging.info("initial position =  " + str(initial_position_center) + " +/- " + str(inital_position_variance))
        logging.info("alpha = " + str(alpha_center) + " +/- " + str(alpha_variance) + "\n\n")

        if isinstance(self.particle_filter.measurement_strategy, AhistoricMeasurementModel):
            for index in range(number_of_particles):
                state = State()
                state.assign_random_position(center=initial_position_center, variance=inital_position_variance)
                state.assign_random_alpha(center=alpha_center, variance=alpha_variance)
                particle = Particle(state=state, weight=0)
                self.particles.append(particle)
        if isinstance(self.particle_filter.measurement_strategy, SlidingDTWMeasurementModel):
            for index in range(number_of_particles):
                state = State()
                state.assign_random_position(center=initial_position_center, variance=inital_position_variance)
                particle = SlidingParticle(state=state, weight=0)
                self.particles.append(particle)

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
            logging.debug("UpdatedParticle: " + str(particle.get_state()))
        logging.info("Number of Particles: " + str(len(self.particles)))
        self.update_steps += 1

    @staticmethod
    def get_values_length(d):
        key, values = d
        return len(values)

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

        od = OrderedDict(sorted(d.items(), key=self.get_values_length, reverse=True))
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

    def get_current_average_alpha(self) -> float:
        alphas = []
        for particle in self.particles:
            alphas.append(particle.state.alpha)
        return mean(alphas)



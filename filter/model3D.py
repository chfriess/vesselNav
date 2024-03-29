from filter.model_interface import ModelInterface
from filter.particle_filter import ParticleFilter
from injectors.alpha_variance_injector import AlphaVariationInjector
from injectors.random_particle_injector import RandomParticleInjector3D
from measurement_models.ahistoric_measurement_model import AhistoricMeasurementModel3D
from measurement_models.sliding_dtw_measurement_model import SlidingCombinedDerivativeDTWMeasurementModel3D, \
    SlidingDTWMeasurementModel3D
from motion_models.motion_model import MotionModel3D
from particles.particle import Particle3D, SlidingParticle3D
from particles.state import State3D
from resamplers.low_variance_resampler import LowVarianceResampler
from utils.map3D import Map3D
from utils.particle_filter_component_enums import MeasurementType, InjectorType
from utils.particle_set import ParticleSet
from utils.position import Position3D
from utils.position_estimate import PositionEstimate, ClusterPositionEstimate3D
from scipy.stats import sem
from statistics import mean
import logging


class Model3D(ModelInterface):
    def setup_particle_filter(self, map_path: str,
                              measurement_model: MeasurementType,
                              injector_type: InjectorType,
                              alpha_center: float):
        map3D = Map3D()
        map3D.load_map(map_path)

        if injector_type == InjectorType.ALPHA_VARIANCE:
            injection_strategy = AlphaVariationInjector(alpha_center=alpha_center)
            logging.info("injector: alpha variance")
        elif injector_type == InjectorType.RANDOM_PARTICLE:
            injection_strategy = RandomParticleInjector3D(map3D)
            logging.info("injector: random particle")
        else:
            raise ValueError("Select a valid injection strategy: alpha variance or random particle")

        if measurement_model == MeasurementType.AHISTORIC:
            measurement_strategy = AhistoricMeasurementModel3D(map3D=map3D)
            logging.info("measurement model: ahistoric")
        elif measurement_model == MeasurementType.SLIDING_DTW:
            measurement_strategy = SlidingCombinedDerivativeDTWMeasurementModel3D(map3D=map3D)
            logging.info("measurement model: sliding_dtw")
        else:
            raise ValueError("Select a valid measurement strategy: ahistoric or sliding dtw")
        motion_model = MotionModel3D(map3D=map3D)
        resampling_strategy = LowVarianceResampler()
        self.particle_filter = ParticleFilter(motion_model=motion_model,
                                              measurement_strategy=measurement_strategy,
                                              resampler=resampling_strategy,
                                              injector=injection_strategy)

    def setup_particles(self, number_of_particles: int,
                        initial_position_center: float = 0.0,
                        initial_position_variance: float = 0.0,
                        alpha_center: float = 2.0,
                        alpha_variance: float = 0.1,
                        initial_branch: int = 0):
        if self.particle_filter is None:
            raise ValueError("You must setup the particle filter before choosing the number of particles")
        self.particles = ParticleSet()
        logging.info("Number of particles = " + str(number_of_particles))
        logging.info("initial position =  " + str(initial_position_center) + " +/- " + str(initial_position_variance))
        logging.info("alpha = " + str(alpha_center) + " +/- " + str(alpha_variance) + "\n\n")
        if isinstance(self.particle_filter.measurement_strategy, AhistoricMeasurementModel3D):
            for _ in range(number_of_particles):
                state = State3D()
                state.set_branch(initial_branch)
                state.assign_random_position(center=initial_position_center, variance=initial_position_variance)
                state.assign_random_alpha(center=alpha_center, variance=alpha_variance)
                particle = Particle3D(state=state, weight=0)
                self.particles.append(particle)
        elif isinstance(self.particle_filter.measurement_strategy, SlidingDTWMeasurementModel3D):
            for _ in range(number_of_particles):
                state = State3D()
                state.set_branch(initial_branch)
                state.assign_random_position(center=initial_position_center, variance=initial_position_variance)
                state.assign_random_alpha(center=alpha_center, variance=alpha_variance)
                particle = SlidingParticle3D(state=state, weight=0)
                self.particles.append(particle)

    def estimate_current_position(self) -> PositionEstimate:
        position_estimate = ClusterPositionEstimate3D()
        particles_per_branch = {}
        for particle in self.particles:
            branch = particle.get_position()["branch"]
            if branch not in particles_per_branch.keys():
                particles_per_branch[branch] = [particle.get_position()["displacement"]]
            else:
                particles_per_branch[branch].append(particle.get_position()["displacement"])
        for key in particles_per_branch.keys():
            clusters = self.calculate_clusters_in_particle_set(particles_per_branch[key])
            for i, _ in enumerate(clusters):
                position_estimate.add_cluster(Position3D(center=mean(clusters[i]),
                                                         error=sem(clusters[i]),
                                                         number_of_particles=len(clusters[i]),
                                                         branch=key))
        return position_estimate
